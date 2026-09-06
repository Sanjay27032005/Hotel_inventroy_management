import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import CustomerLayout from "./layouts/CustomerLayout";
import PortalLayout from "./layouts/PortalLayout";

import Home from "./pages/customer/Home";
import Destinations from "./pages/customer/Destinations";
import Membership from "./pages/customer/Membership";
import Services from "./pages/customer/Services";
import Gallery from "./pages/customer/Gallery";
import More from "./pages/customer/More";
import Contact from "./pages/customer/Contact";
import Dining from "./pages/customer/Dining";
import BookAStay from "./pages/customer/BookAStay";
import ManageBooking from "./pages/customer/ManageBooking";
import Login from "./pages/customer/Login";
import Register from "./pages/customer/Register";
import Account from "./pages/customer/Account";

import PortalLogin from "./pages/admin/PortalLogin";
import Dashboard from "./pages/admin/Dashboard";
import Employees from "./pages/admin/Employees";
import Customers from "./pages/admin/Customers";
import Rooms from "./pages/admin/Rooms";
import Restaurant from "./pages/admin/Restaurant";
import PartyHall from "./pages/admin/PartyHall";
import Pool from "./pages/admin/Pool";
import Spa from "./pages/admin/Spa";
import Club from "./pages/admin/Club";
import Laundry from "./pages/admin/Laundry";
import Bookings from "./pages/admin/Bookings";
import Billing from "./pages/admin/Billing";
import Enquiries from "./pages/admin/Enquiries";
import Reports from "./pages/admin/Reports";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Customer website */}
          <Route element={<CustomerLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/destinations" element={<Destinations />} />
            <Route path="/membership" element={<Membership />} />
            <Route path="/services" element={<Services />} />
            <Route path="/dining" element={<Dining />} />
            <Route path="/gallery" element={<Gallery />} />
            <Route path="/more" element={<More />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/book-a-stay" element={<BookAStay />} />
            <Route path="/manage-booking" element={<ManageBooking />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/account" element={<Account />} />
          </Route>

          {/* Management portal */}
          <Route path="/portal/login" element={<PortalLogin />} />
          <Route
            path="/portal"
            element={
              <ProtectedRoute>
                <PortalLayout />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="employees" element={<Employees />} />
            <Route path="customers" element={<Customers />} />
            <Route path="rooms" element={<Rooms />} />
            <Route path="restaurant" element={<Restaurant />} />
            <Route path="party-hall" element={<PartyHall />} />
            <Route path="pool" element={<Pool />} />
            <Route path="spa" element={<Spa />} />
            <Route path="club" element={<Club />} />
            <Route path="laundry" element={<Laundry />} />
            <Route path="bookings" element={<Bookings />} />
            <Route path="billing" element={<Billing />} />
            <Route path="enquiries" element={<Enquiries />} />
            <Route path="reports" element={<Reports />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
