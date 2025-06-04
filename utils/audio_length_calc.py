import os
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

def get_audio_total_length(directory_path, supported_formats=None):
    """
    Calculates the total length of all supported audio files in a given directory
    and its subdirectories.

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
            file_extension = filename.split('.')[-1].lower()
            if file_extension in supported_formats:
                filepath = os.path.join(root, filename)
                try:
                    # Load the audio file
                    audio = AudioSegment.from_file(filepath, format=file_extension)
                    duration_ms = len(audio) # Length in milliseconds
                    total_duration_seconds += duration_ms / 1000.0 # Convert to seconds
                    processed_files_count += 1
                    print(f"  Processed: {filename} ({duration_ms / 1000:.2f}s)")
                except CouldntDecodeError:
                    print(f"  Skipped (decoding error): {filename} - Ensure ffmpeg is installed and accessible.")
                    skipped_files_count += 1
                except Exception as e:
                    print(f"  Skipped (other error): {filename} - {e}")
                    skipped_files_count += 1

    print(f"\n--- Summary ---")
    print(f"Total files processed: {processed_files_count}")
    print(f"Total files skipped: {skipped_files_count}")

    return total_duration_seconds

def format_duration(total_seconds):
    """
    Formats a total duration in seconds into a human-readable string (HH:MM:SS).
    """
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"


# --- Example Usage ---
if __name__ == "__main__":
    # IMPORTANT: Replace 'your_audio_directory_path' with the actual path
    # to the directory containing your audio files.
    # For example: current_directory = os.getcwd()
    # For example: specific_directory = "/home/user/music"
    audio_directory = input("Input audio directory: ") # You can change this to your desired directory

    # Create dummy input files for demonstration if the directory doesn't exist
    if not os.path.exists(audio_directory):
        os.makedirs(audio_directory)
        print(f"Created dummy input directory: {audio_directory}")
        try:
            from pydub.generators import Sine
            # Create a 10-second dummy WAV file
            sine_wave_1 = Sine(440).to_audio_segment(duration=10000)
            sine_wave_1.export(os.path.join(audio_directory, "dummy_1.wav"), format="wav")
            # Create a 5-second dummy MP3 file (requires LAME encoder for ffmpeg)
            sine_wave_2 = Sine(660).to_audio_segment(duration=5000)
            sine_wave_2.export(os.path.join(audio_directory, "dummy_2.mp3"), format="mp3")
            # Create a 7-second dummy FLAC file
            sine_wave_3 = Sine(880).to_audio_segment(duration=7000)
            sine_wave_3.export(os.path.join(audio_directory, "dummy_3.flac"), format="flac")
            print("Created dummy audio files for testing.")
        except Exception as e:
            print(f"Could not create dummy audio files (requires pydub.generators and potentially LAME for MP3): {e}")
            print(f"Please place some audio files (e.g., .wav, .mp3) in '{audio_directory}' manually for testing.")


    total_audio_length_seconds = get_audio_total_length(audio_directory)

    if total_audio_length_seconds > 0:
        formatted_length = format_duration(total_audio_length_seconds)
        print(f"\nTotal audio length found: {formatted_length}")
    else:
        print("\nNo audio files found or processed in the specified directory.")
