# Gym Monitoring CLI

A lightweight Python command-line tool for managing gym member admissions and tracking fee due dates.

## Features

- Add new members with admission date and fee schedule.
- Record payments and calculate next due dates automatically.
- List members with status highlighting overdue fees.
- Export member roster to CSV.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
gym-monitor --help
```

## Usage Examples

1. **Add a member**
   ```bash
   gym-monitor add-member \
     --name "Jane Doe" \
     --phone "+91-9876543210" \
     --plan-months 3 \
     --fee-amount 2500
   ```

2. **Record a payment**
   ```bash
   gym-monitor record-payment --member-id 1 --amount 2500
   ```

3. **List members**
   ```bash
   gym-monitor list-members
   ```

## Data Storage

Data is stored locally in an SQLite database under `~/.local/share/gym-monitoring/gym.db`. You can override the location with the `--db` flag on any command.
The default configuration supports up to 5,000 active member records at a time.

## Optional Browser Dashboard

For a lightweight, standalone dashboard that runs entirely in the browser (no server required):

1. Open `frontend/index.html` in any modern browser.
2. Add members via the form; records are stored in the browser's `localStorage`.
3. Use the dashboard to review upcoming or overdue fees and to record payments quickly.

> The dashboard is front-end only and is not yet wired to the CLI/database. Keep using the CLI for authoritative records.

## Development

Run the formatter and tests:

```bash
pip install -r requirements-dev.txt
pytest
```

## Roadmap

- SMS reminders for upcoming dues.
- Web dashboard for staff.
- Attendance tracking integration.
