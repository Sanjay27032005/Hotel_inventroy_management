# Hotel & Restaurant Management System (CST-HRM-001)

CoreStone Technologies · Prepared for Harini Paramasivan

A complete hospitality management platform: a customer-facing website (destinations,
membership, all 7 services, gallery, contact, Book a Stay, Manage Your Booking) and an
internal management portal (role-based employee access, per-service booking and billing,
centralized invoicing/payments, dashboards and reports).

## Structure

```
hrm-system/
├── backend/     # FastAPI + PostgreSQL API — see backend/README.md
└── frontend/    # React + Vite + Tailwind — see frontend/README.md
```

## Quick start

**Backend:**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set DATABASE_URL to your Postgres instance
alembic upgrade head
python -m app.seed     # optional: loads starter reference data
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Then open http://localhost:5173 (customer site) and
http://localhost:5173/portal/login (staff portal — default admin login
`admin` / `ChangeMe123!`, change this immediately).

## What's implemented

Every module in the requirement document (Sections 1–75): destinations, membership,
accommodation, restaurant, party hall, swimming pool, spa & massage, club & bar, laundry,
gallery, contact, employee hierarchy (Admin → General Manager / Manager → Billing Person /
Room Servant / Food Servant / Chef) with role-based access control, centralized booking
registry, unified billing/invoicing/payments across all 7 services, dashboards, and the
full set of operational/financial/employee reports from Section 67/43.

Backend business rules — double-booking prevention for rooms/halls/spa therapists, the
Club & Bar billing formula, cloth-based vs quantity-based laundry pricing, and the
BK-2026-000001 style sequential codes — were verified end-to-end (registration → booking →
invoice → payment → lookup) before the frontend was built against them.

See each app's own README for setup detail, and `backend/README.md`'s "Notes on scope
decisions" section for the handful of places the requirement document left an
implementation detail unstated.
