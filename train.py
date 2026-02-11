# ================================
# Spam Email Classifier - Training
# (Optimized for High Accuracy)
# ================================

print("[*] Training started")

import pandas as pd
import pickle
import re
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from scipy.sparse import hstack, csr_matrix

# ----------------
# Text Processing (Enhanced)
# ----------------
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

# ----------------
# Load Dataset
# ----------------
print("[*] Loading dataset...")
df = pd.read_csv("spam.csv", encoding="latin-1")

df = df[['v1', 'v2']]
df.columns = ['label', 'text']
df['label'] = df['label'].map({'ham': 0, 'spam': 1})

# Drop duplicates for cleaner training
df = df.drop_duplicates(subset='text', keep='first')
print(f"    Dataset: {len(df)} messages ({df['label'].sum()} spam, {(df['label']==0).sum()} ham)")

# ----------------
# Feature Engineering
# ----------------
print("[*] Processing text & extracting features...")
df['transformed_text'] = df['text'].apply(transform_text)

# Extra hand-crafted features that help detect spam
df['text_len'] = df['text'].apply(len)
df['has_url'] = df['text'].apply(lambda x: 1 if re.search(r"http|www|\.com", str(x).lower()) else 0)
df['has_phone'] = df['text'].apply(lambda x: 1 if re.search(r"\d{5,}", str(x)) else 0)
df['has_spam_words'] = df['text'].apply(lambda x: 1 if re.search(r"free|win|prize|cash|claim", str(x).lower()) else 0)
df['upper_ratio'] = df['text'].apply(lambda x: sum(1 for c in str(x) if c.isupper()) / max(len(str(x)), 1))
df['exclaim_count'] = df['text'].apply(lambda x: str(x).count('!'))

# ----------------
# Vectorization (Optimized)
# ----------------
print("[*] Vectorizing...")
tfidf = TfidfVectorizer(
    max_features=8000,
    ngram_range=(1, 3),
    stop_words="english",
    min_df=2,
    max_df=0.95,
    sublinear_tf=True,
    strip_accents='unicode',
)

X_tfidf = tfidf.fit_transform(df['transformed_text'])

# Combine TF-IDF with extra features
extra_features = df[['text_len', 'has_url', 'has_phone', 'has_spam_words', 'upper_ratio', 'exclaim_count']].values
scaler = StandardScaler()
extra_scaled = scaler.fit_transform(extra_features)
extra_sparse = csr_matrix(extra_scaled)
X = hstack([X_tfidf, extra_sparse])

y = df['label']
tfidf_count = X_tfidf.shape[1]

# ----------------
# Train / Test Split (stratified)
# ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ----------------
# Train Multiple Models
# ----------------
print("[*] Training models...")

# 1. Naive Bayes (TF-IDF features only - can't handle negatives)
nb = MultinomialNB(alpha=0.05)
nb.fit(X_train[:, :tfidf_count], y_train)
nb_pred = nb.predict(X_test[:, :tfidf_count])
print(f"    Naive Bayes accuracy:          {accuracy_score(y_test, nb_pred):.4f}")

# 2. SVM on full features
svm = CalibratedClassifierCV(LinearSVC(C=1.0, max_iter=10000, class_weight='balanced'), cv=3)
svm.fit(X_train, y_train)
svm_pred = svm.predict(X_test)
print(f"    SVM accuracy:                  {accuracy_score(y_test, svm_pred):.4f}")

# 3. Logistic Regression on full features
lr = LogisticRegression(C=5.0, max_iter=5000, solver='lbfgs', class_weight='balanced')
lr.fit(X_train, y_train)
lr_pred = lr.predict(X_test)
print(f"    Logistic Regression accuracy:  {accuracy_score(y_test, lr_pred):.4f}")

# ----------------
# Ensemble (Majority Voting)
# ----------------
nb_pred_full = nb.predict(X_test[:, :tfidf_count])
ensemble_pred = np.array([
    int(round((nb_pred_full[i] + svm_pred[i] + lr_pred[i]) / 3))
    for i in range(len(y_test))
])

ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
print(f"\n    => Ensemble Accuracy: {ensemble_accuracy:.4f}")

# ----------------
# Cross-Validation
# ----------------
print("\n[*] Cross-validation (Logistic Regression)...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(
    LogisticRegression(C=5.0, max_iter=5000, solver='lbfgs', class_weight='balanced'),
    X, y, cv=cv, scoring='accuracy'
)
print(f"    CV Scores: {cv_scores}")
print(f"    CV Mean:   {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

# ----------------
# Detailed Evaluation
# ----------------
print("\n[*] Classification Report (Ensemble):")
print(classification_report(y_test, ensemble_pred, target_names=["Ham", "Spam"]))

cm = confusion_matrix(y_test, ensemble_pred)
print("[*] Confusion Matrix:")
print(f"    True Negatives:  {cm[0][0]}")
print(f"    False Positives: {cm[0][1]}")
print(f"    False Negatives: {cm[1][0]}")
print(f"    True Positives:  {cm[1][1]}")

# Pick best
scores = {
    'nb': accuracy_score(y_test, nb_pred),
    'svm': accuracy_score(y_test, svm_pred),
    'lr': accuracy_score(y_test, lr_pred),
    'ensemble': ensemble_accuracy
}
best_name = max(scores, key=scores.get)
print(f"\n[+] Best model: {best_name} ({scores[best_name]:.4f})")

# ----------------
# Save Model and Artifacts
# ----------------
print("\n[*] Saving model files...")

artifacts = {
    'nb_model': nb,
    'svm_model': svm,
    'lr_model': lr,
    'scaler': scaler,
    'best_model': best_name,
    'tfidf_feature_count': tfidf_count,
}

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(tfidf, f)

with open("model.pkl", "wb") as f:
    pickle.dump(artifacts, f)

print("[+] Training complete!")
print("[+] Files saved: model.pkl, vectorizer.pkl")
print(f"[+] Best accuracy: {scores[best_name]:.4f}")
