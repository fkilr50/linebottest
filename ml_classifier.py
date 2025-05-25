import logging
import os
import re
from datetime import datetime, timezone, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from supabase import create_client, Client
from dotenv import load_dotenv
from transformers import pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
if not supabase_url or not supabase_key:
    logging.error("SUPABASE_URL or SUPABASE_KEY not set in .env file.")
    raise Exception("SUPABASE_URL or SUPABASE_KEY not set")
supabase: Client = create_client(supabase_url, supabase_key)

# Initialize ML model for sentence generation
try:
    generator = pipeline("text2text-generation", model="levii831/linebottest-model")
    logging.info("Initialized fine-tuned bart-base model for sentence generation from Hugging Face.")
except Exception as e:
    logging.error(f"Failed to initialize fine-tuned bart-base: {e}")
    raise

# Example dataset for training
training_data = [
    ("Show me my assignments", "assignments"),
    ("List my homework", "assignments"),
    ("What are my tasks due this week?", "assignments"),
    ("Any assignments for me?", "assignments"),
    ("Check my homework", "assignments"),
    ("What are my HW?", "assignments"),
    ("Show my HW", "assignments"),
    ("Gimme my homework", "assignments"),
    ("What activities are coming up?", "activities"),
    ("List my events", "activities"),
    ("Show me upcoming activities", "activities"),
    ("Any events this week?", "activities"),
    ("What’s on my calendar?", "activities"),
    ("Show my upcoming events", "activities"),
    ("List activities for this week", "activities"),
    ("顯示我的作業", "assignments"),
    ("有哪些活動？", "activities"),
    ("列出我的作業", "assignments"),
    ("顯示我的活動", "activities"),
]

# Prepare data
prompts, labels = zip(*training_data)

# Train the ML model for classification
vectorizer = TfidfVectorizer(ngram_range=(1, 2))
X = vectorizer.fit_transform(prompts)
model = LogisticRegression()
model.fit(X, labels)

def parse_date(date_str, classification, include_day=True):
    """
    Parse date string and return formatted string or components for flexible formatting.
    - Assignments: Extract end date (e.g., '2025/05/14 08:17 ~ 2025/06/13 23:59' -> {'day': 'Friday', 'date': '2025-06-13', 'time': '23:59'}).
    - Activities: Extract start/end times (e.g., '2025.05.29(四) 下午 06:00 ~ 2025.05.29(四) 下午 08:00' -> {'day': 'Thursday', 'date': '2025-05-29', 'start_time': '18:00', 'end_time': '20:00'}).
    """
    try:
        if classification == "assignments":
            # Extract end date (after ~)
            match = re.search(r"~.*(\d{4}/\d{2}/\d{2})\s+(\d{2}:\d{2})", date_str)
            if not match:
                logging.warning(f"Invalid assignment date format: {date_str}")
                return date_str
            date_part, time_part = match.groups()
            date_obj = datetime.strptime(date_part, "%Y/%m/%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            day_of_week = date_obj.strftime("%A") if include_day else ""
            return {
                "day": day_of_week,
                "date": formatted_date,
                "time": time_part
            }
        else:
            # Extract start and end times for activities
            match = re.match(
                r"(\d{4}\.\d{2}\.\d{2}).*(上午|下午)\s*(\d{2}:\d{2})\s*~\s*(\d{4}\.\d{2}\.\d{2}).*(上午|下午)\s*(\d{2}:\d{2})",
                date_str
            )
            if not match:
                logging.warning(f"Invalid activity date format: {date_str}")
                return date_str
            start_date, start_period, start_time, end_date, end_period, end_time = match.groups()
            start_hour, start_minute = map(int, start_time.split(":"))
            end_hour, end_minute = map(int, end_time.split(":"))
            # Convert to 24-hour format
            if start_period == "下午" and start_hour != 12:
                start_hour += 12
            elif start_period == "上午" and start_hour == 12:
                start_hour = 0
            if end_period == "下午" and end_hour != 12:
                end_hour += 12
            elif end_period == "上午" and end_hour == 12:
                end_hour = 0
            start_date = start_date.replace('.', '-')
            end_date = end_date.replace('.', '-')
            date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            day_of_week = date_obj.strftime("%A") if include_day else ""
            return {
                "day": day_of_week,
                "date": start_date,
                "start_time": f"{start_hour:02d}:{start_minute:02d}",
                "end_time": f"{end_hour:02d}:{end_minute:02d}"
            }
    except Exception as e:
        logging.error(f"Failed to parse date '{date_str}' for {classification}: {e}")
        return date_str

def clean_name(name, classification):
    """
    Clean assignment names by removing 【作業】 prefix; keep activity names raw.
    """
    name = name.strip()
    if classification == "assignments":
        name = re.sub(r"【作業】\s*", "", name)
    return name

def fetch_data(line_id, classification):
    """
    Fetch assignments or activities from Supabase for a given LineID.
    """
    try:
        table_name = "Assignment table" if classification == "assignments" else "Activity table"
        name_field = "AssignmentName" if classification == "assignments" else "ActivityName"
        date_field = "AssignmentDate" if classification == "assignments" else "ActivityDate"
        type_label = "assignment" if classification == "assignments" else "activity"
        
        current_time = datetime.now(timezone(timedelta(hours=8))).isoformat()
        response = supabase.table(table_name)\
            .select(f"{name_field}, {date_field}")\
            .eq("LineID", line_id)\
            .gte("end_datetime", current_time)\
            .execute()
        
        logging.info(f"Raw Supabase data for {type_label}s: {response.data}")
        
        if not response.data:
            logging.info(f"No {type_label}s found for LineID: {line_id}")
            return []
        
        items = []
        for item in response.data:
            name = clean_name(item[name_field], classification)
            date_info = parse_date(item[date_field], classification, include_day=True)
            items.append({"name": name, "date_info": date_info})
        logging.info(f"Fetched {len(items)} {type_label}{'s' if len(items) != 1 else ''} for LineID: {line_id}")
        return items
    except Exception as e:
        logging.error(f"Failed to fetch {classification} for LineID {line_id}: {e}")
        return []

def generate_ml_sentence(prompt, classification, items):
    """
    Generate a natural sentence using bart-base, ensuring all items are listed.
    - Assignments: Use "is due on [day], [date], [time]".
    - Activities: Use "on [day], [date], from [start_time] to [end_time]".
    - Chinese output for Chinese prompts with translated day of week.
    """
    try:
        type_label = "assignment" if classification == "assignments" else "activity"
        type_label_plural = f"{type_label}s" if len(items) != 1 else type_label
        tone = "casual" if any(word in prompt.lower() for word in ["giv", "gimme", "hw"]) else "formal"
        is_chinese = any(ord(c) > 127 for c in prompt)  # Detect Chinese characters
        
        # Day of week translation for Chinese
        day_translation = {
            "Monday": "星期一",
            "Tuesday": "星期二",
            "Wednesday": "星期三",
            "Thursday": "星期四",
            "Friday": "星期五",
            "Saturday": "星期六",
            "Sunday": "星期日"
        }
        
        if not items:
            if is_chinese:
                return f"抱歉，您沒有即將到來的{'作業' if classification == 'assignments' else '活動'}。"
            return f"Sorry, you have no upcoming {type_label_plural}."
        
        # Prepare input for the model
        if classification == "assignments":
            items_text = "; ".join([
                f"{item['name']} due {item['date_info']['day']}, {item['date_info']['date']}, {item['date_info']['time']}"
                for item in items
            ])
        else:
            items_text = "; ".join([
                f"{item['name']} on {item['date_info']['day']}, {item['date_info']['date']}, from {item['date_info']['start_time']} to {item['date_info']['end_time']}"
                for item in items
            ])
        
        input_text = (
            f"Summarize the {type_label_plural} in a {tone} tone for prompt '{prompt}'. "
            f"Use 24-hour time format and short sentences. List all items. "
            f"{'Use due for assignments' if classification == 'assignments' else 'Use on [day], [date], from [start] to [end] for activities'}. Data: {items_text}."
        )
        
        result = generator(input_text, max_length=200, num_beams=5)[0]["generated_text"]
        
        # Post-process to ensure all items are included
        count = len(items)
        if count == 0:
            if is_chinese:
                return f"抱歉，您沒有即將到來的{'作業' if classification == 'assignments' else '活動'}。"
            return f"Sorry, you have no upcoming {type_label_plural}."
        
        # Clean up unwanted prefixes
        if result.startswith("Summarize the"):
            result = result.split(".", 1)[-1].strip() if "." in result else result
        
        # Ensure all items are included
        missing_items = [item for item in items if item["name"] not in result]
        if missing_items or count > result.count("due" if classification == "assignments" else "from"):
            # Fallback to manual construction
            if classification == "assignments":
                sentences = [
                    f"{item['name']} is due on {item['date_info']['day']}, {item['date_info']['date']}, {item['date_info']['time']}."
                    for item in items
                ]
            else:
                sentences = [
                    f"{item['name']} on {item['date_info']['day']}, {item['date_info']['date']}, from {item['date_info']['start_time']} to {item['date_info']['end_time']}."
                    for item in items
                ]
            prefix = f"Yo, you got {count} {type_label_plural}" if tone == "casual" else f"You have {count} {type_label_plural}"
            if is_chinese:
                prefix = f"您有{count}項{'作業' if classification == 'assignments' else '活動'}"
                if classification == "assignments":
                    sentences = [
                        f"{item['name']}預定於{day_translation.get(item['date_info']['day'], item['date_info']['day'])}, {item['date_info']['date']}, {item['date_info']['time']}到期。"
                        for item in items
                    ]
                else:
                    sentences = [
                        f"{item['name']}於{day_translation.get(item['date_info']['day'], item['date_info']['day'])}, {item['date_info']['date']}, 從{item['date_info']['start_time']}至{item['date_info']['end_time']}。"
                        for item in items
                    ]
            result = f"{prefix}. {' '.join(sentences)}"
        
        return result.strip()
    except Exception as e:
        logging.error(f"Failed to generate sentence for '{prompt}': {e}")
        if is_chinese:
            return f"抱歉，您沒有即將到來的{'作業' if classification == 'assignments' else '活動'}。"
        return f"Sorry, you have no upcoming {type_label_plural}."

def classify_prompt(prompt, line_id):
    """
    Classify a user prompt and fetch relevant data.
    """
    try:
        X_prompt = vectorizer.transform([prompt])
        prediction = model.predict(X_prompt)[0]
        logging.info(f"Prompt: '{prompt}' classified as '{prediction}'")
        
        items = fetch_data(line_id, prediction)
        sentence = generate_ml_sentence(prompt, prediction, items)
        logging.info(f"Response for '{prompt}': {sentence}")
        
        return prediction, sentence
    except Exception as e:
        logging.error(f"Failed to classify prompt '{prompt}': {e}")
        return None, None

def main():
    """
    Main function to test the classifier.
    """
    logging.info("Starting ml_classifier.py execution...")
    try:
        test_line_id = "U2d05e1777e259a7a068e91b5f33c942e"
        test_prompts = [
            "What homework do I have?",
            "Show me my upcoming events",
            "Any tasks due soon?",
            "List activities for this week",
            "顯示我的作業",
            "有哪些活動？",
            "What are my HW?",
        ]
        
        for prompt in test_prompts:
            result, sentence = classify_prompt(prompt, test_line_id)
            if not result:
                logging.warning(f"No classification result for prompt: '{prompt}'")
                
    except Exception as e:
        logging.error(f"Error in ml_classifier.py: {e}")

if __name__ == "__main__":
    main()