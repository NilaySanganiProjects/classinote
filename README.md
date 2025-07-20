# ClassiNote

A full-stack intelligent note-taking app with automatic note classification, feedback-driven learning, and a modern web UI.

---

## Features

- **Automatic Note Classification:**  
  Notes are categorized (e.g., todo, study, ideas, finance, etc.) using a machine learning model.
- **Feedback-Driven Learning:**  
  Users can correct misclassified notes, and the model retrains itself automatically after enough feedback.
- **Category Management:**  
  Categories are managed dynamically based on user feedback and training data.
- **View, Edit, Delete Notes:**  
  All notes are organized by category and can be edited or deleted.
- **Modern Web UI:**  
  Built with React and Material UI, featuring a sidebar for categories and a main area for note management.
- **CLI Tools:**  
  Includes Python scripts for command-line note classification and management.

---

## Project Structure

```
.
├── api.py                # FastAPI backend (main API server)
├── classify.py           # CLI note classifier
├── main.py               # Model (re)training script
├── view_notes.py         # CLI note viewing/editing
├── requirements.txt      # Python backend dependencies
├── categories.json       # List of categories
├── feedback.json         # User feedback for retraining
├── vectorizer.pkl        # Saved ML vectorizer
├── classifier.pkl        # Saved ML classifier
├── .retrain_marker.json  # Tracks retrain threshold
├── notes/                # Folder with notes per category (as JSON)
├── classinote-ui/        # React frontend app
│   ├── package.json      # Frontend dependencies
│   ├── src/
│   │   ├── App.js
│   │   ├── api.js
│   │   └── components/
│   │       ├── Sidebar.js
│   │       ├── AddNote.js
│   │       ├── NoteList.js
│   │       └── EditNoteDialog.js
│   └── ... (other React files)
└── ...
```

---

## Setup Instructions

### 1. Backend (Python/FastAPI)

**Requirements:** Python 3.8+, pip

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Train the initial model (if not already trained):**
   ```sh
   python main.py
   ```

3. **Run the API server:**
   ```sh
   uvicorn api:app --reload
   ```
   The API will be available at [http://localhost:8000](http://localhost:8000).

4. **(Optional) Use CLI tools:**
   - Classify a note:  
     `python classify.py`
   - View/edit notes:  
     `python view_notes.py`

---

### 2. Frontend (React)

**Requirements:** Node.js (v16+), npm

1. **Install dependencies:**
   ```sh
   cd classinote-ui
   npm install
   ```

2. **Start the development server:**
   ```sh
   npm start
   ```
   The app will open at [http://localhost:3000](http://localhost:3000).

---

### 3. Connecting Frontend and Backend

- The React app communicates with the FastAPI backend at `http://localhost:8000`.
- If you run both locally, everything should work out of the box.
- If you deploy or change ports, update the `API_BASE` in `classinote-ui/src/api.js`.

---

### 4. CORS Issues

If you get CORS errors, ensure your `api.py` includes:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Usage

- **Add a note:**  
  Enter your note in the UI, and it will be auto-categorized. Confirm or correct the category.
- **View notes:**  
  Select a category in the sidebar to view all notes in that category.
- **Edit/Delete notes:**  
  Use the edit and delete icons next to each note.
- **Feedback:**  
  If a note is misclassified, correct it and the model will learn over time.

---

## Data Files

- **notes/**: Each category has its own JSON file with notes.
- **categories.json**: List of all categories.
- **feedback.json**: Stores user feedback for retraining.
- **vectorizer.pkl/classifier.pkl**: Machine learning model files.

---

## Extending

- Add new categories by providing feedback with a new category name.
- The model retrains automatically after every 5 feedback entries.

---

## License

MIT (or your preferred license) 