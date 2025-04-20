import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import logging

app = Flask(__name__)

line_bot_api = LineBotApi('dSnC5XyuryPz4LZqiqPezEjkVUrt7Ihw1OGvsulf3xIdZfRlNOKdiIKufCW1/LYUDZD/MZSYdftj8ZKuQJOnNCzv6PGBHQDelKYpZGs/waYp5oHYptnVbLFv1QOauUYCKBDsm/J0jmrz2T2uQgohHgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('77290a3cf310d97b2ea31faa35dbdb1a')


@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    logging.basicConfig(level=logging.INFO)
    logging.info(f"thebod:\n{body}")
    app.logger.info("Request body: " + body)

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """ Here is all the messages will be handled and processed by the program """
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))
    print("Received message:", event.message.text)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
