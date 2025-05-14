# Python: These lines bring in tools (libraries) the script needs to work
import time  # Python: A built-in tool to make the script wait (like pausing for a webpage to load)
import logging  # Python: A built-in tool to print messages so you can see what the script is doing
import os  # Python: A built-in tool to check if files (like browser programs) exist on your computer
from pathlib import (
    Path,
)  # Python: A built-in tool to handle file paths (like "C:\Program Files") safely

# Selenium: These tools (installed with pip) control a web browser like a robot clicking buttons
from selenium import (
    webdriver,
)  # Selenium: The main tool to open and control browsers (Edge, Chrome, Firefox)
from selenium.webdriver.common.by import (
    By,
)  # Selenium: Helps find things on a webpage (like a username box)
from selenium.webdriver.edge.service import (
    Service as EdgeService,
)  # Selenium: Connects Selenium to Edge's driver
from selenium.webdriver.chrome.service import (
    Service as ChromeService,
)  # Selenium: Connects Selenium to Chrome's driver
from selenium.webdriver.firefox.service import (
    Service as FirefoxService,
)  # Selenium: Connects Selenium to Firefox's driver
from selenium.webdriver.common.alert import (
    Alert,
)  # Selenium: Handles pop-up alerts (like "timeout" messages)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# webdriver-manager: These tools (installed with pip) download the driver (a helper program) for each browser
from webdriver_manager.microsoft import (
    EdgeChromiumDriverManager,
)  # webdriver-manager: Downloads Edge's driver
from webdriver_manager.chrome import (
    ChromeDriverManager,
)  # webdriver-manager: Downloads Chrome's driver
from webdriver_manager.firefox import (
    GeckoDriverManager,
)  # webdriver-manager: Downloads Firefox's driver

# BeautifulSoup: This tool (installed with pip) reads webpage content (like HTML) for future data extraction
from bs4 import (
    BeautifulSoup,
)  # BeautifulSoup: Reads the webpage's code to pull out information (not used yet)

# Supabase: initialize supabase client
from supabase import create_client, Client

supabase: Client = create_client(
    "https://opvnwapzljuxnncvpbrn.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9wdm53YXB6bGp1eG5uY3ZwYnJuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjY0MDAxNCwiZXhwIjoyMDYyMjE2MDE0fQ.kXweuLkjFzqTRh-dHmRHK2TTsPvKANVJFY-hW4xHBbA",
)

# Python: Set up the logging tool to show messages with time and status (like "Starting Edge...")
# This helps you follow what the script is doing
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Python: A custom function (like a recipe) to check which browsers are on the computer
# It returns a list of available browsers (e.g., ["edge", "chrome"])
def detect_browser():
    # Python: Create paths to where browsers are usually installed on Windows
    edge_path = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")  # Python: Path to Edge
    chrome_path = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")  # Python: Path to Chrome
    firefox_path = Path("C:/Program Files/Mozilla Firefox/firefox.exe")  # Python: Path to Firefox

    # Python: Make an empty list to store browsers we find
    browsers = []
    # Python: Check if each browser exists (if the file is there)
    if os.path.exists(edge_path):  # Python: Checks if Edge is installed
        browsers.append(("edge", edge_path))  # Python: Adds "edge" to the list
    if os.path.exists(chrome_path):  # Python: Checks if Chrome is installed
        browsers.append(("chrome", chrome_path))  # Python: Adds "chrome" to the list
    if os.path.exists(firefox_path):  # Python: Checks if Firefox is installed
        browsers.append(("firefox", firefox_path))  # Python: Adds "firefox" to the list

    # Python: Return the list of found browsers
    return browsers


# Python: A custom function to start a browser (Edge, Chrome, or Firefox)
# It tries each available browser and returns a "driver" (a robot that controls the browser)
def initialize_driver():
    # Python: Get the list of available browsers by calling our detect_browser function
    browsers = detect_browser()
    # Python: If no browsers are found, stop the script and show an error
    if not browsers:
        raise Exception("No supported browsers (Edge, Chrome, Firefox) found on this computer.")  # Python: Error message

    # Python: Try each browser one by one
    for (
        browser_name,
        browser_path,
    ) in browsers:  # Python: Loop through the list of browsers
        try:
            # Python: Print a message saying which browser we’re trying
            logging.info(f"Attempting to start {browser_name.capitalize()}...")

            if browser_name == "edge":
                # Selenium: Create a settings object for Edge (like a control panel for the browser)
                options = webdriver.EdgeOptions()  # Selenium: Settings for Edge
                # Selenium: Set a fake "User-Agent" to make Edge look like a normal browser
                # This helps avoid the portal detecting that we’re using a robot
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/135.0.0.0")
                # Selenium: Hide that we’re using a robot (makes the browser look more human)
                options.add_argument("--disable-blink-features=AutomationControlled")
                # Selenium: Optional - Uncomment to hide the browser window (runs in background)
                # options.add_argument("--headless=new")

                # Python: Check if the manual EdgeDriver (downloaded by you) exists
                manual_driver_path = r"C:\Users\user\edgedriver\msedgedriver.exe"  # Python: Path to manual driver
                if os.path.exists(manual_driver_path):  # Python: If the file is there
                    # Python: Print that we’re using the manual driver
                    logging.info(f"Using manual EdgeDriver at {manual_driver_path}")
                    # Selenium: Start Edge using the manual driver
                    driver = webdriver.Edge(service=EdgeService(manual_driver_path), options=options)
                else:
                    # Python: If no manual driver, try downloading one automatically
                    logging.info("Falling back to automatic EdgeDriver download...")
                    # webdriver-manager: Download EdgeDriver and start Edge
                    driver = webdriver.Edge(
                        service=EdgeService(EdgeChromiumDriverManager().install()),
                        options=options,
                    )

            elif browser_name == "chrome":
                # Selenium: Create a settings object for Chrome
                options = webdriver.ChromeOptions()  # Selenium: Settings for Chrome
                # Selenium: Set a fake User-Agent for Chrome
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
                # Selenium: Hide automation signs
                options.add_argument("--disable-blink-features=AutomationControlled")
                # webdriver-manager: Download ChromeDriver and start Chrome
                driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=options,
                )

            elif browser_name == "firefox":
                # Selenium: Create a settings object for Firefox
                options = webdriver.FirefoxOptions()  # Selenium: Settings for Firefox
                # Selenium: Set a fake User-Agent for Firefox
                options.set_preference(
                    "general.useragent.override",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
                )
                # webdriver-manager: Download GeckoDriver and start Firefox
                driver = webdriver.Firefox(
                    service=FirefoxService(GeckoDriverManager().install()),
                    options=options,
                )

            # Python: Print that the browser started successfully
            logging.info(f"{browser_name.capitalize()} started successfully!")
            # Python: Return the driver (the robot controlling the browser)
            return driver

        except Exception as e:  # Python: Catch any errors (like driver download failing)
            # Python: Print a warning and try the next browser
            logging.warning(f"Failed to start {browser_name.capitalize()}: {e}")
            continue

    # Python: If no browser worked, stop the script with an error
    raise Exception("Could not start any supported browser (Edge, Chrome, Firefox).")


# Python: Try to start the browser by calling our initialize_driver function
try:
    # Selenium: Create a driver (the robot that controls the browser)
    driver = initialize_driver()  # Python: Call our function
except Exception as e:  # Python: Catch any errors
    # Python: Print the error and stop the script
    logging.error(f"Failed to initialize browser: {e}")
    raise

# Python: Define the website URL for the login page
login_url = "https://portalx.yzu.edu.tw/PortalSocialVB/Login.aspx"  # Python: A string (text) with the website address


def attempt_login(username, password):
    try:
        logging.info(f"usernmae: {username} dan pass: {password}")
        logging.info(f"Opening {login_url} for user {username}")
        driver.get(login_url)
        time.sleep(2)

        logging.info(f"Filling in username and password for {username}...")
        username_field = driver.find_element(By.ID, "Txt_UserID")
        password_field = driver.find_element(By.ID, "Txt_Password")
        login_button = driver.find_element(By.ID, "ibnSubmit")

        username_field.send_keys(username)
        password_field.send_keys(password)

        logging.info("Clicking login button...")
        login_button.click()

        logging.info("Waiting for login to finish...")
        time.sleep(5)

        try:
            alert = Alert(driver)
            alert_text = alert.text
            logging.warning(f"Alert detected for {username}: {alert_text}")
            alert.accept()
            return False
        except:
            pass

        page_source = driver.page_source
        if "Login Failed" not in page_source:
            logging.info(f"Login successful for {username}!")
            return True
        else:
            logging.error(f"Login failed for {username}. Check credentials or page content.")
            logging.debug(f"Page content: {page_source[:1000]}...")
            return False

    except Exception as e:
        logging.error(f"Error during login attempt for {username}: {e}")
        return False


# Python: A custom function to click an element by ID
def click_by_id(element_id, start_message, success_message, debug_file):
    try:
        logging.info(start_message)
        element = driver.find_element(By.ID, element_id)
        element.click()
        time.sleep(3)
        logging.info(success_message)
        return True
    except Exception as e:
        logging.warning(f"Failed to click element with ID '{element_id}': {e}")
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logging.info(f"Saved page source to {debug_file}")
        return False