import os
from openai import OpenAI
from file_operations import sanitize_filename
import re
import time

def create_assistant(client):
    assistant = client.beta.assistants.create(
        name="File Naming Assistant",
        instructions="You are a helpful assistant that generates concise and descriptive filenames based on file content. Keep the original filename in mind and try to improve upon it rather than completely changing it. Maintain key information from the original filename. Avoid using generic terms like 'Sheet' or 'List' unless they are specifically relevant to the content.",
        model="gpt-3.5-turbo-16k"
    )
    return assistant

def generate_name_from_content(file_path, client, assistant, content):
    try:
        original_filename = os.path.basename(file_path)
        thread = client.beta.threads.create()
        
        # Truncate content if it's too long
        max_content_length = 15000  # Reduced from 25000
        truncated_content = content[:max_content_length] if len(content) > max_content_length else content
        
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f'Generate a concise and descriptive filename for this file based on its content and the original filename, without file extension. The new filename should be similar in length to the original. Enclose the filename in quotes. Original filename: "{original_filename}" Content: "{truncated_content}"'
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
        
        # Extract the actual filename from the assistant's response
        filename_match = re.search(r'"([^"]*)"', assistant_message)
        if filename_match:
            return filename_match.group(1)
        else:
            return assistant_message.strip()
    
    except Exception as e:
        print(f"Error generating name: {e}")
        return None