import os
# pydub.AudioSegment and CouldntDecodeError are no longer needed at the top-level
# as the __main__ block's dummy file creation uses pydub.generators
# and the main functions now rely on audio_utils.

# Import functions from audio_utils
from utils.audio_utils import is_supported_audio_file, get_file_duration, format_duration

def get_audio_total_length(directory_path, supported_formats=None):
    """
    Calculates the total length of all supported audio files in a given directory
    and its subdirectories using functions from audio_utils.

    Args:
        directory_path (str): The path to the directory to scan.
        supported_formats (list, optional): A list of audio file extensions
                                            to consider (e.g., ["mp3", "wav", "flac"]).
                                            If None, a default list of common formats is used.

    Returns:
        float: The total duration of all audio files in seconds.
               Returns 0.0 if no audio files are found or an error occurs.
    """
    if supported_formats is None:
        supported_formats = ["mp3", "wav", "flac", "ogg", "aac", "m4a"]

    total_duration_seconds = 0.0
    processed_files_count = 0
    skipped_files_count = 0

    print(f"Scanning directory: {directory_path}")
    print(f"Supported audio formats: {', '.join(supported_formats)}")

    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return 0.0

    for root, _, files in os.walk(directory_path):
        for filename in files:
            if is_supported_audio_file(filename, supported_formats):
                filepath = os.path.join(root, filename)
                duration_seconds = get_file_duration(filepath) # file_extension is handled by get_file_duration

                if duration_seconds is not None:
                    total_duration_seconds += duration_seconds
                    processed_files_count += 1
                    # Individual file processing messages are now in get_file_duration or can be added here if needed
                    print(f"  Processed: {filename} ({duration_seconds:.2f}s)")
                else:
                    # get_file_duration already prints a warning for decoding/other errors
                    print(f"  Skipped: {filename} (error during processing)")
                    skipped_files_count += 1
            # Files not in supported_formats are silently skipped by is_supported_audio_file

    print(f"\n--- Summary ---")
    print(f"Total files processed: {processed_files_count}")
    print(f"Total files skipped: {skipped_files_count}")

    return total_duration_seconds

# format_duration function is now imported from audio_utils, so the local definition is removed.

# --- Example Usage ---
if __name__ == "__main__":
    # IMPORTANT: Replace 'your_audio_directory_path' with the actual path
    # to the directory containing your audio files.
    # For example: current_directory = os.getcwd()
    # For example: specific_directory = "/home/user/music"
    audio_directory = input("Input audio directory: ") # You can change this to your desired directory

    # Create dummy input files for demonstration if the directory doesn't exist
    # This part uses pydub.generators.Sine().to_audio_segment(),
    # which does not require a top-level 'from pydub import AudioSegment'.
    if not os.path.exists(audio_directory):
        os.makedirs(audio_directory)
        print(f"Created dummy input directory: {audio_directory}")
        try:
            from pydub.generators import Sine # This specific import is fine here.
            # Create a 10-second dummy WAV file
            sine_wave_1 = Sine(440).to_audio_segment(duration=10000) # duration in ms
            sine_wave_1.export(os.path.join(audio_directory, "dummy_1.wav"), format="wav")
            # Create a 5-second dummy MP3 file (requires LAME encoder for ffmpeg)
            sine_wave_2 = Sine(660).to_audio_segment(duration=5000) # duration in ms
            sine_wave_2.export(os.path.join(audio_directory, "dummy_2.mp3"), format="mp3")
            # Create a 7-second dummy FLAC file
            sine_wave_3 = Sine(880).to_audio_segment(duration=7000) # duration in ms
            sine_wave_3.export(os.path.join(audio_directory, "dummy_3.flac"), format="flac")
            print("Created dummy audio files for testing.")
        except ImportError:
            print("pydub.generators not available to create dummy files. Please ensure pydub is installed.")
        except Exception as e:
            print(f"Could not create dummy audio files (requires pydub.generators and potentially LAME for MP3): {e}")
            print(f"Please place some audio files (e.g., .wav, .mp3) in '{audio_directory}' manually for testing.")


    total_audio_length_seconds = get_audio_total_length(audio_directory)

    if total_audio_length_seconds > 0:
        # format_duration is now imported from utils.audio_utils
        formatted_length = format_duration(total_audio_length_seconds)
        print(f"\nTotal audio length found: {formatted_length}")
    else:
        print("\nNo audio files found or processed in the specified directory.")
