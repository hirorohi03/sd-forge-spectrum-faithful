#  sd-forge-spectrum-faithful (Spectrum Adaptive Forecaster)

<div align="center">

### [🇺🇸 English](README.md) | [🇯🇵 日本語](README_JP.md) 

</div>

[ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl)の`SpectrumSDXLC`ノードをStable Diffusion WebUI Forge/reForgeの拡張機能として動作するよう移植したものです（A1111では動作しません）。

## 🚀 概要

Spectrum機能を利用し、画質劣化と画像変化を最小に抑えながら画像生成の生成時間を削減できます。

SDXL (Forge, reForge, Forge Neo)、およびAnima (Forge Neo) を利用した画像生成で動作することを確認しています。

技術の詳細については、[ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl)や[Spectrumのプロジェクトページ](https://hanjq17.github.io/Spectrum/)などを参照してください。

Forge/reForgeへの移植にあたっては以下の拡張機能の実装を参考にしました。
- [Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo)のSpectrum Integrated
- [sd-webui-reforge-spectrum](https://github.com/wai55555/sd-webui-reforge-spectrum)

## 🚢 移植対象

[ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl)には二つのノードがあり、当拡張機能は`SpectrumSDXLC`を移植したものです。

- `SpectrumSDXLC`
    - [公式のforecasterコード](https://github.com/hanjq17/Spectrum/blob/main/src/utils/basis_utils.py)の忠実な実装
    - 当拡張機能はこちらを移植したもの
- `SpectrumSDXLCalibrated` （レガシー／非準拠ノード）
    - 「キャリブレーション」などの[論文](https://arxiv.org/abs/2603.01623)に忠実ではない原則に反した機能を実装
    - こちらの移植版は[sd-webui-forge-spectrum](https://github.com/hirorohi03/sd-webui-forge-spectrum)で公開済み

[ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl)では以下のように説明されています。

> **レガシー／非準拠ノード：**`SpectrumSDXLCalibrated`ノードは、現在**レガシー**と見なされています。
> 
> *リピーターの方への説明：* このノードの以前のバージョンは、当初公式のforecaster実装を見つけることができなかったため、実質的にゼロから「バイブコーディング」されたものでした。その結果、「キャリブレーション」のような、興味深いものの論文に忠実ではない、いくらか原則に反する追加が行われてしまいました。この問題は、[公式のforecasterコード](https://github.com/hanjq17/Spectrum/blob/main/src/utils/basis_utils.py)を`SpectrumSDXL`ノードに移植することで解決されました。より安定的で原則に基づいた結果を得るため、この正確な実装へ移行してください。

## 📊 性能比較と画像サンプル
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

- いずれも少し異なる画像が生成されます。
- [sd-webui-forge-spectrum](https://github.com/hirorohi03/sd-webui-forge-spectrum)はアーティファクトを生成することが他より多いかもしれません。

## 📦 インストール方法
1. WebUIの**Extensions**タブを開きます。
2. **Install from URL**を選択します。
3. https://github.com/hirorohi03/sd-forge-spectrum-faithful.git を入力し、**Install**をクリックします。
4. **Installed**を選択します。
5. **Apply and quit**をクリックします。
6. WebUIを再起動します。

## 🖼️ 使用方法
txt2imgまたはimg2imgの**Spectrum Adaptive Forecaster**タブのチェックボックスをチェックし、パラメータを設定して生成してください。

## 🛠️ パラメータ設定と推奨値

| パラメータ | 範囲 | 初期値 | 説明 |
| :--- | :--- | :--- | :--- |
| **Prediction Weighting<BR>`w`** | 0.0 - 1.0 | **0.25** | 予測の重み<BR>高：平滑化、低 (0.4～0.5)：シャープネス維持 |
| **Polynomial Degree<BR>`m`** | 1 - 16 | **6** | チェビシェフ多項式の基底関数の係数<BR>高：複雑＆繊細、低 (3)：高速＆安定 |
| **Regularization<BR>`lam`** | 0 - 2 | **0.5** | リッジ正則化強度 (λ)<BR>高 (1)：低精度モードでのlatent爆発、レインボーアーティファクト、黒出力を防止 |
| **Cache Window<BR>`window_size`**| 1 - 10 | **2** | 初期予測ウィンドウサイズ（スキップするステップ数）<BR>高：高速＆低精度、低：低速＆高精度 |
| **Window Growth<BR>`flex_window`** | 0.0 - 2.0 | **0.00** | 各UNetパス実行後にウィンドウに加算する増分値<BR>高：高速＆低精度、低：低速＆高精度 |
| **Warmup Steps<BR>`warmup_steps`** | 0 - 20 | **6** | 予測開始前の初期フルモデル実行ステップ数<BR>高：安定、低：高速 |
| **Stop Caching Step<BR>`stop_caching_step`** | 0.0 - 1.0 | **0.90** | 予測を停止しフルモデル実行に戻すステップ数<BR>全ステップ数に対する割合で指定 |

[Anima Turbo LoRA](https://civitai.com/models/2560840/)や[DMD2 LoRA](https://civitai.com/models/2466415/)などのステップ数削減LoRAと併用する場合はWarmup Stepsを1～2に減らしてください。

## ⚠️ 既知の制約

- この拡張機能を[sd-webui-reforge-spectrum](https://github.com/wai55555/sd-webui-reforge-spectrum)、[sd-webui-forge-spectrum](https://github.com/hirorohi03/sd-webui-forge-spectrum)と同時にインストールすると、WebUI起動時にエラーが発生します。
    - この拡張機能はForge Neoの[Spectrum Integrated](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo)とは競合せずインストールできます。
- この拡張機能とForge Neoの[Spectrum Integrated](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo)と両方を有効にして生成した場合の動作は保証しません。

## 📜 クレジットと参考文献
*   **論文**: [Adaptive Spectral Feature Forecasting for Diffusion Sampling Acceleration](https://arxiv.org/abs/2603.01623)
*   **プロジェクトページ**: [https://hanjq17.github.io/Spectrum/](https://hanjq17.github.io/Spectrum/)
*   **公式リポジトリ**: [hanjq17/Spectrum](https://github.com/hanjq17/Spectrum)
*   **ComfyUI 実装**: [ComfyUI Spectrum SDXL Node](https://github.com/ruwwww/ComfyUI-Spectrum-sdxl) by [A. Izzuddin Al Faruq](https://github.com/ruwwww/)
*   **移植コードの参考**: [sd-webui-reforge-spectrum](https://github.com/wai55555/sd-webui-reforge-spectrum) by [wai55555](https://github.com/wai55555)
*   **移植コードの参考**: [Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) Spectrum Integrated by [Haoming](https://github.com/Haoming02)

## ⚖️ ライセンス
本プロジェクトは **MIT License** の下で公開されています。
