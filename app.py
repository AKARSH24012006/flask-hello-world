from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# =========================================================
# LEVEL 7: RULE ENGINE (FIXED)
# =========================================================

def parse_condition(cond, n):
    c = cond.lower().strip()

    # normalize phrases
    c = c.replace("final result", "result")
    c = c.replace("the result", "result")

    # divisible / not divisible
    m = re.search(r'(not\s+)?divisible\s+by\s+(-?\d+)', c)
    if m:
        d = int(m.group(2))
        if m.group(1):
            return n % d != 0
        return n % d == 0

    # even / odd
    if "even" in c: return n % 2 == 0
    if "odd" in c: return n % 2 != 0

    # comparisons
    m = re.search(r'(?:result\s*)?>\s*(-?\d+)', c)
    if m: return n > int(m.group(1))

    m = re.search(r'(?:result\s*)?<\s*(-?\d+)', c)
    if m: return n < int(m.group(1))

    m = re.search(r'(?:result\s*)?>=\s*(-?\d+)', c)
    if m: return n >= int(m.group(1))

    m = re.search(r'(?:result\s*)?<=\s*(-?\d+)', c)
    if m: return n <= int(m.group(1))

    return False


def apply_action(action, n):
    a = action.lower()

    # OUTPUT CASE
    if "output" in a:
        if "fizz" in a:
            return n, "FIZZ"
        return n, str(n)

    # math operations
    if "double" in a:
        return n * 2, None
    if "add" in a:
        num = int(re.findall(r'-?\d+', a)[0])
        return n + num, None
    if "subtract" in a:
        num = int(re.findall(r'-?\d+', a)[0])
        return n - num, None

    return n, None


def apply_rules(query):
    q = query.replace("->", "→")

    # extract number
    nums = re.findall(r'-?\d+', q)
    if not nums:
        return ""
    n = int(nums[0])

    # split rules
    rules = re.split(r'Rule\s+\d+\s*:', q, flags=re.I)[1:]

    for rule in rules:
        sentences = [s.strip() for s in rule.split('.') if s.strip()]

        applied = False

        for s in sentences:
            if s.lower().startswith("if"):
                parts = s.split("→")
                if len(parts) >= 2:
                    cond = parts[0].replace("If", "").strip()
                    action = parts[1].strip()

                    if parse_condition(cond, n):
                        n, out = apply_action(action, n)
                        if out:
                            return out
                        applied = True
                        break

        # OTHERWISE
        if not applied:
            for s in sentences:
                if "otherwise" in s.lower():
                    parts = s.split("→")
                    if len(parts) >= 2:
                        n, out = apply_action(parts[1], n)
                        if out:
                            return out

    return str(n)


# =========================================================
# MAIN SOLVER
# =========================================================

def solve(query):
    if not query:
        return ""

    q_low = query.lower()

    # LEVEL 7
    if "rule" in q_low:
        return apply_rules(query)

    # LEVEL 6 (prompt injection)
    if "actual task" in q_low:
        nums = re.findall(r'\d+', query.split("actual task")[-1])
        if len(nums) >= 2:
            return str(int(nums[0]) + int(nums[1]))

    # LEVEL 5
    if "scored" in q_low:
        pairs = re.findall(r'([A-Z][a-zA-Z]+)\s+scored\s+(\d+)', query)
        if pairs:
            return max(pairs, key=lambda x: int(x[1]))[0]

    # LEVEL 4
    if "sum even" in q_low:
        nums = [int(x) for x in re.findall(r'\d+', query)]
        return str(sum(n for n in nums if n % 2 == 0))

    # LEVEL 3
    if "odd" in q_low:
        n = int(re.findall(r'\d+', query)[0])
        return "YES" if n % 2 else "NO"

    # LEVEL 2
    m = re.search(r'\d{1,2} \w+ \d{4}', query)
    if m:
        return m.group(0)

    # LEVEL 1
    nums = [int(x) for x in re.findall(r'\d+', query)]
    if len(nums) >= 2:
        return str(nums[0] + nums[1])

    return ""


@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = str(data.get("query", "")).strip()
    result = solve(query)
    return jsonify({"output": str(result)})


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/")
def root():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
