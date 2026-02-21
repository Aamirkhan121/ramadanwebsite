from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import random
import os
from werkzeug.security import generate_password_hash, check_password_hash
# base_sehri = datetime(2026, 2, 19, 5, 12)
# base_iftar = datetime(2026, 2, 19, 18, 24)


app = Flask(__name__)

app.config['SECRET_KEY'] = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///database.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"

# ======================
# MODELS
# ======================

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ======================
# ROUTES
# ======================

quotes = [
    "Ramadan is the month of blessings 🌙",
    "Patience is the key to Jannah 🤍",
    "Allah is with those who are patient ✨",
    "Make dua, Allah is listening 🤲"
]


@app.route('/')
def home():
    today = datetime.now().strftime("%d %B %Y")
    random_quote = random.choice(quotes)
    messages = Message.query.order_by(Message.timestamp.desc()).all()

    start_date = datetime(2026, 2, 19)

    base_sehri = datetime(2026, 2, 19, 5, 00)
    base_iftar = datetime(2026, 2, 19, 17, 45)

    dates = []

    for i in range(30):
        english_date = (start_date + timedelta(days=i)).strftime("%d %B %Y")

        sehri_time = (base_sehri - timedelta(minutes=i)).strftime("%I:%M %p")
        iftar_time = (base_iftar + timedelta(minutes=i)).strftime("%I:%M %p")

        dates.append((i+1, english_date, sehri_time, iftar_time))

    return render_template(
        "index.html",
        today=today,
        quote=random_quote,
        messages=messages,
        dates=dates
    )

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get("name")
    message = request.form.get("message")

    if name and message:
        new_message = Message(name=name, message=message)
        db.session.add(new_message)
        db.session.commit()

    return redirect(url_for('home'))

# ======================
# LOGIN
# ======================

from flask import flash

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Successful ✅", "success")
            return redirect(url_for("admin"))
        else:
            flash("Invalid Username or Password ❌", "danger")

    return render_template("login.html")

@app.route('/admin')
@login_required
def admin():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template("admin.html", messages=messages)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    msg = Message.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    return redirect(url_for("admin"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# ======================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()



        # Create default admin if not exists
        if not User.query.filter_by(username="admin").first():
            admin = User(
    username="admin",
    password=generate_password_hash("khanadmin123")
)
            db.session.add(admin)
            db.session.commit()

    app.run(host="0.0.0.0", debug=True)

# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()

#         # UPDATE PASSWORD (Temporary)
#         user = User.query.filter_by(username="admin").first()
#         if user:
#             user.password = "khanadmin123" 
#             db.session.commit()
#             print("Password Updated Successfully")

#     app.run(host="0.0.0.0", debug=True)