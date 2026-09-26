from flask import Flask, render_template, request, redirect, url_for, session
import os
import psycopg2

app = Flask(__name__)

app.secret_key = "travel_story"

def get_db_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT version();")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return redner_template("dashboard.html" , db=f"Database connected successfully: {result[0]}")

    except Exception as e:
        return redner_template("dashboard.html" , db=f"Error : {e}")

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

USERNAME = "raiv"
PASSWORD = "64843810"

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            session["username"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html",error="Invalid username or password")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html",username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/signup")
def signup():
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
