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


# Python: A custom function to try logging into the portal
# It returns True if login works, False if it fails
def attempt_login():
    try:
        # Selenium: Tell the browser to visit the login page
        logging.info(f"Opening {login_url}")  # Python: Print the URL
        driver.get(login_url)  # Selenium: Opens the webpage
        time.sleep(2)  # Python: Wait 2 seconds for the page to load

        # Selenium: Find the username box, password box, and login button on the page
        logging.info("Filling in username and password...")  # Python: Print a status message
        username_field = driver.find_element(By.ID, "Txt_UserID")  # Selenium: Finds the username box by its ID
        password_field = driver.find_element(By.ID, "Txt_Password")  # Selenium: Finds the password box by its ID
        login_button = driver.find_element(By.ID, "ibnSubmit")  # Selenium: Finds the login button by its ID

        # Selenium: Type your username and password into the boxes
        username_field.send_keys("s1123542")  # Selenium: Types your username (e.g., s1121234)
        password_field.send_keys("Kaiser.lev123")  # Selenium: Types your password (e.g., H123456789@Yzu)

        # Selenium: Click the login button
        logging.info("Clicking login button...")  # Python: Print a status message
        login_button.click()  # Selenium: Clicks the button

        # Python: Wait 5 seconds for the login to finish (gives the website time to respond)
        logging.info("Waiting for login to finish...")  # Python: Print a status message
        time.sleep(5)

        # Selenium: Check if the website shows a pop-up alert (like the timeout message)
        try:
            alert = Alert(driver)  # Selenium: Gets the pop-up alert
            alert_text = alert.text  # Selenium: Reads the alert’s message
            logging.warning(f"Alert detected: {alert_text}")  # Python: Print the alert message
            alert.accept()  # Selenium: Closes the alert by clicking "OK"
            return False  # Python: Return False because the login failed (alert means trouble)
        except:
            pass  # Python: If no alert, keep going

        # Python: Check if the login worked by looking at the webpage’s content
        page_source = driver.page_source  # Selenium: Gets the webpage’s HTML code
        if "Login Failed" not in page_source:  # Python: Check if "Login Failed" is in the HTML
            logging.info("Login successful!")  # Python: Print success message
            return True  # Python: Return True because login worked
        else:
            logging.error("Login failed. Check credentials or page content.")  # Python: Print failure message
            logging.debug(f"Page content: {page_source[:1000]}...")  # Python: Show first 1000 characters of HTML
            return False  # Python: Return False because login failed

    except Exception as e:  # Python: Catch any errors (like webpage not loading)
        logging.error(f"Error during login attempt: {e}")  # Python: Print the error
        return False  # Python: Return False because something went wrong


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


# Python: A custom function to scrape the Activity Sign-up table
def scrape_activities():
    try:
        # Python: Log that we're setting up for scraping
        logging.info("Preparing BeautifulSoup for scraping...")

        # Python: Navigate to English version by clicking the language button
        # Selenium: Call click_by_id to click "MainBar_ibnChangeVersion"
        if not click_by_id("MainBar_ibnChangeVersion", "Switching to English version...", "Switched to English version successfully.", "debug_menu.html"):
            return False

        # Python: Navigate to Activity Sign-up page by clicking the menu link
        # Selenium: Call click_by_id to click "tdP4"
        if not click_by_id("tdP4", "Navigating to Activity Sign-up page by clicking menu link...", "Clicked Activity Sign-up link successfully.", "debug_menu.html"):
            return False
        current_url = driver.current_url
        logging.info(f"Current URL after navigation: {current_url}")

        # Python: Navigate to My Sign-up page by clicking the link
        # Selenium: Call click_by_id to click "linkAlreadyRegistry"
        if not click_by_id("linkAlreadyRegistry", "Navigating to My Sign-up page by clicking link...", "Clicked My Sign-up link successfully.", "debug_my_signup.html"):
            return False
        current_url = driver.current_url
        logging.info(f"Current URL after navigation: {current_url}")

        logging.info("Scraping activity table...")  # Python: Log that we're starting to scrape the activity table
        page_source = driver.page_source  # Selenium: Get the page's HTML code
        soup = BeautifulSoup(page_source, "html.parser")  # BeautifulSoup: Parse the HTML to make it easier to search
        table = soup.find("table", class_="table_1")  # BeautifulSoup: Find the table with class "table_1" (contains activities)
        rows = table.find_all("tr")[1:]  # BeautifulSoup: Get all rows in the table, skipping the header row
        logging.info(f"Activities found: {len(rows)}")  # Python: Log how many activities (rows) we found
        for row in rows:
            cells = row.find_all("td")  # BeautifulSoup: Get all cells (columns) in the row
            subject = cells[1].find("a").get_text(strip=True)  # BeautifulSoup: Extract Subject from the <a> tag in the second column
            date = cells[2].get_text(separator=" ", strip=True)  # BeautifulSoup: Extract Date from the third column, combining <br> tags with spaces
            logging.info(f"Subject: {subject}")
            logging.info(f"Date: {date}")
            logging.info("---")
        logging.info("Scraped activity table successfully.")
        return True
    except Exception as e:
        logging.warning(f"Failed to scrape activity table: {e}")
        return False


# Python: A placeholder function for scraping grades (to be implemented later)
def scrape_grades():
    logging.info("Grades scraping not implemented yet.")
    return False


# Python: Main part of the script that runs everything (literally)
try:
    # Python: Try logging in up to 3 times (in case of alerts or errors)
    max_attempts = 3
    for attempt in range(max_attempts):
        logging.info(f"Login attempt {attempt + 1}/{max_attempts}")
        if attempt_login():
            option = "activities"  # Python: Change to "grades" or use input() later
            scrapers = {"activities": scrape_activities, "grades": scrape_grades}  # Python: Maps "activities" to scrape_activities function  # Python: Maps "grades" to scrape_grades function
            # Python: If option is not in scrapers (e.g., "attendance"), logs "Invalid option"
            scraper = scrapers.get(option, lambda: logging.error("Invalid option"))  # Python: Run the selected scraping function (e.g., scrape_activities())
            scraper()  # Python: Break the loop since login and scraping are done
            break
        else:
            logging.info("Retrying after alert or failure...")  # Python: Print a retry message
            time.sleep(2)  # Python: Wait 2 seconds before trying again
    else:
        logging.error("All login attempts failed.")  # Python: Print if all tries failed

except Exception as e:  # Python: Catch any errors
    logging.error(f"Something went wrong: {e}")  # Python: Print the error

finally:
    logging.info("Closing browser...")  # Python: Print a status message
    driver.quit()  # Selenium: Closes the browser and driver
