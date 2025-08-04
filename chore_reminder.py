from flask import Flask, request, jsonify
from datetime import datetime, timedelta, UTC
import uuid
import threading
import time
import queue

app = Flask(__name__)

# In-memory storage
reminders = {}
# Keep track of which reminders have already been sent
dispatched_reminders = set()
# A queue to hold reminders that need to be dispatched
dispatch_queue = queue.Queue()

# Create a new reminder
@app.route("/reminders", methods=["POST"])
def create_reminder():
    data = request.json
    try:
        reminder_id = str(uuid.uuid4())
        due_date = datetime.fromisoformat(data["due_date"])
        remind_time = due_date - timedelta(minutes=data["remind_offset_minutes"])

        reminder = {
            "reminder_id": reminder_id,
            "chore_name": data["chore_name"],
            "user_id": data["user_id"],
            "due_date": due_date.isoformat(),
            "remind_time": remind_time.isoformat()
        }
        reminders[reminder_id] = reminder
        return jsonify(reminder), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Get all reminders for a user
@app.route("/reminders/<user_id>", methods=["GET"])
def get_reminders(user_id):
    user_reminders = [
        reminder for reminder in reminders.values()
        if reminder["user_id"] == user_id
    ]
    return jsonify(sorted(user_reminders, key=lambda r: r["due_date"])), 200

# Update an existing reminder
@app.route("/reminders/<reminder_id>", methods=["PUT"])
def update_reminder(reminder_id):
    if reminder_id not in reminders:
        return jsonify({"error": "Reminder not found"}), 404

    data = request.json
    reminder = reminders[reminder_id]

    if "chore_name" in data:
        reminder["chore_name"] = data["chore_name"]
    if "due_date" in data and "remind_offset_minutes" in data:
        due_date = datetime.fromisoformat(data["due_date"])
        reminder["due_date"] = due_date.isoformat()
        reminder["remind_time"] = (due_date - timedelta(minutes=data["remind_offset_minutes"])).isoformat()

    reminders[reminder_id] = reminder
    return jsonify(reminder), 200

# Delete a reminder
@app.route("/reminders/<reminder_id>", methods=["DELETE"])
def delete_reminder(reminder_id):
    if reminder_id in reminders:
        del reminders[reminder_id]
        # Also remove from dispatched reminders if it exists
        if reminder_id in dispatched_reminders:
            dispatched_reminders.remove(reminder_id)
        return jsonify({"message": "Reminder deleted"}), 200
    else:
        return jsonify({"error": "Reminder not found"}), 404
    
def dispatch_loop():
    while True:
        now = datetime.now(UTC)
        for reminder_id, reminder in list(reminders.items()):
            remind_time = datetime.fromisoformat(reminder["remind_time"])
            if reminder_id not in dispatched_reminders and remind_time <= now:
                # Print the reminder due message
                print(f"Reminder for user {reminder['user_id']}: Chore '{reminder['chore_name']}' is due!")
                
                # Put the reminder details into the queue
                dispatch_queue.put(reminder)
                dispatched_reminders.add(reminder_id)
								
        time.sleep(60)

# Endpoint to get dispatched reminders
@app.route("/dispatched", methods=["GET"])
def get_dispatched_reminders():
    dispatched = []
    # Get all items currently in the queue
    while not dispatch_queue.empty():
        dispatched.append(dispatch_queue.get())
    return jsonify(dispatched), 200

if __name__ == "__main__":
    # Start background dispatch thread
    dispatch_thread = threading.Thread(target=dispatch_loop, daemon=True)
    dispatch_thread.start()
    
    app.run(debug=True, port=5001)