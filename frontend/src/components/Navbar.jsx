import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Button } from "./ui";

const LINKS = [
  { to: "/destinations", label: "Destinations" },
  { to: "/membership", label: "Membership" },
  { to: "/services", label: "Services" },
  { to: "/dining", label: "Dining" },
  { to: "/gallery", label: "Gallery" },
  { to: "/more", label: "Journal" },
  { to: "/contact", label: "Contact Us" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { user, isCustomer, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 border-b border-ink-700/10 bg-linen-50/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="font-display text-xl text-ink-900">
          CoreStone Grand
        </Link>

        <nav className="hidden items-center gap-7 lg:flex">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `text-sm transition-colors ${isActive ? "text-ink-900 font-medium" : "text-ink-700/70 hover:text-ink-900"}`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-3 lg:flex">
          <Button variant="ghost" size="sm" as={Link} to="/manage-booking">
            Manage Your Booking
          </Button>
          {isCustomer ? (
            <>
              <Button variant="outline" size="sm" as={Link} to="/account">
                {user.display_name || user.username}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  logout();
                  navigate("/");
                }}
              >
                Sign out
              </Button>
            </>
          ) : (
            <Button variant="brass" size="sm" as={Link} to="/book-a-stay">
              Book a Stay
            </Button>
          )}
        </div>

        <button
          className="text-ink-900 lg:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle menu"
          aria-expanded={open}
        >
          <span className="block h-0.5 w-6 bg-current" />
          <span className="mt-1.5 block h-0.5 w-6 bg-current" />
          <span className="mt-1.5 block h-0.5 w-6 bg-current" />
        </button>
      </div>

      {open && (
        <div className="border-t border-ink-700/10 bg-linen-50 px-6 py-4 lg:hidden">
          <nav className="flex flex-col gap-3">
            {LINKS.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={() => setOpen(false)}
                className="text-sm text-ink-800"
              >
                {link.label}
              </NavLink>
            ))}
            <NavLink to="/manage-booking" onClick={() => setOpen(false)} className="text-sm text-ink-800">
              Manage Your Booking
            </NavLink>
            {isCustomer ? (
              <>
                <NavLink to="/account" onClick={() => setOpen(false)} className="text-sm text-ink-800">
                  My account
                </NavLink>
                <button
                  className="text-left text-sm text-wine-700"
                  onClick={() => {
                    logout();
                    setOpen(false);
                    navigate("/");
                  }}
                >
                  Sign out
                </button>
              </>
            ) : (
              <Button variant="brass" size="sm" as={Link} to="/book-a-stay" onClick={() => setOpen(false)}>
                Book a Stay
              </Button>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
