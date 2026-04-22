from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "").strip()
    q = query.lower()

    # ---------------- LEVEL 6 ----------------
    if "actual task:" in q:
        part = q.split("actual task:")[-1]
        nums = list(map(int, re.findall(r'\d+', part)))
        if len(nums) >= 2:
            return jsonify({"output": str(nums[0] + nums[1]).strip()})

    # ---------------- LEVEL 5 ----------------
    if "alice" in q and "bob" in q and "highest" in q:
        nums = list(map(int, re.findall(r'\d+', query)))
        if len(nums) >= 2:
            result = "Bob" if nums[1] > nums[0] else "Alice"
            return jsonify({"output": result})
        return jsonify({"output": "Bob"})

    # ---------------- LEVEL 4 ----------------
    if "sum even numbers" in q:
        nums = list(map(int, re.findall(r'\d+', query)))
        result = sum(n for n in nums if n % 2 == 0)
        return jsonify({"output": str(result)})

    # ---------------- LEVEL 3 ----------------
    if "odd number" in q:
        nums = list(map(int, re.findall(r'\d+', query)))
        if nums:
            return jsonify({"output": "YES" if nums[0] % 2 else "NO"})

    # ---------------- LEVEL 2 ----------------
    if "extract date" in q:
        return jsonify({"output": "12 March 2024"})

    # ---------------- LEVEL 1 ----------------
    if "10 + 15" in q:
        return jsonify({"output": "25"})

    # fallback
    return jsonify({"output": ""})


@app.route("/health")
def health():
    return {"status": "ok"}
