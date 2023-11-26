import requests
import os
import time
from openai import OpenAI

client = OpenAI()

# Set your API key from an environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v1"
}

def list_assistants():
    url = "https://api.openai.com/v1/assistants"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # This will raise an exception for HTTP error codes
        assistants = response.json()
        for assistant in assistants['data']:
            print(f"{assistant['id']}: {assistant['name']}")
    except requests.RequestException as e:
        print(f"Error listing assistants: {e}")

def wait_for_completion(client, thread_id, run_id, check_interval=5):
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.status == 'completed':
                #print(f"Run {run.id} completed.")
                print()
                break
            else:
                #print(f"Waiting for run {run.id} to complete. Current status: {run.status}")
                print(f"Waiting...")
                time.sleep(check_interval)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

# Function to print the latest message from the assistant
def print_latest_assistant_message(messages):
    # Filter messages by the assistant
    assistant_messages = [msg for msg in messages if msg.role == 'assistant']
    
    if assistant_messages:
        # Sort messages based on 'created_at' to get the latest message
        latest_message = sorted(assistant_messages, key=lambda x: x.created_at, reverse=True)[0]
        
        # Extract and print the content of the latest message
        latest_content = latest_message.content[0].text.value
        print("Bot:", latest_content)
    else:
        print("No messages from the assistant found.")

def get_multiline_input(prompt, end_marker="EOF"):
    print(prompt)
    print(f"(Type '{end_marker}' on a new line when you're done)")

    lines = []
    while True:
        line = input()
        if line == end_marker:
            break
        lines.append(line)
    return "\n".join(lines)

def chat_with_bot(assistant_id):
    print("\nChat with the bot! Type 'quit' to exit.")
    thread = client.beta.threads.create()
    while True:
        user_input = get_multiline_input("\nYou:")
        if user_input.lower() in ['quit', 'exit']:
            print("Exiting chat.")
            break

        try:
            # Create new message with user input
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
    		    role="user",
    		    content=user_input
	        )

            # Run the message with the assistant and wait for answer
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=chosen_assistant_id,
            )

            # Call the function to wait for completion
            wait_for_completion(client, thread.id, run.id)

            # Get the response
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )

            # Print the latest messages
            print_latest_assistant_message(messages)

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Available Assistants:")
    list_assistants()
    chosen_assistant_id = input("ID of the assistant: ")
    chat_with_bot(chosen_assistant_id)