# File Organizer

File Organizer is a Python application that automatically renames files based on their content using OpenAI's Assistants API. This tool helps users organize their files more efficiently by generating meaningful names derived from the file contents, incorporating a human-in-the-loop process for optimal results.

## Features

- AI-powered file renaming based on content analysis
- Human-in-the-loop process for reviewing and approving AI-generated file names and tags
- Support for various file types
- Feature-rich graphical user interface built with PyQt6
- Individual tag entry and management
- File summary display for informed tagging decisions
- Search functionality for tagged files
- Display of all available tags used in the system

## Requirements

- Python 3.x
- OpenAI API key
- PyQt6

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Serendipity2-0/file-organizer.git
   cd file-organizer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   openai_api_key=your_api_key_here
   ```

## Usage

1. Run the main script:
   ```
   python main.py
   ```

2. Click the "Select Directory to Rename Files" button in the GUI.

3. Choose the directory containing the files you want to rename.

4. The application will process each file in the selected directory, generating new names based on their content.

5. Review the AI-generated file names in the interface and confirm or modify as needed.

6. For each file, you'll see a summary and can add, remove, or modify tags.

7. Confirm the changes to apply the new file names and tags.

8. Use the search functionality to find files by tags.

9. View all available tags in the system using the "Show Available Tags" button.

10. Use the "Quit" button to exit the application.

## Project Structure

- `main.py`: The main script that runs the GUI and coordinates the file renaming process.
- `file_operations.py`: Contains the FileOperations class for file-related operations.
- `openai_integration.py`: Handles integration with OpenAI's API for content analysis and name generation.
- `content_extractors.py`: Provides functions to extract content from various file types.
- `renamed_files.json`: Logs the files that have been renamed to prevent duplicate processing.
- `requirements.txt`: Lists all the Python dependencies required for the project.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

If you encounter any issues, please check the following:

1. Ensure your OpenAI API key is correctly set in the `.env` file.
2. Make sure you have the necessary permissions to read and write files in the selected directory.
3. If you experience any PyQt6-related issues, make sure you have the latest version installed and your system meets the requirements.

If the problem persists, please create an issue on the GitHub repository with a detailed description of the problem.

## License

This project is open source and available under the [MIT License](LICENSE).
