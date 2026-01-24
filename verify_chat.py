import requests
import json
import uuid
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/chat"
# Replace with a real restaurant UID from your database
RESTAURANT_UID = "PLACEHOLDER_UID"

def test_chat_new_thread():
    print("Testing new thread creation...")
    url = f"{BASE_URL}/{RESTAURANT_UID}/"
    payload = {
        "message": "What is on the menu today?"
    }
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['ai_response'][:100]}...")
        print(f"Thread UID: {data['thread_uid']}")
        return data['thread_uid']
    else:
        print(f"Error: {response.text}")
        return None

def test_chat_continue_thread(thread_uid):
    print(f"\nTesting thread continuation for {thread_uid}...")
    url = f"{BASE_URL}/{RESTAURANT_UID}/"
    payload = {
        "thread_uid": thread_uid,
        "message": "Are there any items without beef?"
    }
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['ai_response'][:100]}...")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    if RESTAURANT_UID == "PLACEHOLDER_UID":
        print("Please set a real RESTAURANT_UID in the script before running.")
        sys.exit(1)

    thread_id = test_chat_new_thread()
    if thread_id:
        test_chat_continue_thread(thread_id)
