
import os
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from google import genai
from groq import Groq


# =========================
# Environment Variables
# =========================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not GEMINI_API_KEY:
    raise RuntimeError("找不到 GEMINI_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("找不到 GROQ_API_KEY")

if not SECRET_KEY or SECRET_KEY == "CHANGE_ME":
    raise RuntimeError("請在 .env 設定安全的 SECRET_KEY")


# =========================
# Flask
# =========================

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Lab 用簡化帳號
# 正式部署應使用密碼雜湊與安全的帳號管理
USERS = {
    "admin": os.getenv("LAB6_PASSWORD", "1234")
}


# =========================
# AI Clients
# =========================

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)


# =========================
# Gemini
# =========================

def ask_gemini(message, previous_interaction_id=None):
    params = {
        "model": GEMINI_MODEL,
        "input": message,
    }

    if previous_interaction_id:
        params["previous_interaction_id"] = previous_interaction_id

    interaction = gemini_client.interactions.create(**params)

    reply = (interaction.output_text or "").strip()

    if not reply:
        reply = "Gemini 沒有回傳文字內容。"

    return reply, interaction.id


# =========================
# GPT-OSS via Groq
# =========================

def ask_gpt(message, history=None):
    messages = [
        {
            "role": "system",
            "content": "請使用繁體中文回答使用者問題。"
        }
    ]

    if history:
        messages.extend(history)

    messages.append({
        "role": "user",
        "content": message
    })

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_completion_tokens=500,
    )

    reply = (
        response.choices[0].message.content or ""
    ).strip()

    if not reply:
        reply = "GPT-OSS 沒有回傳文字內容。"

    return reply


# =========================
# Login Required
# =========================

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "請先登入"}), 401

            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped


# =========================
# Login
# =========================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username in USERS and USERS[username] == password:
            session.clear()
            session["user"] = username
            return redirect(url_for("chat_room"))

        return render_template(
            "login.html",
            msg="帳號或密碼錯誤"
        )

    if "user" in session:
        return redirect(url_for("chat_room"))

    return render_template("login.html")


# =========================
# Chat Page
# =========================

@app.get("/chat")
@login_required
def chat_room():
    return render_template(
        "chat.html",
        username=session["user"]
    )


# =========================
# AI Chat API
# =========================

@app.post("/api/chat")
@login_required
def api_chat():
    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()
    model = str(data.get("model", "gemini")).strip()

    if not message:
        return jsonify({"error": "訊息不可為空"}), 400

    if len(message) > 2000:
        return jsonify({"error": "訊息過長"}), 400

    if model not in ("gemini", "gpt"):
        return jsonify({"error": "不支援的模型"}), 400

    try:
        if model == "gemini":
            previous_id = session.get("gemini_interaction_id")

            reply, interaction_id = ask_gemini(
                message,
                previous_id
            )

            session["gemini_interaction_id"] = interaction_id

        else:
            history = session.get("gpt_history", [])

            reply = ask_gpt(message, history)

            history.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": reply}
            ])

            # 保存最近 4 輪對話
            session["gpt_history"] = history[-8:]

        return jsonify({
            "reply": reply,
            "model": model
        })

    except Exception as error:
        print(
            "[AI API Error]",
            type(error).__name__,
            str(error)
        )

        return jsonify({
            "error": "AI API 呼叫失敗，請檢查 Terminal 訊息。"
        }), 502


# =========================
# Reset Conversation
# =========================

@app.post("/api/reset")
@login_required
def reset_chat():
    session.pop("gemini_interaction_id", None)
    session.pop("gpt_history", None)

    return jsonify({"ok": True})


# =========================
# Logout
# =========================

@app.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


# =========================
# Run Server
# =========================

if __name__ == "__main__":
    print("=== Lab6 Flask AI Chat ===")
    print("Listening on http://0.0.0.0:3000")
    print("Debug mode is OFF")

    app.run(
        host="0.0.0.0",
        port=3000,
        debug=False
    )
