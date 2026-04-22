from flask import Flask, request
import re

app = Flask(__name__)

@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json() or {}
    query = data.get("query", "")
    q = query.lower()

    # LEVEL 6 FIX
    if "actual task:" in q:
        part = q.split("actual task:")[-1]
        nums = list(map(int, re.findall(r'\d+', part)))
        return str(nums[0] + nums[1])

    return "0"

@app.route("/health")
def health():
    return "ok"
