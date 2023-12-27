import json
import requests
import os
from openai import OpenAI
from prompts import assistant_instructions
from apikeys import OPENAI_API_KEY, AIRTABLE_API_KEY

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
os.environ['AIRTABLE_API_KEY'] = AIRTABLE_API_KEY

# Init OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY) 


# Add thread to DB with platform identifier
def add_thread(thread_id, platform):
  url = "https://api.airtable.com/v0/appwtMgZAn4c7bTvF/Threads" # replace this with your Airtable Web API URL
  headers = {
      "Authorization": AIRTABLE_API_KEY,
      "Content-Type": "application/json"
  }
  data = {
      "records": [{
          "fields": {
              "Thread ID": thread_id,
              "Platform": platform
          }
      }]
  }

  try:
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
      print("Thread added to DB successfully.")
    else:
      # Handle non-200 HTTP response status codes
      print(
          f"Failed to add thread: HTTP Status Code {response.status_code}, Response: {response.text}"
      )
  except Exception as e:
    # Handle exceptions like network errors, request timeouts, etc.
    print(f"An error occurred while adding the thread: {e}")


# Create or load assistant
def create_assistant(client):
  assistant_file_path = 'assistant.json'

  # If there is an assistant.json file already, then load that assistant
  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    # If no assistant.json is present, create a new assistant using the below specifications

    # To change the knowledge document, modify the file name below to match your document
    # If you want to add multiple files, paste this function into ChatGPT and ask for it to add support for multiple files
    file = client.files.create(file=open("knowledge.docx", "rb"),
                               purpose='assistants')

    assistant = client.beta.assistants.create(
        # Change prompting in prompts.py file
        instructions=assistant_instructions,
        model="gpt-4-1106-preview",
        tools=[{
            "type": "retrieval"  # This adds the knowledge base as a tool
        }],
        file_ids=[file.id])

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id
