# Factory HRMS & Attendance Portal

A professional, full-stack **Django-based Human Resource Management System (HRMS)** designed for industrial factory environments. This system handles complex role-based access, automated attendance tracking, and leave management with a premium, responsive dashboard.

---

## 🔹 Key Modules

### 👥 Employee Management (HR Admin)
- Combined User & Employee profile management.
- Role-based access control (Admin, Manager, Employee).
- Integrated Add/Edit/View workflows for the workforce.

### 🕒 Attendance & Shifts
- Automated check-in/check-out tracking.
- Support for multiple shifts (Morning, Evening, Night).
- Real-time late arrival detection and cross-midnight shift handling.

### 🏖️ Leave Management
- Leave balances (Annual, Medical, Casual) with allocated vs used tracking.
- Interactive leave application workflow with manager approval.
- Dashboards featuring live leave balance tiles.

### ⏱️ Overtime System
- Automatic overtime calculation based on shift end times.
- Approval workflow with manager comments.

### 📊 Professional Dashboards
- **Admin Dashboard**: Real-time KPIs (Present, Absent, On Leave, Pending Tasks).
- **Employee Dashboard**: Leave balance tiles, today's status, and quick-action buttons.
- Fully responsive design using Bootstrap 5 and FontAwesome 6 icons.

---

## 🔹 Tech Stack

- **Backend:** Django 6.0 (Python)
- **Database:** SQLite (Development) / PostgreSQL-Ready
- **Styling:** Vanilla CSS + Bootstrap 5 (Premium Custom UI)
- **Authentication:** Custom Django Auth with Role-Based Mixins
- **Environment Management:** python-dotenv (Security First)

---

## 🔹 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd factory_employee_portal
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to a new file named `.env` and fill in your local secrets:
```bash
cp .env.example .env
```
*Note: Ensure `DEBUG=True` for local development.*

### 5. Finalize Database & Static Files
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

### 6. Create Admin User & Run
```bash
python manage.py createsuperuser
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` to access the portal.

---

## 🔹 Production Deployment Checklist
- [ ] Set `DEBUG=False` in `.env`.
- [ ] Generate a fresh `SECRET_KEY`.
- [ ] Configure `ALLOWED_HOSTS` with your production domain.
- [ ] Ensure a production-grade web server (Gunicorn/Nginx) is configured.
- [ ] Run `python manage.py check --deploy`.

---

## 🚀 Deploy to Render

This project is pre-configured for one-click deployment on [Render](https://render.com).

### 1. Push to GitHub
Create a new private/public repository on GitHub and push your code there.

### 2. Connect to Render
1. Log in to your Render dashboard.
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically detect the `render.yaml` file and set up:
   - A **Web Service** running Gunicorn and Postgres.
   - Automated migrations and static file collection via `build.sh`.

### 3. Final Production Setup
After deployment, use the Render **Dashboard** to create your first production admin:
- Go to the "Shell" tab of your service.
- Run: `python manage.py createsuperuser`
