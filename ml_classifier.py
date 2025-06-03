import logging
import os
import re
from datetime import datetime, timezone, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from supabase import create_client, Client
from dotenv import load_dotenv
from transformers import pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("supabase").setLevel(logging.WARNING)  # Suppress Supabase HTTP logs
logging.getLogger("httpx").setLevel(logging.WARNING)  # Suppress httpx HTTP logs
logging.getLogger("http.client").setLevel(logging.WARNING)  # Suppress http.client logs

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
except Exception as e:
    logging.error(f"Failed to initialize fine-tuned bart-base: {e}")
    raise

# Course ID to name mapping
COURSE_MAPPING = {
    "IN211": {"en": "Information Privacy", "zh": "資訊隱私"},
    "IN209": {"en": "Introduction to Operating System", "zh": "作業系統導論"},
    "IN207": {"en": "Probability and Statistics", "zh": "機率與統計"},
    "IN208": {"en": "Introduction to Algorithm", "zh": "演算法概論"},
    "IN210": {
        "en": "Assembly Language and Computer Organization",
        "zh": "組合語言與計算機組織",
    },
}

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
    ("What assignment has the nearest deadline?", "nearest_assignments"),
    ("Which homework is due soonest?", "nearest_assignments"),
    ("Show me my closest task", "nearest_assignments"),
    ("Show me my closest task", "nearest_assignments"),
    ("Show me my closest task", "nearest_assignments"),
    ("Show me my closest task", "nearest_assignments"),
    ("Show me my closest task", "nearest_assignments"),
    ("Show me my closest task", "nearest_assignments"),
    ("Show me my closest task", "nearest_assignments"),
    ("show me my tasks", "assignments"),
    ("show me my tasks", "assignments"),
    ("What’s my next assignment?", "nearest_assignments"),
    ("What activity is happening soonest?", "nearest_activities"),
    ("Which event is nearest?", "nearest_activities"),
    ("Show me the next event", "nearest_activities"),
    ("What’s my closest activity?", "nearest_activities"),
    ("顯示我的作業", "assignments"),
    ("有哪些活動？", "activities"),
    ("列出我的作業", "assignments"),
    ("give me my activities", "activities"),
    ("give me my activities", "activities"),
    ("give me my activities", "activities"),
    ("give me my activities", "activities"),
    ("最近的作業是什麼？", "nearest_assignments"),
    ("哪個作業最快到期？", "nearest_assignments"),
    ("最近的活動是什麼？", "nearest_activities"),
    ("下一個活動是什麼？", "nearest_activities"),
    ("When is the deadline for IN208?", "course_due_date"),
    ("Due date for IN211?", "course_due_date"),
    ("What’s the due date for IN210?", "course_due_date"),
    ("When is IN209 assignment due?", "course_due_date"),
    ("Due date for Introduction to Algorithm?", "course_due_date"),
    ("What’s the due date for Information Privacy?", "course_due_date"),
    (
        "When is the deadline for Assembly Language and Computer Organization assignment?",
        "course_due_date",
    ),
    ("Due date for Probability and Statistics?", "course_due_date"),
    ("When is IN207 assignment due?", "course_due_date"),
    ("演算法概論課程的作業何時到期？", "course_due_date"),
    ("IN208的截止日期是什麼？", "course_due_date"),
    ("組合語言與計算機組織課程的作業何時到期？", "course_due_date"),
    ("資訊隱私的作業到期日？", "course_due_date"),
    ("作業系統導論的作業何時到期？", "course_due_date"),
    ("機率與統計課程的作業到期日？", "course_due_date"),
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
        if classification in ("assignments", "nearest_assignments", "course_due_date"):
            # Extract end date (after ~)
            match = re.search(r"~.*(\d{4}/\d{2}/\d{2})\s+(\d{2}:\d{2})", date_str)
            if not match:
                logging.warning(f"Invalid assignment date format: {date_str}")
                return date_str
            date_part, time_part = match.groups()
            date_obj = datetime.strptime(date_part, "%Y/%m/%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            day_of_week = date_obj.strftime("%A") if include_day else ""
            return {"day": day_of_week, "date": formatted_date, "time": time_part}
        else:
            # Extract start and end times for activities
            match = re.match(
                r"(\d{4}\.\d{2}\.\d{2}).*(上午|下午)\s*(\d{2}:\d{2})\s*~\s*(\d{4}\.\d{2}\.\d{2}).*(上午|下午)\s*(\d{2}:\d{2})",
                date_str,
            )
            if not match:
                logging.warning(f"Invalid activity date format: {date_str}")
                return date_str
            start_date, start_period, start_time, end_date, end_period, end_time = (
                match.groups()
            )
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
            start_date = start_date.replace(".", "-")
            end_date = end_date.replace(".", "-")
            date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            day_of_week = date_obj.strftime("%A") if include_day else ""
            return {
                "day": day_of_week,
                "date": start_date,
                "start_time": f"{start_hour:02d}:{start_minute:02d}",
                "end_time": f"{end_hour:02d}:{end_minute:02d}",
            }
    except Exception as e:
        logging.error(f"Failed to parse date '{date_str}' for {classification}: {e}")
        return date_str


def clean_name(name, classification):
    """
    Clean assignment names by removing 【作業】 prefix; keep activity names raw.
    """
    name = name.strip()
    if classification in ("assignments", "nearest_assignments", "course_due_date"):
        name = re.sub(r"【作業】\s*", "", name)
    return name


def fetch_data(line_id, classification, course_id=None):
    """
    Fetch assignments or activities from Supabase for a given LineID.
    For nearest_* classifications, return only the earliest item.
    For course_due_date, filter by course ID.
    """
    try:
        table_name = (
            "Assignment table"
            if classification
            in ("assignments", "nearest_assignments", "course_due_date")
            else "Activity table"
        )
        name_field = (
            "AssignmentName"
            if classification
            in ("assignments", "nearest_assignments", "course_due_date")
            else "ActivityName"
        )
        date_field = (
            "AssignmentDate"
            if classification
            in ("assignments", "nearest_assignments", "course_due_date")
            else "ActivityDate"
        )

        current_time = datetime.now(timezone(timedelta(hours=8))).isoformat()
        query = (
            supabase.table(table_name)
            .select(f"{name_field}, {date_field}")
            .eq("LineID", line_id)
            .gte("end_datetime", current_time)
        )

        if classification == "course_due_date" and course_id:
            query = query.ilike(name_field, f"%{course_id}%")

        response = query.execute()

        if not response.data:
            logging.info(f"No {classification} found for LineID: {line_id}")
            return []

        items = []
        for item in response.data:
            name = clean_name(item[name_field], classification)
            date_info = parse_date(item[date_field], classification, include_day=True)
            items.append({"name": name, "date_info": date_info})

        if not items:
            logging.info(
                f"No valid {classification} after parsing for LineID: {line_id}"
            )
            return []

        # Sort for nearest classifications
        if classification == "nearest_assignments":
            items.sort(
                key=lambda x: datetime.strptime(
                    f"{x['date_info']['date']} {x['date_info']['time']}",
                    "%Y-%m-%d %H:%M",
                )
            )
            items = [items[0]]  # Return only the earliest
        elif classification == "nearest_activities":
            items.sort(
                key=lambda x: datetime.strptime(
                    f"{x['date_info']['date']} {x['date_info']['start_time']}",
                    "%Y-%m-%d %H:%M",
                )
            )
            items = [items[0]]  # Return only the earliest

        return items
    except Exception as e:
        logging.error(f"Failed to fetch {classification} for LineID {line_id}: {e}")
        return []


def generate_ml_sentence(prompt, classification, items, course_id=None):
    """
    Generate a natural sentence using bart-base, ensuring all items are listed.
    - Assignments: Use "[name] is due on [day], [date], [time]."
    - Activities: Use "[name] on [day], [date], from [start_time] to [end_time]."
    - Nearest: Use "Your nearest [type] is [name], due on..." or "...on [day], [date], from..."
    - Course due date: Use "The assignment for [course_id] ([course_name]) is [name], due on [day], [date], [time]."
    - Chinese output for Chinese prompts with translated day of week.
    """
    try:
        is_nearest = classification in ("nearest_assignments", "nearest_activities")
        is_course_due = classification == "course_due_date"
        type_label = (
            "assignment"
            if classification
            in ("assignments", "nearest_assignments", "course_due_date")
            else "activity"
        )
        count = len(items)
        type_label_plural = (
            type_label
            if is_nearest or is_course_due
            else (
                "assignments"
                if type_label == "assignment"
                else "activity" if count == 1 else "activities"
            )
        )
        tone = (
            "casual"
            if any(word in prompt.lower() for word in ["giv", "gimme", "hw", "yo"])
            else "formal"
        )
        is_chinese = any(
            128 <= ord(c) <= 0x9FFF for c in prompt
        )  # Detect Chinese characters

        # Day of week translation for Chinese
        day_translation = {
            "Monday": "星期一",
            "Tuesday": "星期二",
            "Wednesday": "星期三",
            "Thursday": "星期四",
            "Friday": "星期五",
            "Saturday": "星期六",
            "Sunday": "星期日",
        }

        # Fix Chinese spacing
        def fix_chinese_spacing(text):
            return re.sub(r"預\s*定於", "預定於", text)

        if not items:
            if is_course_due:
                course_name = COURSE_MAPPING.get(course_id.upper(), {}).get(
                    "zh" if is_chinese else "en", course_id
                )
                if is_chinese:
                    return fix_chinese_spacing(f"抱歉，沒有找到{course_name}的作業。")
                return f"No assignments found for {course_id} ({course_name})."
            if is_chinese:
                return fix_chinese_spacing(
                    f"抱歉，您沒有即將到來的{'作業' if type_label == 'assignment' else '活動'}。"
                )
            return f"Sorry, you have no upcoming {type_label_plural}."

        # Prepare input for the model
        if classification in ("assignments", "nearest_assignments", "course_due_date"):
            items_text = "; ".join(
                [
                    f"{item['name']} due {item['date_info']['day']}, {item['date_info']['date']}, {item['date_info']['time']}"
                    for item in items
                ]
            )
        else:
            items_text = "; ".join(
                [
                    f"{item['name']} on {item['date_info']['day']}, {item['date_info']['date']}, from {item['date_info']['start_time']} to {item['date_info']['end_time']}"
                    for item in items
                ]
            )

        input_text = (
            f"Summarize the {type_label_plural} in a {tone} tone for prompt '{prompt}'. "
            f"Use 24-hour time format. "
            f"{'Use single sentence: [name], due on [day], [date], [time]' if type_label == 'assignment' and (is_nearest or is_course_due) else 'Use single sentence: [name], on [day], [date], from [start] to [end]' if is_nearest else 'Use short sentences'}. "
            f"{'List only the earliest item' if is_nearest else 'List all items'}. "
            f"{'For course ' + course_id + ': ' if is_course_due else ''}Data: {items_text}."
        )

        result = generator(
            input_text,
            max_length=100 if is_nearest or is_course_due else 200,
            num_beams=5,
        )[0]["generated_text"]
        result = fix_chinese_spacing(result)

        # Post-process to ensure correct output
        if count == 0:
            if is_course_due:
                course_name = COURSE_MAPPING.get(course_id.upper(), {}).get(
                    "zh" if is_chinese else "en", course_id
                )
                if is_chinese:
                    return fix_chinese_spacing(f"抱歉，沒有找到{course_name}的作業。")
                return f"No assignments found for {course_id} ({course_name})."
            if is_chinese:
                return fix_chinese_spacing(
                    f"抱歉，您沒有即將到來的{'作業' if type_label == 'assignment' else '活動'}。"
                )
            return f"Sorry, you have no upcoming {type_label_plural}."

        # Clean up unwanted prefixes
        if result.startswith("Summarize the"):
            result = result.split(".", 1)[-1].strip() if "." in result else result

        # Ensure correct item count and format
        expected_count = 1 if is_nearest else count
        keyword = "due" if type_label == "assignment" else "from"
        if (
            any(item["name"] not in result for item in items)
            or result.count(keyword) != expected_count
            or is_course_due
        ):
            # Fallback to manual construction with improved formatting
            if is_nearest:
                item = items[0]
                if type_label == "assignment":
                    sentence = (
                        f"{item['name']}, due on {item['date_info']['day']}, {item['date_info']['date']}, {item['date_info']['time']}."
                        if not is_chinese
                        else f"{item['name']} 預定於 {day_translation.get(item['date_info']['day'], item['date_info']['day'])}, {item['date_info']['date']}, {item['date_info']['time']} 到期。"
                    )
                else:
                    sentence = (
                        f"{item['name']}, on {item['date_info']['day']}, {item['date_info']['date']}, from {item['date_info']['start_time']} to {item['date_info']['end_time']}."
                        if not is_chinese
                        else f"{item['name']} 於 {day_translation.get(item['date_info']['day'], item['date_info']['day'])}, {item['date_info']['date']}, 從 {item['date_info']['start_time']} 至 {item['date_info']['end_time']}。"
                    )
                prefix = (
                    f"Yo, your nearest {type_label} is:\n"
                    if tone == "casual"
                    else f"Your nearest {type_label} is:\n"
                )
                if is_chinese:
                    prefix = f"您最近的{'作業' if type_label == 'assignment' else '活動'}是：\n"
                result = f"{prefix}{sentence}"
            elif is_course_due:
                course_name = COURSE_MAPPING.get(course_id.upper(), {}).get(
                    "zh" if is_chinese else "en", course_id
                )
                if count == 1:
                    item = items[0]
                    sentence = (
                        f"{item['name']}, due on {item['date_info']['day']}, {item['date_info']['date']}, {item['date_info']['time']}."
                        if not is_chinese
                        else f"{item['name']} 預定於 {day_translation.get(item['date_info']['day'], item['date_info']['day'])}, {item['date_info']['date']}, {item['date_info']['time']} 到期。"
                    )
                    prefix = (
                        f"Yo, the assignment for {course_id} ({course_name}) is:\n"
                        if tone == "casual"
                        else f"The assignment for {course_id} ({course_name}) is:\n"
                    )
                    if is_chinese:
                        prefix = f"{course_id}（{course_name}）的作業是：\n"
                    result = f"{prefix}{sentence}"
                else:
                    sentences = [
                        (
                            f"{item['name']} is due on {item['date_info']['day']}, {item['date_info']['date']}, {item['date_info']['time']}.\n"
                            if not is_chinese
                            else f"{item['name']} 預定於 {day_translation.get(item['date_info']['day'], item['date_info']['day'])}, {item['date_info']['date']}, {item['date_info']['time']} 到期。\n"
                        )
                        for item in items
                    ]
                    prefix = (
                        f"Yo, you got {count} assignments for {course_id} ({course_name}):\n"
                        if tone == "casual"
                        else f"You have {count} assignments for {course_id} ({course_name}):\n"
                    )
                    if is_chinese:
                        prefix = f"{course_id}（{course_name}）有{count}項作業：\n"
                    result = f"{prefix}{''.join(sentences)}"
            else:
                if type_label == "assignment":
                    sentences = [
                        f"{item['name']} is due on {item['date_info']['day']}, {item['date_info']['date']}, {item['date_info']['time']}.\n"
                        for item in items
                    ]
                else:
                    sentences = [
                        f"{item['name']} on {item['date_info']['day']}, {item['date_info']['date']}, from {item['date_info']['start_time']} to {item['date_info']['end_time']}.\n"
                        for item in items
                    ]
                prefix = (
                    f"Yo, you got {count} {type_label_plural}:\n"
                    if tone == "casual"
                    else f"You have {count} {type_label_plural}:\n"
                )
                if is_chinese:
                    prefix = f"您有{count}項{'作業' if type_label == 'assignment' else '活動'}：\n"
                    if type_label == "assignment":
                        sentences = [
                            f"{item['name']} 預定於 {day_translation.get(item['date_info']['day'], item['date_info']['day'])}, {item['date_info']['date']}, {item['date_info']['time']} 到期。\n"
                            for item in items
                        ]
                    else:
                        sentences = [
                            f"{item['name']} 於 {day_translation.get(item['date_info']['day'], item['date_info']['day'])}, {item['date_info']['date']}, 從 {item['date_info']['start_time']} 至 {item['date_info']['end_time']}。\n"
                            for item in items
                        ]
                result = f"{prefix}{''.join(sentences)}"

        return fix_chinese_spacing(result.strip())
    except Exception as e:
        logging.error(f"Failed to generate sentence for '{prompt}': {e}")
        if is_course_due:
            course_name = COURSE_MAPPING.get(course_id.upper(), {}).get(
                "zh" if is_chinese else "id", course_id
            )
            if is_chinese:
                return fix_chinese_spacing(f"抱歉，沒有找到{course_name}的作業。")
            return f"No assignments found for {course_id} ({course_name})."
        if is_chinese:
            return fix_chinese_spacing(
                f"抱歉，您沒有即將到來的{'作業' if type_label == 'assignment' else '活動'}。"
            )
        return f"Sorry, you have no {type_label_plural}."


def classify_prompt(prompt, line_id):
    """
    Classify a user prompt and fetch relevant data.
    """
    try:
        X_prompt = vectorizer.transform([prompt])
        prediction = model.predict(X_prompt)[0]

        # Extract course ID for course_due_date
        course_id = None
        if prediction == "course_due_date":
            # Match course ID or course name (full or partial)
            course_patterns = [
                r"IN\d{3}",  # Course ID
                r"Introduction to Algorithm|演算法概論|Algorithm",
                r"Information Privacy|資訊隱私|Privacy",
                r"Assembly Language and Computer Organization|組合語言與計算機組織|Assembly Language",
                r"Introduction to Operating System|作業系統導論|Operating System",
                r"Probability and Statistics|機率與統計|Statistics",
            ]
            pattern = "|".join(course_patterns)
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                matched = match.group(0).lower()
                # Map to course ID
                course_name_to_id = {
                    "introduction to algorithm": "IN208",
                    "演算法概論": "IN208",
                    "algorithm": "IN208",
                    "information privacy": "IN211",
                    "資訊隱私": "IN211",
                    "privacy": "IN211",
                    "assembly language and computer organization": "IN210",
                    "組合語言與計算機組織": "IN210",
                    "assembly language": "IN210",
                    "introduction to operating system": "IN209",
                    "作業系統導論": "IN209",
                    "operating system": "IN209",
                    "probability and statistics": "IN207",
                    "機率與統計": "IN207",
                    "statistics": "IN207",
                }
                course_id = course_name_to_id.get(
                    matched, matched.upper() if matched.startswith("in") else None
                )

        logging.info(f"Prompt: '{prompt}' classified as '{prediction}'")

        items = fetch_data(line_id, prediction, course_id=course_id)
        sentence = generate_ml_sentence(prompt, prediction, items, course_id=course_id)
        logging.info(f"Response for '{prompt}': {sentence}")

        return prediction, sentence
    except Exception as e:
        logging.error(f"Failed to classify prompt '{prompt}': {e}")
        return None, None


def main(prompt, lineid):
    """
    Main function to test the classifier.
    """
    logging.info("Starting ml_classifier.py execution...")
    try:
        # test_line_id = "U2d05e1777e259a7a068e91b5f33c942e"
        # test_prompts = [
        #     "What homework do I have?",
        #     "Show me my upcoming events",
        #     "Any tasks due soon?",
        #     "List activities for this week",
        #     "顯示我的作業",
        #     "有哪些活動？",
        #     "What are my HW?",
        #     "What assignment has the nearest deadline?",
        #     "What activity is happening soonest?",
        #     "最近的作業是什麼？",
        #     "最近的活動是什麼？",
        #     "When is the deadline for IN208?",
        #     "Due date for IN210?",
        #     "演算法概論課程的作業何時到期？",
        #     "組合語言與計算機組織課程的作業何時到期？",
        #     "What’s the due date for IN211?",
        #     "Due date for Introduction to Algorithm?",
        #     "When is the deadline for Information Privacy?",
        #     "作業系統導論的作業何時到期？"
        # ]

        # for prompt in test_prompts:
        #     result, sentence = classify_prompt(prompt, test_line_id)
        #     if not result:
        #         logging.warning(f"No classification result for prompt: '{prompt}'")
        result, sentence = classify_prompt(prompt, lineid)
        if result:
            return sentence
        else:
            logging.warning(f"No classification result for prompt: '{prompt}'")
    except Exception as e:
        logging.error(f"Error in ml_classifier.py: {e}")


if __name__ == "__main__":
    main()
