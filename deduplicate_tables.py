import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
import schedule
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
if not supabase_url or not supabase_key:
    logging.error("SUPABASE_URL or SUPABASE_KEY not set in .env file.")
    raise Exception("SUPABASE_URL or SUPABASE_KEY not set")
supabase: Client = create_client(supabase_url, supabase_key)

def deduplicate_table(table_name, unique_fields):
    """
    Deduplicate a table based on specified unique fields.
    Keeps the record with the lowest id and deletes the rest.
    """
    try:
        # Fetch all records
        response = supabase.table(table_name).select("*").execute()
        if not response.data:
            logging.info(f"No records found in {table_name}.")
            return

        records = response.data
        logging.info(f"Found {len(records)} total records in {table_name}.")

        # Group records by unique fields
        unique_records = {}
        for record in records:
            key = tuple(record[field] for field in unique_fields)
            if key not in unique_records:
                unique_records[key] = []
            unique_records[key].append(record)

        # Identify and delete duplicates
        total_deleted = 0
        for key, duplicates in unique_records.items():
            if len(duplicates) > 1:
                duplicates.sort(key=lambda x: x['id'])
                for dup in duplicates[1:]:
                    supabase.table(table_name).delete().eq("id", dup["id"]).execute()
                    total_deleted += 1
                    logging.info(f"Deleted duplicate in {table_name}: id={dup['id']}, {unique_fields}={key}")

        logging.info(f"Deduplication complete for {table_name}. Deleted {total_deleted} duplicates.")
    except Exception as e:
        logging.error(f"Failed to deduplicate {table_name}: {e}")

def main():
    logging.info("Starting deduplicate_tables.py execution...")
    try:
        # Deduplicate Activity table
        activity_unique_fields = ["UserID", "ActName", "ActDate"]
        deduplicate_table("Activity table", activity_unique_fields)

        # Deduplicate Assignment table
        assignment_unique_fields = ["UserID", "AsName", "AsDate"]
        deduplicate_table("Assignment table", assignment_unique_fields)
        logging.info("Scheduler started for deduplicate_tables.py, running every 3 minutes.")
    except Exception as e:
        logging.error(f"Error in deduplicate_tables.py: {e}")

if __name__ == "__main__":
    main() 
    schedule.every(3).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)