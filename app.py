import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookParser
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FollowEvent
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    PushMessageRequest,
    PushMessageResponse
)

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
api_client = ApiClient(configuration=configuration)
line_bot_api = MessagingApi(api_client=api_client)
parser = WebhookParser(channel_secret=os.getenv("CHANNEL_SECRET"))

@app.route("/")
def index():
    return "LINE bot is running!"

newusers = {}

@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # Get request body as text
    body = request.get_data(as_text=True)
    # logging.info
    app.logger.info("Request body: " + body)

    # Handle webhook body
    try:
        events = parser.parse(body, signature)
        app.logger.info("Attempt to parse body")
    except InvalidSignatureError:
        app.logger.warning("Invalid signature received.")
        abort(400)
    except Exception as e:
        app.logger.error(f"Error parsing webhook request: {e}")
        abort(500)

    for event in events:
        app.logger.info(f"Processing event type: {type(event)}")
        if isinstance(event, MessageEvent): 
            if isinstance(event.message, TextMessageContent):
                handle_text_message(event)
            else:
                print("It's not a TextMessageContent from user")
        elif isinstance(event, FollowEvent):
            # Bot has been added, asks for id and pass
            newusers[event.source.user_id] = {"id": None, "pass": None}
            handle_follow_event(event)
            continue
        else:
            print("UNhandled event)")

    return 'OK'


def handle_text_message(event: MessageEvent):
    print("Received message:", event.message.text)
    if event.source.user_id in newusers:
        handle_new_user(event)

    else:
        input_text = event.message.text
        app.logger.info(f"Handling text message: '{input_text}' with token {event.reply_token[:10]}...")

        # all input messages will be processed here

        if event.source.user_id in newusers:
            handle_new_user(event)

        elif "assignments" in input_text.lower():
            output_text = "you have 15 remaining assignments"

        elif "activities" in input_text.lower():
            output_text = "you have 3 activities next week"
        
        elif "echo" in input_text.lower():
            output_text = event.message.text.lower().replace("echo", "", 1).strip()
        
        else:
            output_text = f"I received '{input_text}'. Please try 'assignments', 'activities', or 'echo [your text]'."


        # --- v3 Replying ---
        try:
            # 1. Create the ReplyMessageRequest object
            reply_request = ReplyMessageRequest(
                reply_token = event.reply_token,     
                messages = [TextMessage(text = output_text)] # Messages must be in a list
            )

            # 2. Call the reply_message method with the request object
            line_bot_api.reply_message(reply_request)
            app.logger.info(f"Successfully replied: '{output_text}'")

        except Exception as e:
            # Log any errors during the reply process
            app.logger.error(f"Failed to send reply for token {event.reply_token[:10]}...: {e}")


def handle_follow_event(event: FollowEvent):
    userid = event.source.user_id
    newusers[event.source.user_id] = {"id": None, "pass": None}

    print("Bot has been added by:", userid)
    
    output_text = "Hello, I am testBot25.\nPlease state your portal id and pass each in one different message with the following format;\n\nstudent id: 1123xxx\npassword: 123xx" 

    push_request = PushMessageRequest(
        to = userid,
        messages = [TextMessage(text = output_text)]
    )

    line_bot_api.push_message(push_request)
    app.logger.info(f"Successfully sent: '{output_text}'")


def handle_new_user(event):
    user_id = event.source.user_id
    text = event.message.text.lower()
    portalid = ""
    portalpass = ""

    user_data = newusers[user_id]

    response = "Sorry, I didn't understand. Try 'student id: 1123xxx' or 'password: abc123'"

    if user_data["id"] is None and ("student" in text or "id" in text):
        portalid = getid(text)
        if portalid:
            newusers[user_id]["id"] = portalid
            response = f"Student ID received.\n{portalid}"
        else:
            response = "Could not extract ID. Please use the format: 'student id: 1123xxx'"

    if user_data["pass"] is None and ("pass" in text or "password" in text):
        portalpass = getpass(text)
        if portalpass:
            newusers[user_id]["pass"] = portalpass
            response = f"Password received.\n({portalpass})"
        else:
            response = "Could not extract password. Try: 'password: abc123'"
    
    # After both are collected
    if newusers[user_id]["id"] and newusers[user_id]["pass"]:
        app.logger.info(f"User {user_id} registered with ID: {user_data['id']} and pass: {user_data['pass']}")
        response = f"Registration complete. You can now use commands like 'assignments', 'schedule' or 'echo'."
        del newusers[user_id]

    # Reply
    reply_request = ReplyMessageRequest(
        reply_token = event.reply_token,
        messages = [TextMessage(text = response)]
    )
    line_bot_api.reply_message(reply_request)


def getid(body):
    stid = ""
    if "student" in body.lower() or "id" in body.lower():
        try:
            x = body.find('1')
            y = len(body) - x
            for i in range (len(body) - y, (len(body)- y) + 7, 1):
                stid += body[i]
            return stid
        except: 
            return None
    else:
        print("please enter id with the format given")

def getpass(string):
    pword = ""
    if "is" in string.lower():
        x = string.find('is')

        for i in range (x + 3, len(string), 1):
            if string[i] == ' ':
                break
            else:
                pword += string[i]

    elif any(sep in string.lower() for sep in ["=", ":", ";"]):
        x = string.find(':')
        if string[x + 1] == ' ':
            x += 1
        for i in range (x + 1, len(string), 1):
            if string[i] == ' ':
                break
            else:
                pword += string[i]
    return pword 

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
