import os
import hashlib # Added for generate_chunk_filename
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

def get_file_duration(filepath, file_extension=None):
    """
    Calculates the duration of an audio file.

    Args:
        filepath (str): The path to the audio file.
        file_extension (str, optional): The file extension.
                                         If None, it's inferred from filepath.
                                         Defaults to None.

    Returns:
        float or None: The duration of the audio file in seconds,
                       or None if the duration cannot be determined.
    """
    if file_extension is None:
        _, file_extension = os.path.splitext(filepath)

    # pydub expects the extension without the leading dot
    file_extension = file_extension.lstrip('.')

    try:
        # Explicitly pass the format if known, otherwise pydub tries to infer
        if file_extension:
            audio = AudioSegment.from_file(filepath, format=file_extension)
        else:
            # If no extension after stripping, let pydub try to infer
            audio = AudioSegment.from_file(filepath)
        return len(audio) / 1000.0
    except CouldntDecodeError:
        print(f"Warning: Could not decode {filepath} for duration check.")
        return None
    except Exception as e:
        print(f"Warning: Error processing {filepath} for duration: {e}")
        return None

def is_supported_audio_file(filename, supported_formats):
    """
    Checks if the given filename has a supported audio file extension.

    Args:
        filename (str): The name of the file.
        supported_formats (list): A list of supported audio file extensions
                                  (e.g., ['wav', 'mp3']).

    Returns:
        bool: True if the file extension is in supported_formats, False otherwise.
    """
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip('.') in supported_formats

def format_duration(total_seconds):
    """
    Formats a total duration in seconds into a human-readable string (HH:MM:SS).
    """
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"

def get_audio_loudness(filepath, file_extension=None):
    """
    Measures the loudness of an audio file.

    Args:
        filepath (str): The path to the audio file.
        file_extension (str, optional): The file extension.
                                         If None, it's inferred from filepath.
                                         Defaults to None.

    Returns:
        float or None: The loudness of the audio file in dBFS,
                       or None if loudness cannot be determined.
    """
    if file_extension is None:
        _, file_extension = os.path.splitext(filepath)

    file_extension = file_extension.lstrip('.')

    try:
        if file_extension:
            audio = AudioSegment.from_file(filepath, format=file_extension)
        else:
            audio = AudioSegment.from_file(filepath)
        return audio.dBFS
    except CouldntDecodeError:
        print(f"Warning: Could not decode {filepath} for loudness check")
        return None
    except Exception as e:
        print(f"Warning: Error processing {filepath} for loudness: {e}")
        return None

def check_and_delete_if_low_loudness(filepath, loudness_threshold_dbfs, file_extension=None):
    """
    Checks an audio file's loudness and deletes it if it's below a threshold.

    Args:
        filepath (str): The path to the audio file.
        loudness_threshold_dbfs (float): The loudness threshold in dBFS.
                                         Files below this will be deleted.
        file_extension (str, optional): The file extension.
                                         If None, it's inferred. Defaults to None.

    Returns:
        str: A status string: 'deleted', 'kept', 'skipped_error', or 'delete_failed'.
    """
    filename = os.path.basename(filepath)
    loudness = get_audio_loudness(filepath, file_extension)

    if loudness is None:
        print(f"  Skipped (loudness check failed): {filename}")
        return 'skipped_error'

    print(f"  Checking: {filename} (Loudness: {loudness:.2f} dBFS)")

    if loudness < loudness_threshold_dbfs:
        try:
            os.remove(filepath)
            print(f"    DELETED: {filename} (Loudness {loudness:.2f} dBFS is below {loudness_threshold_dbfs} dBFS)")
            return 'deleted'
        except Exception as e:
            print(f"    Error deleting {filename}: {e}")
            return 'delete_failed'
    else:
        print(f"    KEPT: {filename} (Loudness {loudness:.2f} dBFS is at or above {loudness_threshold_dbfs} dBFS)")
        return 'kept'

def generate_chunk_filename(original_filepath, segment_index, naming_convention, audio_format, original_filename):
    """
    Generates a filename for an audio chunk based on the specified convention.

    Args:
        original_filepath (str): The full path to the original audio file.
        segment_index (int): The index of the current audio segment/chunk.
        naming_convention (str): The convention to use ("hash" or "indexed").
        audio_format (str): The desired audio format for the chunk (e.g., "wav").
        original_filename (str): The basename of the original file (e.g., "audio.mp3").

    Returns:
        str: The generated filename for the chunk.
    """
    audio_format = audio_format.lstrip('.') # Ensure no leading dot

    if naming_convention == "hash":
        unique_string = f"{original_filepath}-{segment_index}"
        hash_name = hashlib.md5(unique_string.encode()).hexdigest()
        return f"{hash_name}.{audio_format}"
    elif naming_convention == "indexed":
        base_name, _ = os.path.splitext(original_filename)
        return f"{base_name}_part{segment_index:03d}.{audio_format}"
    else:
        print(f"Warning: Invalid naming convention '{naming_convention}'. Defaulting to 'hash'.")
        # Fallback to hash convention
        unique_string = f"{original_filepath}-{segment_index}"
        hash_name = hashlib.md5(unique_string.encode()).hexdigest()
        return f"{hash_name}.{audio_format}"
