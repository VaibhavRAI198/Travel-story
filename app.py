from flask import Flask, render_template, request, redirect, url_for, session
import os
import psycopg2

app = Flask(**name**)

# ---------------------------------------

# FLASK SECRET KEY

# ---------------------------------------

app.secret_key = "travel_story"

# ---------------------------------------

# DATABASE CONNECTION

# ---------------------------------------

def get_db_connection():

```
database_url = os.environ.get("DATABASE_URL")

if not database_url:
    raise Exception("DATABASE_URL environment variable is not set.")

return psycopg2.connect(database_url)
```

# ---------------------------------------

# HOME

# ---------------------------------------

@app.route("/")
def home():

```
if "username" in session:
    return redirect(url_for("dashboard"))

return redirect(url_for("login"))
```

# ---------------------------------------

# ADMIN LOGIN DETAILS

# ---------------------------------------

USERNAME = "raiv"
PASSWORD = "64843810"

# ---------------------------------------

# LOGIN

# ---------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

```
if request.method == "POST":

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if username == USERNAME and password == PASSWORD:

        session["username"] = username

        return redirect(url_for("dashboard"))

    return render_template(
        "login.html",
        error="Invalid username or password"
    )

return render_template("login.html")
```

# ---------------------------------------

# DASHBOARD

# ---------------------------------------

@app.route("/dashboard")
def dashboard():

```
if "username" not in session:
    return redirect(url_for("login"))

return render_template(
    "dashboard.html",
    username=session["username"]
)
```

# ---------------------------------------

# LOGOUT

# ---------------------------------------

@app.route("/logout")
def logout():

```
session.clear()

return redirect(url_for("login"))
```

# ---------------------------------------

# SIGNUP PAGE

# ---------------------------------------

@app.route("/signup_page")
def signup_page():

```
return render_template("signup.html")
```

# ---------------------------------------

# DATABASE PAGE

# ---------------------------------------

@app.route("/database")
def database():

```
if "username" not in session:
    return redirect(url_for("login"))

return render_template("my_database.html")
```

# ---------------------------------------

# SIGNUP

# ---------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

```
# -----------------------------------
# SHOW SIGNUP PAGE
# -----------------------------------

if request.method == "GET":

    return render_template("signup.html")


# -----------------------------------
# GET FORM DATA
# -----------------------------------

full_name = request.form.get("name", "").strip()
email_id = request.form.get("email", "").strip()
mobile_number = request.form.get("username", "").strip()
password = request.form.get("password", "").strip()
terms = request.form.get("terms")


# -----------------------------------
# VALIDATION
# -----------------------------------

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


# -----------------------------------
# DATABASE VARIABLES
# -----------------------------------

conn = None
cursor = None


try:

    # --------------------------------
    # CONNECT DATABASE
    # --------------------------------

    conn = get_db_connection()

    cursor = conn.cursor()


    # --------------------------------
    # CHECK EMAIL
    # --------------------------------

    cursor.execute(
        """
        SELECT user_id
        FROM user_detail
        WHERE email_id = %s
        """,
        (email_id,)
    )

    existing_email = cursor.fetchone()


    if existing_email:

        return render_template(
            "signup.html",
            error="Email address already exists."
        )


    # --------------------------------
    # CHECK MOBILE NUMBER
    # --------------------------------

    cursor.execute(
        """
        SELECT user_id
        FROM user_detail
        WHERE mobile_number = %s
        """,
        (mobile_number,)
    )

    existing_mobile = cursor.fetchone()


    if existing_mobile:

        return render_template(
            "signup.html",
            error="Mobile number already exists."
        )


    # --------------------------------
    # GET NEXT SERIAL NUMBER
    # --------------------------------

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


    # --------------------------------
    # CREATE NAME PART
    # --------------------------------

    name_part = "".join(
        full_name.split()
    ).lower()[:6]


    # --------------------------------
    # CREATE USER ID
    # --------------------------------

    user_id = f"{name_part}{serial_number:06d}"


    print("--------------------------------")
    print("New User")
    print("User ID       :", user_id)
    print("Full Name     :", full_name)
    print("Email         :", email_id)
    print("Mobile        :", mobile_number)
    print("--------------------------------")


    # --------------------------------
    # INSERT USER
    # --------------------------------

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
        (
            user_id,
            full_name,
            email_id,
            mobile_number,
            password
        )
    )


    # --------------------------------
    # COMMIT
    # --------------------------------

    conn.commit()


    print("ACCOUNT CREATED SUCCESSFULLY")
    print("USER ID:", user_id)


    # --------------------------------
    # REDIRECT LOGIN
    # --------------------------------

    return redirect(url_for("login"))


# -----------------------------------
# DATABASE ERROR
# -----------------------------------

except Exception as e:

    if conn:
        conn.rollback()


    print("--------------------------------")
    print("SIGNUP DATABASE ERROR")
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR:", str(e))
    print("--------------------------------")


    return render_template(
        "signup.html",
        error=f"Database Error: {str(e)}"
    )


# -----------------------------------
# CLOSE DATABASE
# -----------------------------------

finally:

    if cursor:
        cursor.close()

    if conn:
        conn.close()
```

# ---------------------------------------

# APPLICATION START

# ---------------------------------------

if **name** == "**main**":
app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    debug=True
)
