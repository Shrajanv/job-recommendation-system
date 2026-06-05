# 💼 JobReco — AI-Powered Job Recommendation System

A machine learning based job recommendation system built with Python and Flask. Enter your skills and get personalized job matches ranked by relevance using TF-IDF and Cosine Similarity.

---

## 🖥️ Demo Pages

| Page | Description |
|------|-------------|
| `/` | Home — trending skills, categories, top-rated jobs |
| `/recommend` | AI recommendations based on your skills |
| `/jobs` | Browse & search all 950+ jobs |
| `/job/<id>` | Job detail with similar jobs |
| `/profile` | Save your profile for auto-recommendations |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask |
| ML Engine | Scikit-learn (TF-IDF + Cosine Similarity) |
| Database | SQLite |
| Dataset | Glassdoor Jobs (956 real records) |
| Frontend | HTML, CSS, JavaScript |

---

## 🧠 How the ML Works

```
User skills input
       ↓
TF-IDF Vectorization  →  converts text to numeric vectors
       ↓
Cosine Similarity     →  compares user vector vs all job vectors
       ↓
Ranked Results        →  top matches shown with % score
```

- **TF-IDF** gives higher weight to important/rare words in job descriptions
- **Cosine Similarity** measures the angle between two vectors (0% to 100% match)
- **Content-Based Filtering** — recommendations based on job content, not user history
- Model trains **once** and saves as `.pkl` — instant load on every restart after that

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.10 or above
- pip

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/job-recommendation-system.git
cd job-recommendation-system

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup database (downloads real dataset automatically)
python database/setup_db.py

# 6. Train the ML model
python model/recommender.py

# 7. Run the app
python app.py
```

Open browser → **http://127.0.0.1:5000**

> ⚠️ First run takes ~10 seconds to download the dataset and train the model. Every run after that is instant.

---

## 📁 Project Structure

```
job-recommendation-system/
├── app.py                  # Flask routes & main entry point
├── requirements.txt        # Python dependencies
├── run.bat                 # Windows one-click run
├── run.sh                  # Linux/Mac one-click run
├── .gitignore
│
├── database/
│   └── setup_db.py         # Downloads dataset & creates SQLite DB
│
├── model/
│   └── recommender.py      # TF-IDF ML engine (train + predict)
│
├── templates/
│   ├── base.html           # Navbar + footer layout
│   ├── index.html          # Home page
│   ├── recommend.html      # AI recommendations page
│   ├── jobs.html           # Browse & search jobs
│   ├── job_detail.html     # Single job view + similar jobs
│   └── profile.html        # User profile
│
└── static/
    ├── css/style.css       # All styles
    └── js/main.js          # Animations
```

---

## 📊 Dataset

- **Source:** [Glassdoor Jobs Dataset](https://github.com/PlayingNumbers/ds_salary_proj) — publicly available on GitHub
- **Records:** 956 real job postings
- **Fields used:** Job Title, Company, Location, Job Description, Salary, Rating, Sector
- Auto-downloaded on first run via `setup_db.py` — no manual download needed

---

## ✨ Features

- 🤖 AI-powered job recommendations using TF-IDF + Cosine Similarity
- 🔥 Trending skills section based on real market data
- ⭐ Company ratings from Glassdoor dataset
- 🔍 Search & filter jobs by title, location, category
- 👤 User profile — save skills for instant recommendations
- 📱 Responsive design — works on mobile and desktop
- ⚡ Fast — model loads from cache after first training

---

## 👨‍💻 Author

Made as part of MCA Final Year Project  
**[Your Name]** — [Your College Name]

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
