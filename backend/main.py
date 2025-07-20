#main.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import json
import os
from collections import Counter

# 🔹 Step 1: Original training dataset (lowercase + cleaned)
dataset = [
    ("Buy milk and eggs", "todo"),
    ("Complete AI assignment", "study"),
    ("Call mom tomorrow", "todo"),
    ("Idea for startup: reusable notebook", "ideas"),
    ("Revise neural networks", "study"),
    ("Think about app for learning languages", "ideas"),
    ("Doctor appointment at 5 PM", "todo"),
    ("Prepare for viva exam", "study"),
    ("Plan trip to Ladakh", "ideas"),
]

# 🔹 Step 2: Load and clean feedback data
feedback_data = []

if os.path.exists("feedback.json") and os.path.getsize("feedback.json") > 0:
    with open("feedback.json", "r") as f:
        try:
            feedback_entries = json.load(f)
            for entry in feedback_entries:
                note = entry["note"]
                label = entry["label"].strip().lower()
                if label == "reminders":
                    label = "todo"
                feedback_data.append((note, label))
        except json.JSONDecodeError:
            print("⚠️ Warning: feedback.json is invalid or corrupted. Ignoring feedback.")
else:
    print("📭 No feedback data found. Starting with base dataset.")


# 🔹 Step 3: Combine datasets
full_dataset = dataset + feedback_data

# 🔹 Step 4: Update categories.json with new labels
all_labels = [label for note, label in full_dataset]
if os.path.exists("categories.json"):
    with open("categories.json", "r") as f:
        existing_categories = set([c.lower() for c in json.load(f)])
else:
    existing_categories = set()

new_categories = set(all_labels) - existing_categories
if new_categories:
    print(f"🆕 Adding new categories to categories.json: {new_categories}")
    existing_categories.update(new_categories)
    with open("categories.json", "w") as f:
        json.dump(sorted(list(existing_categories)), f, indent=4)

# 🔹 Step 5: Warn about undertrained categories
label_counts = Counter(all_labels)
for label, count in label_counts.items():
    if count < 3:
        print(f"⚠️ Warning: Category '{label}' has only {count} training example(s).")

# 🔹 Step 6: Train the model
texts = [note for note, label in full_dataset]
labels = all_labels

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

clf = MultinomialNB()
clf.fit(X, labels)

# 🔹 Step 7: Save the model
with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("classifier.pkl", "wb") as f:
    pickle.dump(clf, f)

print("✅ Model retrained and saved with feedback and category updates!")
