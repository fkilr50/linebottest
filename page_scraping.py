# Python: These lines bring in tools (libraries) the script needs to work
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

# BeautifulSoup: This tool (installed with pip) reads webpage content (like HTML) for data extraction
from bs4 import (
    BeautifulSoup,
)  # BeautifulSoup: Reads the webpage's code to pull out information

# Supabase: initialize supabase client
from supabase import create_client, Client

supabase: Client = create_client(
    "https://opvnwapzljuxnncvpbrn.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9wdm53YXB6bGp1eG5uY3ZwYnJuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjY0MDAxNCwiZXhwIjoyMDYyMjE2MDE0fQ.kXweuLkjFzqTRh-dHmRHK2TTsPvKANVJFY-hW4xHBbA",
)

# Python: Set up the logging tool to show messages with time and status (like "Starting Edge...")
# This helps you follow what the script is doing
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Python: A custom function to check which browsers are on the computer
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
                # Selenium: Run Edge in headless mode (no visible browser window)
                options.add_argument("--headless=new")
                # Selenium: Set a realistic viewport size to avoid element overlap
                options.add_argument("--window-size=1920,1080")
                # Python: Log that headless mode and viewport are enabled
                logging.info("Edge will run in headless mode with 1920x1080 viewport.")

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
                # Selenium: Run Chrome in headless mode (no visible window)
                options.add_argument("--headless=new")
                # Selenium: Set a realistic viewport size
                options.add_argument("--window-size=1920,1080")
                # Python: Log that headless mode and viewport are enabled
                logging.info("Chrome will run in headless mode with 1920x1080 viewport.")
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
                # Selenium: Run Firefox in headless mode (no visible window)
                options.add_argument("-headless")
                # Selenium: Set a realistic viewport size
                options.add_argument("--width=1920")
                options.add_argument("--height=1080")
                # Python: Log that headless mode and viewport are enabled
                logging.info("Firefox will run in headless mode with 1920x1080 viewport.")
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
def attempt_login(username, password):
    try:
        logging.info(f"Opening {login_url} for user {username}")
        driver.get(login_url)
        # Selenium: Wait up to 10 seconds for login page to load (username field present)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Txt_UserID"))
        )
        logging.info(f"Login page loaded for {username}.")

        logging.info(f"Filling in username and password for {username}...")
        username_field = driver.find_element(By.ID, "Txt_UserID")
        password_field = driver.find_element(By.ID, "Txt_Password")
        login_button = driver.find_element(By.ID, "ibnSubmit")

        username_field.send_keys(username)
        password_field.send_keys(password)

        logging.info("Clicking login button...")
        login_button.click()

        logging.info("Waiting for login to finish...")
        # Selenium: Wait up to 10 seconds for dashboard or alert
        try:
            # Check for alert (failed login) or dashboard (successful login)
            WebDriverWait(driver, 10).until(
                lambda d: EC.alert_is_present()(d) or
                          EC.presence_of_element_located((By.ID, "MainBar_ibnChangeVersion"))(d)
            )
            # Check if alert exists
            try:
                alert = Alert(driver)
                alert_text = alert.text
                logging.warning(f"Alert detected for {username}: {alert_text}")
                alert.accept()
                return False
            except:
                logging.info(f"Dashboard loaded for {username}.")
        except Exception as e:
            logging.warning(f"Timeout waiting for login result for {username}: {e}")

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
        # Selenium: Wait up to 10 seconds for the element to be clickable
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )
        # Python: Log the element's attributes for debugging
        element_title = element.get_attribute("title") or "No title"
        element_src = element.get_attribute("src") or "No src"
        logging.info(f"Element '{element_id}' found with title='{element_title}', src='{element_src}'")

        # Python: Special handling for language switch button
        if element_id == "MainBar_ibnChangeVersion":
            # Python: Check if already in English (title contains "中文" means it's English mode)
            if "中文" in element_title or "VersionEN.png" in element_src:
                logging.info("Page is already in English, skipping language switch.")
                return True

        # Selenium: Try regular click
        try:
            element.click()
        except Exception as e:
            # Selenium: Fallback to JavaScript click if regular click fails
            logging.warning(f"Regular click failed for '{element_id}': {e}. Trying JavaScript click...")
            driver.execute_script("arguments[0].click();", element)

        logging.info(success_message)
        return True
    except Exception as e:
        logging.warning(f"Failed to click element with ID '{element_id}': {e}")
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logging.info(f"Saved page source to {debug_file}")
        return False

# Python: A custom function to scrape the Activity Sign-up table
def scrape_activities(student_id):
    try:
        logging.info(f"Preparing BeautifulSoup for scraping for user {student_id}...")

        if not click_by_id("MainBar_ibnChangeVersion", "Switching to English version...", "Switched to English version successfully.", "debug_menu.html"):
            return False

        if not click_by_id("tdP4", "Navigating to Activity Sign-up page by clicking menu link...", "Clicked Activity Sign-up link successfully.", "debug_menu.html"):
            return False
        current_url = driver.current_url
        logging.info(f"Current URL after navigation: {current_url}")

        if not click_by_id("linkAlreadyRegistry", "Navigating to My Sign-up page by clicking link...", "Clicked My Sign-up link successfully.", "debug_my_signup.html"):
            return False
        current_url = driver.current_url
        logging.info(f"Current URL after navigation: {current_url}")

        logging.info("Scraping activity table...")
        # Selenium: Wait up to 10 seconds for the activity table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table_1"))
        )
        logging.info(f"Activity table loaded for {student_id}.")
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        table = soup.find("table", class_="table_1")
        rows = table.find_all("tr")[1:]
        logging.info(f"Activities found for {student_id}: {len(rows)}")

        for row in rows:
            cells = row.find_all("td")
            subject = cells[1].find("a").get_text(strip=True)
            date = cells[2].get_text(separator=" ", strip=True)

            try:
                datatobeinserted = {"UserID": student_id, "ActName": subject, "ActDate": date}
                response = supabase.table("Activity table").insert(datatobeinserted).execute()

                if response.data:
                    logging.info(f"Successfully inserted for {student_id}: {response.data}")
                else:
                    logging.error(f"Insert failed for {student_id}: {response}")
                    if hasattr(response, "error") and response.error:
                        logging.error(f"Error details: {response.error.message}")

            except Exception as e:
                logging.error(f"Error inserting activity for {student_id}: {str(e)}")
                if hasattr(e, "response") and e.response:
                    try:
                        error_details = e.response.json()
                        logging.error(f"APIError details: {error_details}")
                    except:
                        logging.error("Failed to parse API error details")

            logging.info(f"Subject: {subject}")
            logging.info(f"Date: {date}")
            logging.info("---")

        logging.info(f"Scraped activity table successfully for {student_id}.")
        return True
    except Exception as e:
        logging.warning(f"Failed to scrape activity table for {student_id}: {e}")
        return False

# Python: A placeholder function for scraping grades (to be implemented later)
def scrape_grades():
    logging.info("Grades scraping not implemented yet.")
    return False

# Python: Main part of the script that runs everything
try:
    # Fetch student credentials
    logging.info("Fetching student credentials from Login data table...")
    response = supabase.table("Login data").select("StID, Ps").execute()
    if response.data:
        student_credentials = response.data
        logging.info(f"Retrieved {len(student_credentials)} student credentials.")
    else:
        raise Exception("No credentials found in Login data table.")

    # Process each student
    max_attempts = 3
    for student in student_credentials:
        username = student["StID"]
        password = student["Ps"]
        logging.info(f"Processing student {username}...")

        for attempt in range(max_attempts):
            logging.info(f"Login attempt {attempt + 1}/{max_attempts} for {username}")
            if attempt_login(username, password):
                option = "activities"  # Change to "grades" or use input() later
                scrapers = {"activities": lambda: scrape_activities(username), "grades": scrape_grades}
                scraper = scrapers.get(option, lambda: logging.error("Invalid option"))
                scraper()
                break
            else:
                logging.info(f"Retrying after alert or failure for {username}...")
                # No sleep needed; attempt_login's WebDriverWait handles timing
        else:
            logging.error(f"All login attempts failed for {username}.")

        # Selenium: Ensure browser is idle before next student
        WebDriverWait(driver, 5).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logging.info(f"Browser is idle, proceeding to next student {username}.")

except Exception as e:
    logging.error(f"Something went wrong: {e}")
finally:
    logging.info("Closing browser...")
    driver.quit()