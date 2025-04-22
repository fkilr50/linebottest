import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, abort

from linebot.v3.messaging import MessagingApi, Configuration
from linebot.v3.webhook import WebhookHandler
from linebot.v3.models import TextMessage, TextSendMessage, MessageEvent
from linebot.v3.exceptions import InvalidSignatureError


load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
line_bot_api = MessagingApi(configuration=configuration)
handler = WebhookHandler(channel_secret=os.getenv("CHANNEL_SECRET"))

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
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("Received message:", event.message.text)

    # all input messages will be processed here
    if "assignments" in event.message.text:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"you have 15 remaining assignments"))

    elif "activities" in event.message.text:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"you have 3 activities next week"))
    
    elif "echo" in event.message.text:
        x = event.message.text
        #x.remove("echo")
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"{event.message.text}"))
    
    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"please try something else"))




    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
