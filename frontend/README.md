# HRM System — Frontend (React + Vite + Tailwind)

CST-HRM-001 · Hotel & Restaurant Management System · CoreStone Technologies

## Stack
React 19, Vite, React Router, Tailwind CSS v4, Axios.

## 1. Install dependencies

```bash
cd frontend
npm install
```

## 2. Configure the API URL

```bash
cp .env.example .env
```

By default it points at `http://localhost:8000` (the backend's default port).

## 3. Run the dev server

```bash
npm run dev
```

Visit http://localhost:5173 for the customer website, and
http://localhost:5173/portal/login for the staff/management portal.

## 4. Build for production

```bash
npm run build
```

Output goes to `dist/` — serve it with any static host (Nginx, Vercel, Netlify, etc.)
and point it at your deployed backend via `VITE_API_URL`.

## Structure

```
src/
├── api/            # axios client + one function per backend endpoint, grouped by module
├── context/        # AuthContext (JWT storage, current user, role helpers)
├── components/     # shared UI: buttons/inputs (ui.jsx), admin tables/KPI cards (admin-ui.jsx),
│                   # Navbar, Footer, ProtectedRoute
├── layouts/        # CustomerLayout (public site chrome), PortalLayout (staff sidebar)
├── pages/customer/ # Home, Destinations, Membership, Services, Gallery, More, Contact,
│                   # Book a Stay, Manage Your Booking, Login, Register, Account
└── pages/admin/    # Portal login, Dashboard, Employees, Customers, and one page per
                    # service module (Rooms, Restaurant, Party Hall, Pool, Spa, Club,
                    # Laundry), Bookings, Billing, Enquiries, Reports
```

## Design direction

Warm boutique-hotel palette (deep pine ink `#1A2F29`, linen background, brass-gold accent)
paired with a serif display face (Fraunces) for headings and Inter for body/UI text —
distinct from a generic SaaS admin look, and legible at data-table density in the portal.

## Roles reflected in the UI

The portal sidebar and route guards mirror the backend's role table:
`admin`, `general_manager`, `manager` see the most; `billing_person`, `room_servant`,
`food_servant`, `chef` see only the modules relevant to their job, per Section 59/38 of
the requirement document. A logged-in `customer` never sees `/portal/*` — they use the
public site and `/account`.
