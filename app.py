from flask import Flask, request
import re

app = Flask(__name__)

# ---------- DATE EXTRACTION ----------
def extract_date(text):
    # Matches formats like: 12 March 2024
    match = re.search(r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', text, re.IGNORECASE)
    
    if match:
        return match.group(0)

    return None


# ---------- MAIN SOLVER ----------
def solve_query(query):
    
    # 🔹 LEVEL 2: Date extraction
    if "extract date" in query.lower():
        result = extract_date(query)
        if result:
            return result
        return "No date found"

    # 🔹 LEVEL 1 fallback (math)
    match = re.search(r'what is (\d+)\s*\+\s*(\d+)', query.lower())
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        return f"The sum is {a + b}."

    return "Unknown"


# ---------- API ----------
@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")

    result = solve_query(query)

    return {"output": result}


# ---------- HEALTH ----------
@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
