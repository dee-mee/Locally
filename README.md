# 🛒 Mini Inventory + Billing System

A lightweight, web-based solution for small retail businesses to manage inventory and process sales.

## Features

- 📦 Inventory Management
- 💰 Point of Sale (POS) System
- 🧾 Receipt Generation
- 📊 Sales Tracking & Reporting
- 🔔 Low Stock Alerts
- 🔒 User Authentication
- 🔄 Automated Backups

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap 5
- **Database:** SQLite (default), can be configured for MySQL
- **Automation:** Bash scripts

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mini-inventory-system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the admin panel**
   - Visit: http://127.0.0.1:8000/admin/
   - Login with your superuser credentials

## Project Structure

```
mini-inventory-system/
├── core/               # Django project settings
├── inventory/          # Inventory management app
├── pos/                # Point of Sale app
├── reports/            # Reporting app
├── frontend/           # Frontend assets
│   ├── static/         # CSS, JS, images
│   └── templates/      # HTML templates
└── scripts/            # Automation scripts
    ├── backup.sh       # Database backup
    └── report.sh       # Sales report generator
```

## License

MIT License - Feel free to use and modify for your business needs.
