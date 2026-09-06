import { useEffect, useState } from "react";
import { poolApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Button, Input, Select, Badge, Spinner } from "../../components/ui";

const EMPTY = { customer_id: "", customer_type: "adult", package_type: "hourly", trainer_id: "", booking_date: "", discount: 0, tax: 0 };

export default function Pool() {
  const [prices, setPrices] = useState([]);
  const [trainers, setTrainers] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    setLoading(true);
    Promise.all([poolApi.prices(), poolApi.trainers(), poolApi.bookings()])
      .then(([p, t, b]) => { setPrices(p.data); setTrainers(t.data); setBookings(b.data); })
      .finally(() => setLoading(false));
  }
  useEffect(load, []);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function submit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await poolApi.book({
        ...form,
        customer_id: Number(form.customer_id),
        trainer_id: form.trainer_id ? Number(form.trainer_id) : null,
        discount: Number(form.discount),
        tax: Number(form.tax),
      });
      setForm(EMPTY);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create this pool booking."));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader title="Swimming Pool" description="Package pricing, trainers, and pool bookings." />

      <form onSubmit={submit} className="mb-8 space-y-4 rounded border border-ink-700/10 bg-white p-6">
        <p className="font-medium text-ink-900">New pool booking</p>
        <div className="grid gap-4 sm:grid-cols-4">
          <Input label="Customer ID" required type="number" value={form.customer_id} onChange={update("customer_id")} />
          <Select label="Customer type" value={form.customer_type} onChange={update("customer_type")}>
            <option value="child">Child</option>
            <option value="adult">Adult</option>
            <option value="couple">Couple</option>
          </Select>
          <Select label="Package" value={form.package_type} onChange={update("package_type")}>
            <option value="hourly">Hourly</option>
            <option value="monthly">Monthly</option>
            <option value="trainer">Trainer</option>
          </Select>
          <Input label="Date" type="datetime-local" required value={form.booking_date} onChange={update("booking_date")} />
        </div>
        {form.package_type === "trainer" && (
          <Select label="Trainer" required value={form.trainer_id} onChange={update("trainer_id")}>
            <option value="">Select a trainer</option>
            {trainers.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </Select>
        )}
        {error && <p className="text-sm text-wine-700">{error}</p>}
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? "Booking…" : "Create Booking"}
        </Button>
      </form>

      <div className="mb-8">
        <p className="mb-3 font-medium text-ink-900">Package prices</p>
        <DataTable
          columns={[
            { key: "customer_type", header: "Customer type" },
            { key: "package_type", header: "Package" },
            { key: "price", header: "Price", render: (r) => `₹${r.price}` },
          ]}
          rows={prices}
        />
      </div>

      <p className="mb-3 font-medium text-ink-900">Bookings</p>
      <DataTable
        columns={[
          { key: "booking_code", header: "Booking ID" },
          { key: "package_type", header: "Package" },
          { key: "customer_type", header: "Customer type" },
          { key: "booking_date", header: "Date", render: (r) => new Date(r.booking_date).toLocaleString() },
          { key: "total_amount", header: "Total", render: (r) => `₹${r.total_amount}` },
          { key: "booking_status", header: "Status", render: (r) => <Badge status={r.booking_status} /> },
        ]}
        rows={bookings}
        emptyMessage="No pool bookings yet."
      />
    </div>
  );
}
