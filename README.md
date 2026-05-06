# 🕵️ PlagScan – Academic Plagiarism Detector
### Advanced Computer Programming (ACP) · 3C Model Project

> **Stack:** Python · Flask · SQLite · Pure Python NLP (no heavy dependencies)

---

## 🚀 Quick Start

```bash
pip install flask
python app.py
# Open → http://127.0.0.1:5000
```

---

## 🧠 NLP Techniques (Pure Python)

| Method | What it does | Weight |
|--------|-------------|--------|
| **TF-IDF Cosine** | Measures document-level vector similarity | 40% |
| **Jaccard Index** | Word-set overlap ratio | 25% |
| **3-gram Fingerprint** | Finds copied 3-word phrases | 20% |
| **2-gram Fingerprint** | Finds copied 2-word phrases | 15% |
| **Sentence Matching** | `difflib.SequenceMatcher` per sentence | Display |

---

## 📁 File Structure

```
plagiarism_detector/
├── app.py           Flask routes
├── database.py      SQLite setup + seeding
├── models.py        OOP: BaseModel, Document, CheckResult
├── nlp_engine.py    TextPreprocessor, TFIDFEngine, SimilarityMetrics, PlagiarismAnalyzer
├── templates/
│   ├── base.html    Dark forensic sidebar layout
│   ├── index.html   Dashboard + stats
│   ├── check.html   Submit documents (Direct / Vault mode)
│   ├── report.html  Full analysis report with highlights
│   ├── vault.html   Document library CRUD
│   └── history.html Past checks table
└── requirements.txt
```

---

## ✅ Features

- **Direct Compare** — paste two texts and get instant similarity analysis
- **Vault Mode** — compare submission against stored reference documents
- **Sentence Highlighting** — flagged sentences shown in red inline
- **Matched Phrases** — copied trigrams displayed as evidence chips
- **Risk Levels** — LOW / MEDIUM / HIGH / CRITICAL with color coding
- **History** — all past checks saved to SQLite with all metric scores

---

## 📚 OOP Concepts Demonstrated

```
BaseModel (Abstraction/Inheritance)
   ├── Document      → manages vault storage
   └── CheckResult   → persists check summaries

PlagiarismAnalyzer (Composition + Orchestration)
   ├── TextPreprocessor  → tokenize, split sentences
   ├── TFIDFEngine       → pure-Python TF-IDF cosine similarity
   └── SimilarityMetrics → jaccard, n-gram, sentence matching
```
