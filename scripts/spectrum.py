# https://github.com/Haoming02/sd-webui-forge-classic/blob/neo/extensions-builtin/sd_forge_spectrum/scripts/spectrum.py
# https://github.com/ruwwww/ComfyUI-Spectrum-sdxl/blob/main/src/spectrum_node.py
# https://github.com/wai55555/sd-webui-reforge-spectrum/blob/main/scripts/spectrum_reforge.py

import sys
import math
import torch
import gradio as gr
from spectrum_core_faithful.forecaster import ChebyshevForecaster, Spectrum

from modules import scripts, shared
from modules.infotext_utils import PasteField
from modules.ui_components import InputAccordion


class SpectrumScript(scripts.Script):
    def title(self):
        return "Spectrum Adaptive Forecaster"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, *args, **kwargs):
        with InputAccordion(False, label=self.title()) as enable:
            with gr.Row():
                w = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.25,
                    step=0.05,
                    label="Prediction Weighting (w)",
                    info="higher = long-term trend ; lower = short-term changes",
                )
                m = gr.Slider(
                    minimum=1,
                    maximum=16,
                    value=6,
                    step=1,
                    label="Polynomial Degree (m)",
                    info="higher = complex & subtle patterns ; lower = stable & faster",
                )
            with gr.Row():
                lam = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=0.5,
                    step=0.05,
                    label="Regularization (lam)",
                    info="higher = reduce overfitting ; lower = fit more data",
                )
                window_size = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=2,
                    step=1,
                    label="Cache Window (window_size)",
                    info="higher = skip more steps ; lower = slower but more accurate",
                )
            flex_window = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                value=0.0,
                step=0.05,
                label="Window Growth (flex_window)",
                info="higher = more speed & less accurate ; lower = more consistent accuracy but less speed gain",
            )
            with gr.Row():
                warmup_steps = gr.Slider(
                    minimum=0,
                    maximum=20,
                    value=6,
                    step=1,
                    label="Warmup Steps",
                    info="Run the full model before caching starts",
                )
                stop_caching_step = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.9,
                    step=0.05,
                    label="Stop Caching Step",
                    info="Run the full model for the last few steps",
                )

        self.infotext_fields = [
            PasteField(enable, "spec_enable"),
            PasteField(w, "spec_w"),
            PasteField(m, "spec_m"),
            PasteField(lam, "spec_lam"),
            PasteField(window_size, "spec_window_size"),
            PasteField(flex_window, "spec_flex_window"),
            PasteField(warmup_steps, "spec_warmup_steps"),
            PasteField(stop_caching_step, "spec_stop_caching_step"),
        ]

        return [enable, w, m, lam, window_size, flex_window, warmup_steps, stop_caching_step]

    @staticmethod
    def patch(model, steps: int, w: float, m: int, lam: float, window_size: int, flex_window: float, warmup_steps: int, stop_caching_step: float):
        state = getattr(model, 'spectrum_state', {})
        model.spectrum_state = state

        state = {
            "forecasters": None,  
            "cnt": 0,
            "num_cached": [0],  
            "curr_ws": float(window_size),
            "last_t": -1,
            "total_runs": 0,
        }

        # Remove any lingering hooks from previously bypassed models to clear global memory leaks
        diffusion_model = model.model.diffusion_model
        if hasattr(diffusion_model, "_sp_hooks"):
            for h in diffusion_model._sp_hooks: h.remove()
            diffusion_model._sp_hooks = []
        if hasattr(diffusion_model, "spectrum_hook_handles"):
            for h in diffusion_model.spectrum_hook_handles: h.remove()
            diffusion_model.spectrum_hook_handles = []

        forecast_stream = torch.cuda.Stream() if torch.cuda.is_available() else None

        def spectrum_unet_wrapper(model_function, kwargs):
            x, timestep, c = kwargs["input"], kwargs["timestep"], kwargs["c"]
            batch_size = x.shape[0]
            t_scalar = timestep[0].item() if isinstance(timestep, torch.Tensor) and timestep.numel() > 0 else float(timestep)

            if t_scalar > state["last_t"]:
                state["forecasters"] = None
                state["cnt"] = 0
                state["num_cached"] = [0] * batch_size
                state["curr_ws"] = float(window_size)
                state["total_runs"] += 1
                # print(f"[Spectrum] Detected new pass ({state['total_runs']}) - Reset state")

            state["last_t"] = t_scalar

            if state["forecasters"] is None:
                state["forecasters"] = [
                    Spectrum(
                        cheb_like=ChebyshevForecaster(M=m, K=100, lam=lam, t_max=float(steps)),
                        w=w
                    ) for _ in range(batch_size)
                ]

            if len(state["num_cached"]) != batch_size:
                state["num_cached"] = [0] * batch_size

            do_actual = torch.ones(batch_size, dtype=torch.bool, device=x.device)
            for i in range(batch_size):
                is_micro_final = False
                auto_stop = int(steps * stop_caching_step)
                if state["cnt"] >= auto_stop:
                    is_micro_final = True
                if state["cnt"] >= warmup_steps and not is_micro_final:
                    do_actual[i] = (state["num_cached"][i] + 1) % math.floor(state["curr_ws"]) == 0

            real_mask = do_actual
            forecast_mask = ~do_actual

            out = torch.empty_like(x)

            # ====================== REAL STEP: Run full diffusion_model → capture RAW 4D tensor (post final_layer/unpatchify) ======================
            if real_mask.any():
                x_real = x[real_mask]
                timestep_real = timestep[real_mask.to(timestep.device)] if isinstance(timestep, torch.Tensor) and timestep.shape[0] == batch_size else timestep
                c_real = {k: v[real_mask.to(v.device)] if isinstance(v, torch.Tensor) and v.shape[0] == batch_size else v for k, v in c.items()}

                with torch.cuda.stream(torch.cuda.default_stream()):
                    raw_real = model_function(x_real, timestep_real, **c_real)  # ← RAW 4D tensor from diffusion_model

                # ComfyUI's Sampler automatically applies calculate_denoised externally on the UNet's return value
                out[real_mask] = raw_real

                # Update forecaster with the RAW tensor (Spatial Feature)
                real_indices = real_mask.nonzero().squeeze()
                if real_indices.dim() == 0:
                    real_indices = [real_indices.item()]
                else:
                    real_indices = real_indices.tolist()

                for i, idx in enumerate(real_indices):
                    state["forecasters"][idx].update(state["cnt"], raw_real[i])
                    state["num_cached"][idx] = 0

                # print(f"[Spectrum] Step {state['cnt']}: Real forward (RAW captured) for {real_mask.sum().item()} items")

            # ====================== SKIP STEP: Forecast RAW tensor ======================
            if forecast_mask.any():
                forecast_indices = forecast_mask.nonzero().squeeze()
                if forecast_indices.dim() == 0:
                    forecast_indices = [forecast_indices.item()]
                else:
                    forecast_indices = forecast_indices.tolist()

                out_forecast = torch.empty((len(forecast_indices), *x.shape[1:]), device=x.device, dtype=x.dtype)

                if forecast_stream:
                    with torch.cuda.stream(forecast_stream):
                        for j, i in enumerate(forecast_indices):
                            raw_pred = state["forecasters"][i].predict(state["cnt"])  # forecasted RAW 4D tensor
                            out_forecast[j] = raw_pred

                        out[forecast_mask] = out_forecast
                        for i in forecast_indices:
                            state["num_cached"][i] += 1
                    torch.cuda.current_stream().wait_stream(forecast_stream)
                else:
                    # CPU fallback
                    for j, i in enumerate(forecast_indices):
                        raw_pred = state["forecasters"][i].predict(state["cnt"])
                        out_forecast[j] = raw_pred

                    out[forecast_mask] = out_forecast
                    for i in forecast_indices:
                        state["num_cached"][i] += 1

                # print(f"[Spectrum] Step {state['cnt']}: Forecast (RAW predicted) for {forecast_mask.sum().item()} items")

            if state["cnt"] >= warmup_steps:
                state["curr_ws"] += flex_window

            state["cnt"] += 1
            return out

        new_model = model.clone()

        # SAFEGUARD: Deepcopy model_options to prevent the wrapper from permanently
        # mutating the globally cached CheckpointLoader model in memory.
        import copy
        if hasattr(model, 'model_options'):
            new_model.model_options = copy.deepcopy(model.model_options)

        new_model.set_model_unet_function_wrapper(spectrum_unet_wrapper)
        return new_model

    def process(self, p, enable: bool, *args):
        # ADetailer や Hires fix の二次パス等、本体以外の生成プロセスを検知
        # str(type(p)) による判定に加え、属性チェックを併用
        p_type_name = str(type(p))
        is_secondary = (
            getattr(p, "_in_adetailer", False) or 
            "Postprocessed" in p_type_name or 
            getattr(p, "is_hr_pass", False) # Hiresパスの明示的チェック
        )
        
        if is_secondary:
            self.remove_patch_force()
            return

        # 以前の状態を完全に破棄
        if hasattr(p, "_spectrum_state"):
            del p._spectrum_state
        p._spectrum_state = None
        
        if enable:
            # ログ出力を控えめにし、stdoutへの過剰な干渉を避ける
            # (reForge の時間計測が stdout の進捗バーをパースしている可能性があるため)
            sys.stdout.write("[Spectrum] Enabled for main sampling.\n")
            sys.stdout.flush()
        else:
            self.remove_patch_force()

    def process_before_every_sampling(self, p, enable: bool, *args, **kwargs):
        # サンプリング開始の直前に呼ばれる
        if not enable:
            return

        # 二次プロセスのガード (ADetailer 等)
        p_type_name = str(type(p))
        if getattr(p, "_in_adetailer", False) or "Postprocessed" in p_type_name:
            return

        if shared.opts.skip_early_cond > 0.0 or shared.opts.s_min_uncond > 0.0:
            print('Spectrum does not support "Ignore/Skip Negative Prompt" optimizations...')
            return

        unet = p.sd_model.forge_objects.unet
        unet = self.patch(unet, p.steps, *args)
        p.sd_model.forge_objects.unet = unet

        p.extra_generation_params["spec_enable"] = True
        for k, v in zip(["spec_w", "spec_m", "spec_lam", "spec_window_size", "spec_flex_window",
        "spec_warmup_steps", "spec_stop_caching_step"], args):
            p.extra_generation_params[k] = v

    def remove_patch_force(self):
        import modules.shared as shared
        # shared.sd_model だけでなく、現在のアクティブなモデルからも取得を試みる
        unet = getattr(getattr(shared.sd_model, "forge_objects", None), "unet", None)
        if not unet:
            return
            
        # 完全にキーを削除してサンプラーを元の状態に戻す
        if "model_function_wrapper" in unet.model_options:
            wrap = unet.model_options["model_function_wrapper"]
            # 自分のラッパー、あるいは異常な None の場合に削除
            if wrap is None or (hasattr(wrap, "__name__") and wrap.__name__ == "spectrum_unet_wrapper"):
                del unet.model_options["model_function_wrapper"]
                print("[Spectrum] Extension DISABLED. UNet patch removed safely.")
        
        # Forgeの内部データ構造もクリア
        try:
            if hasattr(unet, "set_model_unet_function_wrapper"):
                # 内部辞書の書き換えを伴うため、Noneをセットせず直接辞書を触ったあとに状態のみリセット
                pass
        except Exception:
            pass

