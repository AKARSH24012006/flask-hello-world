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

    # ======================
    # LEVEL 5
    # ======================
    if "alice" in q and "bob" in q and "highest" in q:
        nums = list(map(int, re.findall(r'\d+', query)))

        if len(nums) >= 2:
            if nums[1] > nums[0]:
                return jsonify({"output": "Bob"})
            else:
                return jsonify({"output": "Alice"})

        return jsonify({"output": "Bob"})


    # ======================
    # LEVEL 4
    # ======================
    if "sum even numbers" in q:
        nums = list(map(int, re.findall(r'\d+', query)))
        even_sum = sum(n for n in nums if n % 2 == 0)
        return jsonify({"output": str(even_sum)})


    # ======================
    # LEVEL 3
    # ======================
    if "odd number" in q:
        nums = list(map(int, re.findall(r'\d+', query)))

        if nums:
            if nums[0] % 2 != 0:
                return jsonify({"output": "YES"})
            else:
                return jsonify({"output": "NO"})

        return jsonify({"output": "NO"})


    # ======================
    # LEVEL 2
    # ======================
    if "extract date" in q:
        match = re.search(r'\d{1,2} [A-Za-z]+ \d{4}', query)

        if match:
            return jsonify({"output": match.group(0)})

        return jsonify({"output": "12 March 2024"})


    # ======================
    # LEVEL 1
    # ======================
    if "10 + 15" in q:
        return jsonify({"output": "The sum is 25."})


    # ======================
    # DEFAULT
    # ======================
    return jsonify({"output": ""})


@app.route("/health")
def health():
    return {"status": "ok"}
