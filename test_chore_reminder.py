import requests
import json
from datetime import datetime, timedelta, UTC
import time
import sys

# Base URL for the Flask app
BASE_URL = "http://127.0.0.1:5001"

# Global variable to store the reminder ID for subsequent tests
last_created_reminder_id = None
test_user = "demo_user"

# --- Helper Functions for API Calls ---

def create_reminder_api(user_id, chore_name, remind_offset_minutes, due_date=None):
    """
    Sends a POST request to create a new reminder.
    """
    if due_date is None:
        # For this demo, let's make it a minute from now
        due_date = datetime.now(UTC) + timedelta(minutes=1)
    
    data = {
        "user_id": user_id,
        "chore_name": chore_name,
        "due_date": due_date.isoformat(),
        "remind_offset_minutes": remind_offset_minutes
    }
    response = requests.post(f"{BASE_URL}/reminders", json=data)
    return response

def get_reminders_api(user_id):
    """
    Sends a GET request to get all reminders for a user.
    """
    response = requests.get(f"{BASE_URL}/reminders/{user_id}")
    return response

def update_reminder_api(reminder_id, new_chore_name, new_due_date=None, new_offset=None):
    """
    Sends a PUT request to update an existing reminder.
    """
    data = {"chore_name": new_chore_name}
    if new_due_date and new_offset is not None:
        data["due_date"] = new_due_date.isoformat()
        data["remind_offset_minutes"] = new_offset
    response = requests.put(f"{BASE_URL}/reminders/{reminder_id}", json=data)
    return response

def delete_reminder_api(reminder_id):
    """
    Sends a DELETE request to remove a reminder.
    """
    response = requests.delete(f"{BASE_URL}/reminders/{reminder_id}")
    return response

def get_dispatched_reminders_api():
    """
    Sends a GET request to get dispatched reminders.
    """
    response = requests.get(f"{BASE_URL}/dispatched")
    return response

# --- Test Functions ---

def test_create_and_get_reminders():
    """
    Tests creating a new reminder and then immediately fetching it to verify.
    """
    global last_created_reminder_id
    print("\n--- TEST: Create and Get Reminders ---")
    print(f"1. Sending POST request to create a reminder for user '{test_user}'.")
    
    response = create_reminder_api(
        user_id=test_user, 
        chore_name="Take out the trash", 
        remind_offset_minutes=30
    )
    
    print(f"   -> Server responded with status code: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"   -> Response JSON: {json.dumps(response_json, indent=2)}")
        last_created_reminder_id = response_json.get("reminder_id")
        print(f"   -> Stored reminder ID: {last_created_reminder_id}")
    except json.JSONDecodeError:
        print("   -> Failed to decode JSON response.")
        
    print("\n2. Sending GET request to fetch all reminders for the user.")
    response = get_reminders_api(test_user)
    print(f"   -> Server responded with status code: {response.status_code}")
    print(f"   -> Response JSON: {json.dumps(response.json(), indent=2)}")

def test_update_reminder():
    """
    Tests updating an existing reminder.
    """
    if not last_created_reminder_id:
        print("\n[ERROR] No reminder has been created yet. Please run option '1' first.")
        return
        
    print("\n--- TEST: Update Reminder ---")
    print(f"1. Sending PUT request to update reminder ID: {last_created_reminder_id}")
    
    response = update_reminder_api(last_created_reminder_id, "Wash the dishes")
    
    print(f"   -> Server responded with status code: {response.status_code}")
    print(f"   -> Response JSON: {json.dumps(response.json(), indent=2)}")
    
    print("\n2. Sending GET request to verify the update.")
    response = get_reminders_api(test_user)
    print(f"   -> Server responded with status code: {response.status_code}")
    print(f"   -> Response JSON: {json.dumps(response.json(), indent=2)}")

def test_dispatch_and_get():
    """
    Tests the dispatching functionality by creating a reminder that is due soon.
    """
    print("\n--- TEST: Dispatch Reminder and Get Dispatched List ---")
    print("1. Creating a new reminder that is due in 5 seconds.")
    
    due_date = datetime.now(UTC) + timedelta(seconds=5)
    response = create_reminder_api(
        user_id=test_user, 
        chore_name="Water the plants", 
        remind_offset_minutes=1, 
        due_date=due_date
    )
    
    print(f"   -> Server responded with status code: {response.status_code}")
    print(f"   -> Response JSON: {json.dumps(response.json(), indent=2)}")
    
    print("\n2. Pausing for 10 seconds to allow the reminder to be dispatched by the service's background thread.")
    print("   Look at the server terminal for the 'Reminder due' message.")
    time.sleep(10)
    
    print("\n3. Sending GET request to fetch dispatched reminders.")
    response = get_dispatched_reminders_api()
    print(f"   -> Server responded with status code: {response.status_code}")
    print(f"   -> Response JSON: {json.dumps(response.json(), indent=2)}")

def test_delete_reminder():
    """
    Tests deleting a reminder.
    """
    if not last_created_reminder_id:
        print("\n[ERROR] No reminder has been created yet. Please run option '1' first.")
        return
        
    print("\n--- TEST: Delete Reminder ---")
    print(f"1. Sending DELETE request for reminder ID: {last_created_reminder_id}")
    
    response = delete_reminder_api(last_created_reminder_id)
    
    print(f"   -> Server responded with status code: {response.status_code}")
    print(f"   -> Response JSON: {json.dumps(response.json(), indent=2)}")
    
    print("\n2. Sending GET request to verify the deletion.")
    response = get_reminders_api(test_user)
    print(f"   -> Server responded with status code: {response.status_code}")
    print(f"   -> Response JSON: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("Welcome to the Interactive Reminder Service Test Program!")
    print("Please ensure your chore_reminder.py service is running on http://127.0.0.1:5001")
    
    while True:
        print("\n--- Menu ---")
        print("1: Create a new reminder and get all reminders")
        print("2: Update the last created reminder")
        print("3: Test reminder dispatching (will wait 10 seconds)")
        print("4: Delete the last created reminder")
        print("5: Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            test_create_and_get_reminders()
        elif choice == '2':
            test_update_reminder()
        elif choice == '3':
            test_dispatch_and_get()
        elif choice == '4':
            test_delete_reminder()
        elif choice == '5':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

