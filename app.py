from flask import Flask, render_template, request, redirect, url_for, session
import os
import psycopg2
import re

app = Flask(__name__)

app.secret_key = "travel_story"

def get_db_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])
        
def show_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        table_names = cursor.fetchall()
        all_tables = {}
        for table in table_names:
            table_name = table[0]
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            columns = cursor.fetchall()
            cursor.execute(
                f'SELECT * FROM "{table_name}"'
            )
            rows = cursor.fetchall()
            all_tables[table_name] = {
                "columns": columns,
                "rows": rows
            }
        cursor.close()
        conn.close()
        return all_tables
    except Exception as e:
        return {
            "error": str(e)
        }

def valid_identifier(name):
    """
    Allow only letters, numbers and underscore.
    Prevents SQL injection through table/column names.
    """
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name))
# ==========================================================
# ADD COLUMN
# ==========================================================
@app.route("/add_column", methods=["POST"])
def add_column():
    table_name = request.form.get("table_name", "").strip()
    column_name = request.form.get("column_name", "").strip()
    data_type = request.form.get("data_type", "").strip()

    if not valid_identifier(table_name):
        return "Invalid table name"

    if not valid_identifier(column_name):
        return "Invalid column name"

    allowed_types = [
        "INTEGER",
        "BIGINT",
        "VARCHAR",
        "TEXT",
        "BOOLEAN",
        "DATE",
        "TIMESTAMP",
        "DECIMAL"
    ]

    if data_type not in allowed_types:
        return "Invalid data type"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # VARCHAR needs a size
        if data_type == "VARCHAR":
            query = f'''
                ALTER TABLE "{table_name}"
                ADD COLUMN "{column_name}" VARCHAR(255);
            '''
        else:
            query = f'''
                ALTER TABLE "{table_name}"
                ADD COLUMN "{column_name}" {data_type};
            '''

        cursor.execute(query)

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/show_tables")

    except Exception as e:
        return f"Error adding column: {e}"


# ==========================================================
# DELETE COLUMN
# ==========================================================

@app.route("/delete_column", methods=["POST"])
def delete_column():

    table_name = request.form.get("table_name", "").strip()
    column_name = request.form.get("column_name", "").strip()

    if not valid_identifier(table_name):
        return "Invalid table name"

    if not valid_identifier(column_name):
        return "Invalid column name"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = f'''
            ALTER TABLE "{table_name}"
            DROP COLUMN "{column_name}";
        '''

        cursor.execute(query)

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/show_tables")

    except Exception as e:
        return f"Error deleting column: {e}"


# ==========================================================
# DELETE ROW
# ==========================================================

@app.route("/delete_row", methods=["POST"])
def delete_row():

    table_name = request.form.get("table_name", "").strip()
    row_id = request.form.get("row_id", "").strip()

    if not valid_identifier(table_name):
        return "Invalid table name"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Assumes every table has an "id" column
        cursor.execute(
            f'DELETE FROM "{table_name}" WHERE id = %s',
            (row_id,)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/show_tables")

    except Exception as e:
        return f"Error deleting row: {e}"


# ==========================================================
# DELETE TABLE
# ==========================================================

@app.route("/delete_table", methods=["POST"])
def delete_table():

    table_name = request.form.get("table_name", "").strip()

    if not valid_identifier(table_name):
        return "Invalid table name"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            f'DROP TABLE IF EXISTS "{table_name}"'
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/show_tables")

    except Exception as e:
        return f"Error deleting table: {e}"


@app.route("/database_login", methods=["POST"])
def database_login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username == USERNAME and password == PASSWORD:

        return render_template(
            "my_database.html",
            result="authorized",
            tables=show_tables()
        )

    else:

        return render_template(
            "my_database.html",
            error="Unauthorized"
        )


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

if __name__ == "__main__":
    app.run(debug=True)
