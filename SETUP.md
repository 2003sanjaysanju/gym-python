# Django Gym Monitoring Setup

## Quick Start

**Important:** Ubuntu/Debian systems require a virtual environment. Follow these steps:

1. **Install python3-venv (if not already installed):**
   ```bash
   sudo apt install python3.12-venv
   ```

2. **Create and activate virtual environment:**
   ```bash
   cd /home/sanjay.santhosh@tahrtech.com/Documents/gym-monitoring
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create admin user (optional, for Django admin):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Open your browser to: `http://127.0.0.1:8000/`
   - Login with:
     - Username: `admin`
     - Password: `power25`

## Note

Always activate the virtual environment before running Django commands:
```bash
source .venv/bin/activate
```

## Features

- ✅ Member management (add, view, delete)
- ✅ Payment recording
- ✅ Search by name or phone
- ✅ Filter by payment status (overdue, due soon, all)
- ✅ Dashboard with statistics
- ✅ Login authentication
- ✅ 5000 member limit

## Database

The application uses SQLite by default (stored in `db.sqlite3`). For production, consider switching to PostgreSQL or MySQL.

## Static Files

Static files (CSS, images) are served from `gym/static/gym/`. Run `python manage.py collectstatic` in production.

