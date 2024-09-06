import os
import tkinter as tk
from tkinter import filedialog, messagebox
from openai import OpenAI
from file_operations import detect_file_type_and_extract_content, rename_file, sanitize_filename, check_if_renamed
from openai_integration import create_assistant, generate_name_from_content
from dotenv import load_dotenv
import time
import json

load_dotenv()  # Load environment variables from .env file

def rename_files_based_on_content(directory_path):
    """
    Rename files in the given directory based on their content using OpenAI's Assistants API.
    
    :param directory_path: Path to the directory containing files to be renamed
    """
    api_key = os.getenv("openai_api_key")
    client = OpenAI(api_key=api_key)
    
    assistant = create_assistant(client)
    
    print(f"Processing files in directory: {directory_path}")
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        if os.path.isfile(file_path):
            print(f"\nProcessing file: {filename}")
            if not check_if_renamed(filename):
                new_name = process_file(file_path, client, assistant, api_key)
                if new_name:
                    if new_name != filename:
                        rename_with_retry(file_path, new_name)
                    else:
                        print(f"Generated name is the same as original for {filename}. Skipping.")
                else:
                    print(f"Failed to generate a new name for {filename}. Skipping.")
            else:
                print(f"File '{filename}' has already been renamed. Skipping.")
    
    print("\nFile renaming process completed.")

def process_file(file_path, client, assistant, api_key):
    content = detect_file_type_and_extract_content(file_path, api_key)
    new_name = generate_name_from_content(file_path, client, assistant, content)
    if new_name:
        return prepare_new_filename(new_name, file_path)
    return None

def prepare_new_filename(new_name, original_file_path):
    new_name = sanitize_filename(new_name)
    _, file_extension = os.path.splitext(original_file_path)
    if not new_name.lower().endswith(file_extension.lower()):
        new_name += file_extension
    return new_name

def rename_with_retry(file_path, new_name):
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            if rename_file(file_path, new_name):
                print(f"Renamed file: '{os.path.basename(file_path)}' to '{new_name}'")
                return True
            else:
                print(f"File '{os.path.basename(file_path)}' was not renamed as it has already been renamed before.")
                return False
        except PermissionError:
            print(f"File is in use. Retrying in 2 seconds... (Attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)
    print(f"Failed to rename file after {max_attempts} attempts: {file_path}")
    return False

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        rename_files_based_on_content(directory)
        messagebox.showinfo("Success", "Files have been renamed based on their content.")
    else:
        messagebox.showwarning("Warning", "No directory selected.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Renamer")
    root.geometry("300x100")

    label = tk.Label(root, text="Click the button to select a directory and rename files:")
    label.pack(pady=10)

    button = tk.Button(root, text="Select Directory", command=select_directory)
    button.pack()

    root.mainloop()