from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# -------------------------
# CLEAN OUTPUT (STRICT)
# -------------------------
def clean_output(text):
    if text is None:
        return ""
    return str(text).strip()

# -------------------------
# LEVEL 1: SUM
# -------------------------
def solve_math(query):
    nums = [int(n) for n in re.findall(r'-?\d+', query)]
    if len(nums) >= 2:
        return f"The sum is {nums[0] + nums[1]}"
    return ""

# -------------------------
# LEVEL 2: DATE
# -------------------------
def extract_date(query):
    match = re.search(
        r'(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        query,
        re.IGNORECASE
    )
    return match.group(1) if match else ""

# -------------------------
# LEVEL 3: ODD
# -------------------------
def check_parity(query):
    nums = re.findall(r'\d+', query)
    if nums:
        return "YES" if int(nums[0]) % 2 else "NO"
    return ""

# -------------------------
# LEVEL 4: SUM EVEN
# -------------------------
def sum_even(query):
    nums = [int(n) for n in re.findall(r'-?\d+', query)]
    return str(sum(n for n in nums if n % 2 == 0)) if nums else ""

# -------------------------
# LEVEL 5: HIGHEST SCORER
# -------------------------
def highest_scorer(query):
    pairs = re.findall(r'([A-Z][a-z]+)\s+scored\s+(\d+)', query)
    if not pairs:
        return ""
    return max(pairs, key=lambda x: int(x[1]))[0]

# -------------------------
# CORE SOLVER (NO FALLBACK BUG)
# -------------------------
def solve(query):
    q = query.lower()

    if "scored" in q and "highest" in q:
        return highest_scorer(query)

    if "sum even" in q:
        return sum_even(query)

    if "odd" in q:
        return check_parity(query)

    if "date" in q:
        return extract_date(query)

    if "sum" in q or "+" in query:
        return solve_math(query)

    return ""

# -------------------------
# MAIN ROUTE (STRICT JSON)
# -------------------------
@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "").strip()

    result = clean_output(solve(query))

    return jsonify({"output": result})

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
