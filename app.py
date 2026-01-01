from flask import Flask, render_template, request, redirect, url_for, session, flash
import pickle
import mysql.connector
import re

# ----------------------
# App Setup
# ----------------------
app = Flask(__name__)
app.secret_key = "change_this_secret_key"

# ----------------------
# Load ML Artifacts
# ----------------------
with open("vectorizer.pkl", "rb") as f:
    tfidf = pickle.load(f)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# ----------------------
# Text Processing
# MUST MATCH train.py
# ----------------------
def transform_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " url ", text)
    text = re.sub(r"\d+", " number ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text

# ----------------------
# Database
# ----------------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="smc_user",
        password="Smc@1234",
        database="smc",
        auth_plugin="mysql_native_password"
    )

# ----------------------
# Routes
# ----------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/index")
def index():
    if "user_id" in session:
        return render_template("index.html")
    return redirect(url_for("signin"))

# ----------------------
# Prediction
# ----------------------
@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        return redirect(url_for("signin"))

    message = request.form.get("message")
    if not message:
        flash("Message cannot be empty")
        return redirect(url_for("index"))

    processed = transform_text(message)
    vector = tfidf.transform([processed])
    result = model.predict(vector)[0]

    prediction = "Spam" if result == 1 else "Not Spam"
    return render_template("result.html", prediction=prediction)

# ----------------------
# Auth
# ----------------------
@app.route("/signin")
def signin():
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("signin.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/register", methods=["POST"])
def register():
    full_name = request.form["full_name"]
    username = request.form["username"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    if password != confirm_password:
        flash("Passwords do not match")
        return redirect(url_for("signup"))

    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            """
            INSERT INTO users (full_name, username, email, phone, password)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (full_name, username, email, phone, password)
        )
        db.commit()
    except Exception:
        db.rollback()
        flash("User already exists")
        return redirect(url_for("signup"))
    finally:
        cur.close()
        db.close()

    flash("Registration successful")
    return redirect(url_for("signin"))

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, email FROM users WHERE email=%s AND password=%s",
        (email, password)
    )
    user = cur.fetchone()
    cur.close()
    db.close()

    if user:
        session["user_id"] = user[0]
        session["email"] = user[1]
        return redirect(url_for("index"))

    flash("Invalid credentials")
    return redirect(url_for("signin"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ----------------------
# Run
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
