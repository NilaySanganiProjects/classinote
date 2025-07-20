#classify.py
import pickle
import json
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Load the trained vectorizer and classifier
with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("classifier.pkl", "rb") as f:
    clf = pickle.load(f)

# Load or create the list of valid categories (lowercase only)
if os.path.exists("categories.json"):
    with open("categories.json", "r") as f:
        valid_categories = [cat.lower() for cat in json.load(f)]
else:
    valid_categories = ["todo", "study", "ideas"]
    with open("categories.json", "w") as f:
        json.dump(valid_categories, f, indent=4)

def save_note_to_category_file(note, category):
    os.makedirs("notes", exist_ok=True)
    file_path = os.path.join("notes", f"{category}.json")

    # Load existing notes if the file exists
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r") as f:
            try:
                notes = json.load(f)
            except json.JSONDecodeError:
                notes = []
    else:
        notes = []

    # Append and save
    notes.append(note)
    with open(file_path, "w") as f:
        json.dump(notes, f, indent=4)

def retrain_model_from_feedback():
    """Retrain the model using feedback data"""
    # Load feedback data
    with open("feedback.json", "r") as f:
        feedback_data = json.load(f)
    
    # Add original training data to maintain base knowledge
    original_data = [
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
    
    # Combine original data with feedback data
    all_texts = [note for note, label in original_data]
    all_labels = [label for note, label in original_data]
    
    # Add feedback data
    for item in feedback_data:
        all_texts.append(item["note"])
        all_labels.append(item["label"])
    
    # Retrain the model
    new_vectorizer = TfidfVectorizer()
    X = new_vectorizer.fit_transform(all_texts)
    
    new_clf = MultinomialNB()
    new_clf.fit(X, all_labels)
    
    # Save the retrained models
    with open("vectorizer.pkl", "wb") as f:
        pickle.dump(new_vectorizer, f)
    
    with open("classifier.pkl", "wb") as f:
        pickle.dump(new_clf, f)
    
    # Update global variables for immediate use
    global vectorizer, clf
    vectorizer = new_vectorizer
    clf = new_clf

# Take user input
note = input("📝 Enter a note: ")

# Vectorize and predict
X_new = vectorizer.transform([note])
predicted_category = clf.predict(X_new)[0].lower()

print(f"✅ This note is classified as: {predicted_category}")

# Ask for feedback
feedback = input("Is this correct? (y/n): ").strip().lower()

if feedback == 'n':
    while True:
        correct_label = input("Enter the correct category (one word, only lowercase letters): ").strip().lower()

        # 🔁 If user enters 'reminders', treat it as 'todo'
        if correct_label == "reminders":
            print("🔁 Treating 'reminders' as 'todo'.")
            correct_label = "todo"

        if not re.match(r"^[a-z]+$", correct_label):
            print("⚠️ Invalid category! Must be a single lowercase word with only letters (no spaces, hyphens, or symbols).")
            continue
        break

    # Add to categories if new
    if correct_label not in valid_categories:
        confirm = input(f"'{correct_label}' is a new category. Add it? (y/n): ").strip().lower()
        if confirm == 'y':
            valid_categories.append(correct_label)
            with open("categories.json", "w") as f:
                json.dump(sorted(list(set(valid_categories))), f, indent=4)
            print(f"🆕 Category '{correct_label}' added to categories.json.")
        else:
            print("❌ Feedback cancelled. Category not saved.")
            exit()
    
    # Save feedback
    feedback_entry = {"note": note, "label": correct_label}

    # Safely load feedback data
    feedback_data = []
    if os.path.exists("feedback.json") and os.path.getsize("feedback.json") > 0:
        with open("feedback.json", "r") as f:
            try:
                feedback_data = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Warning: feedback.json is empty or corrupted. Starting fresh.")
                feedback_data = []

    feedback_data.append(feedback_entry)

    with open("feedback.json", "w") as f:
        json.dump(feedback_data, f, indent=4)

    print("✅ Feedback saved in feedback.json. Thank you!")

    # Also save to the notes/ folder
    save_note_to_category_file(note, correct_label)

    # 🔁 Auto-retrain logic
    THRESHOLD = 5
    retrain_marker_file = ".retrain_marker.json"

    if os.path.exists(retrain_marker_file):
        with open(retrain_marker_file, "r") as f:
            last_marker = json.load(f).get("last_retrained_on", 0)
    else:
        last_marker = 0

    current_feedback_count = len(feedback_data)
    next_threshold = (current_feedback_count // THRESHOLD) * THRESHOLD

    if current_feedback_count >= THRESHOLD and next_threshold > last_marker:
        print("🔁 Feedback threshold reached. Retraining the model...")
        retrain_model_from_feedback()
        with open(retrain_marker_file, "w") as f:
            json.dump({"last_retrained_on": next_threshold}, f)
        print(f"✅ Model retrained at {next_threshold} feedback entries!")

elif feedback == 'y':
    print("🎉 Awesome! Glad I got it right.")
    save_note_to_category_file(note, predicted_category)
else:
    print("⚠️ Invalid input. Skipping feedback.")