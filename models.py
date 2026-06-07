from flask_sqlalchemy import SQLAlchemy
# pyrefly: ignore [missing-import]
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

CATEGORIES = [
    "Produce",
    "Dairy & Eggs",
    "Meat & Seafood",
    "Bakery",
    "Frozen Foods",
    "Beverages",
    "Snacks",
    "Pantry",
    "Personal Care",
    "Household",
    "Other",
]

UNITS = ["pcs", "kg", "g", "lbs", "oz", "L", "ml", "pack", "dozen", "bunch", "can", "bottle"]

CATEGORY_ICONS = {
    "Produce": "🥦",
    "Dairy & Eggs": "🥛",
    "Meat & Seafood": "🥩",
    "Bakery": "🍞",
    "Frozen Foods": "🧊",
    "Beverages": "🥤",
    "Snacks": "🍿",
    "Pantry": "🫙",
    "Personal Care": "🧴",
    "Household": "🏠",
    "Other": "📦",
}


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lists = db.relationship("GroceryList", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class GroceryList(db.Model):
    __tablename__ = "grocery_lists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    is_favourite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("GroceryItem", backref="grocery_list", lazy=True, cascade="all, delete-orphan")

    @property
    def total_items(self):
        return len(self.items)

    @property
    def checked_items(self):
        return sum(1 for item in self.items if item.is_checked)

    @property
    def progress(self):
        if self.total_items == 0:
            return 0
        return int((self.checked_items / self.total_items) * 100)


class GroceryItem(db.Model):
    __tablename__ = "grocery_items"
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey("grocery_lists.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80), default="Other")
    quantity = db.Column(db.Float, default=1)
    unit = db.Column(db.String(30), default="pcs")
    notes = db.Column(db.String(300), default="")
    is_checked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
