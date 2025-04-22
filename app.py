import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, abort

from linebot.v3.messaging import (
    ApiClient, Configuration, MessagingApi,
    TextSendMessage, ReplyMessageRequest # Add other SendMessage types if needed
)
from linebot.v3.webhooks import (
    WebhookParser, MessageEvent, TextMessage, # Add other Event/Message types if needed
    InvalidSignatureError
)

from linebot.v3.messaging.models.text_send_message import TextSendMessage

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
api_client = ApiClient(configuration=configuration)
line_bot_api = MessagingApi(api_client=api_client) # CORRECT: Pass ApiClient here
parser = WebhookParser(channel_secret=os.getenv("CHANNEL_SECRET"))

@app.route("/")
def index():
    return "LINE bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    
    #logging.info(f"thebod:\n{body}")
    #app.logger.info("Request body: " + body)

    # Handle webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        app.logger.warning("Invalid signature received.")
        abort(400)
    except Exception as e:
        app.logger.error(f"Error parsing webhook request: {e}")
        abort(500) # Internal server error

    for event in events:
        app.logger.info(f"Processing event type: {type(event)}")
        if isinstance(event, MessageEvent):
            # Check if the message content is TextMessage
            if isinstance(event.message, TextMessage):
                 # Call your separate function to handle the text message
                 handle_text_message(event)

    return 'OK'


def handle_text_message(event: MessageEvent):
    print("Received message:", event.message.text)

    input_text = event.message.text
    #reply_token = event.reply_token
    app.logger.info(f"Handling text message: '{input_text}' with token {event.reply_token[:10]}...")
    #output_text = ""

    # all input messages will be processed here
    if "assignments" in input_text.lower():
        output_text = "you have 15 remaining assignments"

    elif "activities" in input_text.lower():
        output_text = "you have 3 activities next week"
    
    elif "echo" in input_text.lower():
        output_text = output_text.lower().replace("echo", "", 1).strip()
    
    else:
        output_text = f"I received '{input_text}'. Please try 'assignments', 'activities', or 'echo [your text]'."



     # --- v3 Replying ---
    try:
        # 1. Create the message object to send using TextSendMessage
        message_to_send = TextSendMessage(text=output_text)

        # 2. Create the ReplyMessageRequest object
        reply_request = ReplyMessageRequest(
            reply_token=output_text,
            messages=[message_to_send] # Messages must be in a list
        )

        # 3. Call the reply_message method with the request object
        line_bot_api.reply_message(reply_request)
        app.logger.info(f"Successfully replied: '{output_text}'")

    except Exception as e:
        # Log any errors during the reply process
        app.logger.error(f"Failed to send reply for token {output_text[:10]}...: {e}")



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
