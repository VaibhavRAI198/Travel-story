from flask import Flask, render_template, request, redirect, url_for, session
import os
import psycopg2

app = Flask(__name__)

app.secret_key = "travel_story"

def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL is not configured.")
    return psycopg2.connect(database_url)

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_value = request.form.get("username", "").strip()
        login_password = request.form.get("password", "").strip()
        if not login_value or not login_password:
            return render_template("login.html",error="Please enter username and password.")
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    user_id,
                    full_name,
                    email_id,
                    mobile_number,
                    password
                FROM user_detail
                WHERE
                    user_id = %s
                    OR email_id = %s
                    OR mobile_number = %s
                LIMIT 1
                """,
                (login_value,login_value,login_value)
            )
            user = cursor.fetchone()
            if user is None:
                return render_template("login.html",error="Invalid User ID, Email or Mobile Number.")
            user_id = user[0]
            full_name = user[1]
            email_id = user[2]
            mobile_number = user[3]
            database_password = user[4]
            if login_password != database_password:
                return render_template("login.html",error="Invalid password.")
            session["user_id"] = user_id
            session["username"] = user_id
            session["full_name"] = full_name
            session["email_id"] = email_id
            session["mobile_number"] = mobile_number
            return redirect(url_for("dashboard"))
        except Exception as e:
            return render_template("login.html",error="Unable to connect to database.")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM user_detail
        WHERE user_id = %s
    """, (user_id,))

    row = cursor.fetchone()

    # Get column names before closing cursor
    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    if not row:
        return "User data not found", 404

    # Convert row to dictionary
    user_data = dict(zip(columns, row))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        user_id=user_id,
        user_data=user_data
    )
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/signup_page")
def signup_page():
    return render_template("signup.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    full_name = request.form.get("name", "").strip()
    email_id = request.form.get("email", "").strip()
    mobile_number = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    terms = request.form.get("terms")
    if not full_name:
        return render_template("signup.html",error="Please enter your full name.")
    if not mobile_number:
        return render_template("signup.html",error="Please enter your mobile number.")
    if not email_id:
        return render_template("signup.html",error="Please enter your email.")
    if not password:
        return render_template("signup.html",error="Please enter a password.")
    if not terms:
        return render_template("signup.html",error="Please accept Terms & Conditions.")
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_id
            FROM user_detail
            WHERE email_id = %s
            """,(email_id,))
        existing_email = cursor.fetchone()
        if existing_email:
            return render_template("signup.html",error="Email address already exists.")
        cursor.execute(
            """
            SELECT user_id
            FROM user_detail
            WHERE mobile_number = %s
            """,(mobile_number,))
        existing_mobile = cursor.fetchone()
        if existing_mobile:
            return render_template("signup.html",error="Mobile number already exists.")
        cursor.execute(
            """
            SELECT COALESCE(
                MAX(
                    CAST(
                        SUBSTRING(user_id FROM '[0-9]+$')
                        AS INTEGER
                    )
                ),
                0
            ) + 1
            FROM user_detail
            """
        )
        result = cursor.fetchone()
        serial_number = result[0]
        name_part = "".join(full_name.split()).lower()[:6]
        user_id = f"{name_part}{serial_number:06d}"
        cursor.execute(
            """
            INSERT INTO user_detail
            (
                user_id,
                full_name,
                email_id,
                mobile_number,
                password
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (user_id,full_name,email_id,mobile_number,password))
        conn.commit()
        return redirect(url_for("dashboard"))
    except Exception as e:
        if conn:
            conn.rollback()
        return render_template("signup.html",error=f"Database Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT", 5000)),debug=True)
