from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# -------------------------
# HELPERS (STRICT NORMALIZATION)
# -------------------------
def clean_output(text):
    if text is None:
        return ""
    # exact matching requirements
    text = str(text).strip()
    text = text.replace(".", "").replace(",", "")
    text = re.sub(r"\s+", " ", text)
    return text

# -------------------------
# LEVEL 1: BASIC MATH
# -------------------------
def solve_math(query):
    # Extract numbers
    nums = re.findall(r'-?\d+', query)
    if len(nums) >= 2:
        a, b = int(nums[0]), int(nums[1])
        return f"The sum is {a + b}"
    return None

# -------------------------
# LEVEL 2: DATE EXTRACTION
# -------------------------
def extract_date(query):
    match = re.search(
        r'(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        query,
        re.IGNORECASE
    )
    if match:
        return match.group(1)
    return None

# -------------------------
# LEVEL 3: ODD CHECK
# -------------------------
def check_odd(query):
    nums = re.findall(r'\d+', query)
    if nums:
        n = int(nums[0])
        return "YES" if n % 2 == 1 else "NO"
    return None

# -------------------------
# LEVEL 4: SUM EVEN NUMBERS
# -------------------------
def sum_even_numbers(query):
    nums = list(map(int, re.findall(r'-?\d+', query)))
    if nums:
        return str(sum(n for n in nums if n % 2 == 0))
    return None

# -------------------------
# LEVEL 5: HIGHEST SCORER
# -------------------------
def find_highest_scorer(query):
    # Normalize text
    q = query.replace(",", " ").replace(".", " ").replace("and", " ")

    # Extract pairs
    pairs = re.findall(r'([A-Z][a-z]+)\s+scored\s+(\d+)', q)

    if not pairs:
        return None

    # Find highest
    best_name = max(pairs, key=lambda x: int(x[1]))[0]
    return best_name

# -------------------------
# MAIN ROUTE
# -------------------------
@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")

    # Try all handlers
    result = (
        solve_math(query)
        or extract_date(query)
        or check_odd(query)
        or sum_even_numbers(query)
        or find_highest_scorer(query)
    )

    return jsonify({"output": clean_output(result)})

# -------------------------
# HEALTH CHECK
# -------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
