from flask import Flask, request
import re

app = Flask(__name__)

MONTHS = "(January|February|March|April|May|June|July|August|September|October|November|December)"

# ---------- DATE ----------
def extract_date(text):
    match = re.search(rf'\b\d{{1,2}}\s+{MONTHS}\s+\d{{4}}\b', text, re.IGNORECASE)
    if match:
        return match.group(0)
    return None

# ---------- ODD / EVEN ----------
def check_odd_even(query):
    match = re.search(r'\b(\d+)\b', query)
    if match:
        num = int(match.group(1))
        if "odd" in query.lower():
            return "YES" if num % 2 == 1 else "NO"
        if "even" in query.lower():
            return "YES" if num % 2 == 0 else "NO"
    return None

# ---------- LEVEL 1 ----------
def solve_math(query):
    match = re.search(r'what is (\d+)\s*\+\s*(\d+)', query.lower())
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        return f"The sum is {a + b}."
    return None

# ---------- MAIN ----------
def solve_query(query):

    # 🔥 LEVEL 3 (highest priority)
    odd_even = check_odd_even(query)
    if odd_even:
        return odd_even

    # 🔥 LEVEL 2
    date = extract_date(query)
    if date:
        return date.strip()

    # 🔥 LEVEL 1
    math = solve_math(query)
    if math:
        return math

    return "Unknown"


# ---------- API ----------
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
