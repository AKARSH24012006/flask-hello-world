from flask import Flask, request, Response, jsonify
import re

app = Flask(__name__)

# -------------------------
# HELPERS
# -------------------------
def clean_output(text):
    if text is None:
        return ""
    return str(text).strip()

# -------------------------
# LEVEL 1: MATH / SUM
# -------------------------
def solve_math(query):
    nums = [int(n) for n in re.findall(r'-?\d+', query)]
    q = query.lower()
    if not nums:
        return ""
    if "product" in q or "multiply" in q:
        result = 1
        for n in nums:
            result *= n
        return str(result)
    if "difference" in q or "subtract" in q:
        if len(nums) >= 2:
            return str(nums[0] - nums[1])
    return str(sum(nums))

# -------------------------
# LEVEL 2: DATE EXTRACTION
# -------------------------
def extract_date(query):
    patterns = [
        r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
        r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})',
        r'(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
    ]
    for p in patterns:
        m = re.search(p, query, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""

# -------------------------
# LEVEL 3: ODD / EVEN CHECK
# -------------------------
def check_parity(query):
    nums = re.findall(r'-?\d+', query)
    q = query.lower()
    if not nums:
        return ""
    n = int(nums[0])
    if "odd" in q:
        return "YES" if n % 2 != 0 else "NO"
    if "even" in q:
        return "YES" if n % 2 == 0 else "NO"
    return ""

# -------------------------
# LEVEL 4: SUM EVEN / ODD
# -------------------------
def sum_by_parity(query):
    nums = [int(n) for n in re.findall(r'-?\d+', query)]
    q = query.lower()
    if not nums:
        return ""
    if "even" in q:
        return str(sum(n for n in nums if n % 2 == 0))
    if "odd" in q:
        return str(sum(n for n in nums if n % 2 != 0))
    return str(sum(nums))

# -------------------------
# LEVEL 5: HIGHEST / LOWEST SCORER
# -------------------------
def find_scorer(query, mode="highest"):
    patterns = [
        r'([A-Z][a-zA-Z]*)\s+scored\s+(-?\d+)',
        r'([A-Z][a-zA-Z]*)\s+got\s+(-?\d+)',
        r'([A-Z][a-zA-Z]*)\s+has\s+(-?\d+)',
        r'([A-Z][a-zA-Z]*)\s+earned\s+(-?\d+)',
        r'([A-Z][a-zA-Z]*)\s+made\s+(-?\d+)',
        r'([A-Z][a-zA-Z]*)\s+with\s+(-?\d+)',
        r'([A-Z][a-zA-Z]*)\s*[:=\-]\s*(-?\d+)',
    ]
    pairs = []
    for p in patterns:
        pairs.extend(re.findall(p, query))
    if not pairs:
        return ""

    seen, unique = set(), []
    for name, score in pairs:
        key = (name, score)
        if key not in seen:
            seen.add(key)
            unique.append((name, int(score)))

    if mode == "highest":
        return max(unique, key=lambda x: x[1])[0]
    if mode == "lowest":
        return min(unique, key=lambda x: x[1])[0]
    return ""

# -------------------------
# CORE SOLVER
# -------------------------
def solve(query):
    q = query.lower()

    has_scored  = bool(re.search(r'\bscore[ds]?\b|\bgot\b|\bearned\b', q))
    has_highest = any(w in q for w in ['highest', 'top', 'most', 'max', 'best', 'maximum'])
    has_lowest  = any(w in q for w in ['lowest', 'least', 'min', 'worst', 'minimum'])

    if has_scored and has_highest:
        return find_scorer(query, "highest")
    if has_scored and has_lowest:
        return find_scorer(query, "lowest")
    if "sum" in q and ("even" in q or "odd" in q):
        return sum_by_parity(query)
    if re.search(r'is\s+-?\d+\s+(odd|even)', q) or re.search(r'(odd|even)\s*\??\s*$', q):
        return check_parity(query)
    if "date" in q or re.search(r'\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', q, re.I):
        return extract_date(query)
    if "sum" in q or "add" in q or "+" in query or "total" in q or "plus" in q:
        return solve_math(query)

    # cascading fallback
    return (
        find_scorer(query, "highest")
        or extract_date(query)
        or solve_math(query)
        or ""
    )

# -------------------------
# MAIN ROUTE — PLAIN TEXT RESPONSE
# -------------------------
@app.route("/v1/answer", methods=["POST", "GET"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    if not data and request.form:
        data = request.form.to_dict()
    if not data and request.args:
        data = request.args.to_dict()

    query = (
        data.get("query")
        or data.get("input")
        or data.get("prompt")
        or data.get("question")
        or data.get("text")
        or data.get("q")
        or ""
    ).strip()

    result = clean_output(solve(query))

    # Return PLAIN TEXT — body is literally just "Bob" (no braces, no quotes, no keys)
    return Response(result, mimetype="text/plain; charset=utf-8")

# -------------------------
# HEALTH CHECK
# -------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
