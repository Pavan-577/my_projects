from flask import Flask, render_template, request, jsonify, redirect, session
from openai import OpenAI
import sqlite3
import os
import PyPDF2

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------- OPENROUTER --------
OPENROUTER_API_KEY = "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"

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "mistralai/mixtral-8x7b-instruct"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------- DATABASE --------

def get_db():
    return sqlite3.connect("users.db")

def init_db():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        message TEXT
    )
    """)

    db.commit()
    db.close()

init_db()

# -------- LOGIN --------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cur.fetchone()
        db.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/chatpage")
        else:
            return "Invalid login"

    return render_template("login.html")

# -------- CHAT PAGE --------

@app.route("/chatpage")
def chatpage():
    if "user_id" not in session:
        return redirect("/")
    return render_template("index.html")

# -------- LOAD HISTORY --------

@app.route("/load_history")
def load_history():
    if "user_id" not in session:
        return jsonify({"history": []})

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT name FROM users WHERE id=?", (session["user_id"],))
    name = cur.fetchone()[0]

    cur.execute(
        "SELECT role, message FROM chats WHERE user_id=? ORDER BY id ASC",
        (session["user_id"],)
    )
    rows = cur.fetchall()
    db.close()

    history = [{"role": r, "message": m} for r, m in rows]
    return jsonify({"name": name, "history": history})

# -------- CHAT API --------

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"reply": "Login again"})

    user_msg = request.json["message"]
    user_id = session["user_id"]

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT name FROM users WHERE id=?", (user_id,))
    name = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO chats (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, "user", user_msg)
    )

    cur.execute(
        "SELECT role, message FROM chats WHERE user_id=? ORDER BY id DESC LIMIT 8",
        (user_id,)
    )
    history = cur.fetchall()[::-1]

    messages = [{
        "role": "system",
        "content": f"You are ChatGPT-like assistant. User name is {name}."
    }]

    for r, m in history:
        messages.append({"role": r, "content": m})

    if "pdf_text" in session:
        messages.append({
            "role": "system",
            "content": f"PDF content:\n{session['pdf_text']}"
        })

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=500
    )

    bot_reply = response.choices[0].message.content

    cur.execute(
        "INSERT INTO chats (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, "assistant", bot_reply)
    )

    db.commit()
    db.close()

    return jsonify({"reply": bot_reply})

# -------- CLEAR --------

@app.route("/clear", methods=["POST"])
def clear():
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM chats WHERE user_id=?", (session["user_id"],))
    db.commit()
    db.close()
    session.pop("pdf_text", None)
    return jsonify({"status": "cleared"})

# -------- UPLOAD PDF --------

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    text = ""
    reader = PyPDF2.PdfReader(path)
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()

    session["pdf_text"] = text[:2000]
    return jsonify({"status": "PDF uploaded"})

# -------- LOGOUT --------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
