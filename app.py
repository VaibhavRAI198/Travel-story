from flask import Flask, render_template, request, redirect, url_for, session
import os
import psycopg2

app = Flask(__name__)

app.secret_key = "travel_story"

def get_db_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255),
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            city_name VARCHAR(150) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS places (
            id SERIAL PRIMARY KEY,
            city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
            place_name VARCHAR(200) NOT NULL,
            about_place TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS place_images (
            id SERIAL PRIMARY KEY,
            place_id INTEGER REFERENCES places(id) ON DELETE CASCADE,
            image_name VARCHAR(255) NOT NULL,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("Tables created!")

create_tables()

@app.route("/show-tables")
def show_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()

        cursor.close()
        conn.close()

        table_list = "<h2>Tables in Render Database</h2><ul>"

        for table in tables:
            table_list += f"<li>{table[0]}</li>"

        table_list += "</ul>"

        return table_list

    except Exception as e:
        return f"<h2>Database Error</h2><p>{e}</p>"
        
@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template("dashboard.html" , db=f"Database connected successfully: {result[0]}")
    except Exception as e:
        return render_template("dashboard.html" , db=f"Error : {e}")

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
