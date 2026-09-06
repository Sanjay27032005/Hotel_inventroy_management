import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="border-t border-ink-700/10 bg-ink-900 text-linen-100">
      <div className="mx-auto max-w-7xl px-6 py-14">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p className="font-display text-lg text-linen-50">CoreStone Grand</p>
            <p className="mt-3 max-w-xs text-sm text-linen-200/70">
              Discover. Book. Stay. Dine. Relax. Manage. One property, every hospitality service
              you need, handled in one place.
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-linen-50">Explore</p>
            <ul className="mt-3 space-y-2 text-sm text-linen-200/70">
              <li><Link to="/destinations" className="hover:text-linen-50">Destinations</Link></li>
              <li><Link to="/services" className="hover:text-linen-50">Services</Link></li>
              <li><Link to="/membership" className="hover:text-linen-50">Membership</Link></li>
              <li><Link to="/gallery" className="hover:text-linen-50">Gallery</Link></li>
            </ul>
          </div>
          <div>
            <p className="text-sm font-medium text-linen-50">Guests</p>
            <ul className="mt-3 space-y-2 text-sm text-linen-200/70">
              <li><Link to="/book-a-stay" className="hover:text-linen-50">Book a Stay</Link></li>
              <li><Link to="/manage-booking" className="hover:text-linen-50">Manage Your Booking</Link></li>
              <li><Link to="/contact" className="hover:text-linen-50">Contact Us</Link></li>
              <li><Link to="/register" className="hover:text-linen-50">Create an Account</Link></li>
            </ul>
          </div>
          <div>
            <p className="text-sm font-medium text-linen-50">Reach us</p>
            <ul className="mt-3 space-y-2 text-sm text-linen-200/70">
              <li>ECR Road, Puducherry, India</li>
              <li>+91 90000 00000</li>
              <li>reservations@corestone-hrm.com</li>
            </ul>
          </div>
        </div>
        <div className="mt-12 flex flex-col gap-2 border-t border-linen-100/10 pt-6 text-xs text-linen-200/50 sm:flex-row sm:justify-between">
          <p>© {new Date().getFullYear()} CoreStone Grand. A CoreStone Technologies property.</p>
          <p>CST-HRM-001</p>
        </div>
      </div>
    </footer>
  );
}
