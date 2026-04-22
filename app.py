from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)


def solve(query):
    if not query:
        return ""

    q_low = query.lower()

    # ---------------- LEVEL 6 (Prompt Injection Fix) ----------------
    task = query
    for marker in ["actual task:", "actual task :", "real task:",
                   "actual question:", "real question:", "true task:"]:
        idx = q_low.find(marker)
        if idx != -1:
            task = query[idx + len(marker):].strip()
            break

    t_low = task.lower()

    # Math expression (13 + 7, etc.)
    m = re.search(r'(-?\d+)\s*([+\-*/xX×])\s*(-?\d+)', task)
    if m:
        a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
        if op == '+': return a + b
        if op == '-': return a - b
        if op in ('*', 'x', 'X', '×'): return a * b
        if op == '/' and b != 0: return a // b

    task_nums = [int(n) for n in re.findall(r'-?\d+', task)]
    if task_nums:
        if any(w in t_low for w in ["plus", "add", "sum", "total"]):
            return sum(task_nums)
        if any(w in t_low for w in ["minus", "subtract", "difference"]) and len(task_nums) >= 2:
            return task_nums[0] - task_nums[1]
        if any(w in t_low for w in ["times", "multiply", "product"]):
            r = 1
            for n in task_nums:
                r *= n
            return r

    # ---------------- LEVEL 5 ----------------
    if "scored" in q_low:
        pairs = re.findall(r'([A-Z][a-zA-Z]+)\s+scored\s+(-?\d+)', query)
        if pairs:
            if any(w in q_low for w in ["highest", "most", "top", "best", "max"]):
                return max(pairs, key=lambda x: int(x[1]))[0]
            if any(w in q_low for w in ["lowest", "least", "worst", "min"]):
                return min(pairs, key=lambda x: int(x[1]))[0]

    # ---------------- LEVEL 4 ----------------
    if "sum" in q_low:
        ns = [int(n) for n in re.findall(r'-?\d+', query)]
        if "even" in q_low:
            return sum(n for n in ns if n % 2 == 0)
        if "odd" in q_low:
            return sum(n for n in ns if n % 2 != 0)

    # ---------------- LEVEL 3 ----------------
    if "odd" in q_low or "even" in q_low:
        ns = re.findall(r'-?\d+', query)
        if ns:
            n = int(ns[0])
            if "odd" in q_low:
                return "YES" if n % 2 else "NO"
            if "even" in q_low:
                return "YES" if not n % 2 else "NO"

    # ---------------- LEVEL 2 ----------------
    date_m = re.search(
        r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        query, re.I
    )
    if date_m:
        return date_m.group(1)

    # ---------------- LEVEL 1 ----------------
    m = re.search(r'(-?\d+)\s*([+\-*/])\s*(-?\d+)', query)
    if m:
        a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/' and b != 0: return a // b

    all_nums = [int(n) for n in re.findall(r'-?\d+', query)]
    if len(all_nums) >= 2:
        return sum(all_nums)

    return ""


@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = str(
        data.get("query")
        or data.get("input")
        or data.get("prompt")
        or data.get("question")
        or ""
    ).strip()

    result = solve(query)

    # 🔥 CRITICAL FIX (TYPE HANDLING)
    if isinstance(result, int):
        return jsonify({"output": result})
    else:
        return jsonify({"output": str(result)})


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/")
def root():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
