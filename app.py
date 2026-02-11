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
app.secret_key = os.getenv("SECRET_KEY", "change_this_secret_key_in_production")

# ----------------------
# Load ML Artifacts
# ----------------------
import numpy as np
from scipy.sparse import hstack, csr_matrix

with open("vectorizer.pkl", "rb") as f:
    tfidf = pickle.load(f)

with open("model.pkl", "rb") as f:
    artifacts = pickle.load(f)

nb_model = artifacts['nb_model']
svm_model = artifacts['svm_model']
lr_model = artifacts['lr_model']
scaler = artifacts['scaler']
best_model_name = artifacts['best_model']
tfidf_feature_count = artifacts['tfidf_feature_count']

# ----------------------
# Text Processing
# MUST MATCH train.py
# ----------------------
def transform_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|https\S+", " urllink ", text)
    text = re.sub(r"\S+@\S+", " emailaddr ", text)
    text = re.sub(r"\b\d{10,}\b", " phonenumber ", text)
    text = re.sub(r"\b\d{4,5}[-\s]?\d{5,6}\b", " phonenumber ", text)
    text = re.sub(r"\b\d+\b", " number ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_extra_features(raw_text):
    """Extract the same extra features used during training."""
    text_len = len(raw_text)
    has_url = 1 if re.search(r"http|www|\.com", raw_text.lower()) else 0
    has_phone = 1 if re.search(r"\d{5,}", raw_text) else 0
    has_spam_words = 1 if re.search(r"free|win|prize|cash|claim", raw_text.lower()) else 0
    upper_ratio = sum(1 for c in raw_text if c.isupper()) / max(len(raw_text), 1)
    exclaim_count = raw_text.count('!')
    return [[text_len, has_url, has_phone, has_spam_words, upper_ratio, exclaim_count]]

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
    tfidf_vector = tfidf.transform([processed])

    # Build extra features (same as training)
    extra = extract_extra_features(message)
    extra_scaled = scaler.transform(extra)
    extra_sparse = csr_matrix(extra_scaled)
    full_vector = hstack([tfidf_vector, extra_sparse])

    # Ensemble prediction (majority vote of NB + SVM + LR)
    nb_pred = nb_model.predict(tfidf_vector)[0]
    svm_pred = svm_model.predict(full_vector)[0]
    lr_pred = lr_model.predict(full_vector)[0]
    result = int(round((nb_pred + svm_pred + lr_pred) / 3))

    # Get confidence from LR (supports predict_proba)
    lr_proba = lr_model.predict_proba(full_vector)[0]
    confidence = max(lr_proba) * 100

    prediction = "Spam" if result == 1 else "Not Spam"
    return render_template("result.html", prediction=prediction, confidence=f"{confidence:.1f}%")

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
    # Use environment variable for port (required by most hosting platforms)
    port = int(os.getenv("PORT", 5050))
    # Only enable debug in development
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
