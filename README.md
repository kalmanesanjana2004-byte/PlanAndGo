# 🚚 PackAndGo — Online Goods Shifting & Transportation Management System

A modern, full-stack Django web application for booking and managing goods transportation services.

---

## 🎯 Features

### User Module
- Register / Login / Logout / Forgot Password
- Book transportation (Bike, Mini Truck, Pickup Van, Tempo, Large Truck)
- Upload item images
- Real-time booking status tracking
- Payment page (Cash, UPI, Card, Net Banking)
- Review & rating system
- Complaint submission
- Notification system

### Driver Module
- Driver registration with vehicle details
- Accept/reject available bookings
- Update delivery status (Confirmed → Picked Up → In Transit → Delivered)
- Earnings dashboard with monthly chart
- Availability toggle

### Admin Module
- Analytics dashboard with charts (revenue, booking status, vehicle distribution)
- Manage users (activate/deactivate)
- Manage drivers (approve/reject/suspend)
- Manage all bookings
- View payments & revenue
- Handle complaints with responses

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.x, Python 3.13 |
| Database | SQLite |
| Frontend | Bootstrap 5, HTML5, CSS3, JavaScript |
| Icons | Font Awesome 6 |
| Charts | Chart.js |
| Image Upload | Pillow |

---

## 🚀 Quick Start

### 1. Clone / Download the project

```bash
cd PackAndGo
```

### 2. Install dependencies

```bash
pip install django pillow
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Seed sample data

```bash
python manage.py seed_data
```

### 5. Start the server

```bash
python manage.py runserver
```

### 6. Open in browser

```
http://127.0.0.1:8000/
```

---

## 🔑 Login Credentials (after seeding)

| Role | Username | Password | URL |
|------|----------|----------|-----|
| Admin | `admin` | `admin123` | `/admin-panel/` |
| User | `rahul_sharma` | `user123` | `/dashboard/` |
| Driver | `ravi` | `driver123` | `/driver/dashboard/` |
| Django Admin | `admin` | `admin123` | `/admin/` |

---

## 📁 Project Structure

```
PackAndGo/
├── PackAndGo/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/               # Main application
│   ├── models.py       # Database models
│   ├── views.py        # View functions
│   ├── urls.py         # URL routing
│   ├── forms.py        # Form definitions
│   ├── admin.py        # Admin configuration
│   └── management/
│       └── commands/
│           └── seed_data.py
├── templates/          # HTML templates
│   ├── base.html
│   ├── components/     # Reusable components
│   ├── public/         # Landing, About, Services, Contact
│   ├── auth/           # Login, Register, Forgot Password
│   ├── user/           # User dashboard pages
│   ├── driver/         # Driver dashboard pages
│   └── admin_panel/    # Admin dashboard pages
├── static/
│   ├── css/main.css    # Custom styles
│   └── js/main.js      # Custom JavaScript
├── media/              # Uploaded files
├── db.sqlite3          # SQLite database
└── manage.py
```

---

## 🚗 Vehicle Types & Pricing

| Vehicle | Base Price | Per KM Rate |
|---------|-----------|-------------|
| Bike Delivery | ₹50 | ₹8/km |
| Mini Truck | ₹200 | ₹15/km |
| Pickup Van | ₹300 | ₹18/km |
| Tempo | ₹400 | ₹22/km |
| Large Truck | ₹600 | ₹30/km |

**Price Formula:** `Base + (Distance × Rate) + 10% Handling Fee`

---

## 📄 Pages

| Page | URL |
|------|-----|
| Landing | `/` |
| About | `/about/` |
| Services | `/services/` |
| Contact | `/contact/` |
| Register | `/register/` |
| Login | `/login/` |
| User Dashboard | `/dashboard/` |
| New Booking | `/booking/new/` |
| Booking History | `/booking/history/` |
| Booking Detail | `/booking/<id>/` |
| Payment | `/booking/<id>/payment/` |
| Profile | `/profile/` |
| Driver Register | `/driver/register/` |
| Driver Dashboard | `/driver/dashboard/` |
| Admin Dashboard | `/admin-panel/` |

---

## 🎨 UI Design

- **Color Theme:** Dark blue + Purple gradients + White cards
- **Glassmorphism** cards with backdrop blur
- **Smooth animations** and hover effects
- **Mobile responsive** with Bootstrap 5
- **Font Awesome** icons throughout
- **Chart.js** for analytics charts
- **Loading animation** on page load
- **Auto-dismiss** toast notifications
