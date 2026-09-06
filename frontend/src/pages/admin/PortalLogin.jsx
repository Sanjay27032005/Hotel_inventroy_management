import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { apiErrorMessage } from "../../api/client";
import { Input, Button } from "../../components/ui";

export default function PortalLogin() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const user = await login(form.username, form.password);
      if (user.role === "customer") {
        setError("This login is for hotel staff. Guests can sign in from the main site.");
        return;
      }
      navigate(location.state?.from?.pathname || "/portal/dashboard");
    } catch (err) {
      setError(apiErrorMessage(err, "Incorrect username or password."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-900 px-6">
      <div className="w-full max-w-sm">
        <p className="text-center font-display text-2xl text-linen-50">CoreStone Grand</p>
        <p className="mt-1 text-center text-xs text-linen-200/60">Management Portal</p>

        <form className="mt-8 space-y-4 rounded border border-linen-100/10 bg-ink-800 p-8" onSubmit={submit}>
          <Input
            label="Username"
            required
            labelClassName="text-linen-200/80"
            className="bg-ink-900 text-linen-50 border-linen-100/20"
            value={form.username}
            onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
          />
          <Input
            label="Password"
            type="password"
            required
            labelClassName="text-linen-200/80"
            className="bg-ink-900 text-linen-50 border-linen-100/20"
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
          />
          {error && <p className="text-sm text-brass-400">{error}</p>}
          <Button type="submit" variant="brass" disabled={loading} className="w-full">
            {loading ? "Signing in…" : "Sign In"}
          </Button>
        </form>
      </div>
    </div>
  );
}
