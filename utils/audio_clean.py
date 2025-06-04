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
    Formats a total duration in seconds into a human-readable string (HH:MM:SS.ms).
    """
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"

def delete_low_loudness_audio_files(directory_path, loudness_threshold_dbfs, supported_formats=None):
    """
    Walks through a directory, checks the loudness of audio files,
    and deletes those whose whole loudness is lower than the specified threshold.

    Args:
        directory_path (str): The path to the directory to scan.
        loudness_threshold_dbfs (float): The loudness threshold in dBFS (decibels relative to full scale).
                                         Files with loudness below this value will be deleted.
        supported_formats (list, optional): A list of audio file extensions
                                            to consider (e.g., ["mp3", "wav", "flac"]).
                                            If None, a default list of common formats is used.
    """
    if supported_formats is None:
        supported_formats = ["mp3", "wav", "flac", "ogg", "aac", "m4a"]

    deleted_files_count = 0
    checked_files_count = 0
    skipped_files_count = 0

    print(f"\n--- Deleting Low Loudness Audio Files ---")
    print(f"Scanning directory: {directory_path}")
    print(f"Loudness threshold: {loudness_threshold_dbfs} dBFS")
    print(f"Supported audio formats: {', '.join(supported_formats)}")

    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    for root, _, files in os.walk(directory_path):
        for filename in files:
            file_extension = filename.split('.')[-1].lower()
            if file_extension in supported_formats:
                filepath = os.path.join(root, filename)
                checked_files_count += 1
                try:
                    audio = AudioSegment.from_file(filepath, format=file_extension)
                    loudness = audio.dBFS # Calculate loudness in dBFS

                    print(f"  Checking: {filename} (Loudness: {loudness:.2f} dBFS)")

                    if loudness < loudness_threshold_dbfs:
                        os.remove(filepath)
                        deleted_files_count += 1
                        print(f"    DELETED: {filename} (Loudness {loudness:.2f} dBFS is below {loudness_threshold_dbfs} dBFS)")
                    else:
                        print(f"    KEPT: {filename} (Loudness {loudness:.2f} dBFS is at or above {loudness_threshold_dbfs} dBFS)")

                except CouldntDecodeError:
                    print(f"  Skipped (decoding error): {filename} - Ensure ffmpeg is installed and accessible.")
                    skipped_files_count += 1
                except Exception as e:
                    print(f"  Skipped (other error): {filename} - {e}")
                    skipped_files_count += 1

    print(f"\n--- Deletion Summary ---")
    print(f"Total files checked: {checked_files_count}")
    print(f"Total files deleted: {deleted_files_count}")
    print(f"Total files skipped: {skipped_files_count}")


# --- Example Usage ---
if __name__ == "__main__":
    # IMPORTANT: Replace 'your_audio_directory_path' with the actual path
    # to the directory containing your audio files.
    # For example: current_directory = os.getcwd()
    # For example: specific_directory = "/home/user/music"
    audio_directory = "input_audio" # You can change this to your desired directory
    low_loudness_audio_directory = "input_audio" # Directory for loudness test

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

    # --- Test for low loudness deletion ---
    # Create a separate directory for testing loudness deletion,
    # as files will be removed from it.
    if os.path.exists(low_loudness_audio_directory):
        import shutil
        shutil.rmtree(low_loudness_audio_directory) # Clean up previous test runs
    os.makedirs(low_loudness_audio_directory)
    print(f"\nCreated test directory for loudness deletion: {low_loudness_audio_directory}")

    try:
        from pydub.generators import Sine
        # Create a loud dummy file
        loud_sine = Sine(1000).to_audio_segment(duration=2000, volume=-10) # -10 dBFS (relatively loud)
        loud_sine.export(os.path.join(low_loudness_audio_directory, "loud_audio.wav"), format="wav")

        # Create a quiet dummy file
        quiet_sine = Sine(500).to_audio_segment(duration=2000, volume=-40) # -40 dBFS (relatively quiet)
        quiet_sine.export(os.path.join(low_loudness_audio_directory, "quiet_audio.wav"), format="wav")
        print("Created dummy loud and quiet audio files for loudness testing.")
    except Exception as e:
        print(f"Could not create dummy loud/quiet audio files: {e}")
        print(f"Please manually place 'loud_audio.wav' (e.g., -10dBFS) and 'quiet_audio.wav' (e.g., -40dBFS) in '{low_loudness_audio_directory}' for testing.")


    # --- Run the loudness deletion script ---
    # Set a threshold. For example, -30 dBFS means anything quieter than this will be deleted.
    loudness_threshold = -30.0
    delete_low_loudness_audio_files(low_loudness_audio_directory, loudness_threshold)

    # --- Original total length calculation (still available) ---
    total_audio_length_seconds = get_audio_total_length(audio_directory)

    if total_audio_length_seconds > 0:
        formatted_length = format_duration(total_audio_length_seconds)
        print(f"\nTotal audio length found in '{audio_directory}': {formatted_length}")
    else:
        print(f"\nNo audio files found or processed in '{audio_directory}'.")
