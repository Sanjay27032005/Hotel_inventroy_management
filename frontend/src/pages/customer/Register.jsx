import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { customerApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import { Input, Button } from "../../components/ui";

const EMPTY = {
  first_name: "", last_name: "", email: "", phone: "", address: "", country: "", state: "", city: "",
  username: "", password: "",
};

export default function Register() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function submit(e) {
    e.preventDefault();
    setLoading(false);
    setError("");

    // Validation
    if (!form.email.includes("@gmail.com")) {
      setError("Please provide a valid @gmail.com email address.");
      return;
    }
    if (!/^\d{10}$/.test(form.phone)) {
      setError("Phone number must be exactly 10 digits.");
      return;
    }

    setLoading(true);
    try {
      await customerApi.register(form);
      await login(form.username, form.password);
      navigate("/account");
    } catch (err) {
      setError(apiErrorMessage(err, "We couldn't create your account. Please check your details."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl px-6 py-16">
      <h1 className="font-display text-3xl text-ink-900">Create an account</h1>
      <p className="mt-2 text-sm text-ink-700/70">Track your bookings, invoices and membership in one place.</p>

      <form className="mt-8 space-y-4 rounded border border-ink-700/10 bg-white p-8" onSubmit={submit}>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="First Name" required value={form.first_name} onChange={update("first_name")} />
          <Input label="Last Name" required value={form.last_name} onChange={update("last_name")} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Email" type="email" required value={form.email} onChange={update("email")} />
          <Input label="Phone" required value={form.phone} onChange={update("phone")} />
        </div>
        <Input label="Address" value={form.address} onChange={update("address")} />
        <div className="grid gap-4 sm:grid-cols-3">
          <Input label="Country" value={form.country} onChange={update("country")} />
          <Input label="State" value={form.state} onChange={update("state")} />
          <Input label="City" value={form.city} onChange={update("city")} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Username" required value={form.username} onChange={update("username")} />
          <Input label="Password" type="password" required value={form.password} onChange={update("password")} />
        </div>
        {error && <p className="text-sm text-wine-700">{error}</p>}
        <Button type="submit" variant="brass" disabled={loading} className="w-full">
          {loading ? "Creating account…" : "Create Account"}
        </Button>
      </form>
      <p className="mt-4 text-center text-sm text-ink-700/70">
        Already have an account? <Link to="/login" className="text-brass-600 hover:underline">Sign in</Link>
      </p>
    </div>
  );
}
