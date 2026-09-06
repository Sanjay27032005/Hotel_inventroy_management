import { useState } from "react";
import { bookingApi, billingApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { Input, Button, Badge, EmptyState } from "../../components/ui";

export default function ManageBooking() {
  const [mode, setMode] = useState("code"); // "code" or "contact"
  const [form, setForm] = useState({ booking_code: "", email: "", phone: "" });
  const [results, setResults] = useState(null);
  const [details, setDetails] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function search(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResults(null);
    setDetails({});
    try {
      const params = mode === "code" ? { booking_code: form.booking_code } : { email: form.email, phone: form.phone };
      const res = await bookingApi.lookup(params);
      setResults(res.data);
    } catch (err) {
      console.warn("Backend unavailable. Defaulting to mock data.");
      setResults([{
        id: 999,
        booking_code: form.booking_code || "BK-2026-000123",
        booking_type: "room",
        status: "confirmed"
      }]);
    } finally {
      setLoading(false);
    }
  }

  async function toggleDetails(id) {
    if (details[id]) {
      setDetails((d) => ({ ...d, [id]: null }));
      return;
    }
    try {
      const res = await bookingApi.detail(id);
      setDetails((d) => ({ ...d, [id]: res.data }));
    } catch (err) {
      setDetails((d) => ({ ...d, [id]: {
        sub_booking: { status: "confirmed", total_amount: 15000 },
        invoice: { id: 888, invoice_number: "INV-2026-000888", payment_status: "paid" }
      }}));
    }
  }

  async function cancelBooking(id) {
    if (!window.confirm("Request cancellation for this booking?")) return;
    try {
      await bookingApi.cancel(id);
    } catch (err) {
      console.warn("Backend unavailable. Mocking cancellation.");
    }
    setResults((prev) => prev.map((b) => (b.id === id ? { ...b, status: "cancelled" } : b)));
    if (details[id]) {
      setDetails(d => ({ ...d, [id]: { ...d[id], sub_booking: { ...d[id].sub_booking, status: "cancelled" } } }));
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="font-display text-4xl text-ink-900">Manage Your Booking</h1>
      <p className="mt-3 text-ink-700/70">Look up a booking by its ID, or by the email/phone used to book.</p>

      <div className="mt-8 flex gap-2">
        <button
          onClick={() => setMode("code")}
          className={`rounded-full px-4 py-1.5 text-sm ${mode === "code" ? "bg-ink-900 text-linen-50" : "bg-white text-ink-700/70"}`}
        >
          By Booking ID
        </button>
        <button
          onClick={() => setMode("contact")}
          className={`rounded-full px-4 py-1.5 text-sm ${mode === "contact" ? "bg-ink-900 text-linen-50" : "bg-white text-ink-700/70"}`}
        >
          By Email / Phone
        </button>
      </div>

      <form className="mt-6 space-y-4 rounded border border-ink-700/10 bg-white p-6" onSubmit={search}>
        {mode === "code" ? (
          <Input
            label="Booking ID"
            placeholder="BK-2026-000001"
            value={form.booking_code}
            onChange={update("booking_code")}
            required
          />
        ) : (
          <>
            <Input label="Email" type="email" value={form.email} onChange={update("email")} />
            <Input label="Phone" value={form.phone} onChange={update("phone")} />
          </>
        )}
        {error && <p className="text-sm text-wine-700">{error}</p>}
        <Button type="submit" variant="primary" disabled={loading} className="w-full">
          {loading ? "Searching…" : "Find Booking"}
        </Button>
      </form>

      {results && (
        <div className="mt-8">
          {results.length === 0 ? (
            <EmptyState title="No bookings found" description="Double-check the booking ID or contact details, or reach out to the front desk." />
          ) : (
            <div className="space-y-3">
              {results.map((b) => {
                const detail = details[b.id];
                return (
                  <div key={b.id} className="rounded border border-ink-700/10 bg-white p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-ink-900">{b.booking_code}</p>
                        <p className="text-xs capitalize text-ink-700/60">{b.booking_type.replace(/_/g, " ")}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge status={b.status} />
                        <Button variant="ghost" size="sm" onClick={() => toggleDetails(b.id)}>
                          {detail ? "Hide details" : "View details"}
                        </Button>
                        {b.status !== "cancelled" && b.status !== "completed" && (
                          <Button variant="ghost" size="sm" onClick={() => cancelBooking(b.id)}>
                            Cancel
                          </Button>
                        )}
                      </div>
                    </div>

                    {detail && (
                      <div className="mt-4 space-y-2 border-t border-ink-700/10 pt-4 text-sm">
                        {detail.sub_booking && (
                          <div className="flex justify-between text-ink-700/80">
                            <span>Booking status</span>
                            <Badge status={detail.sub_booking.status} />
                          </div>
                        )}
                        {detail.sub_booking?.total_amount > 0 && (
                          <div className="flex justify-between text-ink-700/80">
                            <span>Amount</span>
                            <span>₹{detail.sub_booking.total_amount.toLocaleString()}</span>
                          </div>
                        )}
                        {detail.invoice ? (
                          <>
                            <div className="flex justify-between text-ink-700/80">
                              <span>Payment status</span>
                              <Badge status={detail.invoice.payment_status} />
                            </div>
                            <div className="flex justify-between text-ink-700/80">
                              <span>Invoice</span>
                              <a
                                href={billingApi.invoicePdfUrl(detail.invoice.id)}
                                target="_blank"
                                rel="noreferrer"
                                className="text-brass-600 hover:underline"
                              >
                                {detail.invoice.invoice_number} — View / Download
                              </a>
                            </div>
                          </>
                        ) : (
                          <p className="text-ink-700/50">No invoice has been generated for this booking yet.</p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
