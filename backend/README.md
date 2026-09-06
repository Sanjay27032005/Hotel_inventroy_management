# HRM System — Backend (FastAPI + PostgreSQL)

CST-HRM-001 · Hotel & Restaurant Management System · CoreStone Technologies

## Stack
FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic migrations, JWT auth (python-jose), bcrypt password hashing.

## 1. Install dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set a real `DATABASE_URL` pointing at your PostgreSQL instance, e.g.:

```
DATABASE_URL=postgresql://hrm_user:hrm_password@localhost:5432/hrm_db
```

Create the database first:

```bash
createdb hrm_db
# or, from psql:
# CREATE DATABASE hrm_db;
```

Set a real `SECRET_KEY` (any long random string) before deploying anywhere beyond your own machine.

## 3. Create the schema

Option A — Alembic (recommended, keeps a migration history):

```bash
alembic upgrade head
```

Option B — quick start (creates tables directly from the models, useful for local dev):
the app also auto-creates any missing tables on startup, so this step is optional if
you just want to try the app immediately.

## 4. Load starter/reference data (optional but recommended)

Departments, room types & rooms, a sample restaurant table + menu, event types & halls,
swimming pool package prices, spa services, club menu items, laundry cloth prices, and
membership plans:

```bash
python -m app.seed
```

## 5. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

- API docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 6. First login

On first startup, if no admin user exists, one is created automatically from the
`SEED_ADMIN_USERNAME` / `SEED_ADMIN_PASSWORD` values in your `.env`
(defaults: `admin` / `ChangeMe123!`). **Change this password immediately** via a real
account-management flow before using this anywhere but locally — there's no
forced-password-change flow built in yet.

Log in via `POST /api/auth/login` (OAuth2 password form: `username`, `password`) to get
a bearer token, then send it as `Authorization: Bearer <token>` on subsequent requests.

## Project layout

```
app/
├── core/          # config, DB session, security (JWT/hashing), role-based auth dependencies
├── models/        # SQLAlchemy models, one file per domain (48 tables total)
├── routers/       # one FastAPI router per module (auth, employees, rooms, restaurant, ...)
├── services/      # cross-cutting helpers: sequential code generation, billing math
├── seed.py        # loads master/reference data
└── main.py        # app assembly, CORS, router registration, startup seeding
alembic/           # migration environment (wired to app.core.database.Base)
```

## Role-based access

Roles: `admin`, `general_manager`, `manager`, `billing_person`, `room_servant`,
`food_servant`, `chef`, `customer`. Admin always has full access. See
`app/core/deps.py` for the exact permission groups used by each router
(`require_admin`, `require_management`, `require_billing`, `require_staff_any`, etc.),
matching the Role-Based Access Control table in the requirement document (Section 59/38).

## Notes on scope decisions

A few places in the 75-section requirement document left an implementation detail
unstated; the choices made (documented inline in the relevant router/model) were:
- **Central booking registry** (`bookings` table): every service booking (room, table,
  spa, event, pool, laundry) also creates a row here with the shared `BK-2026-000001`
  style code, so "Manage Your Booking" can look up any booking type from one place.
- **Cloth-based vs quantity-based laundry pricing**: cloth-based pricing charges the
  configured flat rate once per cloth type per order; quantity-based pricing multiplies
  by the given quantity, per Section 35/26.
- **Club & Bar billing formula** follows Section 33 exactly: `Subtotal + Entry Fee +
  Food + Drinks + Tips + Service Charges − Membership Discount + Tax = Grand Total`.
- **"Quantity-wise Sales" laundry report** (Section 67 lists this separately from
  "Cloth-wise Sales") is interpreted as a breakdown by pricing method (cloth-based vs
  quantity-based orders), since that's the axis the document's own laundry section
  distinguishes billing on.
- **Room booking modification** (Section 50's "Modify booking") is implemented for room
  bookings specifically — the most common case and the only one the document describes in
  any detail. Other service types support cancel + rebook rather than in-place edits.

## What's new since the first pass

Everything below was added after an explicit audit against every section of the
requirement document, to close gaps the first implementation pass had left:

- **Automatic membership discounts** (Section 6): an active membership's discount
  percentage is now computed and applied automatically on room, restaurant, party hall,
  pool, spa, and laundry bookings — combined with any manual discount staff enter, rather
  than requiring staff to calculate it by hand. Club & Bar already had its own
  membership-discount logic and was left as-is.
- **Automatic notifications** (Section 72): booking confirmation, cancellation, check-in,
  check-out, food order placement and "ready", event/pool/spa booking confirmation,
  laundry "received" and "ready", payment received, and refunds all now queue an in-app
  notification for the customer.
- **Audit logging** (Section 71): login, employee creation/login-creation/deactivation,
  invoice generation, payments, and refunds are recorded in the `audit_logs` table, and
  feed the new Employee Activity report.
- **15 additional report endpoints** to reach full coverage of Section 67's list:
  accommodation check-in/check-out reports, restaurant category-wise sales, spa massage
  service report and spa revenue, pool customer-type and trainer-package reports, laundry
  quantity-wise sales and laundry revenue, financial daily/monthly revenue, invoice report,
  discount report, employee activity, and user login activity.
- **Printable invoice PDFs** (`GET /api/billing/invoices/{id}/pdf`): a real PDF matching
  the field layout from Sections 15/21/63 (hotel details, invoice number, date, customer,
  line items, subtotal/discount/tax/additional charges/grand total, payment method/status).
- **Manage Your Booking now shows invoice and payment status** (`GET
  /api/bookings/{id}/detail`), and cancelling through it now properly releases the
  underlying room/table and syncs the sub-booking's own status — previously it only
  updated the central booking registry, leaving the room marked unavailable.
- **The "More" menu's static content** (Dining, Meetings & Conferences, Timeless
  Weddings, Holiday Stays, Hotel Safaris, Hotel Wellness, Gifting, Business Users, About
  Hotel, Sky View Residences) is now backed by an admin-editable `InfoPage` model instead
  of being hardcoded in the frontend.
