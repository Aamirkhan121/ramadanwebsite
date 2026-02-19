from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    today = datetime.now().strftime("%d %B %Y")
    return render_template("index.html", today=today)

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get("name")
    message = request.form.get("message")
    return f"Thank you {name}, your message has been received!"

if __name__ == "__main__":
    app.run(host="0.0.0.0")