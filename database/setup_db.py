import sqlite3, os, csv, io, re, urllib.request

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

DATASET_URL = "https://raw.githubusercontent.com/PlayingNumbers/ds_salary_proj/master/glassdoor_jobs.csv"

# Skill keywords to extract from descriptions
SKILL_KEYWORDS = [
    "python","r","sql","java","scala","c++","c#","javascript","typescript",
    "machine learning","deep learning","tensorflow","pytorch","keras","sklearn",
    "pandas","numpy","spark","hadoop","hive","kafka","airflow","dbt",
    "aws","azure","gcp","docker","kubernetes","terraform","linux","git",
    "tableau","power bi","excel","looker","matplotlib","seaborn","plotly",
    "nlp","computer vision","statistics","probability","a/b testing",
    "flask","django","fastapi","react","node","mongodb","postgresql","mysql",
    "scikit-learn","xgboost","lightgbm","bert","transformers","opencv",
    "data analysis","data engineering","data visualization","etl","api",
]

def extract_skills(description):
    desc_lower = description.lower()
    found = [s for s in SKILL_KEYWORDS if s in desc_lower]
    return " ".join(found[:15]) if found else "data analysis python sql"

def clean_salary(sal):
    if not sal or sal == "-1": return None
    # "$53K-$91K (Glassdoor est.)" → "53K-91K"
    sal = re.sub(r'\(.*?\)', '', sal).strip()
    sal = sal.replace("$","").replace(" ","")
    return sal if sal else None

def sector_to_category(sector):
    mapping = {
        "Information Technology": "Software Development",
        "Finance": "Finance & Banking",
        "Health Care": "Healthcare",
        "Biotech & Pharmaceuticals": "Healthcare",
        "Education": "Education",
        "Retail": "Retail & E-commerce",
        "Manufacturing": "Manufacturing",
        "Insurance": "Finance & Banking",
        "Media": "Media & Marketing",
        "Aerospace & Defense": "Engineering",
        "Oil, Gas, Energy & Utilities": "Engineering",
        "Real Estate": "Business & Management",
        "Transportation & Logistics": "Operations",
        "Business Services": "Business & Management",
        "Government": "Government & Public Sector",
    }
    return mapping.get(sector, "Technology")

def get_experience(title):
    title_l = title.lower()
    if any(x in title_l for x in ["senior","sr.","lead","principal","staff","director","vp","head"]):
        return "5+ years"
    elif any(x in title_l for x in ["junior","jr","entry","associate","intern","i "," i,"]):
        return "0-2 years"
    elif any(x in title_l for x in [" ii "," iii ","manager","mid"]):
        return "3-5 years"
    return "2-4 years"

def create_database():
    print("Downloading real jobs dataset from GitHub...")
    try:
        req = urllib.request.Request(DATASET_URL, headers={"User-Agent":"Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=15).read().decode("utf-8","ignore")
        reader = csv.DictReader(io.StringIO(raw))
        rows = [r for r in reader if r.get("Job Title","").strip() and r.get("Job Description","").strip()]
        print(f"Downloaded {len(rows)} job records.")
        use_online = True
    except Exception as e:
        print(f"Could not download dataset ({e}), using built-in records.")
        use_online = False
        rows = []

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        DROP TABLE IF EXISTS jobs;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS applications;

        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT DEFAULT 'Full-time',
            experience TEXT NOT NULL,
            salary TEXT,
            description TEXT NOT NULL,
            skills TEXT NOT NULL,
            category TEXT NOT NULL,
            rating REAL DEFAULT 0,
            posted_date TEXT DEFAULT (date('now'))
        );

        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            skills TEXT,
            experience TEXT,
            education TEXT,
            preferred_location TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            job_id INTEGER,
            applied_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        );
    """)

    if use_online:
        jobs = []
        seen = set()
        for r in rows:
            title = r["Job Title"].strip()
            company = r["Company Name"].strip().split("\n")[0].strip()
            location = r["Location"].strip()
            desc = r["Job Description"].strip()[:800]
            salary = clean_salary(r.get("Salary Estimate",""))
            sector = r.get("Sector","Technology").strip()
            rating = float(r.get("Rating", 0) or 0)
            key = (title.lower(), company.lower())
            if key in seen: continue
            seen.add(key)
            jobs.append((
                title, company if company else "Company",
                location if location else "USA",
                "Full-time", get_experience(title),
                salary, desc,
                extract_skills(desc),
                sector_to_category(sector),
                round(rating, 1)
            ))

        c.executemany("""
            INSERT INTO jobs (title,company,location,job_type,experience,salary,description,skills,category,rating)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, jobs)
        print(f"Inserted {len(jobs)} unique jobs into database.")
    else:
        # Fallback built-in records
        fallback = [
            ("Python Developer","TechSoft Pvt Ltd","Bangalore","Full-time","1-3 years","5-8 LPA",
             "Build REST APIs and data pipelines using Flask and SQLAlchemy.",
             "python flask rest api sql git linux","Software Development",4.2),
            ("Machine Learning Engineer","DataMinds AI","Hyderabad","Full-time","2-4 years","10-15 LPA",
             "Build and deploy ML models using PyTorch and TensorFlow.",
             "machine learning python tensorflow pytorch sklearn nlp","Data Science & AI",4.5),
            ("Data Analyst","Analytics Corp","Mumbai","Full-time","0-2 years","4-6 LPA",
             "Analyze datasets to extract insights. Build dashboards using Tableau.",
             "sql excel python data analysis tableau statistics","Data Science & AI",4.0),
            ("Full Stack Developer","Innovate Labs","Pune","Full-time","2-4 years","7-12 LPA",
             "Build full-stack web applications using Node.js and React.",
             "react nodejs javascript mongodb sql rest api docker git","Web Development",4.3),
            ("DevOps Engineer","CloudOps Inc","Chennai","Full-time","2-5 years","8-14 LPA",
             "Manage CI/CD pipelines and cloud infrastructure.",
             "docker kubernetes aws linux ci/cd jenkins terraform git","DevOps & Cloud",4.1),
        ]
        c.executemany("""
            INSERT INTO jobs (title,company,location,job_type,experience,salary,description,skills,category,rating)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, fallback)
        print(f"Inserted {len(fallback)} fallback jobs.")

    conn.commit()
    conn.close()
    total = len(jobs) if use_online else 5
    print(f"Database ready at {DB_PATH} with {total} jobs.")

if __name__ == "__main__":
    create_database()
