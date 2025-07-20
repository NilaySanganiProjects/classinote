from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pickle
import json
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Data Models ---
class NoteIn(BaseModel):
    note: str

class FeedbackIn(BaseModel):
    note: str
    correct_label: str

class NoteEditIn(BaseModel):
    note: str

# --- Load Model and Data ---
def load_vectorizer():
    with open("vectorizer.pkl", "rb") as f:
        return pickle.load(f)

def load_classifier():
    with open("classifier.pkl", "rb") as f:
        return pickle.load(f)

def load_categories():
    if os.path.exists("categories.json"):
        with open("categories.json", "r") as f:
            return [cat.lower() for cat in json.load(f)]
    else:
        return ["todo", "study", "ideas"]

def save_categories(categories):
    with open("categories.json", "w") as f:
        json.dump(sorted(list(set(categories))), f, indent=4)

def save_note_to_category_file(note, category):
    os.makedirs("notes", exist_ok=True)
    file_path = os.path.join("notes", f"{category}.json")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r") as f:
            try:
                notes = json.load(f)
            except json.JSONDecodeError:
                notes = []
    else:
        notes = []
    notes.append(note)
    with open(file_path, "w") as f:
        json.dump(notes, f, indent=4)

def load_notes(category):
    file_path = os.path.join("notes", f"{category}.json")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_notes(category, notes):
    file_path = os.path.join("notes", f"{category}.json")
    with open(file_path, "w") as f:
        json.dump(notes, f, indent=4)

def retrain_model_from_feedback():
    with open("feedback.json", "r") as f:
        feedback_data = json.load(f)
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
    all_texts = [note for note, label in original_data]
    all_labels = [label for note, label in original_data]
    for item in feedback_data:
        all_texts.append(item["note"])
        all_labels.append(item["label"])
    new_vectorizer = TfidfVectorizer()
    X = new_vectorizer.fit_transform(all_texts)
    new_clf = MultinomialNB()
    new_clf.fit(X, all_labels)
    with open("vectorizer.pkl", "wb") as f:
        pickle.dump(new_vectorizer, f)
    with open("classifier.pkl", "wb") as f:
        pickle.dump(new_clf, f)

# --- API Endpoints ---
@app.post("/classify")
def classify_note(note_in: NoteIn):
    vectorizer = load_vectorizer()
    clf = load_classifier()
    X_new = vectorizer.transform([note_in.note])
    predicted_category = clf.predict(X_new)[0].lower()
    return {"predicted_category": predicted_category}

@app.post("/feedback")
def feedback(feedback_in: FeedbackIn):
    valid_categories = load_categories()
    correct_label = feedback_in.correct_label.strip().lower()
    if correct_label == "reminders":
        correct_label = "todo"
    if not re.match(r"^[a-z]+$", correct_label):
        raise HTTPException(status_code=400, detail="Invalid category format.")
    if correct_label not in valid_categories:
        valid_categories.append(correct_label)
        save_categories(valid_categories)
    feedback_entry = {"note": feedback_in.note, "label": correct_label}
    feedback_data = []
    if os.path.exists("feedback.json") and os.path.getsize("feedback.json") > 0:
        with open("feedback.json", "r") as f:
            try:
                feedback_data = json.load(f)
            except json.JSONDecodeError:
                feedback_data = []
    feedback_data.append(feedback_entry)
    with open("feedback.json", "w") as f:
        json.dump(feedback_data, f, indent=4)
    save_note_to_category_file(feedback_in.note, correct_label)
    # Retrain if needed
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
        retrain_model_from_feedback()
        with open(retrain_marker_file, "w") as f:
            json.dump({"last_retrained_on": next_threshold}, f)
    return {"message": "Feedback saved."}

@app.get("/categories")
def get_categories():
    return {"categories": load_categories()}

@app.get("/notes/{category}")
def get_notes(category: str):
    notes = load_notes(category)
    return {"notes": notes}

@app.post("/notes/{category}")
def add_note(category: str, note_in: NoteIn):
    save_note_to_category_file(note_in.note, category)
    return {"message": "Note added."}

@app.put("/notes/{category}/{index}")
def edit_note(category: str, index: int, note_edit: NoteEditIn):
    notes = load_notes(category)
    if not (0 <= index < len(notes)):
        raise HTTPException(status_code=404, detail="Note not found.")
    notes[index] = note_edit.note
    save_notes(category, notes)
    return {"message": "Note updated."}

@app.delete("/notes/{category}/{index}")
def delete_note(category: str, index: int):
    notes = load_notes(category)
    if not (0 <= index < len(notes)):
        raise HTTPException(status_code=404, detail="Note not found.")
    notes.pop(index)
    save_notes(category, notes)
    return {"message": "Note deleted."} 