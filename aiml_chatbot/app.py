from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME =  "tinyllama"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()

    if not user_msg:
        return jsonify({"reply": "Ask me something 🙂"})

    # Simple greeting
    if user_msg.lower() in ["hi", "hello", "hii", "hiiii", "hey"]:
        return jsonify({"reply": "Hi 😄 How can I help you today?"})

    payload = {
        "model": MODEL_NAME,
        "prompt": user_msg,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )
        data = response.json()

        # 👇 THIS IS THE IMPORTANT FIX
        reply = data.get("response")

        if reply and reply.strip():
            return jsonify({"reply": reply.strip()})

        # If model returned nothing
        return jsonify({"reply": "I’m thinking… can you try again once?"})

    except Exception as e:
        return jsonify({"reply": "Local AI is not responding. Please restart Ollama."})

if __name__ == "__main__":
    app.run(debug=True)
