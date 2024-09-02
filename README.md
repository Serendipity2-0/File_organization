# File Organizer

File Organizer is a Python application that automatically renames files based on their content using OpenAI's Assistants API. This tool helps users organize their files more efficiently by generating meaningful names derived from the file contents.

## Features

- Rename files based on their content using AI
- Support for various file types
- User-friendly graphical interface
- Handling of file permission errors with retry mechanism
- Logging of renamed files to prevent duplicate processing

## Requirements

- Python 3.x
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/file-organizer.git
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

2. Click the "Select Directory" button in the GUI.

3. Choose the directory containing the files you want to rename.

4. The application will process each file in the selected directory, generating new names based on their content.

5. Renamed files will be logged to prevent reprocessing in future runs.

## Project Structure

- `main.py`: The main script that runs the GUI and coordinates the file renaming process.
- `file_operations.py`: Contains functions for file operations like renaming and content extraction.
- `openai_integration.py`: Handles integration with OpenAI's API for content analysis and name generation.
- `content_extractors.py`: Provides functions to extract content from various file types.
- `renamed_files.json`: Logs the files that have been renamed to prevent duplicate processing.
- `requirements.txt`: Lists all the Python dependencies required for the project.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).