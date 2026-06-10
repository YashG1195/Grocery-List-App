from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
# pyrefly: ignore [missing-import]
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, GroceryList, GroceryItem, CATEGORIES, UNITS, CATEGORY_ICONS
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "grocery-dev-fallback-key-2024")
# Use an absolute path so the DB is always created next to app.py
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "grocery.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access your grocery lists."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ──────────────────────────────────────────────
# Auth Routes
# ──────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
        elif User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f"Welcome, {username}! Start building your grocery lists.", "success")
            return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=request.form.get("remember"))
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# ──────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────

@app.route("/")
@login_required
def dashboard():
    favourites = GroceryList.query.filter_by(user_id=current_user.id, is_favourite=True)\
        .order_by(GroceryList.created_at.desc()).all()
    all_lists = GroceryList.query.filter_by(user_id=current_user.id)\
        .order_by(GroceryList.created_at.desc()).all()
    return render_template("index.html", favourites=favourites, all_lists=all_lists)


# ──────────────────────────────────────────────
# List Management
# ──────────────────────────────────────────────

@app.route("/list/new", methods=["POST"])
@login_required
def new_list():
    name = request.form.get("name", "").strip()
    if not name:
        flash("List name cannot be empty.", "error")
        return redirect(url_for("dashboard"))
    grocery_list = GroceryList(name=name, user_id=current_user.id)
    db.session.add(grocery_list)
    db.session.commit()
    flash(f'List "{name}" created!', "success")
    return redirect(url_for("list_detail", list_id=grocery_list.id))


@app.route("/list/<int:list_id>")
@login_required
def list_detail(list_id):
    grocery_list = GroceryList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    # Group items by category
    items_by_category = {}
    for item in grocery_list.items:
        cat = item.category
        if cat not in items_by_category:
            items_by_category[cat] = []
        items_by_category[cat].append(item)
    # Sort categories in CATEGORIES order
    sorted_categories = [(c, items_by_category[c]) for c in CATEGORIES if c in items_by_category]
    return render_template(
        "list_detail.html",
        grocery_list=grocery_list,
        sorted_categories=sorted_categories,
        categories=CATEGORIES,
        units=UNITS,
        category_icons=CATEGORY_ICONS,
    )


@app.route("/list/<int:list_id>/delete", methods=["POST"])
@login_required
def delete_list(list_id):
    grocery_list = GroceryList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    name = grocery_list.name
    db.session.delete(grocery_list)
    db.session.commit()
    flash(f'List "{name}" deleted.', "info")
    return redirect(url_for("dashboard"))


@app.route("/list/<int:list_id>/favourite", methods=["POST"])
@login_required
def toggle_favourite(list_id):
    grocery_list = GroceryList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    grocery_list.is_favourite = not grocery_list.is_favourite
    db.session.commit()
    return jsonify({"is_favourite": grocery_list.is_favourite})


@app.route("/list/<int:list_id>/rename", methods=["POST"])
@login_required
def rename_list(list_id):
    grocery_list = GroceryList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    new_name = request.form.get("name", "").strip()
    if new_name:
        grocery_list.name = new_name
        db.session.commit()
        flash(f'List renamed to "{new_name}".', "success")
    return redirect(url_for("list_detail", list_id=list_id))


# ──────────────────────────────────────────────
# Item Management
# ──────────────────────────────────────────────

@app.route("/list/<int:list_id>/item/add", methods=["POST"])
@login_required
def add_item(list_id):
    grocery_list = GroceryList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "Other")
    quantity = request.form.get("quantity", 1)
    unit = request.form.get("unit", "pcs")
    notes = request.form.get("notes", "").strip()

    if not name:
        flash("Item name cannot be empty.", "error")
        return redirect(url_for("list_detail", list_id=list_id))

    try:
        quantity = float(quantity)
    except (ValueError, TypeError):
        quantity = 1.0

    item = GroceryItem(
        list_id=grocery_list.id,
        name=name,
        category=category,
        quantity=quantity,
        unit=unit,
        notes=notes,
    )
    db.session.add(item)
    db.session.commit()
    flash(f'"{name}" added to list.', "success")
    return redirect(url_for("list_detail", list_id=list_id))


@app.route("/item/<int:item_id>/toggle", methods=["POST"])
@login_required
def toggle_item(item_id):
    item = GroceryItem.query.get_or_404(item_id)
    # Verify ownership
    if item.grocery_list.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    item.is_checked = not item.is_checked
    db.session.commit()
    progress = item.grocery_list.progress
    return jsonify({"is_checked": item.is_checked, "progress": progress})


@app.route("/item/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = GroceryItem.query.get_or_404(item_id)
    if item.grocery_list.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    list_id = item.list_id
    db.session.delete(item)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/list/<int:list_id>/clear-checked", methods=["POST"])
@login_required
def clear_checked(list_id):
    grocery_list = GroceryList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    GroceryItem.query.filter_by(list_id=list_id, is_checked=True).delete()
    db.session.commit()
    flash("Checked items removed.", "info")
    return redirect(url_for("list_detail", list_id=list_id))


# ──────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
