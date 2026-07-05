from flask import Flask, render_template, request, session

# import tensorflow as tf
# import numpy as np
# import matplotlib.pyplot as plt
import sqlite3
import random
import os

app = Flask(__name__)

app.secret_key = "learning_path_secret_2026"

# DATABASE - Initialize with error handling
def init_db():
    try:
        conn = sqlite3.connect("learning.db", check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY,
            username TEXT,
            recommendation TEXT,
            confidence REAL,
            progress INTEGER
        )
        """)
        conn.commit()
        return conn, cursor
    except Exception as e:
        print(f"Database error: {e}")
        return None, None

conn, cursor = init_db()

if conn is None:
    # Fallback: create in-memory database
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY,
        username TEXT,
        recommendation TEXT,
        confidence REAL,
        progress INTEGER
    )
    """)
    conn.commit()

# MODEL - Using dummy prediction (TensorFlow removed for deployment)

model = None
labels = {

0:"Python Basics",

1:"NumPy + Pandas",

2:"Deep Learning",

3:"HTML + CSS",

4:"React",

5:"Full Stack Project",

6:"Data Analysis",

7:"Machine Learning",

8:"Deep Learning Project",

9:"Linux",

10:"AWS",

11:"Cloud Deployment"

}

roadmaps = {

"Python Basics":[
"Week 1 → Python",
"Week 2 → Variables",
"Week 3 → Loops",
"Week 4 → Mini Project"
],

"Machine Learning":[
"Week 1 → Python",
"Week 2 → Statistics",
"Week 3 → ML",
"Week 4 → Project"
],

"Deep Learning":[
"Week 1 → Neural Networks",
"Week 2 → CNN",
"Week 3 → TensorFlow",
"Week 4 → Deployment"
]

}

@app.route("/")
def home():
    # Check if user is logged in
    if "user" in session:
        return render_template("index.html", username=session["user"])
    else:
        # Redirect to login if not authenticated
        return render_template("login.html")

@app.route("/health")
def health():
    return {"status": "ok"}, 200

@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")
@app.route(
"/register",
methods=["GET","POST"]
)

def register():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            cursor.execute(
                """
                INSERT INTO users(
                    username,
                    password
                )
                VALUES(
                    ?,?
                )
                """,
                (
                    username,
                    password
                )
            )
            conn.commit()
            return render_template(
                "login.html"
            )
        except Exception as e:
            print(f"Register error: {e}")
            return "Registration failed", 500

    return render_template(
        "register.html"
    )

@app.route(
"/login",
methods=["GET","POST"]
)

def login():
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE username = ?
                AND password = ?
                """,
                (
                    username,
                    password
                )
            )
            user = cursor.fetchone()

            if user:
                session["user"] = username
                # Redirect to home page (now shows index.html)
                return render_template(
                    "index.html",
                    username=username
                )

            return "Invalid Login"
        except Exception as e:
            print(f"Login error: {e}")
            return "Login failed", 500

    return render_template(
        "login.html"
    )

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return render_template("login.html")
    
    return render_template(
        "dashboard.html",
        username=session.get("user")   
    )

@app.route(
"/predict",
methods=["POST"]
)

def predict():
    if "user" not in session:
        return render_template("login.html"), 401
    
    try:
        course = int(
            request.form.get("course", 0)
        )

        skill = int(
            request.form.get("skill", 0)
        )

        hours = int(
            request.form.get("hours", 0)
        )

        quiz = int(
            request.form.get("quiz", 0)
        )

        # Dummy prediction without NumPy/TensorFlow
        prediction_score = (course + skill + hours + quiz) % 12
        predicted = prediction_score

        confidence = round(
            random.uniform(70, 99),
            2
        )

        recommendation = labels.get(
            predicted,
            "Python Basics"
        )

        roadmap = roadmaps.get(
            recommendation,
            [
                "Week 1 → Start Learning"
            ]
        )

        progress = min(
            int(
                hours * 10
                + quiz * 0.5
            ),
            100
        )

        completed = []

        if progress >= 25:
            completed.append(
                "✓ Week 1"
            )

        if progress >= 50:
            completed.append(
                "✓ Week 2"
            )

        if progress >= 75:
            completed.append(
                "✓ Week 3"
            )

        if progress >= 100:
            completed.append(
                "✓ Week 4"
            )

        # Skip matplotlib graph generation
        graph_file = "graph.png"

        # Try to save to database
        try:
            cursor.execute(
                """
                INSERT INTO history(
                    username,
                    recommendation,
                    confidence,
                    progress
                )
                VALUES(?, ?, ?, ?)
                """,
                (
                    session.get("user", "Guest"),
                    recommendation,
                    confidence,
                    progress
                )
            )
            conn.commit()

            history = cursor.execute(
                """
                SELECT
                    username,
                    recommendation,
                    confidence,
                    progress
                FROM history
                WHERE username = ?
                ORDER BY id DESC
                LIMIT 5
                """,
                (
                    session.get("user", "Guest"),
                )
            ).fetchall()
        except Exception as db_error:
            print(f"Database error: {db_error}")
            history = []

        return render_template(
            "result.html",
            recommendation=recommendation,
            confidence=confidence,
            roadmap=roadmap,
            progress=progress,
            completed=completed,
            graph=graph_file,
            history=history
        )
    except Exception as e:
        print(f"Predict error: {e}")
        return f"Error in prediction: {str(e)}", 500
import os

if __name__=="__main__":

    app.run(

        host="0.0.0.0",

        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )

    )
