import schedule as s
from datetime import datetime, timedelta, timezone
import time
import threading
import app
import os
import schedule
from supabase import create_client, Client
from flask import Flask, request, abort
from linebot.v3 import (
    WebhookParser
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest
)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
api_client = ApiClient(configuration=configuration)
line_bot_api = MessagingApi(api_client=api_client)
parser = WebhookParser(channel_secret=os.getenv("CHANNEL_SECRET"))


# Checker for activities
def assignmentchecker():
    now_utc = datetime.now(timezone.utc)

    response = (
        supabase.table("Assignment table")
        .select("LineID", "Assignment Name", "end_datetime", "flag3", "flag1")
        .execute()
    )

    push_text = ""
    for entry in response.data:
        if entry["flag3"] == None and entry["end_datetime"].date() == (now_utc + timedelta(days=3)).date(): # AND the time is less than three days
            push_text = f"You have the assignment ({entry["Assignment_Name"]}) due in 3 days"
            response = (
                supabase.table("Assignment table")
                .update({"flag3": 1})
                .eq("id", entry["id"])
                .execute()
            )
        elif entry["flag1"] == None and entry["end_datetime"].date() == (now_utc + timedelta(days=1)).date(): # AND the time is less than a day
            push_text = f"You have the assignment ({entry["Assignment_Name"]}) due in 1 day"
            response = (
                supabase.table("Assignment table")
                .update({"flag1": 1})
                .eq("id", entry["id"])
                .execute()
            )
        else:
            continue

        if push_text != None:
            push_request = PushMessageRequest(
            to = entry["LineID"],
            messages = [TextMessage(text = push_text)]
            ) 

            line_bot_api.push_message(push_request)
            app.logger.info(f"Successfully sent: '{push_text}'")

# Checker for activities
def activitieschecker(): 
    now_utc = datetime.now(timezone.utc)

    response = (
        supabase.table("Activities table")
        .select("id", "LineID", "Activity Name", "end_datetime", "flag3", "flag1")
        .execute()
    )

    for entry in response.data:
        push_text = ""
        if entry["flag3"] == None and entry["end_datetime"].date() == (now_utc + timedelta(days=3)).date(): # AND the time is less than three days
            push_text = f"You have the activity ({entry["Activities_Name"]}) due in 3 days"
            response = (
                supabase.table("Activities table")
                .update({"flag3": 1})
                .eq("id", entry["id"])
                .execute()
            )
        elif entry["flag1"] == None and entry["end_datetime"].date() == (now_utc + timedelta(days=1)).date(): # AND the time is less than a day
            push_text = f"You have the activity ({entry["Activities_Name"]}) due in 1 day"
            response = (
                supabase.table("Activities table")
                .update({"flag1": 1})
                .eq("id", entry["id"])
                .execute()
            )
        else:
            continue
        
        if push_text:
            push_request = PushMessageRequest(
            to = entry["LineID"],
            messages = [TextMessage(text = push_text)]
            )

            line_bot_api.push_message(push_request)
            app.logger.info(f"Successfully sent: '{push_text}'")
    

# --- Background Task Function using 'schedule' library ---
def run_scheduled_tasks():
    """This function will be the target of our background thread."""
    print("Background task runner started.")
    # Schedule your checker functions
    schedule.every(3).minutes.do(assignmentchecker)
    schedule.every(3).minutes.do(activitieschecker)

    while True:
        schedule.run_pending()
        time.sleep(3) # Check schedule every second

# --- Function to Start Background Thread ---
def start_reminder_thread():
    print("Starting reminder background thread...")
    thread = threading.Thread(target = run_scheduled_tasks)
    thread.daemon = True 
    thread.start()
    print("Reminder background thread started.")

# --- Main Execution Block ---
if __name__ == "__main__":
    start_reminder_thread()  # Start the background thread for reminders
    # Start the Flask web server (for LINE webhooks)
    # Gunicorn will handle this in production based on your Procfile
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on host 0.0.0.0, port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False) # debug=False, use_reloader=False for stability with threads