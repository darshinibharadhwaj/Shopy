# Shopy – Full-Stack E-Commerce Web Application

A full-stack e-commerce platform built with Flask, SQLAlchemy, and vanilla JS. Supports product browsing/search, user registration & login, a shopping cart, and checkout.

## Features
- Product catalog with search
- User authentication (register/login/logout) with hashed passwords
- Session-based shopping cart
- Checkout flow
- Responsive UI (mobile & desktop)

## Tech Stack
Python, Flask, Flask-SQLAlchemy, MySQL (or SQLite for local dev), HTML, CSS, JavaScript

## Getting Started

### 1. Clone and install dependencies
```bash
git clone https://github.com/<your-username>/shopy.git
cd shopy
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run (SQLite, zero config)
```bash
python app.py
```
Visit http://127.0.0.1:5000

### 3. (Optional) Use MySQL instead
```bash
export SHOPY_DB_URI="mysql+pymysql://<user>:<password>@localhost/shopy_db"
python app.py
```

## Project Structure
```
shopy/
├── app.py                 # Flask app, models, routes
├── requirements.txt
├── templates/             # Jinja2 HTML templates
└── static/
    ├── css/style.css
    └── js/script.js
```

## Screenshots
_Add screenshots here once deployed (see portfolio guide)._

## License
MIT
