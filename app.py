from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# -------------------------
# CLEAN OUTPUT (STRICT)
# -------------------------
def clean_output(text):
    if text is None:
        return ""
    text = str(text).strip()
    text = text.replace(".", "").replace(",", "")
    text = re.sub(r"\s+", " ", text)
    return text

# -------------------------
# LEVEL 1: SUM
# -------------------------
def solve_math(query):
    nums = re.findall(r'-?\d+', query)
    if len(nums) >= 2:
        return f"The sum is {int(nums[0]) + int(nums[1])}"
    return None

# -------------------------
# LEVEL 2: DATE
# -------------------------
def extract_date(query):
    match = re.search(
        r'(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        query,
        re.IGNORECASE
    )
    return match.group(1) if match else None

# -------------------------
# LEVEL 3: ODD
# -------------------------
def check_odd(query):
    nums = re.findall(r'\d+', query)
    if nums:
        return "YES" if int(nums[0]) % 2 else "NO"
    return None

# -------------------------
# LEVEL 4: SUM EVEN
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
    q = query.replace(",", " ").replace(".", " ").replace("and", " ")
    pairs = re.findall(r'([A-Z][a-z]+)\s+scored\s+(\d+)', q)

    if not pairs:
        return None

    best = max(pairs, key=lambda x: int(x[1]))[0]
    return best

# -------------------------
# MAIN ROUTE (FIXED PRIORITY)
# -------------------------
@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "").strip()
    q = query.lower()

    # 🔥 CORRECT ORDER (IMPORTANT)

    if "scored" in q and "highest" in q:
        result = find_highest_scorer(query)

    elif "sum even" in q:
        result = sum_even_numbers(query)

    elif "odd" in q:
        result = check_odd(query)

    elif "date" in q:
        result = extract_date(query)

    else:
        result = solve_math(query)

    return jsonify({"output": clean_output(result)})

# -------------------------
# HEALTH
# -------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
