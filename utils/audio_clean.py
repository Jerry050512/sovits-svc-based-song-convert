import os
# Updated import line to include all necessary functions from audio_utils
from utils.audio_utils import (
    is_supported_audio_file,
    check_and_delete_if_low_loudness,
    get_audio_total_length,  # Added for completeness, though not used in __main__
    format_duration          # Added for completeness, though not used in __main__
)

# Local definitions of get_audio_total_length and format_duration are now removed.
# Their pydub-specific imports are also gone along with them.

def delete_low_loudness_audio_files(directory_path, loudness_threshold_dbfs, supported_formats=None):
    """
    Walks through a directory, checks the loudness of audio files using audio_utils,
    and deletes those whose loudness is lower than the specified threshold.

    Args:
        directory_path (str): The path to the directory to scan.
        loudness_threshold_dbfs (float): The loudness threshold in dBFS.
        supported_formats (list, optional): A list of audio file extensions.
    """
    if supported_formats is None:
        supported_formats = ["mp3", "wav", "flac", "ogg", "aac", "m4a"]

    deleted_files_count = 0
    checked_files_count = 0
    skipped_files_count = 0  # For files that caused errors during loudness check or deletion

    print(f"\n--- Deleting Low Loudness Audio Files ---")
    print(f"Scanning directory: {directory_path}")
    print(f"Loudness threshold: {loudness_threshold_dbfs} dBFS")
    print(f"Supported audio formats: {', '.join(supported_formats)}")

    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    for root, _, files in os.walk(directory_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            if is_supported_audio_file(filename, supported_formats):
                checked_files_count += 1
                # file_extension is inferred by check_and_delete_if_low_loudness
                status = check_and_delete_if_low_loudness(filepath, loudness_threshold_dbfs)

                if status == 'deleted':
                    deleted_files_count += 1
                elif status == 'skipped_error' or status == 'delete_failed':
                    skipped_files_count += 1
                # 'kept' status does not require special counting beyond being 'checked'

    print(f"\n--- Deletion Summary ---")
    print(f"Total files checked (supported types): {checked_files_count}")
    print(f"Total files deleted: {deleted_files_count}")
    print(f"Total files skipped (errors or delete failed): {skipped_files_count}")


# --- Example Usage ---
if __name__ == "__main__":
    low_loudness_audio_directory = input("Input audio directory for loudness check & deletion: ")

    # The dummy file creation part was commented out in the previous step to focus on refactoring.
    # It can be restored if pydub.generators is confirmed to be available and needed.
    # if not os.path.exists(low_loudness_audio_directory):
    #     os.makedirs(low_loudness_audio_directory)
    # print(f"Created/ensured directory: {low_loudness_audio_directory}")
    # try:
    #     from pydub.generators import Sine
    #     # Create a loud dummy file
    #     loud_sine = Sine(1000).to_audio_segment(duration=2000, volume=-10)
    #     loud_sine.export(os.path.join(low_loudness_audio_directory, "loud_audio.wav"), format="wav")
    #     # Create a quiet dummy file
    #     quiet_sine = Sine(500).to_audio_segment(duration=2000, volume=-40)
    #     quiet_sine.export(os.path.join(low_loudness_audio_directory, "quiet_audio.wav"), format="wav")
    #     # Create a very quiet file for testing deletion
    #     very_quiet_sine = Sine(200).to_audio_segment(duration=1000, volume=-50)
    #     very_quiet_sine.export(os.path.join(low_loudness_audio_directory, "very_quiet_audio.wav"), format="wav")
    #     print("Attempted to create dummy audio files for loudness testing.")
    # except ImportError:
    #     print("pydub.generators not available to create dummy files. Please create them manually.")
    # except Exception as e:
    #     print(f"Could not create dummy loud/quiet audio files: {e}")

    # Example: If you wanted to use the imported get_audio_total_length and format_duration:
    # print("\nCalculating total length of remaining audio (example):")
    # total_length = get_audio_total_length(low_loudness_audio_directory) # Uses imported function
    # if total_length > 0:
    #     print(f"Total length: {format_duration(total_length)}") # Uses imported function
    # else:
    #     print("No audio files found to calculate total length.")

    loudness_threshold = -30.0
    print(f"\nRunning loudness deletion script with threshold: {loudness_threshold} dBFS")
    delete_low_loudness_audio_files(low_loudness_audio_directory, loudness_threshold)
