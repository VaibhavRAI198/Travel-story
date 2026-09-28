from flask import Flask, render_template, request, redirect, url_for, session
import os
import psycopg2
import re

app = Flask(__name__)

app.secret_key = "travel_story"

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

@app.route("/signup_page")
def signup_page():
    return render_template("signup.html")

@app.route("/database")
def database():
    return render_template("my_database.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

if request.method == "GET":
    return render_template("signup.html")

full_name = request.form.get("name", "").strip()
email_id = request.form.get("email", "").strip()
mobile_number = request.form.get("username", "").strip()
password = request.form.get("password", "").strip()
terms = request.form.get("terms")

# -----------------------------
# VALIDATION
# -----------------------------

if not full_name:
    return render_template(
        "signup.html",
        error="Please enter your full name."
    )

if not mobile_number:
    return render_template(
        "signup.html",
        error="Please enter your mobile number."
    )

if not email_id:
    return render_template(
        "signup.html",
        error="Please enter your email."
    )

if not password:
    return render_template(
        "signup.html",
        error="Please enter a password."
    )

if not terms:
    return render_template(
        "signup.html",
        error="Please accept Terms & Conditions."
    )

conn = None
cursor = None

try:

    conn = get_db_connection()
    cursor = conn.cursor()

    # -----------------------------
    # GET NEXT SERIAL NUMBER
    # -----------------------------

    cursor.execute("""
        SELECT COALESCE(MAX(
            CAST(
                SUBSTRING(user_id FROM '[0-9]+$')
                AS INTEGER
            )
        ), 0) + 1
        FROM user_detail
    """)

    result = cursor.fetchone()
    serial_number = result[0]

    # -----------------------------
    # CREATE USER ID
    # -----------------------------

    name_part = "".join(
        full_name.split()
    ).lower()[:6]

    # If name has less than 6 characters,
    # still create a valid ID.

    user_id = f"{name_part}{serial_number:06d}"

    print("Generated User ID:", user_id)

    # -----------------------------
    # INSERT DATA
    # -----------------------------

    cursor.execute("""
        INSERT INTO user_detail
        (
            user_id,
            full_name,
            email_id,
            mobile_number,
            password
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        user_id,
        full_name,
        email_id,
        mobile_number,
        password
    ))

    conn.commit()

    print("ACCOUNT CREATED:", user_id)

    return redirect(url_for("login"))

except Exception as e:

    if conn:
        conn.rollback()

    # IMPORTANT:
    # Print the actual PostgreSQL error
    print("================================")
    print("SIGNUP DATABASE ERROR:")
    print(type(e).__name__)
    print(str(e))
    print("================================")

    return render_template(
        "signup.html",
        error=f"Database Error: {str(e)}"
    )

finally:

    if cursor:
        cursor.close()

    if conn:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
