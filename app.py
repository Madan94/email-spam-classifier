from flask import Flask, render_template, request, redirect, url_for, session, flash
import pickle
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

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
# Database (Supabase)
# ----------------------
def get_db() -> Client:
    supabase_url = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
    supabase_key = os.getenv("SUPABASE_KEY", "your-anon-key")
    return create_client(supabase_url, supabase_key)

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

    supabase = get_db()
    try:
        # Insert new user
        response = supabase.table("users").insert({
            "full_name": full_name,
            "username": username,
            "email": email,
            "phone": phone,
            "password": password
        }).execute()
        
        if response.data:
            flash("Registration successful")
            return redirect(url_for("signin"))
        else:
            flash("Registration failed")
            return redirect(url_for("signup"))
    except Exception as e:
        # Check if it's a unique constraint violation
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            flash("User already exists")
        else:
            flash("Registration failed. Please try again.")
        return redirect(url_for("signup"))

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    supabase = get_db()
    try:
        # Query user by email and password
        response = supabase.table("users").select("id, email").eq("email", email).eq("password", password).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials")
            return redirect(url_for("signin"))
    except Exception:
        flash("Login failed. Please try again.")
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
