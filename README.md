#  sd-forge-spectrum-faithful (Spectrum Adaptive Forecaster)

<div align="center">

### [🇺🇸 English](README.md) | [🇯🇵 日本語](README_JP.md) 

</div>

This is a Port of `SpectrumSDXLC` node from [ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl) to run as an extension for Stable Diffusion WebUI Forge/reForge (it does not work on A1111). 

## 🚀 Overview

By utilizing the Spectrum feature and the Calibration feature uniquely implemented by the ComfyUI Spectrum SDXL Node, you can reduce image generation time while minimizing image degradation and visual changes.

I have confirmed that it works for image generation using SDXL (Forge, reForge, Forge Neo) and Anima (Forge Neo).

For technical details, please refer to the [ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl) or the [Spectrum project page](https://hanjq17.github.io/Spectrum/).

When porting to Forge/reForge, I referred to the implementation of the following extensions:
- [Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) Spectrum Integrated
- [sd-webui-reforge-spectrum](https://github.com/wai55555/sd-webui-reforge-spectrum)

## 🚢 Scope of porting

There are two nodes in [ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl), and this extension is a port of `SpectrumSDXLC`.

- `SpectrumSDXLC`
    - Porting of the [official forecaster code](https://github.com/hanjq17/Spectrum/blob/main/src/utils/basis_utils.py)
    - This extension is a port of this one
- `SpectrumSDXLCalibrated` （レガシー／非準拠ノード）
    - There are some non-principled additions like "calibration" which are not faithful to the [paper](https://arxiv.org/abs/2603.01623)
    - This port has already been released as [sd-webui-forge-spectrum](https://github.com/hirorohi03/sd-webui-forge-spectrum)

The [ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl) explains it as follows:

> **Legacy / Non-Faithful Node:** The `SpectrumSDXLCalibrated` node is now considered **legacy**. 
> 
> *Clarification for returning users:* The previous version of this node was essentially "vibe-coded" from scratch because I couldn't initially find the official forecaster implementation. This led to some non-principled additions like "calibration" which, while interesting, are not faithful to the paper. This has now been solved by porting the [official forecaster code](https://github.com/hanjq17/Spectrum/blob/main/src/utils/basis_utils.py) into the `SpectrumSDXL` node. Please migrate to the faithful implementation for more stable and principled results.

## 📊 Performance Comparison and Sample Images
- Stable Diffusion WebUI Forge - Neo v2.23
- Python 3.13.12
- PyTorch 2.11.0+cu130
- SageAttention 2
- RTX 5090

**waiIllustriousSDXL_v160 (30-step Euler)**
| Normal | sd-forge-spectrum-faithful (This) | [Spectrum Integrated](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) | [sd-webui-reforge-spectrum](https://github.com/wai55555/sd-webui-reforge-spectrum) | [sd-webui-forge-spectrum](https://github.com/hirorohi03/sd-webui-forge-spectrum) (Calibrated 0.5) |
| :---: | :---: | :---: | :---: | :---: |
| ![Normal1](/images/sdxl1_normal.png) | ![Faith1](/images/sdxl1_faith.png) | ![Neo1](/images/sdxl1_neo.png) | ![Reforge1](/images/sdxl1_reforge.png) | ![Cal1](/images/sdxl1_cal.png) |
| **3.22 s** | **1.87 s** | **1.79 s** | **1.98 s** | **1.85 s** |
| ![Normal2](/images/sdxl2_normal.png) | ![Faith2](/images/sdxl2_faith.png) | ![Neo2](/images/sdxl2_neo.png) | ![Reforge2](/images/sdxl2_reforge.png) | ![Cal2](/images/sdxl2_cal.png) |
| **3.23 s** | **1.91 s** | **1.77 s** | **1.79 s** | **1.84 s** |

**anima-base-v1.0 (30-step er-sde)**
| Normal  | spectrum-faithful (This) | [Spectrum Integrated](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) | [sd-webui-reforge-spectrum](https://github.com/wai55555/sd-webui-reforge-spectrum) | [sd-webui-forge-spectrum](https://github.com/hirorohi03/sd-webui-forge-spectrum) (Calibrated 0.5) |
| :---: | :---: | :---: | :---: | :---: |
| ![Anima_Normal](/images/anima_normal.png) | ![Anima_Faith](/images/anima_faith.png) | ![Anima_Neo](/images/anima_neo.png) | ![Anima_Reforge](/images/anima_reforge.png) | ![Anima_Cal](/images/anima_cal.png) |
| **6.50 s** | **3.45 s** | **4.11 s** | **3.82 s** | **3.49 s** |

- Each one generates slightly different images.
- [sd-webui-forge-spectrum](https://github.com/hirorohi03/sd-webui-forge-spectrum) may generate artifacts more frequently than the others.

## 📦 Installation
1. Open the **Extensions** tab in your WebUI.
2. Select **Install from URL**.
3. Enter https://github.com/hirorohi03/sd-webui-forge-spectrum.git and click **Install**.
4. Select **Installed**.
5. Click **Apply and quit**.
6. Restart your WebUI.

Coming soon.

## 🖼️ How to Use
Check the checkbox in the **Spectrum Adaptive Forecaster** tab of txt2img or img2img, set the parameters, and generate the image.

## 🛠️ Parameter Settings and Recommended Values
| Parameter | Range | Default | Description |
| :--- | :--- | :--- | :--- |
| **Prediction Weighting<BR>`w`** | 0.0 - 1.0 | **0.25** | Prediction weight<BR>High: Smoothing, Low (0.4–0.5): Maintains sharpness |
| **Polynomial Degree<BR>`m`** | 1 - 16 | **6** | Coefficients of Chebyshev polynomial basis functions<BR>High: Complex & delicate, Low (3): Fast & stable |
| **Regularization<BR>`lam`** | 0 - 2 | **0.5** | Ridge regularization strength (λ)<BR>High (1): Prevents latent explosion, rainbow artifacts, and black output in low-precision mode |
| **Cache Window<BR>`window_size`** | 1 - 10 | **2** | Initial prediction window size (number of steps to skip)<BR>High: Fast & low accuracy, Low: Slow & high accuracy |
| **Window Growth<BR>`flex_window`** | 0.0 - 2.0 | **0.00** | Incremental value added to the window after each UNet path execution<BR>High: Fast & low accuracy, Low: Slow & high accuracy |
| **Warmup Steps<BR>`warmup_steps`** | 0 - 20 | **6** | Number of initial full model execution steps before starting prediction<BR>High: Stable, Low: Fast |
| **Stop Caching Step<BR>`stop_caching_step`** | 0.0 - 1.0 | **0.90** | Number of steps at which prediction stops and returns to full model execution<BR>Specified as a percentage of the total number of steps |

If you are using this extension with Low Step LoRAs such as [Anima Turbo LoRA] or [DMD2 LoRA], please reduce the Warmup Steps to 1 or 2.

## ⚠️ Known Limitations

- If you install this extension with [sd-webui-reforge-spectrum](https://github.com/wai55555/sd-webui-reforge-spectrum) or [sd-webui-forge-spectrum](https://github.com/hirorohi03/sd-webui-forge-spectrum) at the same time, an error will occur when launching the WebUI.
    - You can install this extension without conflicting with Forge Neo's [Spectrum Integrated](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo).
- I do not guarantee proper operation if both this extension and Forge Neo's [Spectrum Integrated](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) are enabled and generated.

## 📜 Credits & References
*   **Paper**: [Adaptive Spectral Feature Forecasting for Diffusion Sampling Acceleration](https://arxiv.org/abs/2603.01623)
*   **Project Page**: [https://hanjq17.github.io/Spectrum/](https://hanjq17.github.io/Spectrum/)
*   **Official Implementation**: [hanjq17/Spectrum](https://github.com/hanjq17/Spectrum)
*   **ComfyUI Implementation**: [ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl) by [A. Izzuddin Al Faruq](https://github.com/ruwwww/)
*   **Reference for porting code**: [sd-webui-reforge-spectrum](https://github.com/wai55555/sd-webui-reforge-spectrum) by [wai55555](https://github.com/wai55555)
*   **Reference for porting code**: [Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) Spectrum Integrated by [Haoming](https://github.com/Haoming02)

## ⚖️ License
This project is licensed under the **MIT License**.
