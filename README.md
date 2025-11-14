# Gym Monitoring System

A Django web application for managing gym member admissions and tracking fee due dates.

## Features

- ✅ Web-based dashboard for easy access
- ✅ Add new members with admission date and fee schedule
- ✅ Record payments and calculate next due dates automatically
- ✅ Search members by name or phone number
- ✅ Filter members by payment status (overdue, due soon, all)
- ✅ Dashboard statistics (total members, overdue, due soon)
- ✅ Secure login authentication
- ✅ Member limit: 5,000 members
- ✅ Responsive design with modern UI

## Quick Start

See [SETUP.md](SETUP.md) for detailed setup instructions.

**Quick setup:**
```bash
# Install python3-venv if needed
sudo apt install python3.12-venv

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

Then open `http://127.0.0.1:8000/` in your browser.

## Login Credentials

- **Username:** `admin`
- **Password:** `power25`

## Data Storage

Data is stored in an SQLite database (`db.sqlite3`) in the project root. The application supports up to 5,000 active member records.

## Project Structure

```
gym-monitoring/
├── gym/              # Django app
│   ├── models.py     # Member and Payment models
│   ├── views.py      # View functions
│   ├── forms.py      # Django forms
│   ├── templates/    # HTML templates
│   └── static/       # CSS and static assets
├── gym_web/          # Django project settings
├── manage.py         # Django management script
└── requirements.txt  # Python dependencies
```

## Development

The project uses Django 5.2+ and Python 3.9+.

## Roadmap

- SMS reminders for upcoming dues
- Payment history reports
- Export to CSV/Excel
- Attendance tracking integration
- Multi-user support with roles
