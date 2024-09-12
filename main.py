import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, 
                             QFileDialog, QMessageBox, QInputDialog, QLineEdit, 
                             QListWidget, QHBoxLayout, QDialog, QDialogButtonBox, QTextEdit,
                             QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QFont
from file_operations import FileOperations
from openai_integration import OpenAIIntegration
from dotenv import load_dotenv

class TagDialog(QDialog):
    def __init__(self, suggested_tags, file_summary, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Summary and Tags")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)

        # File summary
        summary_label = QLabel("File Summary:")
        layout.addWidget(summary_label)

        self.summary_text = QTextEdit(self)
        self.summary_text.setPlainText(file_summary)
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(200)
        layout.addWidget(self.summary_text)

        # Tag input
        tag_label = QLabel("Enter a tag and press Enter:")
        layout.addWidget(tag_label)

        self.tag_input = QLineEdit(self)
        self.tag_input.returnPressed.connect(self.add_tag)
        layout.addWidget(self.tag_input)

        # Tag list
        self.tag_list = QListWidget(self)
        for tag in suggested_tags:
            self.tag_list.addItem(tag)
        layout.addWidget(self.tag_list)

        # Buttons to remove tags and clear all
        button_layout = QHBoxLayout()
        remove_tag_btn = QPushButton("Remove Selected Tag")
        remove_tag_btn.clicked.connect(self.remove_selected_tag)
        button_layout.addWidget(remove_tag_btn)

        clear_tags_btn = QPushButton("Clear All Tags")
        clear_tags_btn.clicked.connect(self.clear_all_tags)
        button_layout.addWidget(clear_tags_btn)

        layout.addLayout(button_layout)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def add_tag(self):
        tag = self.tag_input.text().strip()
        if tag and not self.tag_exists(tag):
            self.tag_list.addItem(tag)
            self.tag_input.clear()

    def tag_exists(self, tag):
        for i in range(self.tag_list.count()):
            if self.tag_list.item(i).text().lower() == tag.lower():
                return True
        return False

    def remove_selected_tag(self):
        for item in self.tag_list.selectedItems():
            self.tag_list.takeItem(self.tag_list.row(item))

    def clear_all_tags(self):
        self.tag_list.clear()

    def get_tags(self):
        return [self.tag_list.item(i).text() for i in range(self.tag_list.count())]

class FileRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.file_ops = FileOperations()
        self.openai_integration = OpenAIIntegration()
        self.search_results = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Renamer and Tag Search')
        self.setGeometry(300, 300, 500, 550)  # Increased height to accommodate the new button
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QPushButton {
                padding: 5px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)

        layout = QVBoxLayout()

        title_label = QLabel('File Renamer and Tag Search')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        self.rename_btn = QPushButton('Select Directory to Rename Files', self)
        self.rename_btn.clicked.connect(self.select_directory)
        layout.addWidget(self.rename_btn)

        layout.addSpacing(20)

        search_label = QLabel('Search files by tags:')
        layout.addWidget(search_label)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter tags separated by commas")
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton('Search', self)
        self.search_btn.clicked.connect(self.search_files)
        search_layout.addWidget(self.search_btn)

        layout.addLayout(search_layout)

        self.results_list = QListWidget(self)
        self.results_list.itemDoubleClicked.connect(self.open_file)
        layout.addWidget(self.results_list)

        show_tags_btn = QPushButton('Show Available Tags', self)
        show_tags_btn.clicked.connect(self.show_available_tags)
        layout.addWidget(show_tags_btn)

        # Add Quit button
        quit_btn = QPushButton('Quit', self)
        quit_btn.clicked.connect(self.close)
        quit_btn.setStyleSheet("""
            background-color: #f44336;
            color: white;
            font-weight: bold;
        """)
        layout.addWidget(quit_btn)

        self.setLayout(layout)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            try:
                renamed_count = self.rename_files_based_on_content(directory)
                QMessageBox.information(self, "Success", f"File renaming process completed. {renamed_count} files renamed.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred during the renaming process: {str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "No directory selected.")

    def rename_files_based_on_content(self, directory_path):
        client = self.openai_integration.create_client()
        assistant = self.openai_integration.create_assistant(client)
        renamed_count = 0
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                try:
                    if not self.file_ops.check_if_renamed(filename):
                        new_name, tags = self.process_file(file_path, client, assistant)
                        if new_name and self.rename_with_confirmation(file_path, new_name, tags or []):
                            renamed_count += 1
                    else:
                        print(f"File '{filename}' has already been renamed. Skipping.")
                except Exception as e:
                    print(f"Error processing file '{filename}': {str(e)}")
        
        return renamed_count

    def process_file(self, file_path, client, assistant):
        try:
            content = self.file_ops.detect_file_type_and_extract_content(file_path)
            new_name, tags = self.openai_integration.generate_name_from_content(file_path, client, assistant, content)
            if new_name:
                return self.file_ops.prepare_new_filename(new_name, file_path), tags
        except Exception as e:
            print(f"Error processing file '{file_path}': {str(e)}")
        return None, None

    def rename_with_confirmation(self, file_path, suggested_name, suggested_tags):
        original_name = os.path.basename(file_path)
        message = f"Do you want to rename '{original_name}' to '{suggested_name}'?"
        
        if suggested_name == original_name:
            message += " (Note: The suggested name is the same as the original name)"
        
        reply = QMessageBox.question(self, 'Confirm Rename', message, 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            new_name = suggested_name
        else:
            custom_name, ok = QInputDialog.getText(self, "Custom Name", "Enter a custom name for the file:", text=suggested_name)
            if ok and custom_name:
                new_name = self.file_ops.prepare_new_filename(custom_name, file_path)
            else:
                print(f"Renaming cancelled for '{original_name}'")
                return False

        # Generate file summary
        file_summary = self.generate_file_summary(file_path)

        # Ask user to confirm or modify tags
        tag_dialog = TagDialog(suggested_tags, file_summary, self)
        if tag_dialog.exec() == QDialog.DialogCode.Accepted:
            tags = tag_dialog.get_tags()
        else:
            print(f"Tagging cancelled for '{original_name}'")
            return False

        # Proceed with renaming and tagging
        if new_name != original_name:
            return self.file_ops.rename_with_retry(file_path, new_name, tags)
        else:
            print(f"Name unchanged. Logging and applying tags for '{original_name}'")
            self.file_ops.log_rename(file_path, file_path, tags)
            self.file_ops.apply_tags(file_path, tags)
            return True

    def generate_file_summary(self, file_path):
        try:
            content = self.file_ops.detect_file_type_and_extract_content(file_path)
            # Generate a more structured summary
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_type = os.path.splitext(file_path)[1]
            
            summary = f"File Name: {file_name}\n"
            summary += f"File Type: {file_type}\n"
            summary += f"File Size: {file_size} bytes\n\n"
            summary += "Content Preview:\n"
            
            # Truncate the content if it's too long
            max_content_length = 500
            content_preview = content[:max_content_length] + "..." if len(content) > max_content_length else content
            summary += content_preview
            
            return summary
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def search_files(self):
        tags = [tag.strip().replace(" ", "_") for tag in self.search_input.text().split(',') if tag.strip()]
        if not tags:
            QMessageBox.warning(self, "Warning", "Please enter at least one tag to search.")
            return

        try:
            self.search_results = self.file_ops.search_files_by_tags(tags)
            self.results_list.clear()
            if self.search_results:
                for result in self.search_results:
                    self.results_list.addItem(f"{result['new_name']} (Tags: {', '.join(result['tags'])})")
            else:
                self.results_list.addItem("No matching files found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during the search: {str(e)}")

    def open_file(self, item):
        index = self.results_list.row(item)
        if 0 <= index < len(self.search_results):
            file_path = self.search_results[index].get('full_path')
            if file_path and os.path.exists(file_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            else:
                QMessageBox.warning(self, "File Not Found", f"The file '{file_path}' could not be found.")
        else:
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid file from the list.")

    def show_available_tags(self):
        try:
            all_tags = self.file_ops.get_all_tags()
            if all_tags:
                tags_str = ", ".join(sorted(all_tags))
                QMessageBox.information(self, "Available Tags", f"Available tags:\n\n{tags_str}")
            else:
                QMessageBox.information(self, "Available Tags", "No tags available. Rename some files first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while retrieving tags: {str(e)}")

def main():
    load_dotenv()
    app = QApplication(sys.argv)
    ex = FileRenamer()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()