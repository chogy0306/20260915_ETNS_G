import os
from functools import wraps

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            DATABASE_URL, sslmode="require", cursor_factory=psycopg2.extras.RealDictCursor
        )
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = psycopg2.connect(DATABASE_URL, sslmode="require")
    with db, db.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        cur.execute(
            "ALTER TABLE todos ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"
        )
    db.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            return render_template("register.html", error="아이디와 비밀번호를 입력해주세요.")

        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                return render_template("register.html", error="이미 사용 중인 아이디입니다.")
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, generate_password_hash(password)),
            )
        db.commit()
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다.")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM todos WHERE user_id = %s ORDER BY done ASC, created_at DESC",
            (session["user_id"],),
        )
        todos = cur.fetchall()
    remaining = sum(1 for t in todos if not t["done"])
    return render_template(
        "index.html", todos=todos, remaining=remaining, username=session["username"]
    )


@app.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form.get("title", "").strip()
    if title:
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO todos (title, user_id) VALUES (%s, %s)", (title, session["user_id"])
            )
        db.commit()
    return redirect(url_for("index"))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
@login_required
def toggle(todo_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE todos SET done = NOT done WHERE id = %s AND user_id = %s",
            (todo_id, session["user_id"]),
        )
    db.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>", methods=["POST"])
@login_required
def delete(todo_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "DELETE FROM todos WHERE id = %s AND user_id = %s", (todo_id, session["user_id"])
        )
    db.commit()
    return redirect(url_for("index"))


@app.route("/edit/<int:todo_id>", methods=["POST"])
@login_required
def edit(todo_id):
    title = request.form.get("title", "").strip()
    if title:
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE todos SET title = %s WHERE id = %s AND user_id = %s",
                (title, todo_id, session["user_id"]),
            )
        db.commit()
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
