from flask import Flask, request, jsonify
import google.generativeai as genai
import httpx, os

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

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
    response = model.generate_content(f"Answer accurately and concisely for an AI benchmark.\n\n{prompt}")
    return jsonify({"output": response.text.strip()})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
