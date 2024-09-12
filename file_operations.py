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
import platform
import subprocess

LOG_FILE = 'renamed_files.json'

class FileOperations:
    def __init__(self):
        self.log_file = LOG_FILE

    def detect_file_type_and_extract_content(self, file_path):
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
            api_key = os.getenv("openai_api_key")  # Get the API key from environment variables
            return extract_audio_content(file_path, api_key)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def sanitize_filename(self, filename):
        sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
        sanitized = re.sub(r'_+', '_', sanitized)
        sanitized = sanitized.strip('_')
        if not sanitized or sanitized.startswith('.'):
            sanitized = 'unnamed_file' + sanitized
        return sanitized[:255]

    def sanitize_tag(self, tag):
        return re.sub(r'[^a-zA-Z0-9_]', '_', tag).strip('_')

    def log_rename(self, original_path, new_path, tags):
        log_entry = {
            "original_name": os.path.basename(original_path),
            "new_name": os.path.basename(new_path),
            "full_path": new_path,
            "tags": [self.sanitize_tag(tag) for tag in tags]
        }
        
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = []
        
        log_data.append(log_entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"Logged rename: '{os.path.basename(original_path)}' to '{os.path.basename(new_path)}' with tags: {', '.join(tags)}")

    def check_if_renamed(self, filename):
        print(f"Checking if '{filename}' has been renamed before...")
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                log_data = json.load(f)
            
            for entry in log_data:
                if entry["original_name"] == filename or entry["new_name"] == filename:
                    print(f"'{filename}' has been renamed before.")
                    return True
        
        print(f"'{filename}' has not been renamed before.")
        return False

    def apply_tags(self, file_path, tags):
        system = platform.system()
        
        if system == "Darwin":  # macOS
            tags_arg = ','.join(f'"{tag}"' for tag in tags)
            command = f"xattr -w com.apple.metadata:_kMDItemUserTags '{tags_arg}' '{file_path}'"
            subprocess.run(command, shell=True, check=True)
            print(f"Applied tags {tags} to '{file_path}'")
        elif system == "Windows":
            print(f"Tags for '{file_path}': {', '.join(tags)}")
            print("Note: Windows doesn't support native file tagging. Consider using a third-party solution.")
        else:
            print(f"Tagging not supported on {system}. Tags for '{file_path}': {', '.join(tags)}")

    def rename_with_retry(self, file_path, new_name, tags):
        original_name = os.path.basename(file_path)
        
        if self.check_if_renamed(original_name):
            print(f"File '{original_name}' has already been renamed. Skipping.")
            return False
        
        directory = os.path.dirname(file_path)
        new_path = os.path.join(directory, new_name)
        
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                os.rename(file_path, new_path)
                self.apply_tags(new_path, tags)
                self.log_rename(file_path, new_path, tags)
                return True
            except OSError as e:
                print(f"Error renaming file (attempt {attempt + 1}/{max_attempts}): {e}")
                if attempt == max_attempts - 1:
                    print(f"Failed to rename file after {max_attempts} attempts: {file_path}")
                    return False
                import time
                time.sleep(1)  # Wait for 1 second before retrying

    def prepare_new_filename(self, new_name, original_file_path):
        new_name = self.sanitize_filename(new_name)
        _, file_extension = os.path.splitext(original_file_path)
        if not new_name.lower().endswith(file_extension.lower()):
            new_name += file_extension
        return new_name

    def search_files_by_tags(self, tags):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                log_data = json.load(f)
            
            matching_files = []
            for entry in log_data:
                if all(self.sanitize_tag(tag).lower() in [self.sanitize_tag(t).lower() for t in entry["tags"]] for tag in tags):
                    matching_files.append(entry)
            
            return matching_files
        else:
            return []

    def get_all_tags(self):
        all_tags = set()
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                log_data = json.load(f)
            
            for entry in log_data:
                all_tags.update(self.sanitize_tag(tag).lower() for tag in entry["tags"])
        
        return all_tags