# YZU LINE BOT
![image](https://github.com/user-attachments/assets/78b73076-1ee5-459f-ab0e-6da788e49901)

## Introduction

YZU LINE BOT is an interactive LINE Bot designed to streamline and simplify access to essential university-related information and tasks for both students and professors. It also serves as an alternative to the YZU APP or in some cases, even the YZU Portal. Through LINE, this bot provides a  way to quickly and easily access your Portal info, reducing the need to navigate complex university web portals directly.

You simply login through the LINE BOT and ask away whatever questions you have about your Portal data. The core of this project can be divided into three parts; The LineBot, Scraper, Database and LLM. All these parts are essential for the bot to work properly and as intended. 

## Running the Code
Setting up the bot requires many different steps to be done first before being able to chat with the bot. 

### 1. Line Side
Because this bot is powered with the line-bot sdk, we have to first make sure that our code has properly connect to LINE's servers by entering the correct channel infomations into the code's env file. These channel informations can be found in the LINE Official Account Manager.
![image](https://github.com/user-attachments/assets/f20548db-dad1-45e4-b455-786f65fcca44)
![image](https://github.com/user-attachments/assets/e9a6c8a0-113b-4354-be10-8e231825e2c2)

### 2. Host Side
After making sure that everything on the side of LINE is correct, we have to setup an API gateway and then entering that link into the Webhook URL in our LINE Official Account Manager.
![image](https://github.com/user-attachments/assets/1a302878-fd7f-40f8-a8ea-bb76ce0a1076)

### 3. Running the code
Now that the setup is complete, the bot is now able to take in HTTP requests and reply back to the user in LINE by running the code in VSCode.
![image](https://github.com/user-attachments/assets/e5b60436-3076-4d3f-aef0-3726b8b4e905)



