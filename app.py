from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3, sys, os

sys.path.insert(0, os.path.dirname(__file__))
from model.recommender import (
    recommend_jobs, get_similar_jobs, get_all_categories,
    search_jobs, get_job_by_id, get_stats, get_trending_skills, load_model
)

app = Flask(__name__)
app.secret_key = "jobrecosecret2024"
DB_PATH = os.path.join(os.path.dirname(__file__), "database/jobs.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    categories = get_all_categories()
    stats = get_stats()
    trending = get_trending_skills(12)
    conn = get_db()
    featured = [dict(r) for r in conn.execute("SELECT * FROM jobs ORDER BY rating DESC LIMIT 6").fetchall()]
    conn.close()
    return render_template("index.html", categories=categories, featured_jobs=featured,
                           stats=stats, trending=trending)

@app.route("/recommend", methods=["GET","POST"])
def recommend():
    categories = get_all_categories()
    recommendations = []
    user_skills    = session.get("user_skills", "")
    user_experience = session.get("user_experience", "")

    if request.method == "POST":
        user_skills     = request.form.get("skills", "")
        user_experience = request.form.get("experience", "")
        session["user_skills"]     = user_skills
        session["user_experience"] = user_experience

    if user_skills.strip():
        recommendations = recommend_jobs(user_skills, user_experience, top_n=10)

    return render_template("recommend.html", recommendations=recommendations,
                           user_skills=user_skills, user_experience=user_experience,
                           categories=categories)

@app.route("/jobs")
def jobs_list():
    categories = get_all_categories()
    query    = request.args.get("q","")
    location = request.args.get("location","")
    category = request.args.get("category","")

    if query or location or category:
        jobs = search_jobs(query, location, category)
    else:
        conn = get_db()
        jobs = [dict(r) for r in conn.execute("SELECT * FROM jobs ORDER BY rating DESC LIMIT 200").fetchall()]
        conn.close()

    return render_template("jobs.html", jobs=jobs, categories=categories,
                           query=query, location=location, selected_category=category)

@app.route("/job/<int:job_id>")
def job_detail(job_id):
    job = get_job_by_id(job_id)
    if not job: return redirect(url_for("jobs_list"))
    similar = get_similar_jobs(job_id, top_n=4)
    categories = get_all_categories()
    return render_template("job_detail.html", job=job, similar=similar, categories=categories)

@app.route("/profile", methods=["GET","POST"])
def profile():
    categories = get_all_categories()
    message = ""
    if request.method == "POST":
        name     = request.form.get("name","")
        email    = request.form.get("email","")
        skills   = request.form.get("skills","")
        experience = request.form.get("experience","")
        education  = request.form.get("education","")
        location   = request.form.get("location","")
        conn = get_db()
        try:
            conn.execute("""INSERT INTO users (name,email,skills,experience,education,preferred_location)
                VALUES (?,?,?,?,?,?)
                ON CONFLICT(email) DO UPDATE SET name=excluded.name,skills=excluded.skills,
                experience=excluded.experience,education=excluded.education,
                preferred_location=excluded.preferred_location""",
                (name,email,skills,experience,education,location))
            conn.commit()
            session["user_email"]     = email
            session["user_name"]      = name
            session["user_skills"]    = skills
            session["user_experience"]= experience
            message = "success"
        except Exception as e:
            message = f"error:{e}"
        finally:
            conn.close()

    user = None
    if "user_email" in session:
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE email=?", (session["user_email"],)).fetchone()
        conn.close()
        if row: user = dict(row)

    return render_template("profile.html", categories=categories, user=user, message=message)

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    d = request.get_json()
    results = recommend_jobs(d.get("skills",""), d.get("experience",""), top_n=6)
    return jsonify({"status":"ok","results":results})

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

if __name__ == "__main__":
    db_path    = os.path.join(os.path.dirname(__file__), "database/jobs.db")
    model_path = os.path.join(os.path.dirname(__file__), "model/tfidf_model.pkl")
    if not os.path.exists(db_path):
        print("Setting up database...")
        from database.setup_db import create_database
        create_database()
    if not os.path.exists(model_path):
        print("Training ML model...")
        from model.recommender import train_model
        train_model()
    print("\n JobReco running at http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
