import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { apiErrorMessage } from "../../api/client";
import { Input, Button } from "../../components/ui";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const user = await login(form.username, form.password);
      if (user.role === "customer") navigate("/account");
      else navigate("/portal/dashboard");
    } catch (err) {
      setError(apiErrorMessage(err, "Incorrect username or password."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-6 py-16">
      <h1 className="font-display text-3xl text-ink-900">Sign in</h1>
      <p className="mt-2 text-sm text-ink-700/70">Access your bookings, invoices and account details.</p>

      <form className="mt-8 space-y-4 rounded border border-ink-700/10 bg-white p-8" onSubmit={submit}>
        <Input
          label="Username"
          required
          value={form.username}
          onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
        />
        <Input
          label="Password"
          type="password"
          required
          value={form.password}
          onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
        />
        {error && <p className="text-sm text-wine-700">{error}</p>}
        <Button type="submit" variant="brass" disabled={loading} className="w-full">
          {loading ? "Signing in…" : "Sign In"}
        </Button>
      </form>
      <p className="mt-4 text-center text-sm text-ink-700/70">
        New here? <Link to="/register" className="text-brass-600 hover:underline">Create an account</Link>
      </p>
    </div>
  );
}
