import sqlite3, os, pickle, collections
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB_PATH  = os.path.join(os.path.dirname(__file__), "../database/jobs.db")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "tfidf_model.pkl")

def get_all_jobs():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    jobs = [dict(r) for r in conn.execute("SELECT * FROM jobs").fetchall()]
    conn.close()
    return jobs

def build_corpus(jobs):
    return [f"{j['title']} {j['description']} {j['skills']} {j['category']} {j['experience']}".lower()
            for j in jobs]

def train_model():
    print("Training TF-IDF model...")
    jobs = get_all_jobs()
    corpus = build_corpus(jobs)
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2),
                                  max_features=5000, min_df=2, sublinear_tf=True)
    matrix = vectorizer.fit_transform(corpus)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "jobs": jobs}, f)
    print(f"Model trained on {len(jobs)} jobs. Saved to {MODEL_PATH}")
    return vectorizer, matrix, jobs

def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            d = pickle.load(f)
        return d["vectorizer"], d["matrix"], d["jobs"]
    return train_model()

def recommend_jobs(user_skills, user_experience="", top_n=8):
    vectorizer, matrix, jobs = load_model()
    query = f"{user_skills} {user_experience}".lower().strip()
    if not query:
        return jobs[:top_n]
    vec = vectorizer.transform([query])
    scores = cosine_similarity(vec, matrix).flatten()
    top_idx = scores.argsort()[::-1][:top_n]
    results = []
    for i in top_idx:
        j = dict(jobs[i])
        j["score"] = round(float(scores[i]) * 100, 1)
        results.append(j)
    return results

def get_similar_jobs(job_id, top_n=4):
    vectorizer, matrix, jobs = load_model()
    idx = next((i for i,j in enumerate(jobs) if j["id"]==job_id), None)
    if idx is None: return []
    scores = cosine_similarity(matrix[idx], matrix).flatten()
    scores[idx] = 0
    top_idx = scores.argsort()[::-1][:top_n]
    results = []
    for i in top_idx:
        j = dict(jobs[i])
        j["score"] = round(float(scores[i])*100,1)
        results.append(j)
    return results

def get_trending_skills(top_n=12):
    """Count most frequent skills across all jobs."""
    jobs = get_all_jobs()
    counter = collections.Counter()
    for j in jobs:
        for skill in j["skills"].split():
            if len(skill) > 2:
                counter[skill.lower()] += 1
    return [{"skill": s, "count": c} for s,c in counter.most_common(top_n)]

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    cats  = c.execute("SELECT COUNT(DISTINCT category) FROM jobs").fetchone()[0]
    locs  = c.execute("SELECT COUNT(DISTINCT location) FROM jobs").fetchone()[0]
    top_cat = c.execute("SELECT category, COUNT(*) as n FROM jobs GROUP BY category ORDER BY n DESC LIMIT 1").fetchone()
    conn.close()
    return {"total_jobs": total, "categories": cats,
            "locations": locs, "top_category": top_cat[0] if top_cat else ""}

def get_all_categories():
    conn = sqlite3.connect(DB_PATH)
    cats = [r[0] for r in conn.execute("SELECT DISTINCT category FROM jobs ORDER BY category").fetchall()]
    conn.close()
    return cats

def search_jobs(query="", location="", category=""):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    sql = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if query:
        sql += " AND (title LIKE ? OR description LIKE ? OR skills LIKE ?)"
        params += [f"%{query}%"]*3
    if location:
        sql += " AND location LIKE ?"
        params.append(f"%{location}%")
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " LIMIT 200"
    jobs = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return jobs

def get_job_by_id(job_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

if __name__ == "__main__":
    train_model()
    r = recommend_jobs("python machine learning data science")
    print("Top results:")
    for j in r[:4]: print(f"  [{j['score']}%] {j['title']} @ {j['company']}")
    print("Trending:", [s["skill"] for s in get_trending_skills(6)])
