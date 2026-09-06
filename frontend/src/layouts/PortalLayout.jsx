import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_SECTIONS = [
  {
    label: "Overview",
    items: [{ to: "/portal/dashboard", label: "Dashboard", roles: ["admin", "general_manager", "manager"] }],
  },
  {
    label: "People",
    items: [
      { to: "/portal/employees", label: "Employees", roles: ["admin", "general_manager", "manager"] },
      { to: "/portal/customers", label: "Customers", roles: ["admin", "general_manager", "manager", "billing_person", "room_servant", "food_servant", "chef"] },
    ],
  },
  {
    label: "Services",
    items: [
      { to: "/portal/rooms", label: "Accommodation", roles: ["admin", "general_manager", "manager", "room_servant", "billing_person"] },
      { to: "/portal/restaurant", label: "Restaurant", roles: ["admin", "general_manager", "manager", "food_servant", "chef", "billing_person"] },
      { to: "/portal/party-hall", label: "Party Hall", roles: ["admin", "general_manager", "manager", "billing_person"] },
      { to: "/portal/pool", label: "Swimming Pool", roles: ["admin", "general_manager", "manager", "billing_person"] },
      { to: "/portal/spa", label: "Spa & Massage", roles: ["admin", "general_manager", "manager", "billing_person"] },
      { to: "/portal/club", label: "Club & Bar", roles: ["admin", "general_manager", "manager", "billing_person"] },
      { to: "/portal/laundry", label: "Laundry", roles: ["admin", "general_manager", "manager", "billing_person"] },
    ],
  },
  {
    label: "Front desk",
    items: [
      { to: "/portal/bookings", label: "Bookings & Stay Requests", roles: ["admin", "general_manager", "manager", "billing_person"] },
      { to: "/portal/billing", label: "Billing & Invoices", roles: ["admin", "general_manager", "manager", "billing_person"] },
      { to: "/portal/enquiries", label: "Enquiries", roles: ["admin", "general_manager", "manager"] },
    ],
  },
  {
    label: "Insights",
    items: [{ to: "/portal/reports", label: "Reports", roles: ["admin", "general_manager"] }],
  },
];

export default function PortalLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen bg-linen-100">
      <aside className="hidden w-64 shrink-0 flex-col bg-ink-900 text-linen-100 lg:flex">
        <div className="border-b border-linen-100/10 px-6 py-5">
          <p className="font-display text-lg text-linen-50">CoreStone Grand</p>
          <p className="text-xs text-linen-200/50">Management Portal</p>
        </div>
        <nav className="flex-1 overflow-y-auto px-4 py-5">
          {NAV_SECTIONS.map((section) => {
            const visible = section.items.filter((item) => item.roles.includes(user?.role));
            if (visible.length === 0) return null;
            return (
              <div key={section.label} className="mb-6">
                <p className="px-2 text-xs font-medium text-linen-200/40">{section.label}</p>
                <div className="mt-2 flex flex-col gap-0.5">
                  {visible.map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      className={({ isActive }) =>
                        `rounded px-3 py-2 text-sm transition-colors ${
                          isActive ? "bg-brass-500 text-ink-900 font-medium" : "text-linen-200/80 hover:bg-linen-100/10"
                        }`
                      }
                    >
                      {item.label}
                    </NavLink>
                  ))}
                </div>
              </div>
            );
          })}
        </nav>
        <div className="border-t border-linen-100/10 px-6 py-4">
          <p className="text-sm text-linen-50">{user?.display_name || user?.username}</p>
          <p className="text-xs capitalize text-linen-200/50">{user?.role?.replace(/_/g, " ")}</p>
          <button
            className="mt-3 text-sm text-brass-400 hover:text-brass-500"
            onClick={() => {
              logout();
              navigate("/portal/login");
            }}
          >
            Sign out
          </button>
        </div>
      </aside>

      <div className="flex-1 overflow-x-hidden">
        <main className="mx-auto max-w-6xl px-6 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
