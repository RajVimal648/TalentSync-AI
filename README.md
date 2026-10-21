# TalentSync AI

> **Intelligent Resume Compatibility & Career Fit Platform**  
> An enterprise-grade, explainable NLP platform that evaluates candidate resumes against target job descriptions, pinpoints critical skill gaps, and generates actionable ATS optimization roadmaps.

---

## 🎯 Overview

**TalentSync AI** is a modern, full-stack application built with **Python Flask** and an explainable **TF-IDF NLP Vector Matching Engine**. TalentSync AI provides mathematical transparency, deterministic scoring, and clear diagnostics to help job seekers and hiring teams audit resume parseability and role alignment.

---

## ✨ Key Capabilities

- **PDF Ingestion & Text Parsing:** Server-side parsing with `pypdf` plus client-side PDF.js fallback.
- **Explainable TF-IDF NLP Engine:** Deterministic semantic vector similarity:
  $$\text{Cosine Similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$
- **Weighted ATS Scoring Formula:**
  $$\text{Final ATS Score} = (\text{TF-IDF Cosine Similarity} \times 70\%) + (\text{Section Completeness} \times 30\%)$$
- **Skill Extraction & Gap Detection:** Identifies matching technical competencies and highlights missing target skills.
- **Roadmap to 80%+ ATS Benchmark:** Clear, prioritized checklist for keywords, quantifiable impact metrics, and structural formatting.
- **Clean, Minimalist UI:** Built with a modern, flat aesthetic using clean typography, refined borders, and zero clutter.
- **Visual Analytics:** Chart.js doughnut score distribution gauge and bar charts for top TF-IDF keyword weights.
- **Supabase Cloud Database & SQLite:** Seamlessly integrates with **Supabase (PostgreSQL)** cloud database via PostgREST, with automatic local SQLite fallback.
- **Secure Authentication:** User registration and sign-in with salted PBKDF2/SHA-256 password hashing (`werkzeug.security`).

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask 3.1, Werkzeug
- **NLP & Parsing:** TF-IDF Cosine Similarity, PyPDF, Regex Tokenization
- **Database:** Supabase (PostgreSQL) via `supabase-py` & SQLite fallback
- **Frontend:** Jinja2 Templates, HTML5, Tailwind CSS, JavaScript (ES6+), Chart.js

---

## 📁 Project Structure

```text
AI-Resume-Analyser/
├── app.py                      # Flask application factory, routing & REST APIs
├── resume_engine.py            # Explainable NLP engine, TF-IDF matcher & PDF extractor
├── database.py                 # Hybrid database manager (Supabase + SQLite fallback)
├── supabase_schema.sql         # Supabase PostgreSQL schema with RLS & indexes
├── database.sql                # Relational MySQL schema script
├── requirements.txt            # Python dependencies (Flask, pypdf, supabase, etc.)
├── test_app.py                 # Automated unit test suite
├── .env.example                # Environment variables template
├── templates/
│   └── index.html              # Clean modern Jinja2 UI template
├── static/
│   ├── css/
│   │   └── styles.css          # Clean minimalist layout & print styling
│   └── js/                     # Static scripts
└── uploads/                    # PDF upload staging directory
```

---

## ⚡ Supabase Setup (3 Quick Steps)

### Step 1: Create Tables in Supabase
1. Open your project on [Supabase Dashboard](https://supabase.com/dashboard).
2. Go to **SQL Editor** in the left sidebar.
3. Paste the contents of [`supabase_schema.sql`](file:///c:/Users/Admin/Desktop/Github%20AI/AI-Resume-Analyser/supabase_schema.sql) and click **Run**.

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your Supabase credentials (found in **Project Settings -> API**):
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```

### Step 3: Run the Application
```bash
python app.py
```
TalentSync will automatically detect your Supabase credentials and use Supabase for all users, resumes, and scan history. *(If credentials are not provided, it safely uses the built-in SQLite database).*

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python app.py
```
Visit **`http://127.0.0.1:5000/`** in your browser.

### 3. Run Unit Tests
```bash
python test_app.py
```

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the main application dashboard |
| `POST` | `/api/upload-pdf` | Extracts raw text from an uploaded resume PDF |
| `POST` | `/api/analyze` | Analyzes compatibility, calculates ATS score, and stores scan |
| `GET` | `/api/roles` | Retrieves preset job roles and skills taxonomy |
| `GET` | `/api/history` | Fetches historical scans |
| `DELETE`| `/api/history` | Clears historical scans |
| `DELETE`| `/api/history/<id>`| Deletes a single scan record |
| `POST` | `/api/auth/register`| Registers new user with hashed password |
| `POST` | `/api/auth/login` | Authenticates existing user session |
| `POST` | `/api/auth/logout` | Clears user session |
| `GET` | `/api/auth/current-user`| Returns current logged-in user profile |

---

Made by **Raj**
