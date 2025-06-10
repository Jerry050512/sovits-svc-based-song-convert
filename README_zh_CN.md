# 基于 So-Vits SVC 的歌声克隆

本指南提供了使用 So-Vits SVC 模型进行歌声克隆的全面教程。请按照以下步骤准备数据、训练自定义模型并执行声音推理。


## 🚀 快速开始

整个过程通常包括准备音频数据、训练自定义模型，然后使用该模型预测和转换新的声乐轨道。

### 1. 准备数据

在训练模型之前，您需要收集高质量的声乐录音。

#### 1.1 获取歌曲数据

1.  **下载歌曲：** 从互联网下载歌曲。
2.  **提取人声：** 从音乐中分离出人声轨道。
3.  **分割音频：** 将提取的人声音频分割成小片段（理想情况下为 5-10 秒）。
4.  **训练模型：** 使用这些处理过的人声数据来训练您的自定义声音模型。
5.  **推断新歌曲：** 从新歌曲中提取人声，使用您训练好的模型进行转换，然后与原始音乐重新混合。

对于本演示，我们收集了 **84 首五月天歌曲**，这些歌曲选自他们过去 15 年发行的 3 张专辑、1 张精选集、1 张演唱会专辑和 5 张单曲。总时长约为 6 小时，有效人声数据时长约为 5 小时 19 分钟。

#### 1.2 从音乐中提取人声

如果您没有纯粹的人声轨道，则需要将它们与完整歌曲分离。这里推荐两种工具：

* **Ultimate Vocal Remover (UVR)**：因其高效性而强烈推荐。
* **Spleeter**：一个著名的 Python 库，用于将音频分割成各种音轨，包括人声和伴奏。

***如果您已经拥有纯人声音频文件，请跳过此部分。***

#### 1.3 预处理音频数据

获得纯人声轨道后，您需要为训练做准备。

* **分割音频文件：** 将您的人声音频分割成 5-10 秒的片段。您可以使用 `utils/audio_split.py` 脚本来完成此操作。

    ```python
    from utils.audio_split import split_audio_files

    split_audio_files(
        input_directory="path/to/your/raw_vocal_audio",
        output_directory="path/to/your/split_audio_output",
        audio_format="wav",
        segment_duration_ms=5000, # 5000ms = 5 秒
        naming_convention="hash"
    )
    ```

* **删除不必要的片段（例如，静音）：** 使用 `utils/audio_clean.py` 通过删除静音或低响度片段来清理您的数据集。

    ```python
    from utils.audio_clean import delete_low_loudness_audio_files

    # 设置响度阈值。例如，-30 dBFS 意味着任何比此安静的都将被删除。
    loudness_threshold = -30.0
    delete_low_loudness_audio_files("path/to/your/split_audio_output", loudness_threshold)
    ```

## ⚔️ 开始训练！

数据准备就绪后，是时候设置和训练模型了。

### 2.1 预训练模型下载

下载所需的预训练模型并将其放置在指定目录中：

* **So-Vits:** [D_0.pth, G_0.pth](https://huggingface.co/langeheris/Sovits-4.0-V2-Pretrained-Model/tree/main)
* **DDSP-SVC:** [model_0.pt](https://github.com/yxlllc/DDSP-SVC/releases/tag/5.0)
* **NSF-HIFIGAN:** [nsf_hifigan_20221211.zip](https://github.com/openvpi/vocoders/releases/download/nsf-hifigan-v1/nsf_hifigan_20221211.zip)

**放置说明：**

1.  将 `checkpoint_best_legacy_500.pt` 放入 `pretrain` 目录。
2.  将 `D_0.pth` 和 `G_0.pth` 放入 `logs/44k` 目录。
3.  将 `model_0.pt` 放入 `logs/44k/diffusion` 目录。
4.  从 `nsf_hifigan_20221211.zip` 中提取的四个文件放入 `pretrain/nsf_hifigan` 目录。

---

### 2.2 准备训练数据集

运行这些命令来处理您的音频文件并生成训练所需的数据集：

```bash
python resample.py
python preprocess_flist_config.py --speech_encoder vec768l12
python preprocess_hubert_f0.py --f0_predictor dio
python preprocess_hubert_f0.py --f0_predictor dio --use_diff --num_processes 4
```

这些命令执行以下关键步骤：

* **重采样音频文件：** 确保所有音频都以一致的采样率。
* **生成并分割数据集：** 将数据处理成适合模型训练的格式。
* **预处理 Hubert 和 F0：** 提取对歌声克隆至关重要的特征。

**注意：** 根据您系统的 CPU 核心数调整 `--num_processes` 参数以获得最佳性能。

---

## 🏋️ 训练！

现在您可以训练主模型和扩散模型了。

* **训练主模型：**

    ```bash
    python train.py -c configs/config.json -m 44k
    ```

* **训练扩散模型：**

    ```bash
    python train_diff.py -c configs/diffusion.yaml
    ```

---

## 🎤 推断

训练成功后，您可以使用您的模型转换新的声乐轨道。

**推断命令示例：**

```bash
python inference_main.py -m "logs/44k/G_94400.pth" -c "configs/config.json" -n "lemon.wav" -t 0 -s "ashin" -lg 1 -shd -dm "logs/44k/diffusion/model_9000.pt"
```

**命令行参数解释：**

* `-m`：主生成器模型（`.pth` 文件）的路径。
* `-c`：配置文件（`.json`）的路径。
* `-n`：要转换的输入音频文件的名称/路径。
* `-t`：移调值（例如，`0` 表示不移调，正/负值表示更高/更低的音高）。
* `-s`：说话人名称（如果您的数据集中有多个说话人）。
* `-lg`：输出响度增益。
* `-shd`：**使用浅层扩散。** 包含此标志以在推断时启用浅层扩散。
* `-dm`：**扩散模型路径。** 指定您训练好的扩散模型的路径。