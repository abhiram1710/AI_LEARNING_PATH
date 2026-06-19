from flask import Flask, render_template, request, session

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

app = Flask(__name__)

app.secret_key = "learning_path_secret_2026"

# DATABASE

conn = sqlite3.connect(
"learning.db",
check_same_thread=False
)

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

# MODEL

model = tf.keras.models.load_model(
"models/path_model.keras"
)

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
    return render_template(
    "index.html"
)
@app.route(
"/register",
methods=["GET","POST"]
)

def register():
    if request.method == "POST":
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

    return render_template(
        "register.html"
    )

@app.route(
"/login",
methods=["GET","POST"]
)

def login():
    if request.method == "POST":
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
            return render_template(
                "dashboard.html",
                username=username
            )

        return "Invalid Login"

    return render_template(
        "login.html"
    )

@app.route("/dashboard")
def dashboard():
    
    
    
    return render_template(
        "dashboard.html",

    username=session.get(
        "user"
    )   

)

@app.route(
"/predict",
methods=["POST"]
)

def predict():
    course = int(
        request.form["course"]
    )

    skill = int(
        request.form["skill"]
    )

    hours = int(
        request.form["hours"]
    )

    quiz = int(
        request.form["quiz"]
    )

    X = np.array([[
        course,
        skill,
        hours,
        quiz
    ]])

    prediction = model.predict(
        X,
        verbose=0
    )

    predicted = np.argmax(
        prediction
    )

    confidence = round(
        float(
            np.max(
                prediction
            )
        ) * 100,
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

    plt.figure()
    plt.bar(
        [
            "Hours",
            "Quiz",
            "Progress"
        ],
        [
            hours,
            quiz,
            progress
        ]
    )
    plt.savefig(
        "static/graph.png"
    )
    plt.close()

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

    return render_template(
        "result.html",
        recommendation=recommendation,
        confidence=confidence,
        roadmap=roadmap,
        progress=progress,
        completed=completed,
        graph="graph.png",
        history=history
    )
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
