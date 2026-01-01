# ================================
# Spam Email Classifier - Training
# ================================

print("🚀 Training started")

import pandas as pd
import pickle
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ----------------
# Text Processing
# ----------------
def transform_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " url ", text)
    text = re.sub(r"\d+", " number ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text

# ----------------
# Load Dataset
# ----------------
print("📂 Loading dataset...")
df = pd.read_csv("spam.csv", encoding="latin-1")

df = df[['v1', 'v2']]
df.columns = ['label', 'text']
df['label'] = df['label'].map({'ham': 0, 'spam': 1})

print("🧠 Processing text...")
df['transformed_text'] = df['text'].apply(transform_text)

# ----------------
# Vectorization (KEY ACCURACY BOOST)
# ----------------
print("🔢 Vectorizing...")
tfidf = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    stop_words="english",
    min_df=2
)

X = tfidf.fit_transform(df['transformed_text'])
y = df['label']

# ----------------
# Train / Test Split
# ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ----------------
# Model Training
# ----------------
print("🤖 Training model...")
model = MultinomialNB(alpha=0.1)
model.fit(X_train, y_train)

# ----------------
# Evaluation
# ----------------
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"🎯 Accuracy: {accuracy:.4f}")

# ----------------
# Save Model
# ----------------
print("💾 Saving model files...")
with open("vectorizer.pkl", "wb") as f:
    pickle.dump(tfidf, f)

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Training complete")
print("📦 Files saved: model.pkl, vectorizer.pkl")
