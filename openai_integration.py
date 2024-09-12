import os
from openai import OpenAI
from file_operations import FileOperations
import re
import time

class OpenAIIntegration:
    def __init__(self):
        self.file_ops = FileOperations()

    def create_client(self):
        api_key = os.getenv("openai_api_key")
        return OpenAI(api_key=api_key)

    def create_assistant(self, client):
        assistant = client.beta.assistants.create(
            name="File Naming and Tagging Assistant",
            instructions="""You are an expert file naming and tagging assistant that generates concise, descriptive, and SEO-friendly filenames based on file content and context, as well as relevant tags. Your task is to create:

1. Filenames that are:
   [existing filename criteria]

2. Tags that are:
   - Relevant: Accurately represent the main topics or themes of the file.
   - Concise: Use single words or short phrases.
   - Informative: Provide additional context not captured in the filename.
   - Limited: Provide 3-5 tags per file.

Always enclose your suggested filename in quotes and provide a comma-separated list of tags enclosed in square brackets.

Example response:
"2023-Annual-Marketing-Strategy-v2.1" [marketing, strategy, annual-report, 2023]""",
            model="gpt-3.5-turbo-16k"
        )
        return assistant

    def generate_name_from_content(self, file_path, client, assistant, content):
        try:
            original_filename = os.path.basename(file_path)
            thread = client.beta.threads.create()
            
            # Truncate content if it's too long
            max_content_length = 15000  # Reduced from 25000
            truncated_content = content[:max_content_length] if len(content) > max_content_length else content
            
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f'Generate a concise and descriptive filename for this file based on its content and the original filename, without file extension. Enclose the filename in quotes. Original filename: "{original_filename}" Content: "{truncated_content}"'
            )
            
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            
            while run.status != 'completed':
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            assistant_message = messages.data[0].content[0].text.value
            
            # Extract the actual filename and tags from the assistant's response
            filename_match = re.search(r'"([^"]*)"', assistant_message)
            tags_match = re.search(r'\[(.*?)\]', assistant_message)
            
            if filename_match and tags_match:
                filename = filename_match.group(1)
                tags = [tag.strip() for tag in tags_match.group(1).split(',')]
                return filename, tags
            else:
                return None, None
        
        except Exception as e:
            print(f"Error generating name and tags: {e}")
            return None, None