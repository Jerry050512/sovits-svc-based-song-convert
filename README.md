# Singing Voice Clone based on So-Vits SVC

## Getting-Started

### Prepare Data

1. Download songs from the Internet.
2. Use tools to extract the vocal voice from music.
3. Split the audio data into pieces (about 5s ~ 10s).
4. Use vocal voice to train custom model.
5. Predict for a new song(extract new vocal voice and convert and remix with music).

In this demo tutorial, we collect 84 songs of Mayday from their 3 albums, 1 music collection, 1 live album, and 5 singles released in recent 15 years. Total time length: 06:06:04.06. (Valid time: 05:19:14.98)

There are few ways to extract vocal voice from music. Here are two recommendations: Ultimate Vocal Remover (UVR) & Spleeter. Skip these two sections if you have pure vocal voice.

#### Ultimate Vocal Remover (Recommend)

#### Spleeter

Skip this section if you have use UVR to get vocal voice from the music.

#### Pre-Process the Audio Data

Now, you've got the pure vocal voice. You need to split them into data pieces (around 5s ~ 10s). You may use the `utils/audio_split.py` to finish the work. Just use the function in this way: 
```python
split_audio_files(
    input_directory=input_dir,
    output_directory=output_dir,
    audio_format="wav",
    segment_duration_ms=5000,
    naming_convention="hash"
)
```

Then, you may need to remove unnessary pieces (like the silent pieces). You may use the `utils/audio_clean.py` to accomplish the task. Work this way: 
```python
# --- Run the loudness deletion script ---
# Set a threshold. For example, -30 dBFS means anything quieter than this will be deleted.
loudness_threshold = -30.0
delete_low_loudness_audio_files(low_loudness_audio_directory, loudness_threshold)
```

### Strike for Training!

#### Pre-Trained Model Download

- So-Vits: [D_0.pth, G_0.pth](https://huggingface.co/langeheris/Sovits-4.0-V2-Pretrained-Model/tree/main)
- DDSP-SVC: [model_0.pt](https://github.com/yxlllc/DDSP-SVC/releases/tag/5.0)