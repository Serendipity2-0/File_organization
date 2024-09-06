import os
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt
from openai import OpenAI
from file_operations import detect_file_type_and_extract_content, rename_file, sanitize_filename, check_if_renamed
from openai_integration import create_assistant, generate_name_from_content
from dotenv import load_dotenv
import time
import json

load_dotenv()  # Load environment variables from .env file

class FileRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Renamer')
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        label = QLabel('Click the button to select a directory and rename files:')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.btn = QPushButton('Select Directory', self)
        self.btn.clicked.connect(self.select_directory)
        layout.addWidget(self.btn)

        self.setLayout(layout)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.rename_files_based_on_content(directory)
            QMessageBox.information(self, "Success", "File renaming process completed.")
        else:
            QMessageBox.warning(self, "Warning", "No directory selected.")

    def rename_files_based_on_content(self, directory_path):
        api_key = os.getenv("openai_api_key")
        client = OpenAI(api_key=api_key)
        
        assistant = create_assistant(client)
        
        print(f"Processing files in directory: {directory_path}")
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                print(f"\nProcessing file: {filename}")
                if not check_if_renamed(filename):
                    new_name = self.process_file(file_path, client, assistant, api_key)
                    self.rename_with_confirmation(file_path, new_name or filename)
                else:
                    print(f"File '{filename}' has already been renamed. Skipping.")
        
        print("\nFile renaming process completed.")

    def process_file(self, file_path, client, assistant, api_key):
        content = detect_file_type_and_extract_content(file_path, api_key)
        new_name = generate_name_from_content(file_path, client, assistant, content)
        if new_name:
            return self.prepare_new_filename(new_name, file_path)
        return None

    def prepare_new_filename(self, new_name, original_file_path):
        new_name = sanitize_filename(new_name)
        _, file_extension = os.path.splitext(original_file_path)
        if not new_name.lower().endswith(file_extension.lower()):
            new_name += file_extension
        return new_name

    def rename_with_confirmation(self, file_path, suggested_name):
        original_name = os.path.basename(file_path)
        if suggested_name == original_name:
            message = f"The suggested name is the same as the original name. Do you want to rename '{original_name}'?"
        else:
            message = f"Do you want to rename '{original_name}' to '{suggested_name}'?"
        
        reply = QMessageBox.question(self, 'Confirm Rename', message, 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if suggested_name != original_name:
                self.rename_with_retry(file_path, suggested_name)
            else:
                custom_name, ok = QInputDialog.getText(self, "Custom Name", "Enter a custom name for the file:", text=suggested_name)
                if ok and custom_name and custom_name != original_name:
                    custom_name = self.prepare_new_filename(custom_name, file_path)
                    self.rename_with_retry(file_path, custom_name)
                else:
                    print(f"Renaming cancelled for '{original_name}'")
        else:
            custom_name, ok = QInputDialog.getText(self, "Custom Name", "Enter a custom name for the file:", text=suggested_name)
            if ok and custom_name and custom_name != original_name:
                custom_name = self.prepare_new_filename(custom_name, file_path)
                self.rename_with_retry(file_path, custom_name)
            else:
                print(f"Renaming cancelled for '{original_name}'")

    def rename_with_retry(self, file_path, new_name):
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileRenamer()
    ex.show()
    sys.exit(app.exec())