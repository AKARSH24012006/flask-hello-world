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
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": """You are answering test questions for an AI benchmark. Your answers MUST be:
1. One short, declarative sentence
2. Direct and factual with no preamble
3. Match this exact style:
   - "What is 10+15?" → "The sum is 25."
   - "What is the capital of France?" → "The capital of France is Paris."
   - "What color is the sky?" → "The sky is blue."
   - "Who wrote Hamlet?" → "Hamlet was written by William Shakespeare."
4. Use simple, common words
5. Start with "The" when possible
6. No markdown, no lists, no explanations
7. Maximum 15 words"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 80,
            "temperature": 0.1
        },
        timeout=15
    )
    result = resp.json()
    try:
        output = result["choices"][0]["message"]["content"].strip()
        # Clean up common issues
        output = output.replace("**", "").replace("*", "")
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1]
    except:
        output = str(result)
    return jsonify({"output": output})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
