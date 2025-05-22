from page_scraping import *

# Main execution of page_scraping.py
try:
    response = supabase.table("Login data").select("LineID, StID, Ps").execute()
    if not response.data:
        raise Exception("No credentials found.")
    student_credentials = response.data
    max_attempts = 3
    for student in student_credentials:
        lineid = student["LineID"]
        username = student["StID"]
        undecryptpassword = student["Ps"]
        undecryptpassword = ast.literal_eval(undecryptpassword)
        password = cypher.decrypt(undecryptpassword).decode()
        logging.info(f"Processing student {username}...")
        for attempt in range(max_attempts):
            if attempt_login(username, password):
                option = "assignments"
                scrapers = {
                    "activities": lambda: scrape_activities(lineid, username),
                    "assignments": lambda: scrape_assignments(lineid, username)
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