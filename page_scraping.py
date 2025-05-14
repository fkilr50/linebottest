import logging
import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from bs4 import BeautifulSoup

from supabase import create_client, Client

# Initialize Supabase client
supabase: Client = create_client(
    "https://opvnwapzljuxnncvpbrn.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9wdm53YXB6bGp1eG5uY3ZwYnJuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjY0MDAxNCwiZXhwIjoyMDYyMjE2MDE0fQ.kXweuLkjFzqTRh-dHmRHK2TTsPvKANVJFY-hW4xHBbA",
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Detect available browsers
def detect_browser():
    edge_path = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
    chrome_path = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
    firefox_path = Path("C:/Program Files/Mozilla Firefox/firefox.exe")
    browsers = []
    if os.path.exists(edge_path):
        browsers.append(("edge", edge_path))
    if os.path.exists(chrome_path):
        browsers.append(("chrome", chrome_path))
    if os.path.exists(firefox_path):
        browsers.append(("firefox", firefox_path))
    return browsers

# Initialize browser driver
def initialize_driver():
    browsers = detect_browser()
    if not browsers:
        raise Exception("No supported browsers found.")
    
    for browser_name, browser_path in browsers:
        try:
            if browser_name == "edge":
                options = webdriver.EdgeOptions()
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/136.0.3240.64")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920,1080")
                manual_driver_path = r"C:\Users\user\edgedriver\msedgedriver.exe"
                if os.path.exists(manual_driver_path):
                    driver = webdriver.Edge(service=EdgeService(manual_driver_path), options=options)
                else:
                    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            elif browser_name == "chrome":
                options = webdriver.ChromeOptions()
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920,1080")
                driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            elif browser_name == "firefox":
                options = webdriver.FirefoxOptions()
                options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0")
                options.add_argument("-headless")
                options.add_argument("--width=1920")
                options.add_argument("--height=1080")
                driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
            
            return driver
        except Exception as e:
            logging.warning(f"Failed to start {browser_name}: {e}")
            continue
    
    raise Exception("Could not start any browser.")

# Initialize driver
try:
    driver = initialize_driver()
except Exception as e:
    logging.error(f"Failed to initialize browser: {e}")
    raise

# Login URL
login_url = "https://portalx.yzu.edu.tw/PortalSocialVB/Login.aspx"

# Attempt login
def attempt_login(username, password):
    try:
        driver.get(login_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Txt_UserID")))
        driver.refresh()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Txt_UserID")))
        username_field = driver.find_element(By.ID, "Txt_UserID")
        password_field = driver.find_element(By.ID, "Txt_Password")
        login_button = driver.find_element(By.ID, "ibnSubmit")
        username_field.send_keys(username)
        password_field.send_keys(password)
        time.sleep(1)
        login_button.click()
        WebDriverWait(driver, 10).until(
            lambda d: EC.alert_is_present()(d) or EC.presence_of_element_located((By.ID, "MainBar_ibnChangeVersion"))(d)
        )
        try:
            alert = Alert(driver)
            logging.warning(f"Login failed for {username}: {alert.text}")
            alert.accept()
            return False
        except:
            if "Login Failed" not in driver.page_source:
                logging.info(f"Login successful for {username}!")
                return True
            logging.warning(f"Login failed for {username}.")
            return False
    except Exception as e:
        logging.warning(f"Login failed for {username}: {e}")
        return False

# Click element by ID
def click_by_id(element_id):
    try:
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, element_id)))
        if element_id == "MainBar_ibnChangeVersion":
            title = element.get_attribute("title") or ""
            src = element.get_attribute("src") or ""
            if "中文" in title or "VersionEN.png" in src:
                return True
        try:
            element.click()
        except:
            driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        logging.warning(f"Failed to click element {element_id}: {e}")
        return False

# Scrape activities
def scrape_activities(student_id):
    try:
        if not click_by_id("MainBar_ibnChangeVersion"):
            return False
        if not click_by_id("tdP4"):
            return False
        if not click_by_id("linkAlreadyRegistry"):
            return False
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table_1")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", class_="table_1")
        rows = table.find_all("tr")[1:]
        logging.info(f"Activities found for {student_id}: {len(rows)}")
        for row in rows:
            cells = row.find_all("td")
            subject = cells[1].find("a").get_text(strip=True)
            date = cells[2].get_text(separator=" ", strip=True)

            try:
                data = {"UserID": student_id, "ActName": subject, "ActDate": date}
                response = supabase.table("Activity table").insert(data).execute()
                if response.data:
                    logging.info(f"Inserted activity for {student_id}: {subject}, Date: {date}")
                else:
                    logging.warning(f"Insert failed for {student_id}: {response}")
            except Exception as e:
                logging.warning(f"Insert failed for {student_id}: {e}")
                
        return True
    except Exception as e:
        logging.warning(f"Failed to scrape activities for {student_id}: {e}")
        return False

# Scrape assignments
def scrape_assignments(student_id):
    try:
        if not click_by_id("MainBar_ibnChangeVersion"):
            return False
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#divTasks table")))
        time.sleep(2)
        page_source = driver.page_source
        try:
            soup = BeautifulSoup(page_source, "lxml")
        except:
            soup = BeautifulSoup(page_source, "html.parser")
        tasks_div = soup.find("div", id="divTasks")
        if not tasks_div:
            logging.warning("No tasks_div found.")
            return False
        tables = tasks_div.find_all("table")
        assignments = []
        for table in tables:
            td = table.find("td", style="width:100%;")
            if not td:
                continue
            title = td.find("a").get_text(strip=True) if td.find("a") else "Unknown Title"
            time_range = table.find_next(string=lambda text: text and "時間：" in text)
            time_range = time_range.replace("時間：", "").strip() if time_range else "No Time Range"
            
            try:
                data = {"UserID": student_id, "AsName": title, "AsDate": time_range}
                response = supabase.table("Assignment table").insert(data).execute()
                if response.data:
                    logging.info(f"Inserted assignments for {student_id}: {title}, Duration: {time_range}")
                else:
                    logging.warning(f"Insert failed for {student_id}: {response}")
            except Exception as e:
                logging.warning(f"Insert failed for {student_id}: {e}")

        logging.info(f"Scraped assignments successfully for {student_id}.")
        return True
    except Exception as e:
        logging.warning(f"Failed to scrape assignments for {student_id}: {e}")
        return False

# Main execution
try:
    response = supabase.table("Login data").select("StID, Ps").execute()
    if not response.data:
        raise Exception("No credentials found.")
    student_credentials = response.data
    max_attempts = 3
    for student in student_credentials:
        username = student["StID"]
        password = student["Ps"]
        logging.info(f"Processing student {username}...")
        for attempt in range(max_attempts):
            if attempt_login(username, password):
                option = "assignments"
                scrapers = {
                    "activities": lambda: scrape_activities(username),
                    "assignments": lambda: scrape_assignments(username)
                }
                scraper = scrapers.get(option, lambda: logging.error("Invalid option"))
                scraper()
                break
            logging.warning(f"Retrying login for {username}...")
        else:
            logging.warning(f"All login attempts failed for {username}.")
        WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")
except Exception as e:
    logging.error(f"Error: {e}")
finally:
    logging.info("Closing browser...")
    driver.quit()