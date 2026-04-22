from flask import Flask, request, jsonify
import httpx, os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def fetch_asset(url):
    try:
        r = httpx.get(url, timeout=5, follow_redirects=True)
        if r.status_code == 200:
            return r.text[:4000]
    except: pass
    return ""

@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")
    context = "".join(f"\n---\n{fetch_asset(u)}" for u in data.get("assets", []))
    prompt = f"Reference material:{context}\n\nQuestion: {query}" if context else query

    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a precise AI assistant. Give only the direct answer in one short sentence. No explanations, no extra words. For math: 'The sum is X.' or 'The product is X.' etc. Match the expected output format exactly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 100
        },
        timeout=15
    )
    result = resp.json()
    try:
        output = result["choices"][0]["message"]["content"].strip()
    except:
        output = str(result)
    return jsonify({"output": output})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
