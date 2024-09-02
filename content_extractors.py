from PyPDF2 import PdfReader
import docx
import pandas as pd
import csv
import os
from openai import OpenAI

def extract_pdf_content(file_path):
    """
    Extract the text content from a PDF file.
    
    :param file_path: Path to the PDF file
    :return: Extracted text content as a string
    """
    content = ""
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            content += page.extract_text()
    return content

def extract_word_content(file_path):
    """
    Extract the text content from a Word document.
    
    :param file_path: Path to the Word file
    :return: Extracted text content as a string
    """
    doc = docx.Document(file_path)
    return ' '.join([paragraph.text for paragraph in doc.paragraphs])

def extract_text_content(file_path):
    """
    Extract the content from a text file.
    
    :param file_path: Path to the text file
    :return: Extracted text content as a string
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_excel_content(file_path):
    """
    Extract sheet names and column headers from all sheets in an Excel file.
    
    :param file_path: Path to the Excel file
    :return: Summary of sheet names and their column headers as a string
    """
    xl = pd.ExcelFile(file_path)
    sheets_summary = []
    
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)
        columns = ', '.join(df.columns)
        sheets_summary.append(f"Sheet '{sheet_name}': {columns}")
    
    return ' | '.join(sheets_summary)

def extract_csv_content(file_path):
    """
    Extract column headers and a sample of data from a CSV file.
    
    :param file_path: Path to the CSV file
    :return: Summary of column headers and a sample of data as a string
    """
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        headers = next(csv_reader, None)
        if headers:
            sample_data = [next(csv_reader, None) for _ in range(5)]  # Get up to 5 rows as a sample
            headers_str = ', '.join(headers)
            sample_str = ' | '.join([', '.join(row) if row else '' for row in sample_data])
            return f"Headers: {headers_str}\nSample data: {sample_str}"
        else:
            return "Empty CSV file"

def extract_audio_content(file_path, api_key):
    """
    Extract the text content from an audio file using OpenAI's Whisper model.
    
    :param file_path: Path to the audio file
    :param api_key: OpenAI API key
    :return: Transcribed text content as a string
    """
    client = OpenAI(api_key=api_key)
    
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    
    return transcription.text