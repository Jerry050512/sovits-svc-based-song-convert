import os
# import hashlib # Removed, as this is now handled by audio_utils.generate_chunk_filename
from pydub import AudioSegment
from pydub.utils import make_chunks
from utils.audio_utils import generate_chunk_filename # Added import

def split_audio_files(
    input_directory,
    output_directory,
    audio_format="wav",
    segment_duration_ms=5000,  # 5 seconds in milliseconds
    naming_convention="hash"  # "hash" or "indexed"
):
    """
    Walks through a directory, reads audio files, and splits them into smaller pieces.
    Uses generate_chunk_filename from audio_utils for naming output files.

    Args:
        input_directory (str): The path to the directory to walk through.
        output_directory (str): The path where the split audio files will be saved.
        audio_format (str): The format of the audio files to process (e.g., "wav", "mp3", "flac").
                             Default is "wav".
        segment_duration_ms (int): The duration of each audio segment in milliseconds.
                                   Default is 5000ms (5 seconds).
        naming_convention (str): The naming convention for the split files.
                                 Refer to utils.audio_utils.generate_chunk_filename for details.
                                 Default is "hash".
    """

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created output directory: {output_directory}")

    for root, _, files in os.walk(input_directory):
        for filename in files:
            if filename.endswith(f".{audio_format}"):
                original_filepath = os.path.join(root, filename)
                print(f"Processing: {original_filepath}")

                try:
                    audio = AudioSegment.from_file(original_filepath, format=audio_format)
                    chunks = make_chunks(audio, segment_duration_ms)

                    for i, chunk in enumerate(chunks):
                        # Replace old naming logic with a call to the utility function
                        output_filename = generate_chunk_filename(
                            original_filepath=original_filepath,
                            segment_index=i,
                            naming_convention=naming_convention,
                            audio_format=audio_format,
                            original_filename=filename
                        )

                        output_filepath = os.path.join(output_directory, output_filename)
                        chunk.export(output_filepath, format=audio_format)
                        print(f"  Exported: {output_filepath}")

                except Exception as e:
                    print(f"Error processing {original_filepath}: {e}")

if __name__ == "__main__":
    input_dir = input("Input audio directory: ")  # Replace with your input directory
    output_dir = input("Input output directory: ") # Replace with your desired output directory

    # Create dummy input files for demonstration
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created dummy input directory: {input_dir}")
        # Create a dummy audio file using pydub for testing
        try:
            from pydub.generators import Sine
            sine_wave = Sine(440).to_audio_segment(duration=10000) # 10 seconds of sine wave
            sine_wave.export(os.path.join(input_dir, "test_audio_1.wav"), format="wav")
            sine_wave_2 = Sine(880).to_audio_segment(duration=7500) # 7.5 seconds of sine wave
            sine_wave_2.export(os.path.join(input_dir, "test_audio_2.wav"), format="wav")
            print("Created dummy audio files for testing.")
        except Exception as e:
            print(f"Could not create dummy audio files (requires pydub.generators): {e}")
            print("Please place some .wav files in 'input_audio' manually for testing.")


    # Example 1: Split WAV files into 5-second pieces with hash names
    split_audio_files(
        input_directory=input_dir,
        output_directory=output_dir,
        audio_format="wav",
        segment_duration_ms=8000,
        naming_convention="hash"
    )

    # print("\n--- Splitting with Indexed Naming ---")
    # # Example 2: Split MP3 files (if you have them) into 3-second pieces with indexed names
    # # You would need to change audio_format to "mp3" and have mp3 files in your input_dir
    # split_audio_files(
    #     input_directory=input_dir,
    #     output_directory="output_audio_indexed",
    #     audio_format="wav", # Change to "mp3" if you have mp3s
    #     segment_duration_ms=3000,
    #     naming_convention="indexed"
    # )