import os
import json
import sqlite3
import uuid
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "change-this-secret-key"

DATABASE = "fitness_app.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal TEXT,
            level TEXT,
            days_per_week TEXT,
            workout_type TEXT,
            session_length TEXT,
            equipment TEXT,
            limitations TEXT,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            plan_json TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS progress_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            caption TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            rating TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (plan_id) REFERENCES workout_plans(id)
        )
    """)

    conn.commit()
    conn.close()


init_db()


def login_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return route(*args, **kwargs)
    return wrapper


def current_user():
    if "user_id" not in session:
        return None

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    conn.close()

    return user


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_llm_plan(goal, level, days_per_week, workout_type, session_length, equipment, limitations):
    try:
        days = int(days_per_week)
    except ValueError:
        days = 3

    days = max(1, min(days, 7))

    if not goal:
        goal = "General Health"

    if not level:
        level = "Beginner"

    if not workout_type:
        workout_type = "gym"

    if not session_length:
        session_length = "45"

    if not equipment:
        equipment = "basic gym equipment"

    if not limitations:
        limitations = "none"

    workout_days = [
        {
            "day": "Monday",
            "focus": "Full Body Strength",
            "exercises": [
                {"name": "Squats", "sets": "3", "reps": "10", "rest": "60 sec"},
                {"name": "Chest Press", "sets": "3", "reps": "10", "rest": "60 sec"},
                {"name": "Lat Pulldown", "sets": "3", "reps": "12", "rest": "60 sec"},
                {"name": "Plank", "sets": "3", "reps": "30 sec", "rest": "45 sec"}
            ]
        },
        {
            "day": "Tuesday",
            "focus": "Cardio + Core",
            "exercises": [
                {"name": "Treadmill Walk/Jog", "sets": "1", "reps": "20 min", "rest": "none"},
                {"name": "Bicycle Crunches", "sets": "3", "reps": "15", "rest": "45 sec"},
                {"name": "Leg Raises", "sets": "3", "reps": "12", "rest": "45 sec"}
            ]
        },
        {
            "day": "Wednesday",
            "focus": "Lower Body Strength",
            "exercises": [
                {"name": "Lunges", "sets": "3", "reps": "10 each leg", "rest": "60 sec"},
                {"name": "Leg Press", "sets": "3", "reps": "10", "rest": "75 sec"},
                {"name": "Glute Bridges", "sets": "3", "reps": "12", "rest": "60 sec"}
            ]
        },
        {
            "day": "Thursday",
            "focus": "Upper Body Strength",
            "exercises": [
                {"name": "Shoulder Press", "sets": "3", "reps": "10", "rest": "60 sec"},
                {"name": "Rows", "sets": "3", "reps": "12", "rest": "60 sec"},
                {"name": "Bicep Curls", "sets": "3", "reps": "12", "rest": "45 sec"}
            ]
        },
        {
            "day": "Friday",
            "focus": "Conditioning + Mobility",
            "exercises": [
                {"name": "Bike or Elliptical", "sets": "1", "reps": "20 min", "rest": "none"},
                {"name": "Bodyweight Squats", "sets": "3", "reps": "15", "rest": "45 sec"},
                {"name": "Stretching", "sets": "1", "reps": "10 min", "rest": "none"}
            ]
        },
        {
            "day": "Saturday",
            "focus": "Active Recovery",
            "exercises": [
                {"name": "Walking", "sets": "1", "reps": "30 min", "rest": "none"},
                {"name": "Stretching", "sets": "1", "reps": "15 min", "rest": "none"}
            ]
        },
        {
            "day": "Sunday",
            "focus": "Rest Day",
            "exercises": [
                {"name": "Recovery", "sets": "1", "reps": "Full day", "rest": "as needed"}
            ]
        }
    ]

    selected_calendar = workout_days[:days]

    plan_json = {
        "summary": (
            f"This is a {days}-day {workout_type} fitness plan for a {level} user "
            f"focused on {goal}. Each session is designed to be around "
            f"{session_length} minutes and uses {equipment}. Limitations/notes: {limitations}."
        ),
        "calendar": selected_calendar,
        "tips": [
            "Warm up for 5 minutes before each workout.",
            "Focus on proper form before increasing weight.",
            "Track your workouts and progress pictures weekly."
        ]
    }

    raw_text = json.dumps(plan_json, indent=2)
    return plan_json, raw_text


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            error = "Please complete all fields."
        else:
            conn = get_db()

            try:
                conn.execute(
                    """
                    INSERT INTO users (name, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (name, email, generate_password_hash(password), datetime.now().isoformat())
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "An account with this email already exists."
                conn.close()

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()

    conn = get_db()

    profile = conn.execute(
        "SELECT * FROM profiles WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    latest_plan = conn.execute(
        """
        SELECT * FROM workout_plans
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    photos = conn.execute(
        """
        SELECT * FROM progress_photos
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    plan_data = None

    if latest_plan:
        plan_data = json.loads(latest_plan["plan_json"])

    return render_template(
        "dashboard.html",
        user=user,
        profile=profile,
        latest_plan=latest_plan,
        plan_data=plan_data,
        photos=photos
    )


@app.route("/generate", methods=["POST"])
@login_required
def generate():
    goal = request.form.get("goal", "")
    level = request.form.get("level", "")
    days_per_week = request.form.get("days_per_week", "")
    workout_type = request.form.get("workout_type", "")
    session_length = request.form.get("session_length", "")
    equipment = request.form.get("equipment", "")
    limitations = request.form.get("limitations", "")

    plan_json, raw_text = generate_llm_plan(
        goal,
        level,
        days_per_week,
        workout_type,
        session_length,
        equipment,
        limitations
    )

    conn = get_db()

    old_profile = conn.execute(
        "SELECT * FROM profiles WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if old_profile:
        conn.execute(
            """
            UPDATE profiles
            SET goal = ?, level = ?, days_per_week = ?, workout_type = ?,
                session_length = ?, equipment = ?, limitations = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (
                goal,
                level,
                days_per_week,
                workout_type,
                session_length,
                equipment,
                limitations,
                datetime.now().isoformat(),
                session["user_id"]
            )
        )
    else:
        conn.execute(
            """
            INSERT INTO profiles
            (user_id, goal, level, days_per_week, workout_type,
             session_length, equipment, limitations, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                goal,
                level,
                days_per_week,
                workout_type,
                session_length,
                equipment,
                limitations,
                datetime.now().isoformat()
            )
        )

    conn.execute(
        """
        INSERT INTO workout_plans
        (user_id, title, plan_json, raw_text, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            f"{goal} Plan",
            json.dumps(plan_json),
            raw_text,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


@app.route("/edit-plan/<int:plan_id>", methods=["GET", "POST"])
@login_required
def edit_plan(plan_id):
    conn = get_db()

    plan = conn.execute(
        """
        SELECT * FROM workout_plans
        WHERE id = ? AND user_id = ?
        """,
        (plan_id, session["user_id"])
    ).fetchone()

    if not plan:
        conn.close()
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "")
        summary = request.form.get("summary", "")

        day_count = int(request.form.get("day_count", 0))
        tip_count = int(request.form.get("tip_count", 0))

        calendar = []

        for day_index in range(day_count):
            day_name = request.form.get(f"day_{day_index}_day", "")
            focus = request.form.get(f"day_{day_index}_focus", "")

            exercises = []

            exercise_index = 0

            while True:
                exercise_name = request.form.get(
                    f"day_{day_index}_exercise_{exercise_index}_name"
                )

                if exercise_name is None:
                    break

                exercises.append({
                    "name": exercise_name,
                    "sets": request.form.get(
                        f"day_{day_index}_exercise_{exercise_index}_sets", ""
                    ),
                    "reps": request.form.get(
                        f"day_{day_index}_exercise_{exercise_index}_reps", ""
                    ),
                    "rest": request.form.get(
                        f"day_{day_index}_exercise_{exercise_index}_rest", ""
                    )
                })

                exercise_index += 1

            calendar.append({
                "day": day_name,
                "focus": focus,
                "exercises": exercises
            })

        tips = []

        for tip_index in range(tip_count):
            tip = request.form.get(f"tip_{tip_index}", "")

            if tip:
                tips.append(tip)

        updated_plan = {
            "summary": summary,
            "calendar": calendar,
            "tips": tips
        }

        conn.execute(
            """
            UPDATE workout_plans
            SET title = ?, plan_json = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                title,
                json.dumps(updated_plan),
                datetime.now().isoformat(),
                plan_id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    plan_data = json.loads(plan["plan_json"])

    conn.close()

    return render_template(
        "edit_plan.html",
        plan=plan,
        plan_data=plan_data,
        error=""
    )


@app.route("/upload-photo", methods=["POST"])
@login_required
def upload_photo():
    photo = request.files.get("photo")
    caption = request.form.get("caption", "")

    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        photo.save(filepath)

        conn = get_db()

        conn.execute(
            """
            INSERT INTO progress_photos (user_id, filename, caption, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                session["user_id"],
                unique_filename,
                caption,
                datetime.now().isoformat()
            )
        )

        conn.commit()
        conn.close()

    return redirect(url_for("dashboard"))


@app.route("/feedback", methods=["POST"])
@login_required
def feedback():
    plan_id = request.form.get("plan_id")
    rating = request.form.get("rating")
    notes = request.form.get("notes", "")

    conn = get_db()

    conn.execute(
        """
        INSERT INTO feedback (user_id, plan_id, rating, notes, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            plan_id,
            rating,
            notes,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)