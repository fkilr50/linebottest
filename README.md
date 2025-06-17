# YZU LINE BOT
![image](https://github.com/user-attachments/assets/78b73076-1ee5-459f-ab0e-6da788e49901)

## Introduction (Overall Project)

YZU LINE BOT is an interactive LINE Bot designed to streamline and simplify access to essential university-related information and tasks for both students and professors. It also serves as an alternative to the YZU APP or in some cases, even the YZU Portal. Through LINE, this bot provides a way to quickly and easily access your Portal info, reducing the need to navigate complex university web portals directly.

You simply login through the LINE BOT and ask away whatever questions you have about your Portal data. The core of this project can be divided into three parts: The LineBot, Scraper, Database and LLM. All these parts are essential for the bot to work properly and as intended.

---

## Setting Up and Running the YZU LINE Bot

This section guides you through the necessary steps to get the entire YZU LINE Bot operational.

### 1. LINE Messaging API Setup

To connect the bot to LINE's servers, you need to configure it with your LINE Channel Access Token and Channel Secret.

1.  Create a provider and a channel for your bot on the [LINE Developers Console](https://developers.line.biz/console/). Choose the "Messaging API" channel type.
2.  Once your channel is created, navigate to the "Messaging API" tab within your channel's settings.
3.  You will find your **Channel secret** here.
4.  Scroll down to "Channel access token" and issue a **Channel access token (long-lived)**.
5.  These values need to be added to your project's environment configuration (e.g., a `.env` file for the main bot application).

*(The images below show the LINE Official Account Manager, which is related but the core credentials for the SDK are from the LINE Developers Console shown above.)*

![image](https://github.com/user-attachments/assets/f20548db-dad1-45e4-b455-786f65fcca44)
*LINE Official Account Manager - Basic Settings*

![image](https://github.com/user-attachments/assets/e9a6c8a0-113b-4354-be10-8e231825e2c2)
*LINE Official Account Manager - Messaging API Settings*

### 2. Webhook and Hosting Setup

Your bot needs a publicly accessible HTTPS URL (webhook) for LINE to send messages to.

1.  Deploy your main bot application to a hosting service that provides an HTTPS endpoint (e.g., Heroku, AWS, Google Cloud, Render).
2.  Once deployed, take the public URL of your bot's webhook endpoint.
3.  Go back to your channel's "Messaging API" tab in the LINE Developers Console.
4.  Enter your public HTTPS URL into the "Webhook URL" field.
5.  Enable "Use webhook".

![image](https://github.com/user-attachments/assets/1a302878-fd7f-40f8-a8ea-bb76ce0a1076)
*Webhook URL setting in LINE Developers Console*

---

### 3. Page Scraping Component Setup (`page_scraping.py`)

This component is responsible for gathering data from the YZU portal. The following instructions are specifically for setting up and running `page_scraping.py`.

#### Table of Contents (Page Scraping)
- [Introduction to Page Scraping](#introduction-to-page-scraping)
- [Prerequisites for Page Scraping](#prerequisites-for-page-scraping)
- [Setup Instructions for Page Scraping](#setup-instructions-for-page-scraping)
  - [3.1. Clone the Repository](#31-clone-the-repository)
  - [3.2. Set Up a Virtual Environment](#32-set-up-a-virtual-environment-recommended)
  - [3.3. Install Dependencies](#33-install-dependencies)
  - [3.4. Set Up Supabase](#34-set-up-supabase)
  - [3.5. Configure Environment Variables for Scraping](#35-configure-environment-variables-for-scraping)
  - [3.6. Add YZU Credentials to Supabase](#36-add-yzu-credentials-to-supabase)
- [Running the Page Scraping Script](#running-the-page-scraping-script)
- [Troubleshooting Page Scraping Issues](#troubleshooting-page-scraping-issues)
- [Notes on Page Scraping](#notes-on-page-scraping)

#### Introduction to Page Scraping

The `page_scraping.py` script automatically logs into the YZU student portal, navigates to assignments and activities sections, and extracts this data. It utilizes:
- **Selenium:** For browser automation.
- **BeautifulSoup:** For parsing HTML.
- **Supabase:** As a backend to store scraped data.

This script periodically updates the Supabase database, which the main WaiZiYu LINE bot queries. *This section is particularly aimed at students in the IN208 Algorithm course who might be new to web scraping or Supabase, focusing solely on this script.*

---

#### Prerequisites for Page Scraping

Ensure you have:
*   **Python:** Version 3.8+.
*   **Web Browser:** Recent Microsoft Edge, Google Chrome, or Mozilla Firefox.
*   **Git:** For cloning.
*   **Supabase Account:** Free account at [Supabase](https://supabase.com/).
*   **YZU Portal Credentials:** Your YZU student ID and password.
*   **Operating System:** Windows, Linux, or macOS.

---

#### Setup Instructions for Page Scraping

##### 3.1. Clone the Repository

If you haven't already, clone the project:
```bash
git clone https://github.com/fkilr50/wai-zi-yu.git
cd wai-zi-yu
```

##### 3.2. Set Up a Virtual Environment (Recommended)

Navigate to the project directory (`wai-zi-yu`) and create/activate a virtual environment:
```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```
*(You should see `(venv)` in your terminal prompt.)*

##### 3.3. Install Dependencies

Install required Python libraries for scraping:
```bash
pip install selenium beautifulsoup4 supabase cryptography python-dotenv schedule webdriver_manager
```

##### 3.4. Set Up Supabase

1.  Create a new project on [Supabase](https://supabase.com/).
2.  Go to the **SQL Editor** in your Supabase project dashboard.
3.  Click **+ New query** and run the following SQL to create tables:

    ```sql
    create table public."Assignment table" (
      id bigint generated by default as identity not null,
      created_at timestamp with time zone not null default now(),
      "AssignmentName" text null,
      "AssignmentDate" text null,
      "UserID" text null,
      "LineID" text null,
      end_datetime timestamp with time zone null,
      flag3 smallint null,
      flag1 smallint null,
      constraint "Assignment table_pkey" primary key (id)
    );

    create table public."Activity table" (
      id bigint generated by default as identity not null,
      created_at timestamp with time zone not null default now(),
      "ActivityName" text null,
      "UserID" text null,
      "ActivityDate" text not null,
      "LineID" text null,
      end_datetime timestamp with time zone null,
      flag3 smallint null,
      flag1 smallint null,
      constraint "Activity table_pkey" primary key (id)
    );

    create table public."Login data" (
      id bigint generated by default as identity not null,
      created_at timestamp with time zone not null default now(),
      "LineID" text not null,
      "StID" text not null,
      "Ps" text not null,
      constraint "Login data_pkey" primary key (id),
      constraint "Login data_LineID_key" unique ("LineID"),
      constraint "Login data_StID_key" unique ("StID")
    );
    ```

##### 3.5. Configure Environment Variables for Scraping

In the root of the `wai-zi-yu` project, create a `.env` file for the scraper's Supabase credentials and encryption key.

1.  **Get Supabase URL & Key:** From your Supabase project: **Project Settings** > **API**. Use **Project URL** for `SUPABASE_URL` and the `anon` `public` key for `SUPABASE_KEY`.
2.  **Generate Fernet Key (`FKEY`):** For encrypting YZU passwords. In terminal (venv active):
    ```bash
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ```
    Copy the outputted key.
3.  **Create `.env` file** (ensure it's in `.gitignore`):
    ```env
    SUPABASE_URL="YOUR_SUPABASE_URL_HERE"
    SUPABASE_KEY="YOUR_SUPABASE_ANON_PUBLIC_KEY_HERE"
    FKEY="YOUR_GENERATED_FERNET_KEY_HERE"
    ```

##### 3.6. Add YZU Credentials to Supabase

1.  **Encrypt YZU Password:** Use the `FKEY` from `.env`. Run this Python snippet (replace placeholders):
    ```python
    from cryptography.fernet import Fernet
    fkey_from_env = b"YOUR_GENERATED_FERNET_KEY_HERE" # Exact FKEY from .env
    password_to_encrypt = b"your_yzu_password" # Your YZU password
    fernet = Fernet(fkey_from_env)
    encrypted_password = fernet.encrypt(password_to_encrypt)
    print(f"Encrypted password: {encrypted_password.decode()}")
    ```
    Copy the output.
2.  **Insert into `Login data` Table:** In Supabase Table Editor for `Login data`:
    *   `LineID`: Placeholder like `"local_user_test"` (for standalone scraping test).
    *   `StID`: Your YZU Student ID (e.g., `"s1123522"`).
    *   `Ps`: The **encrypted password** from the previous step.
    *   Save the row.

---

#### Running the Page Scraping Script

With the virtual environment active and in the project's root directory:
```bash
python page_scraping.py
```
Expected sample logs:
```
INFO - Starting page_scraping.py execution...
INFO - Login successful for s1123522!
INFO - Inserted assignment: 【作業】[演算法概論IN208] Algorithm...
INFO - Scheduler started, running every 3 minutes.
```
The script runs once, then schedules itself. Stop with `Ctrl+C`.

---

#### Troubleshooting Page Scraping Issues

*   **Browser/WebDriver Errors:** Update `webdriver_manager` (`pip install --upgrade webdriver_manager`). Ensure browser is installed and updated.
*   **Supabase Connection Issues:** Check `.env` for correct `SUPABASE_URL`, `SUPABASE_KEY`. Verify internet and Supabase project status.
*   **YZU Login Failures:** Confirm `StID` and encrypted `Ps` in Supabase. Ensure `FKEY` used for encryption matches `.env`. Test YZU login manually.
*   **`ModuleNotFoundError`:** Activate virtual environment. Ensure dependencies installed in it.

---

#### Notes on Page Scraping

*   **Scope:** This sub-section focuses *only* on `page_scraping.py`.
*   **YZU-Specific:** Scraper is tailored for YZU portal.
*   **Ethical Scraping:** For personal use. Default 3-min schedule is respectful; avoid overly frequent requests.
*   **Support:** For issues with `page_scraping.py`, open a GitHub issue.

We hope this page scraping component is a helpful tool for your IN208 Algorithm course and for managing your YZU assignments and activities. Happy scraping!

---

### 4. Running the Main LINE Bot Application

After all components (LINE API, Hosting, Page Scraping for data population) are set up:

1.  Ensure your main LINE Bot application code (not `page_scraping.py`) is configured with its own environment variables (LINE Channel tokens, Supabase URL/Key for the bot to read data, any LLM API keys, etc.).
2.  Run your main bot application on your hosting provider or locally for testing (if you've configured a tool like ngrok for a public webhook during local development).

For example, if your main bot is `main_bot_app.py`:
```bash
# Ensure correct .env for the main bot is loaded
python main_bot_app.py
```

You should then be able to interact with your bot via the LINE application.

![image](https://github.com/user-attachments/assets/e5b60436-3076-4d3f-aef0-3726b8b4e905)
*Example of running the bot code (likely the main bot application) in VSCode.*
