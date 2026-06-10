# 🛒 GroceryFlow

🚀 **Live Demo:** [https://grocery-list-app-c63k.onrender.com](https://grocery-list-app-c63k.onrender.com)

A user-friendly **grocery shopping manager** built with Python & Flask. Create, organize, and manage your grocery lists effortlessly — with category sorting, quantity specification, real-time updates, and favourite lists for quick access.

## ✨ Features

- 🔐 **User Authentication** — Register & login with secure hashed passwords
- 📋 **Multiple Lists** — Create, rename, and delete as many lists as you need
- ⭐ **Favourites** — Star lists for quick access on future shopping trips
- 🥦 **Category Sorting** — 11 categories (Produce, Dairy, Meat, Bakery, Frozen, Beverages, Snacks, Pantry, Personal Care, Household, Other)
- ⚖️ **Quantity & Units** — Specify amounts (e.g. 2.5 kg, 1 dozen, 3 cans)
- ✅ **Real-time Check-off** — Mark items as done without page reloads (Fetch API)
- 📊 **Progress Tracking** — Animated circular progress ring per list
- 🗒️ **Item Notes** — Add details like "organic" or "low-sodium"
- 🎨 **Dark Glassmorphism UI** — Modern, responsive design with micro-animations

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/grocery-list-app.git
cd grocery-list-app

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Open your browser at **http://127.0.0.1:5000**

## 📁 Project Structure

```
grocery-list-app/
├── app.py                  # Flask app & all routes
├── models.py               # SQLAlchemy models (User, GroceryList, GroceryItem)
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/style.css       # Dark glassmorphism design system
│   └── js/app.js           # Fetch API real-time interactions
└── templates/
    ├── base.html           # Layout shell
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── index.html          # Dashboard
    └── list_detail.html    # List detail & item management
```

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-Login, Flask-SQLAlchemy |
| Database | SQLite (via SQLAlchemy ORM) |
| Frontend | HTML5, Vanilla CSS, Vanilla JavaScript |
| Fonts | Outfit (Google Fonts) |
| Icons | Font Awesome 6 |

## 📸 Screenshots

> Register → Login → Dashboard → Add Lists → Add Items → Check off → Track Progress

## 📄 License

MIT License — feel free to use and modify.
