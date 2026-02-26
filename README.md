# 🚀 RECRUITER ATS DASHBOARD  
### AI-Powered Resume Screening & Candidate Ranking System

An intelligent Applicant Tracking System (ATS) built using Python 3.11 and Streamlit that parses resumes, analyzes job descriptions, detects job roles across multiple domains, and ranks candidates using a weighted scoring engine based on skills, experience, and education.

---

## 📌 FEATURES

### 📄 Resume Parsing

- Extracts Name, Email, Phone
- Extracts Technical & Soft Skills
- Detects Experience (in years)
- Detects Education Level
- Supports PDF resumes
- Optimized using LRU caching for performance

---

### 🧠 Smart Job Description Analysis

- Paste any Job Description
- Automatically detects best matching job role
- Detects domain (Technology, Finance, Legal, Healthcare, etc.)
- Detects required education & experience
- Lock / Edit JD workflow (simulates real ATS behavior)

---

### 🌍 Multi-Domain Role Inference

Supports 10+ professional domains:

- Technology
- Finance
- Healthcare
- Legal
- Education
- Engineering
- Management
- HR
- Sales & Marketing
- Design

Includes domain calibration logic for improved ranking accuracy.

---

### ⚖️ Weighted Scoring Engine

Candidates are ranked using:

- Critical Skills (Highest weight)
- Core Skills
- Optional Skills
- Soft Skills
- Experience validation
- Education matching
- Role discriminators (Hard + Soft gates)
- Domain calibration logic

---

### 📊 Recruiter Dashboard

- Ranked candidate cards
- Adjustable shortlist threshold
- Skill gap analysis
- Fit & rejection reasoning
- Alternative role comparison

#### Confidence Bands

- 🟢 Strong Fit
- 🔵 Good Fit
- 🟡 Borderline
- 🔴 Weak Fit

---

### 📤 Export Options

- CSV Export
- Excel (.xlsx) Export

🟢 Green rows = Shortlisted  
🔴 Red rows = Rejected  

---

## 🏗️ SYSTEM ARCHITECTURE

```
Resume Upload
      ↓
Resume Parser
      ↓
Job Description
      ↓
JD Profiler → Role Detection
      ↓
Weighted Skill Matching Engine
      ↓
Ranking & Confidence Scoring
      ↓
Recruiter Dashboard + CSV / Excel Export
```

---

## 📂 PROJECT STRUCTURE

```
Resume_Project/

│── app.py
│
├── resume_parser/
├── job_profile/
├── ranking/
├── matching/
├── analysis/
├── utils/
├── job_database/
├── feedback/
│
├── output/
└── debug_inference.py
```

---

## 🛠️ TECH STACK

- Python 3.11
- Streamlit
- NumPy
- OpenPyXL
- Custom NLP utilities
- Rule-based domain inference
- LRU caching for performance optimization

---

## ▶️ HOW TO RUN LOCALLY

### 1️⃣ Clone Repository

```
git clone (https://github.com/PradyumKarale/Recruiter-ATS-Dashboard-Python-Streamlit-NLP.git)
cd Recruiter-ATS-Dashboard-Python-Streamlit-NLP
```

### 2️⃣ Create Virtual Environment

```
python -m venv .venv
.venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.lock.txt
```

### 4️⃣ Run Application

```
streamlit run app.py
```

---

## 🔄 WORKFLOW

1. Upload one or more resumes (PDF)
2. Paste Job Description
3. Lock Job Description
4. View ranked candidates
5. Download CSV or Excel report

---

## 📈 EXAMPLE OUTPUT

```
Rank 1 → Strong Fit (82%)
Rank 2 → Good Fit (73%)
Rank 3 → Weak Fit (41%)
```

---

### Each Candidate Includes

- Matched Skills
- Missing Skills
- Education Match
- Experience Validation
- Alternative Role Comparison
- Recruiter Feedback

---

## 🧠 ENGINEERING HIGHLIGHTS

- Multi-domain rule-based job inference
- Weighted normalized scoring system
- Hard skill gate discriminators
- Education-level validation engine
- Experience-based calibration
- Domain confidence scaling
- Resume–role comparison reasoning
- Structured recruiter-friendly exports
- Modular architecture for scalability

---

## 🚀 FUTURE IMPROVEMENTS

- ML-based semantic similarity scoring
- Resume embeddings (BERT / Sentence Transformers)
- Database integration (PostgreSQL)
- Recruiter login system
- Cloud deployment (Streamlit Cloud / Render)
- REST API version

---

## 👨‍💻 AUTHOR

Pradyum Karale  
B.Tech Computer Science & Engineering  
MIT World Peace University, Pune  

GitHub: https://github.com/PradyumKarale
