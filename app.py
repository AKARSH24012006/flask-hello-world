from flask import Flask, request, jsonify
import anthropic, httpx, os

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

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
    msg = client.messages.create(
        model="claude-opus-4-5", max_tokens=512,
        system="Answer accurately and concisely for an AI benchmark.",
        messages=[{"role": "user", "content": f"{context}\n\n{query}" if context else query}]
    )
    return jsonify({"output": msg.content[0].text.strip()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
