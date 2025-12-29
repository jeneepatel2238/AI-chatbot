from flask import Flask, render_template, request, jsonify
import sqlite3
import re
from openai import OpenAI

app = Flask(__name__)

# ✅ CREATE THE CLIENT HERE
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



SYSTEM_PROMPT = """
You are a friendly AI chatbot for any small business.
Your tasks:
- Greet users warmly
- Answer FAQs
- Explain services or products
- Collect leads (name, email, phone)
- Offer to book appointments
"""

def save_lead(name, contact):
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS leads (name TEXT, contact TEXT)")
    c.execute("INSERT INTO leads VALUES (?, ?)", (name, contact))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    print("USER:", user_message)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    bot_reply = response.output_text
    print("BOT:", bot_reply)

    # Lead capture
    email = re.search(r'[\w\.-]+@[\w\.-]+', user_message or "")
    phone = re.search(r'\+?\d{10,15}', user_message or "")

    if email or phone:
        save_lead(
            "Unknown",
            f"{email.group(0) if email else ''} {phone.group(0) if phone else ''}"
        )

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
