from flask import Flask, request, jsonify
import httpx, os, re

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# (Optional) fetch asset content
def fetch_asset(url):
    try:
        r = httpx.get(url, timeout=5, follow_redirects=True)
        if r.status_code == 200:
            return r.text[:2000]
    except:
        pass
    return ""

@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "").strip()

    # =========================
    # ⚡ FAST LOGIC (NO AI)
    # =========================

    # Addition
    match = re.search(r'(\d+)\s*\+\s*(\d+)', query)
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        return jsonify({"output": f"The sum is {a + b}."})

    # Subtraction
    match = re.search(r'(\d+)\s*-\s*(\d+)', query)
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        return jsonify({"output": f"The difference is {a - b}."})

    # Multiplication
    match = re.search(r'(\d+)\s*\*\s*(\d+)', query)
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        return jsonify({"output": f"The product is {a * b}."})

    # Division
    match = re.search(r'(\d+)\s*/\s*(\d+)', query)
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        if b != 0:
            return jsonify({"output": f"The quotient is {a // b}."})

    # =========================
    # 🤖 FALLBACK → AI (only if needed)
    # =========================

    context = "".join(f"\n---\n{fetch_asset(u)}" for u in data.get("assets", []))
    prompt = f"Reference material:{context}\n\nQuestion: {query}" if context else query

    try:
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": "Answer in one short sentence starting with 'The'. Maximum 15 words."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.1
            },
            timeout=10
        )

        result = resp.json()
        output = result["choices"][0]["message"]["content"].strip()

    except:
        output = "The answer is not available."

    return jsonify({"output": output})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
