# Smart Offline College Attendance & Academic Management System

A Flask + MariaDB attendance and academic management system built to run entirely
on a college LAN, with no internet connection required for normal operation.

Roles: **Admin**, **Teacher**, **Student** — each with their own dashboard,
permissions, and views. Core features: bulk attendance, attendance calendar,
low-attendance early warning, analytics, reports (CSV/Excel/PDF), audit log,
and database backup.

---

## Quickest way to start (recommended — no typing commands)

If you don't want to run commands manually every time, use the included
one-click scripts instead of Sections 1–8 below:

**Windows:**
1. Double-click `install.bat` once (installs everything, takes a few minutes).
2. After that, double-click `start.bat` any time to run the system — it
   opens your browser automatically to `http://localhost:5000`.
3. Keep the black window open while using the system; closing it stops the
   server.

**Mac / Linux:**
1. Open a terminal in the `AttendanceSystem` folder and run `./install.sh`
   once.
2. After that, run `./start.sh` any time to start the system.

This does exactly what Sections 1–8 below describe, just without typing each
command by hand. You still need Python installed first (see Section 1) —
these scripts can't install Python itself.

---

## Desktop GUI app (.exe, works fully offline)

Instead of opening a browser, you can run the system as a normal desktop
window:

- **Quick try:** double-click `run_desktop.bat` (after `install.bat` once).
- **Make a real .exe:** double-click `build_exe.bat` once (needs internet
  one time). It creates `dist\AttendanceSystem\AttendanceSystem.exe`.
  Copy that whole folder to any Windows PC and double-click the .exe — no
  Python needed there. The database is stored in a `database` folder next
  to the .exe (keep it; that is your data).

The desktop window is private to that one PC. To let other PCs on the LAN
use the system, run `start.bat` on the server PC instead.

---

## 1. Prerequisites

On the **server PC** only:

- Python 3.10+ (python.org)
- MariaDB or MySQL Server (mariadb.org)

Client PCs (teacher/student/admin computers) need **nothing installed** — just
a web browser, connected to the same LAN/Wi-Fi as the server.

---

## 2. Install Python packages

Open a terminal in the `AttendanceSystem` folder on the server PC:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

---

## 3. Set up MariaDB

Open the MariaDB/MySQL command line (or a GUI tool like HeidiSQL/phpMyAdmin) and run:

```sql
CREATE DATABASE attendance_system CHARACTER SET utf8mb4;
CREATE USER 'attendance_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON attendance_system.* TO 'attendance_user'@'localhost';
FLUSH PRIVILEGES;
```

Only the server PC needs direct database access in the setup described in this README —
client PCs only talk to the Flask web app over HTTP.

---

## 4. Configure environment variables

```bash
cp .env.example .env      # macOS/Linux
copy .env.example .env    # Windows
```

Edit `.env` and fill in:

- `FLASK_SECRET_KEY` — any long random string
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` — matching what you created in step 3

`.env` is never committed to source control and is only read locally.

> **Quick local testing without MariaDB:** set `DB_ENGINE=sqlite` in `.env`
> to use a local SQLite file instead — useful for a first look before setting
> up MariaDB.

---

## 5. Vendor the frontend libraries (for true offline use)

The app deliberately does not load Bootstrap/Chart.js from an internet CDN at
runtime — see `static/vendor/README.txt` for the one-time download steps (run
once, on any PC with internet, then copy the 3 files into `static/vendor/` on
the server PC). Until those files are present, pages will load without
styling/charts.

---

## 6. Initialize the database

```bash
# Windows (cmd):
set FLASK_APP=app.py
# macOS/Linux:
export FLASK_APP=app.py

flask init-db
```

This creates all tables and default attendance thresholds (Warning 75%,
Critical 65% — changeable later from Admin > Settings).

### Optional: load demo data

```bash
flask seed-demo
```

Creates a demo admin, 3 demo teachers, 20 demo students across two divisions,
and roughly 25 sessions of sample attendance history (including a couple of
students deliberately below the warning threshold, so the low-attendance
features are visible immediately).

**Demo credentials (change all passwords before real use):**

| Role    | Username        | Password      |
|---------|-----------------|---------------|
| Admin   | admin           | Admin@123     |
| Teacher | anita.sharma    | Teacher@123   |
| Teacher | ravi.kulkarni   | Teacher@123   |
| Teacher | neha.joshi      | Teacher@123   |
| Student | student001      | Student@123   |
| Student | student002 … student020 | Student@123 |

All demo names, IDs, and records are fictional.

---

## 7. Start the Flask server

```bash
python app.py
```

By default this listens on `0.0.0.0:5000`, meaning it accepts connections
from any device on the LAN, not just the server PC itself.

---

## 8. Access the application

**From the server PC itself:**

```
http://localhost:5000
```

**From another PC on the same LAN/Wi-Fi (teacher, student, or admin machine):**

1. On the server PC, find its local IP address:
   - Windows: `ipconfig` (look for IPv4 Address, e.g. 192.168.1.50)
   - macOS/Linux: `ifconfig` or `ip addr`
2. On the client PC's browser, go to:

   ```
   http://SERVER-IP:5000
   ```

   e.g. `http://192.168.1.50:5000`

Both devices must be connected to the same local network. No internet
connection is required for this to work.

If a client PC can't connect, check the server PC's firewall — allow inbound
connections on port 5000 (or whichever port you configure).

---

## 9. Creating a backup

Go to **Admin > Backup** and click "Create Backup Now".

- If `DB_ENGINE=sqlite`, this copies the database file into `backups/`.
- If using MariaDB/MySQL (the recommended production setup), run this from
  the server PC's terminal instead, then place the resulting file in
  `backups/` if you'd like it listed on the Backup page:

  ```bash
  mysqldump -u attendance_user -p attendance_system > backups/attendance_backup_YYYYMMDD.sql
  ```

  To restore:

  ```bash
  mysql -u attendance_user -p attendance_system < backups/attendance_backup_YYYYMMDD.sql
  ```

---

## 10. Project structure

```
AttendanceSystem/
├── app.py                  Flask app factory, CLI commands, entrypoint
├── config.py                Configuration (env-driven)
├── requirements.txt
├── .env.example
├── models/__init__.py        All SQLAlchemy models
├── routes/                   Blueprints: auth, admin, teacher, student, reports, errors
├── services/seed.py          Demo data seeding
├── utils/helpers.py          Role guards, audit logging, attendance calculations
├── templates/                 Jinja2 templates (auth/admin/teacher/student/errors)
├── static/                    css/js/vendor (locally hosted, no CDN dependency)
├── database/                  SQLite file lives here if DB_ENGINE=sqlite
├── backups/                   Backup files
└── reports/                   Reserved for server-side report caching
```

---

## 11. Deploying live on the internet (GitHub + Render)

This system was originally designed for offline college-LAN use, but it can
also be deployed as a normal live website that anyone with the URL can open.

**Before going public, understand these trade-offs:**
- **CSRF protection is not enabled.** That's an acceptable risk on a closed
  LAN, but for a public site, ask to have CSRF protection added to every
  form before using it with real people.
- **Use a real PostgreSQL database, not SQLite.** Most free hosts (including
  Render's free tier) wipe local files like a SQLite database on every
  restart/redeploy. Attach a real (free) PostgreSQL database instead — the
  app already supports this automatically (see below).
- **Change the default admin password immediately** after first deploy —
  anyone who finds the URL can otherwise try `admin` / `Admin@123`.

### Step 1 — Push the code to GitHub

```bash
cd AttendanceSystem
git init
git add .
git commit -m "College attendance system"
```

Then create a new empty repository on github.com (no README/license, so it
stays empty), and push:

```bash
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

(`.env`, `venv/`, and the local database file are already excluded via
`.gitignore`, so nothing sensitive gets uploaded.)

### Step 2 — Deploy on Render (free tier)

1. Go to render.com and sign up/log in (you can sign in with your GitHub
   account).
2. **New +** → **Blueprint** → connect your GitHub repo → Render will read
   `render.yaml` (already included in this project) and set up both the
   web service and a free PostgreSQL database automatically.
   - If you'd rather do it by hand instead: **New +** → **Web Service** →
     connect your repo → Build Command: `pip install -r requirements.txt` →
     Start Command: `gunicorn app:app`. Then separately **New +** →
     **PostgreSQL** (free) and copy its "Internal Database URL" into the web
     service's environment variables as `DATABASE_URL`.
3. Under the web service's **Environment** tab, set:
   - `FLASK_SECRET_KEY` — any long random string
   - `FLASK_DEBUG` — `False`
4. Click **Deploy**. Render gives you a live URL like
   `https://your-app-name.onrender.com` — that's your public website.
5. Log in with `admin` / `Admin@123` (created automatically on first start)
   and **change the password immediately**.

Every time you `git push` new changes, Render redeploys automatically.

### Alternative platforms

Railway.app and PythonAnywhere.com work similarly (GitHub-connected,
free tier, Postgres/MySQL add-ons) if you'd rather not use Render.

---

## 12. Security notes

- Passwords are hashed with Werkzeug's `generate_password_hash` (never stored in plain text).
- All database queries use the SQLAlchemy ORM (parameterized), preventing SQL injection.
- Sessions are server-side (Flask-Login) with a configurable timeout (`SESSION_LIFETIME_MINUTES` in `.env`).
- Role-based route guards (`@roles_required`) block admin/teacher/student pages from being accessed by the wrong role.
- Deactivating a student or teacher disables their login but **preserves** their attendance history — nothing is deleted.
- Change every demo password before using this system with real student data.

---

## 13. Verification notes

This project was built and statically verified (every Python file compiles;
every template was rendered successfully against realistic mock data matching
the actual model relationships; every `url_for()` reference in the templates
was checked against the registered Flask routes) in an environment without
internet or MariaDB access, so it could not be run end-to-end there. Before
relying on it in production, please:

1. Run `flask init-db` and `flask seed-demo`, then manually walk through:
   login (all 3 roles) → dashboard → take attendance → student calendar →
   analytics → reports export (CSV/Excel/PDF) → backup.
2. Double-check MariaDB connection settings for your environment.
3. For very large classes (100+ students), consider adding pagination to the
   students list if load time becomes noticeable.
