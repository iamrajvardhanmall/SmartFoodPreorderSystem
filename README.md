<h1 align="center">🍱 Smart Food Stall Pre-Ordering System</h1>

<p align="center">
  A multi-stall campus food pre-ordering web app built with <strong>Django 6</strong> &amp; <strong>Bootstrap 5</strong>.
  Students pre-order meals from multiple stalls, stall owners manage their own orders,
  and admins oversee the entire system — all in one place.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-6.0.2-green?style=flat-square&logo=django" />
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/Bootstrap-5.3-purple?style=flat-square&logo=bootstrap" />
  <img src="https://img.shields.io/badge/Database-SQLite-lightgrey?style=flat-square&logo=sqlite" />
  <img src="https://img.shields.io/badge/Charts-Chart.js%204.4-orange?style=flat-square" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [User Roles](#-user-roles)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Sample Data](#-sample-data)
- [Screenshots & Pages](#-screenshots--pages)
- [URL Reference](#-url-reference)
- [How Stall Owner Accounts Work](#-how-stall-owner-accounts-work)

---

## 🌐 Overview

University canteens are chaotic during break times — long queues, cold food, and wasted time. The **Smart Food Stall Pre-Ordering System** solves this by letting students pre-order food from any campus stall before their break, with real-time slot capacity tracking.

> Built as a 3rd-year B.Tech CSE mini-project.

---

## ✨ Features

### 👨‍🎓 Student
- Register and log in securely
- Browse all active food stalls and their menus
- Filter menu by stall
- Place pre-orders from **any stall** in a single order form
- Live slot capacity bar — see how full each time slot is before ordering
- Filter food items by stall directly in the order form (no page reload)
- View full order history filtered by status (Pending / Completed / Cancelled) and by stall
- Cancel pending orders (releases the time slot seat)
- Dashboard with stats, stall-wise order breakdown, and slot availability

### 🏪 Stall Owner
- Dedicated login → goes directly to their stall dashboard
- **5-digit unique Stall Code** as their owner identity
- View all orders placed at their specific stall
- Filter orders by status
- Mark orders as **Completed** ✅ or **Cancelled** ❌
- See today's order count and revenue at a glance

### 🔧 Admin
- Full system dashboard: today's orders, revenue, pending count
- **Per-stall revenue breakdown** for the current day
- Create / edit / delete food stalls
- Create stall owner accounts (auto-generates 5-digit code)
- Add / edit / delete food items (assign to stall)
- Manage time slots and their capacities
- Update order statuses for all students
- **Demand Analytics** page:
  - Bar chart: orders per food item (last 7 days)
  - Bar chart: orders per stall (last 7 days)
  - AI demand prediction (7-day moving average, flags "High Demand" items)
  - Slot occupancy table

---

## 👥 User Roles

| Role | How to Create | Where They Go After Login |
|---|---|---|
| **Admin** | `python manage.py createsuperuser` or Django `/admin/` | `/admin-panel/` |
| **Stall Owner** | Admin creates via `/admin-panel/stall-owners/` | `/stall-owner/dashboard/` |
| **Student** | Self-register at `/register/` | `/dashboard/` |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0.2 (Python 3.13) |
| Frontend | Bootstrap 5.3, Bootstrap Icons |
| Database | SQLite (development) |
| Charts | Chart.js 4.4 (CDN) |
| Image uploads | Pillow 12.x |
| Auth | Django built-in auth (session-based) |

---

## 🗂 Project Structure

```
Smart-Food-Pre-order-System/
├── foodstall/                  # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── preorder/                   # Main Django app
│   ├── migrations/
│   ├── fixtures/
│   │   └── stalls_and_items.json   # Sample stalls, food items, time slots
│   ├── templates/
│   │   ├── base.html               # Shared nav + layout
│   │   ├── home.html               # Public landing page (stall cards)
│   │   ├── registration/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── student/
│   │   │   ├── dashboard.html
│   │   │   ├── menu.html
│   │   │   ├── order.html
│   │   │   └── my_orders.html
│   │   ├── stall_owner/
│   │   │   └── dashboard.html      # Stall owner order management
│   │   └── admin_dashboard/
│   │       ├── dashboard.html
│   │       ├── stalls.html
│   │       ├── stall_owners.html   # Create/manage stall owner accounts
│   │       ├── edit_stall.html
│   │       ├── food_items.html
│   │       ├── edit_food.html
│   │       ├── time_slots.html
│   │       ├── edit_slot.html
│   │       └── analytics.html
│   ├── models.py       # FoodStall, FoodItem, TimeSlot, Order, DemandAnalytics, StallOwner
│   ├── views.py        # All view functions (student, stall owner, admin)
│   ├── forms.py        # All Django forms
│   ├── urls.py         # URL patterns
│   ├── admin.py        # Django admin config
│   └── custom_filters.py   # Template filters: percentage, subtract, multiply
├── static/
│   ├── css/style.css
│   └── js/
│       ├── main.js
│       └── order.js    # Live slot capacity + stall filter logic
├── manage.py
└── requirements.txt
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Smart-Food-Pre-order-System.git
cd Smart-Food-Pre-order-System
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django==6.0.2 pillow
```

Or if a `requirements.txt` is present:

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create an admin (superuser)

```bash
python manage.py createsuperuser
```

### 6. Load sample data (stalls, food items, time slots)

```bash
python manage.py loaddata preorder/fixtures/stalls_and_items.json
```

This loads:
- **3 food stalls** (South Indian, North Indian, Snacks & Beverages)
- **6 food items** assigned to their respective stalls
- **5 time slots** across the day

### 7. Start the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

---

## 🗃 Sample Data

After loading the fixture you'll have:

| Stall | Items | Location |
|---|---|---|
| Stall A — South Indian | Masala Dosa ₹35, Idli ₹20 | Block A, Ground Floor |
| Stall B — North Indian | Aloo Paratha ₹30, Rajma Rice ₹45 | Block B, First Floor |
| Stall C — Snacks & Beverages | Veg Sandwich ₹25, Fresh Lime Soda ₹15 | Block C, Ground Floor |

**Time Slots:** 10:00–10:15 AM · 10:15–10:30 AM · 12:30–12:45 PM · 12:45–1:00 PM · 3:30–3:45 PM

---

## 📸 Screenshots & Pages

| Page | URL | Role |
|---|---|---|
| Landing Page (Stall Cards) | `/` | Public |
| Register | `/register/` | Public |
| Login | `/login/` | Public |
| Student Dashboard | `/dashboard/` | Student |
| Menu (grouped by stall) | `/menu/` | Student |
| Place Order | `/order/` | Student |
| My Orders | `/my-orders/` | Student |
| Stall Owner Dashboard | `/stall-owner/dashboard/` | Stall Owner |
| Admin Dashboard | `/admin-panel/` | Admin |
| Manage Stalls | `/admin-panel/stalls/` | Admin |
| Manage Stall Owners | `/admin-panel/stall-owners/` | Admin |
| Manage Food Items | `/admin-panel/food/` | Admin |
| Manage Time Slots | `/admin-panel/slots/` | Admin |
| Demand Analytics | `/admin-panel/analytics/` | Admin |

---

## 🔗 URL Reference

```
/                                          → Landing page
/register/                                 → Student registration
/login/  · /logout/                        → Authentication

/dashboard/                                → Student dashboard
/menu/                                     → Browse stalls & menu (?stall=<id>)
/order/                                    → Place an order
/my-orders/                                → Order history (?status=...&stall=...)
/cancel-order/<id>/                        → Cancel a pending order

/stall-owner/dashboard/                    → Stall owner order management
/stall-owner/orders/update/<id>/           → Mark order completed/cancelled

/admin-panel/                              → Admin dashboard
/admin-panel/stalls/                       → Manage stalls
/admin-panel/stall-owners/                 → Manage stall owner accounts
/admin-panel/food/                         → Manage food items (?stall=<id>)
/admin-panel/slots/                        → Manage time slots
/admin-panel/orders/update/<id>/           → Update order status
/admin-panel/analytics/                    → Demand analytics & charts
```

---

## 🏪 How Stall Owner Accounts Work

1. Admin goes to **Manage Stall Owners** → `/admin-panel/stall-owners/`
2. Clicks **Add Stall Owner**, fills in: stall assignment, name, username, password
3. A **unique 5-digit Stall Code** is auto-generated (e.g. `47382`)
4. The stall owner logs in at `/login/` with their username & password
5. They land on `/stall-owner/dashboard/` showing **only orders from their stall**
6. Their Stall Code is always visible in the navbar dropdown for identification
7. They can mark orders **Completed ✅** or **Cancelled ❌** in real time

---

## 📄 License

This project is for educational purposes. Developed by Rajvardhan Mall

---

<p align="center">Made with ❤️ using Django &amp; Bootstrap</p>
