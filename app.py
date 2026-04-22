from flask import Flask, request
import re

app = Flask(__name__)

MONTHS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# ---------- LEVEL 3: ODD / EVEN ----------
def check_odd_even(query):
    q = query.lower()

    # extract number
    match = re.search(r'\b\d+\b', q)
    if not match:
        return None

    num = int(match.group(0))

    # detect type
    if "odd" in q:
        return "YES" if num % 2 != 0 else "NO"

    if "even" in q:
        return "YES" if num % 2 == 0 else "NO"

    return None


# ---------- LEVEL 2: DATE ----------
def month_name(m):
    return MONTHS[m]

def extract_date(text):

    # 1️⃣ 12 March 2024
    match = re.search(r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', text, re.IGNORECASE)
    if match:
        return match.group(0)

    # 2️⃣ March 12, 2024 → convert
    match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4}', text, re.IGNORECASE)
    if match:
        parts = re.findall(r'\d+|[A-Za-z]+', match.group(0))
        return f"{int(parts[1])} {parts[0]} {parts[2]}"

    # 3️⃣ 12/03/2024 → convert
    match = re.search(r'\b\d{1,2}/\d{1,2}/\d{4}\b', text)
    if match:
        d, m, y = match.group(0).split('/')
        return f"{int(d)} {month_name(int(m))} {y}"

    # 4️⃣ 2024-03-12 → convert
    match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', text)
    if match:
        y, m, d = match.group(0).split('-')
        return f"{int(d)} {month_name(int(m))} {y}"

    return None


# ---------- LEVEL 1: MATH ----------
def solve_math(query):
    q = query.lower()

    # addition
    match = re.search(r'what is (\d+)\s*\+\s*(\d+)', q)
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        return f"The sum is {a + b}."

    # subtraction
    match = re.search(r'what is (\d+)\s*-\s*(\d+)', q)
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        return f"The difference is {a - b}."

    return None


# ---------- MAIN SOLVER ----------
def solve_query(query):

    # 🔥 PRIORITY 1 → LEVEL 3
    result = check_odd_even(query)
    if result:
        return result

    # 🔥 PRIORITY 2 → LEVEL 2
    result = extract_date(query)
    if result:
        return result.strip()

    # 🔥 PRIORITY 3 → LEVEL 1
    result = solve_math(query)
    if result:
        return result

    return "Unknown"


# ---------- API ----------
@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")

    return {"output": solve_query(query)}


# ---------- HEALTH ----------
@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
