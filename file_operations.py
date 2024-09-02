import os
import re
import json
from content_extractors import (
    extract_pdf_content,
    extract_word_content,
    extract_text_content,
    extract_excel_content,
    extract_csv_content,
    extract_audio_content,
)

LOG_FILE = 'renamed_files.json'

def detect_file_type_and_extract_content(file_path, api_key):
    """
    Detect the file type based on extension and extract content accordingly.
    
    :param file_path: Path to the file
    :param api_key: OpenAI API key (needed for audio transcription)
    :return: Extracted content as a string
    """
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == '.pdf':
        return extract_pdf_content(file_path)
    elif file_extension in ['.doc', '.docx']:
        return extract_word_content(file_path)
    elif file_extension in ['.txt', '.md']:
        return extract_text_content(file_path)
    elif file_extension in ['.xls', '.xlsx']:
        return extract_excel_content(file_path)
    elif file_extension == '.csv':
        return extract_csv_content(file_path)
    elif file_extension in ['.mp3', '.wav', '.m4a', '.flac']:
        return extract_audio_content(file_path, api_key)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def sanitize_filename(filename):
    """
    Sanitize the filename by removing or replacing invalid characters.
    
    :param filename: The original filename
    :return: A sanitized filename
    """
    # Remove any character that isn't alphanumeric, underscore, dash, or dot
    sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    
    # Replace multiple consecutive underscores with a single underscore
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading and trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure the filename is not empty and doesn't start with a dot
    if not sanitized or sanitized.startswith('.'):
        sanitized = 'unnamed_file' + sanitized
    
    # Truncate filename if it's too long (Windows has a 255 character limit)
    return sanitized[:255]

def log_rename(original_name, new_name):
    """
    Log the renamed file information to a JSON file if it hasn't been logged before.
    
    :param original_name: The original filename
    :param new_name: The new filename
    """
    log_entry = {
        "original_name": original_name,
        "new_name": new_name
    }
    
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            log_data = json.load(f)
    else:
        log_data = []
    
    # Check if the rename operation has already been logged
    if not any(entry["original_name"] == original_name and entry["new_name"] == new_name for entry in log_data):
        log_data.append(log_entry)
        
        with open(LOG_FILE, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"Logged rename: '{original_name}' to '{new_name}'")
    else:
        print(f"Rename operation already logged: '{original_name}' to '{new_name}'")
    print(f"Logged rename: '{original_name}' to '{new_name}'")

def check_if_renamed(filename):
    """
    Check if a file has been renamed before.
    
    :param filename: The filename to check
    :return: True if the file has been renamed before, False otherwise
    """
    print(f"Checking if '{filename}' has been renamed before...")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            log_data = json.load(f)
        
        for entry in log_data:
            if entry["original_name"] == filename or entry["new_name"] == filename:
                print(f"'{filename}' has been renamed before.")
                return True
    
    print(f"'{filename}' has not been renamed before.")
    return False

def rename_file(file_path, new_name):
    """
    Rename a file and log the change.
    
    :param file_path: The current path of the file
    :param new_name: The new name for the file
    :return: The path of the renamed file
    """
    original_name = os.path.basename(file_path)
    
    if check_if_renamed(original_name):
        print(f"File '{original_name}' has already been renamed. Skipping.")
        return file_path
    
    directory = os.path.dirname(file_path)
    new_path = os.path.join(directory, new_name)
    
    try:
        os.rename(file_path, new_path)
        log_rename(original_name, new_name)
        print(f"Renamed file: '{original_name}' to '{new_name}'")
        return new_path
    except OSError as e:
        print(f"Error renaming file: {e}")
        return file_path