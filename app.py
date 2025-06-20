import os   # app.py
import logging
import schedule as s

from page_scraping import attempt_login, initialize_driver # tanya gemini bsk ini maksudnya paa apakah semuanya jadi ke run gt
from dotenv import load_dotenv
load_dotenv()
#print(f"load_dotenv() executed. Found and loaded .env")

from flask import Flask, request, abort
from cryptography.fernet import Fernet
from ml_classifier import main
# from transformers import pipeline
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
#print("URL:", url[:10])

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
    PushMessageRequest
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

#classifier = pipeline("zero-shot-classification")

key: str = os.environ.get("FKEY")
key_bytes = key.encode('utf-8')
cypher = Fernet(key_bytes) 

configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
api_client = ApiClient(configuration=configuration)
line_bot_api = MessagingApi(api_client=api_client)
parser = WebhookParser(channel_secret=os.getenv("CHANNEL_SECRET"))

@app.route("/")
def index():
    return "LINE bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value for security purposes
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

    # setelah textnya di process, set route replynya disini
    for event in events:
        app.logger.info(f"Processing event type: {type(event)}")
        if isinstance(event, MessageEvent): # A lot of different types of MessageEvent
            if isinstance(event.message, TextMessageContent):
                handle_text_message(event)
            else:
                print("It's not a TextMessageContent from user")
        elif isinstance(event, FollowEvent):
            # Bot has been added, asks for id and pass
            handle_follow_event(event)
        else:
            print("Unhandled event)")

    return 'OK'


# huggingface input and output in this function
def handle_text_message(event: MessageEvent): 
    print("Received message:", event.message.text)
    
    response = (
        supabase.table("Login data")
        .select("LineID")
        .eq("LineID", event.source.user_id)
        .execute()
    )

    if response.data:
        input_text = event.message.text
        app.logger.info(f"Handling text message: '{input_text}' with token {event.reply_token[:10]}...")

        # all input messages will be processed here
        #label = classify(input_text)
        if "echo" in event.message.text:
            output_text = event.message.text.lower().replace("echo", "", 1).strip()

        else:
            output_text = main(event.message.text, event.source.user_id)

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
    else:
        handle_new_user(event)

def handle_follow_event(event: FollowEvent):
    userid = event.source.user_id

    print("Bot has been added by:", userid)
    #push greeting message
    output_text = "Hello, I am testBotN.\nPlease state whether you are a \"Student\" or \"Professor\"." 

    push_request = PushMessageRequest(
        to = userid,
        messages = [TextMessage(text = output_text)]
    )

    line_bot_api.push_message(push_request)
    app.logger.info(f"Successfully sent: '{output_text}'")

    
def handle_new_user(event):
    text = event.message.text.lower()
    response1 = (
        supabase.table("temp student login data")
        .select("LineID")
        .eq("LineID", event.source.user_id)
        .execute()
    )

    response2 = (
        supabase.table("temp professor login data")
        .select("LineID")
        .eq("LineID", event.source.user_id)
        .execute()
    )

    if response1.data:
        handle_new_user_student(event)
    elif response2.data:
        handle_new_user_professor(event)
    else: 
        if "student" in text:
            response = (
                supabase.table("temp student login data")
                .insert({"LineID": event.source.user_id})
                .execute()
            )
            output_text = "Please state your portal id and password EACH IN ONE SEPARATE MESSAGE:) with the following format;\n\nstudent id: 1123xxx\npassword: 123xx"

        elif "professor" in text:
            response = (
                supabase.table("temp professor login data")
                .insert({"LineID": event.source.user_id})
                .execute()
            )
            output_text = output_text = "Please state your portal id and password each in one separate message with the following format;\n\nprofessor id: 1123xxx\npassword: 123xx"

        else:
            output_text = "Text not recognized.\nPlease state whether you are a \"Student\" or \"Professor\"."
        
        reply_request = ReplyMessageRequest(
            reply_token = event.reply_token,     
            messages = [TextMessage(text = output_text)] # Messages must be in a list
        )
        line_bot_api.reply_message(reply_request)
        app.logger.info(f"Successfully replied: '{output_text}'")

def handle_new_user_professor(event):
    user_id = event.source.user_id
    text = event.message.text 

    response = (
        supabase.table("temp professor login data")
        .select("PrID", "Ps")
        .eq("LineID", str(user_id))
        .execute()
    )
    tempid =  response.data[0].get("PrID") 
    tempps =  response.data[0].get("Ps") 

    output_text = "Sorry, I didn't understand. Please enter with the correct format"

    if tempid is None and ("professor" in text or "id" in text):
        portalid = getpid(text)
        if portalid:
            response = (
                supabase.table("temp professor login data")
                .update({"PrID": portalid})
                .eq("LineID", user_id)
                .execute()
            )
            output_text = f"Professor ID received.\n({portalid})"
        else:
            output_text = "Could not extract ID. Please use the format: 'professor id: 1123xxx'"

    if tempps is None and ("pass" in text or "password" in text):
        portalpass = getpass(text)
        #app.logger.info(f"portalpass adalah: {portalpass}")
        if portalpass:
            response = (
                supabase.table("temp professor login data")
                .update({"Ps": portalpass})
                .eq("LineID", user_id)
                .execute()
            )
            output_text = f"Password received.\n({portalpass})"
            #app.logger.info(f"portalpass adalah: {newusers[user_id]["pass"]}")
        else:
            output_text = "Could not extract password. Try: 'password: abc123'"

    #   refresh with new data
    response = (
        supabase.table("temp professor login data")
        .select("PrID", "Ps")
        .eq("LineID", str(user_id))
        .execute()
    )
    tempid =  response.data[0].get("PrID") 
    tempps =  response.data[0] .get("Ps") 

    # after both are collected
    if tempid and tempps:
        app.logger.info(f"User {user_id} registering with ID: {tempid}")
        driver = initialize_driver()
        if attempt_login(driver, tempid, tempps) == True:
            
            encpass = enkrip(tempps)
            try:
                datatobeinserted = {
                    "LineID": user_id,
                    "PrID": tempid,
                    "Ps": encpass
                }

                response = (
                    supabase.table("Login data")
                    .insert(datatobeinserted)
                    .execute()
                )

                if response.data:
                    print(f"Successfully inserted data into supa: {response}")
                else:
                    print("Insert failed.")
                    if hasattr(response, 'error') and response.error:
                        print(f"Error details: {response.error.message}")

            except Exception as e:
                print(f"An error occurred: {e}")
                if hasattr(e, 'json') and callable(e.json):
                    try:
                        print(f"APIError details: {e.json()}")
                    except:
                        pass

            response = (
                supabase.table("temp professor login data")
                .delete()
                .eq("LineID", user_id)
                .execute()
            )   
            output_text = f"Registration complete. You can now inquire about your assignments, activities, or test with ''!"
        else:
            response = (
                supabase.table("temp professor login data")
                .update({"Ps": None, "PrID": None})
                .eq("LineID", user_id)
                .execute()
            )
            output_text = "Failed to login with current StudentID and Password.\nPlease recheck and try again."

    # Reply
    reply_request = ReplyMessageRequest(
        reply_token = event.reply_token,
        messages = [TextMessage(text = output_text)]
    )
    line_bot_api.reply_message(reply_request)


def handle_new_user_student(event):
    user_id = event.source.user_id
    text = event.message.text 

    #fetching past data
    response = (
        supabase.table("temp student login data")
        .select("StID", "Ps")
        .eq("LineID", str(user_id))
        .execute()
    )
    tempid =  response.data[0].get("StID") 
    tempps =  response.data[0].get("Ps") 

    #user_data = newusers[user_id]

    output_text = "Sorry, I didn't understand. Please enter with the correct format"

    if tempid is None and ("student" in text or "id" in text):
        portalid = getid(text)
        if portalid:
            #newusers[user_id]["id"] = f"s{portalid}"
            response = (
                supabase.table("temp student login data")
                .update({"StID": portalid})
                .eq("LineID", user_id)
                .execute()
            )
            output_text = f"Student ID received.\n({portalid})"
        else:
            output_text = "Could not extract ID. Please use the format: 'student id: 1123xxx'"

    if tempps is None and ("pass" in text or "password" in text):
        portalpass = getpass(text)
        #app.logger.info(f"portalpass adalah: {portalpass}")
        if portalpass:
            #newusers[user_id]["pass"] = portalpass
            
            response = (
                supabase.table("temp student login data")
                .update({"Ps": portalpass})
                .eq("LineID", user_id)
                .execute()
            )
            output_text = f"Password received.\n({portalpass})"
            #app.logger.info(f"portalpass adalah: {newusers[user_id]["pass"]}")
        else:
            output_text = "Could not extract password. Try: 'password: abc123'"

    #   refresh with new data
    response = (
        supabase.table("temp student login data")
        .select("StID", "Ps")
        .eq("LineID", str(user_id))
        .execute()
    )
    tempid =  response.data[0].get("StID") 
    tempps =  response.data[0] .get("Ps") 

    # after both are collected
    if tempid and tempps:
        app.logger.info(f"User {user_id} registering with ID: {tempid}")
        driver = initialize_driver()
        if attempt_login(driver, tempid, tempps) == True:
            
            encpass = enkrip(tempps)
            try:
                datatobeinserted = {
                    "LineID": user_id,
                    "StID": tempid,
                    "Ps": encpass
                }

                response = (
                    supabase.table("Login data")
                    .insert(datatobeinserted)
                    .execute()
                )

                if response.data:
                    print(f"Successfully inserted data into supa: {response}")
                else:
                    print("Insert failed.")
                    if hasattr(response, 'error') and response.error:
                        print(f"Error details: {response.error.message}")

            except Exception as e:
                print(f"An error occurred: {e}")
                if hasattr(e, 'json') and callable(e.json):
                    try:
                        print(f"APIError details: {e.json()}")
                    except:
                        pass

            #response = f"Registration complete. You can now use commands like 'assignments', 'activities' or 'echo'."
            #del newusers[user_id]
            response = (
                supabase.table("temp student login data")
                .delete()
                .eq("LineID", user_id)
                .execute()
            )   
            output_text = f"Registration complete. You can now use commands like 'assignments', 'activities' or 'echo'."
        else:
            response = (
                supabase.table("temp student login data")
                .update({"Ps": None, "StID": None})
                .eq("LineID", user_id)
                .execute()
            )
            output_text = "Failed to login with current StudentID and Password.\nPlease recheck and try again."

    # Reply
    reply_request = ReplyMessageRequest(
        reply_token = event.reply_token,
        messages = [TextMessage(text = output_text)]
    )
    line_bot_api.reply_message(reply_request)

def getpid(string):
    prid = ""
    if any(sep in string.lower() for sep in ["=", ":", ";", "is"]):
        x = string.find(':')
        if string[x + 1] == ' ':
            x += 1
        for i in range (x + 1, len(string), 1):
            if string[i] == ' ':
                break
            else:
                prid += string[i]
    return prid

def getid(string):
    stid = ""
    if "student" in string.lower() or "id" in string.lower():
        try:
            x = string.find('1')
            y = len(string) - x
            for i in range (len(string) - y, (len(string)- y) + 7, 1):
                stid += string[i]
            return 's' + stid
        except: 
            return None
    else:
        print("please enter id with the format given")

def getpass(string):
    pword = ""
    if any(sep in string.lower() for sep in ["=", ":", ";", "is"]):
        x = string.find(':')
        if string[x + 1] == ' ':
            x += 1
        for i in range (x + 1, len(string), 1):
            if string[i] == ' ':
                break
            else:
                pword += string[i]
    return pword 


"""def classify(line):
    res = classifier(
        line,
        candidate_labels = ["assignments", "activities", "other"]
    )
    app.logger.info(f"res adalah: {res}")
    largest = reduce(max, res["scores"])
    for i in range (0, len(res["labels"]), 1):
        if res["scores"][i] == largest:
            hasil = res["labels"][i]
    print(hasil)
    return str(hasil)"""

def enkrip(password):
    password = password.encode()
    token = cypher.encrypt(password) 
    return str(token)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)