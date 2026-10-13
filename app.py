import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DB_PATH = os.environ.get("DATABASE_PATH", "gadget_lending.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        );
        CREATE TABLE IF NOT EXISTS gadgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            total_quantity INTEGER NOT NULL DEFAULT 1,
            available_quantity INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            gadget_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            purpose TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            requested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            approved_at TEXT,
            returned_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(gadget_id) REFERENCES gadgets(id)
        );
        """)
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@devapps.local")
        admin_password = os.environ.get("ADMIN_PASSWORD", "Admin123!")
        admin = conn.execute("SELECT id FROM users WHERE email=?", (admin_email,)).fetchone()
        if not admin:
            conn.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                         ("Administrator", admin_email, generate_password_hash(admin_password), "admin"))
        if conn.execute("SELECT COUNT(*) AS n FROM gadgets").fetchone()["n"] == 0:
            conn.executemany(
                "INSERT INTO gadgets(name,category,total_quantity,available_quantity) VALUES(?,?,?,?)",
                [("Laptop", "Computer", 8, 8), ("Projector", "Presentation", 3, 3),
                 ("Arduino Kit", "Electronics", 10, 10), ("Digital Camera", "Media", 4, 4)]
            )

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("This page is only available to the administrator.", "danger")
            return redirect(url_for("inventory"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("inventory"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter your name, a valid email, and a password of at least 6 characters.", "danger")
        else:
            try:
                with db() as conn:
                    conn.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'student')",
                                 (name, email, generate_password_hash(password)))
                flash("Registration successful. You can now log in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That email address is already registered.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        if user and check_password_hash(
            user["password_hash"], password
        ):
            session.clear()
            session.update(
                user_id=user["id"],
                name=user["name"],
                role=user["role"]
            )

            flash(
                "Welcome, {}!".format(user["name"]),
                "success"
            )

            if user["role"] == "admin":
                return redirect(url_for("admin_requests"))

            return redirect(url_for("inventory"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "info")
    return redirect(url_for("login"))

@app.route("/inventory")
@login_required
def inventory():
    with db() as conn:
        gadgets = conn.execute("SELECT * FROM gadgets ORDER BY name").fetchall()
    return render_template("inventory.html", gadgets=gadgets)

@app.route("/borrow/<int:gadget_id>", methods=["POST"])
@login_required
def borrow(gadget_id):
    if session.get("role") == "admin":
        flash("Admin accounts cannot submit student borrowing requests.", "warning")
        return redirect(url_for("inventory"))
    purpose = request.form.get("purpose", "").strip()
    try:
        quantity = int(request.form.get("quantity", "1"))
    except ValueError:
        quantity = 0
    with db() as conn:
        gadget = conn.execute("SELECT * FROM gadgets WHERE id=?", (gadget_id,)).fetchone()
        if not gadget:
            flash("Gadget not found.", "danger")
        elif quantity < 1 or quantity > gadget["available_quantity"]:
            flash("Choose a quantity currently available.", "danger")
        elif not purpose:
            flash("Please enter the purpose of borrowing.", "danger")
        else:
            conn.execute("INSERT INTO loans(user_id,gadget_id,quantity,purpose) VALUES(?,?,?,?)",
                         (session["user_id"], gadget_id, quantity, purpose))
            flash("Borrowing request submitted for admin approval.", "success")
    return redirect(url_for("requests_page"))

@app.route("/requests")
@login_required
def requests_page():
    with db() as conn:
        if session.get("role") == "admin":
            loans = conn.execute("""SELECT l.*,u.name AS student_name,g.name AS gadget_name
                FROM loans l JOIN users u ON u.id=l.user_id JOIN gadgets g ON g.id=l.gadget_id
                ORDER BY l.requested_at DESC""").fetchall()
        else:
            loans = conn.execute("""SELECT l.*,g.name AS gadget_name
                FROM loans l JOIN gadgets g ON g.id=l.gadget_id WHERE l.user_id=?
                ORDER BY l.requested_at DESC""", (session["user_id"],)).fetchall()
    return render_template("requests.html", loans=loans)

@app.route("/admin/requests")
@admin_required
def admin_requests():
    with db() as conn:
        loans = conn.execute("""SELECT l.*,u.name AS student_name,u.email,g.name AS gadget_name,
            g.available_quantity FROM loans l JOIN users u ON u.id=l.user_id
            JOIN gadgets g ON g.id=l.gadget_id ORDER BY
            CASE l.status WHEN 'Pending' THEN 0 ELSE 1 END, l.requested_at DESC""").fetchall()
    return render_template("admin_requests.html", loans=loans)

@app.route("/admin/loan/<int:loan_id>/<action>", methods=["POST"])
@admin_required
def decide_loan(loan_id, action):
    if action not in ("approve", "reject"):
        flash("Invalid action.", "danger")
        return redirect(url_for("admin_requests"))
    with db() as conn:
        loan = conn.execute("""SELECT l.*,g.available_quantity,g.name AS gadget_name
            FROM loans l JOIN gadgets g ON g.id=l.gadget_id WHERE l.id=?""", (loan_id,)).fetchone()
        if not loan or loan["status"] != "Pending":
            flash("This request no longer has a pending status.", "warning")
        elif action == "reject":
            conn.execute("UPDATE loans SET status='Rejected' WHERE id=?", (loan_id,))
            flash("Borrowing request rejected.", "info")
        elif loan["quantity"] > loan["available_quantity"]:
            flash("Not enough available quantity to approve this request.", "danger")
        else:
            conn.execute("UPDATE gadgets SET available_quantity=available_quantity-? WHERE id=?",
                         (loan["quantity"], loan["gadget_id"]))
            conn.execute("UPDATE loans SET status='Approved', approved_at=CURRENT_TIMESTAMP WHERE id=?", (loan_id,))
            flash("Borrowing request approved.", "success")
    return redirect(url_for("admin_requests"))

@app.route("/returns")
@login_required
def returns_page():
    with db() as conn:
        if session.get("role") == "admin":
            loans = conn.execute("""SELECT l.*,u.name AS student_name,g.name AS gadget_name
                FROM loans l JOIN users u ON u.id=l.user_id JOIN gadgets g ON g.id=l.gadget_id
                WHERE l.status='Approved' ORDER BY l.approved_at DESC""").fetchall()
        else:
            loans = conn.execute("""SELECT l.*,g.name AS gadget_name FROM loans l
                JOIN gadgets g ON g.id=l.gadget_id WHERE l.user_id=? AND l.status='Approved'
                ORDER BY l.approved_at DESC""", (session["user_id"],)).fetchall()
    return render_template("returns.html", loans=loans)

@app.route("/return/<int:loan_id>", methods=["POST"])
@login_required
def confirm_return(loan_id):
    with db() as conn:
        loan = conn.execute("SELECT * FROM loans WHERE id=?", (loan_id,)).fetchone()
        allowed = loan and loan["status"] == "Approved" and (
            session.get("role") == "admin" or loan["user_id"] == session.get("user_id"))
        if not allowed:
            flash("This return cannot be confirmed.", "danger")
        else:
            conn.execute("UPDATE loans SET status='Returned', returned_at=CURRENT_TIMESTAMP WHERE id=?", (loan_id,))
            conn.execute("UPDATE gadgets SET available_quantity=available_quantity+? WHERE id=?",
                         (loan["quantity"], loan["gadget_id"]))
            flash("Return confirmed and inventory updated.", "success")
    return redirect(url_for("returns_page"))

@app.route("/history")
@login_required
def history():
    with db() as conn:
        if session.get("role") == "admin":
            loans = conn.execute("""SELECT l.*,u.name AS student_name,g.name AS gadget_name
                FROM loans l JOIN users u ON u.id=l.user_id JOIN gadgets g ON g.id=l.gadget_id
                ORDER BY l.requested_at DESC""").fetchall()
        else:
            loans = conn.execute("""SELECT l.*,g.name AS gadget_name FROM loans l
                JOIN gadgets g ON g.id=l.gadget_id WHERE l.user_id=?
                ORDER BY l.requested_at DESC""", (session["user_id"],)).fetchall()
    return render_template("history.html", loans=loans)

@app.route("/admin/gadgets", methods=["GET", "POST"])
@admin_required
def manage_gadgets():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        try:
            quantity = int(request.form.get("quantity", "0"))
        except ValueError:
            quantity = 0
        if name and category and quantity > 0:
            with db() as conn:
                conn.execute("INSERT INTO gadgets(name,category,total_quantity,available_quantity) VALUES(?,?,?,?)",
                             (name, category, quantity, quantity))
            flash("Gadget added to inventory.", "success")
        else:
            flash("Enter a name, category, and quantity greater than zero.", "danger")
        return redirect(url_for("manage_gadgets"))
    with db() as conn:
        gadgets = conn.execute("SELECT * FROM gadgets ORDER BY name").fetchall()
    return render_template("manage_gadgets.html", gadgets=gadgets)

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
