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

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/database")
def database():
    return render_template("my_database.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        full_name = request.form.get("name", "").strip()
        email_id = request.form.get("email", "").strip()
        mobile_number = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        terms = request.form.get("terms")
        if not full_name:
            error = "Please enter your full name."
        elif not mobile_number:
            error = "Please enter your mobile number."
        elif not email_id:
            error = "Please enter your email."
        elif not password:
            error = "Please enter a password."
        elif not terms:
            error = "Please accept Terms & Conditions."
        if error:
            return render_template("signup.html",error=error)
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(MAX(
                    CAST(SUBSTRING(user_id FROM '[0-9]+$') AS INTEGER)
                ), 0) + 1
                FROM user_detail
            """)
            serial_number = cursor.fetchone()[0]
            name_part = "".join(
                full_name.split()
            ).lower()[:6]
            user_id = f"{name_part}{serial_number:06d}"
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
            return redirect(url_for("login"))
        except psycopg2.errors.UniqueViolation:
            if conn:
                conn.rollback()
            error = "Email, mobile number, or User ID already exists."
            return render_template("signup.html",error=error)
        except Exception as e:
            if conn:
                conn.rollback()
            error = "Unable to create account."
            return render_template("signup.html",error=error)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template("signup.html",error=error)

if __name__ == "__main__":
    app.run(debug=True)
