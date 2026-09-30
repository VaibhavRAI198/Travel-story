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


def get_user_data(user_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM user_detail
            WHERE user_id = %s
            """,
            (user_id,)
        )

        row = cursor.fetchone()

        if not row:
            return None

        columns = [desc[0] for desc in cursor.description]

        return dict(zip(columns, row))

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


def login_required():
    if "user_id" not in session:
        return None

    user_data = get_user_data(session["user_id"])

    if not user_data:
        session.clear()
        return None

    return user_data


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
            return render_template(
                "login.html",
                error="Please enter username and password."
            )

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
                WHERE user_id = %s
                   OR email_id = %s
                   OR mobile_number = %s
                LIMIT 1
                """,
                (
                    login_value,
                    login_value,
                    login_value
                )
            )

            user = cursor.fetchone()

            if user is None:
                return render_template(
                    "login.html",
                    error="Invalid User ID, Email or Mobile Number."
                )

            user_id = user[0]
            full_name = user[1]
            email_id = user[2]
            mobile_number = user[3]
            database_password = user[4]

            if login_password != database_password:
                return render_template(
                    "login.html",
                    error="Invalid password."
                )

            session["user_id"] = user_id
            session["username"] = user_id
            session["full_name"] = full_name
            session["email_id"] = email_id
            session["mobile_number"] = mobile_number

            return redirect(url_for("dashboard"))

        except Exception:
            return render_template(
                "login.html",
                error="Unable to connect to database."
            )

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    user_data = login_required()

    if not user_data:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        user_data=user_data,
        section="dashboard"
    )


@app.route("/my_profile")
def my_profile():
    user_data = login_required()

    if not user_data:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        user_data=user_data,
        section="my_profile"
    )


@app.route("/setting")
def setting():
    user_data = login_required()

    if not user_data:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        user_data=user_data,
        section="setting"
    )


@app.route("/about_me")
def about_me():
    user_data = login_required()

    if not user_data:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        user_data=user_data,
        section="about_me"
    )


@app.route("/city")
def city():
    user_data = login_required()

    if not user_data:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        user_data=user_data,
        section="city"
    )


@app.route("/add_city")
def add_city():
    user_data = login_required()

    if not user_data:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        user_data=user_data,
        section="add_city"
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

        cursor.execute(
            """
            SELECT user_id
            FROM user_detail
            WHERE email_id = %s
            """,
            (email_id,)
        )

        if cursor.fetchone():
            return render_template(
                "signup.html",
                error="Email address already exists."
            )

        cursor.execute(
            """
            SELECT user_id
            FROM user_detail
            WHERE mobile_number = %s
            """,
            (mobile_number,)
        )

        if cursor.fetchone():
            return render_template(
                "signup.html",
                error="Mobile number already exists."
            )

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

        if not name_part:
            name_part = "user"

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
            (
                user_id,
                full_name,
                email_id,
                mobile_number,
                password
            )
        )

        conn.commit()

        return redirect(url_for("login"))

    except Exception as e:
        if conn:
            conn.rollback()

        return render_template(
            "signup.html",
            error=f"Database Error: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    section = request.form.get("section")

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if section == "personal":
            full_name = request.form.get(
                "full_name",
                ""
            ).strip()

            gender = request.form.get(
                "gender",
                ""
            ).strip() or None

            date_of_birth = request.form.get(
                "date_of_birth",
                ""
            ).strip() or None

            if not full_name:
                return redirect(url_for("my_profile"))

            cursor.execute(
                """
                UPDATE user_detail
                SET
                    full_name = %s,
                    gender = %s,
                    date_of_birth = %s
                WHERE user_id = %s
                """,
                (
                    full_name,
                    gender,
                    date_of_birth,
                    user_id
                )
            )

            session["full_name"] = full_name

        elif section == "contact":
            email_id = request.form.get(
                "email_id",
                ""
            ).strip()

            mobile_number = request.form.get(
                "mobile_number",
                ""
            ).strip()

            if not email_id or not mobile_number:
                return redirect(url_for("my_profile"))

            cursor.execute(
                """
                SELECT user_id
                FROM user_detail
                WHERE email_id = %s
                AND user_id != %s
                """,
                (
                    email_id,
                    user_id
                )
            )

            if cursor.fetchone():
                return redirect(url_for("my_profile"))

            cursor.execute(
                """
                SELECT user_id
                FROM user_detail
                WHERE mobile_number = %s
                AND user_id != %s
                """,
                (
                    mobile_number,
                    user_id
                )
            )

            if cursor.fetchone():
                return redirect(url_for("my_profile"))

            cursor.execute(
                """
                UPDATE user_detail
                SET
                    email_id = %s,
                    mobile_number = %s
                WHERE user_id = %s
                """,
                (
                    email_id,
                    mobile_number,
                    user_id
                )
            )

            session["email_id"] = email_id
            session["mobile_number"] = mobile_number

        elif section == "preferences":
            time_zone = request.form.get(
                "time_zone",
                ""
            ).strip() or None

            cursor.execute(
                """
                UPDATE user_detail
                SET time_zone = %s
                WHERE user_id = %s
                """,
                (
                    time_zone,
                    user_id
                )
            )

        conn.commit()

    except Exception:
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(url_for("my_profile"))

@app.route("/add_city_function", methods=["POST"])
def add_city_function():
    user_data = login_required()

    if not user_data:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    city_name = request.form.get("city_name", "").strip()

    if not city_name:
        return render_template(
            "dashboard.html",
            username=session.get("username"),
            user_data=user_data,
            section="add_city",
            add_city_result="Please enter city name."
        )

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT city_id
            FROM city
            WHERE user_id = %s
            AND LOWER(city_name) = LOWER(%s)
            LIMIT 1
            """,
            (user_id, city_name)
        )

        user_existing_city = cursor.fetchone()

        if user_existing_city:
            return render_template(
                "dashboard.html",
                username=session.get("username"),
                user_data=user_data,
                section="add_city",
                add_city_result="You have already added this city."
            )

        cursor.execute(
            """
            SELECT city_id, city_name
            FROM city
            WHERE LOWER(city_name) = LOWER(%s)
            LIMIT 1
            """,
            (city_name,)
        )

        existing_city = cursor.fetchone()

        if existing_city:
            city_id = existing_city[0]

        else:
            cursor.execute(
                """
                SELECT city_id
                FROM city
                ORDER BY city_id DESC
                LIMIT 1
                """
            )

            row = cursor.fetchone()

            if row:
                last_city_id = str(row[0])

                try:
                    serial_number = int(
                        "".join(
                            character
                            for character in last_city_id
                            if character.isdigit()
                        )
                    ) + 1
                except (ValueError, TypeError):
                    serial_number = 1
            else:
                serial_number = 1

            city_id = f"city{serial_number:06d}"

        cursor.execute(
            """
            INSERT INTO city
            (
                city_id,
                user_id,
                city_name
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                city_id,
                user_id,
                city_name
            )
        )

        conn.commit()

        return render_template(
            "dashboard.html",
            username=session.get("username"),
            user_data=get_user_data(user_id),
            section="add_city",
            add_city_result="City Added Successfully."
        )

    except Exception:
        if conn:
            conn.rollback()

        return render_template(
            "dashboard.html",
            username=session.get("username"),
            user_data=user_data,
            section="add_city",
            add_city_result="Unable to add city."
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()




if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
