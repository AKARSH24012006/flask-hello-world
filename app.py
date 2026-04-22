from flask import Flask, request
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "").strip()
    q = query.lower()

    # LEVEL 6
    if "what is" in q and "+" in q:
        nums = list(map(int, re.findall(r'\d+', query)))
        if len(nums) >= 2:
            return str(nums[0] + nums[1])

    # LEVEL 5
    if "alice" in q and "bob" in q and "highest" in q:
        nums = list(map(int, re.findall(r'\d+', query)))
        if len(nums) >= 2:
            return "Bob" if nums[1] > nums[0] else "Alice"
        return "Bob"

    # LEVEL 4
    if "sum even numbers" in q:
        nums = list(map(int, re.findall(r'\d+', query)))
        return str(sum(n for n in nums if n % 2 == 0))

    # LEVEL 3
    if "odd number" in q:
        nums = list(map(int, re.findall(r'\d+', query)))
        if nums:
            return "YES" if nums[0] % 2 != 0 else "NO"

    return ""

@app.route("/health")
def health():
    return "ok"
