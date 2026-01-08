from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
import re
from openai import OpenAI


app = Flask(__name__)

# ✅ CREATE THE CLIENT HERE
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


ADMIN_PASSWORD = "admin123"  # change later

def save_lead(name, contact):
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS leads (name TEXT, contact TEXT)")
    c.execute("INSERT INTO leads VALUES (?, ?)", (name, contact))
    conn.commit()
    conn.close()

def get_leads():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS leads (name TEXT, contact TEXT)")
    c.execute("SELECT rowid, name, contact FROM leads ORDER BY rowid DESC")
    leads = c.fetchall()
    conn.close()
    return leads


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=user_message
    )

    bot_reply = response.output[0].content[0].text

    return jsonify({"reply": bot_reply})



Greeting:
{config['greeting']}

Services:
{config['services']}

Your goals:
- Answer questions clearly
- Collect leads (email or phone)
- Encourage bookings: {config['booking_link']}
- Share contact info when asked: {config['contact_info']}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
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

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")

        if password != ADMIN_PASSWORD:
            return "Unauthorized", 401

        leads = get_leads()
        return render_template("admin.html", leads=leads)

    return """
    <h2>Admin Login</h2>
    <form method="post">
        <input type="password" name="password" placeholder="Admin Password" required>
        <button type="submit">Login</button>
    </form>
    """

def init_client_config():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS client_config (
            id INTEGER PRIMARY KEY,
            business_name TEXT,
            services TEXT,
            greeting TEXT,
            booking_link TEXT,
            contact_info TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_default_client():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM client_config")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO client_config 
            (business_name, services, greeting, booking_link, contact_info)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Sample Business",
            "Consulting, Web Design, Marketing",
            "Hi 👋 Welcome! How can we help you today?",
            "https://calendly.com/sample",
            "contact@sample.com | 555-123-4567"
        ))
    conn.commit()
    conn.close()

def get_client_config():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("""
        SELECT business_name, services, greeting, booking_link, contact_info
        FROM client_config LIMIT 1
    """)
    row = c.fetchone()
    conn.close()

    return {
        "business_name": row[0],
        "services": row[1],
        "greeting": row[2],
        "booking_link": row[3],
        "contact_info": row[4],
    }


if __name__ == "__main__":
    init_client_config()
    insert_default_client()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


