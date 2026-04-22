from flask import Flask, request
import re

app = Flask(__name__)

MONTHS = "(January|February|March|April|May|June|July|August|September|October|November|December)"

def extract_date(text):
    
    # 1️⃣ Standard: 12 March 2024
    match = re.search(rf'\b\d{{1,2}}\s+{MONTHS}\s+\d{{4}}\b', text, re.IGNORECASE)
    if match:
        return match.group(0)

    # 2️⃣ With commas: March 12, 2024
    match = re.search(rf'{MONTHS}\s+\d{{1,2}},\s*\d{{4}}', text, re.IGNORECASE)
    if match:
        parts = re.findall(r'\d+|[A-Za-z]+', match.group(0))
        return f"{parts[1]} {parts[0]} {parts[2]}"

    # 3️⃣ Slash format: 12/03/2024
    match = re.search(r'\b\d{1,2}/\d{1,2}/\d{4}\b', text)
    if match:
        d, m, y = match.group(0).split('/')
        return f"{int(d)} {month_name(int(m))} {y}"

    # 4️⃣ ISO: 2024-03-12
    match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', text)
    if match:
        y, m, d = match.group(0).split('-')
        return f"{int(d)} {month_name(int(m))} {y}"

    return None


def month_name(m):
    months = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return months[m]


def clean_output(text):
    return re.sub(r'\s+', ' ', text.strip())


def solve_query(query):
    result = extract_date(query)
    if result:
        return clean_output(result)
    return "Unknown"


@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")

    return {"output": solve_query(query)}


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
