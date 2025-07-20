#view_notes.py
import os
import json

def list_categories():
    if not os.path.exists("categories.json"):
        print("📭 No categories found.")
        return []

    with open("categories.json", "r") as f:
        return json.load(f)

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

def show_notes(category, notes):
    if not notes:
        print(f"📭 No notes in '{category}'.")
        return False

    print(f"\n🗂 Notes in '{category}':")
    for i, note in enumerate(notes, 1):
        print(f"{i}. {note}")
    print()
    return True

def edit_note(notes, index):
    old_note = notes[index]
    new_note = input(f"✏️ Enter new text for note {index+1}:\n> ").strip()
    if new_note:
        notes[index] = new_note
        print("✅ Note updated.")
    else:
        print("❌ Empty note. Skipping update.")

def delete_note(notes, index):
    print(f"🗑️ Deleting: {notes[index]}")
    confirm = input("Are you sure? (y/n): ").strip().lower()
    if confirm == 'y':
        notes.pop(index)
        print("✅ Note deleted.")
    else:
        print("❌ Deletion canceled.")

# Main app logic
if __name__ == "__main__":
    print("📚 Available Categories:")
    categories = list_categories()
    if not categories:
        exit()

    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")

    category = input("\nEnter category name to view/edit/delete notes: ").strip().lower()

    if category not in categories:
        print("❌ Invalid category name.")
        exit()

    notes = load_notes(category)

    if not show_notes(category, notes):
        exit()

    action = input("What do you want to do? [e]dit / [d]elete / [q]uit: ").strip().lower()

    if action not in ['e', 'd']:
        print("👋 Exiting.")
        exit()

    try:
        index = int(input("Enter the note number: ")) - 1
        if not (0 <= index < len(notes)):
            print("❌ Invalid note number.")
            exit()
    except ValueError:
        print("❌ Please enter a valid number.")
        exit()

    if action == 'e':
        edit_note(notes, index)
    elif action == 'd':
        delete_note(notes, index)

    save_notes(category, notes)
