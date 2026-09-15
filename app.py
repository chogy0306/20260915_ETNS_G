import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, request, url_for

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

app = Flask(__name__)


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
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    db.close()


@app.route("/")
def index():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM todos ORDER BY done ASC, created_at DESC")
        todos = cur.fetchall()
    remaining = sum(1 for t in todos if not t["done"])
    return render_template("index.html", todos=todos, remaining=remaining)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("INSERT INTO todos (title) VALUES (%s)", (title,))
        db.commit()
    return redirect(url_for("index"))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("UPDATE todos SET done = NOT done WHERE id = %s", (todo_id,))
    db.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    db.commit()
    return redirect(url_for("index"))


@app.route("/edit/<int:todo_id>", methods=["POST"])
def edit(todo_id):
    title = request.form.get("title", "").strip()
    if title:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE todos SET title = %s WHERE id = %s", (title, todo_id))
        db.commit()
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
