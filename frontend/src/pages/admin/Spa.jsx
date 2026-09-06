import { useEffect, useState } from "react";
import { spaApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Button, Input, Select, Badge, Spinner } from "../../components/ui";

const EMPTY = { customer_id: "", spa_service_id: "", therapist_id: "", booking_date: "", start_time: "", duration_minutes: 60, discount: 0, tax: 0 };

export default function Spa() {
  const [services, setServices] = useState([]);
  const [therapists, setTherapists] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    setLoading(true);
    Promise.all([spaApi.services(), spaApi.therapists(), spaApi.bookings()])
      .then(([s, t, b]) => { setServices(s.data); setTherapists(t.data); setBookings(b.data); })
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
      await spaApi.book({
        ...form,
        customer_id: Number(form.customer_id),
        spa_service_id: Number(form.spa_service_id),
        therapist_id: form.therapist_id ? Number(form.therapist_id) : null,
        duration_minutes: Number(form.duration_minutes),
        discount: Number(form.discount),
        tax: Number(form.tax),
      });
      setForm(EMPTY);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create this spa booking."));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader title="Spa & Massage" description="Services, therapists, and appointment bookings." />

      <form onSubmit={submit} className="mb-8 space-y-4 rounded border border-ink-700/10 bg-white p-6">
        <p className="font-medium text-ink-900">New spa booking</p>
        <div className="grid gap-4 sm:grid-cols-3">
          <Input label="Customer ID" required type="number" value={form.customer_id} onChange={update("customer_id")} />
          <Select label="Service" required value={form.spa_service_id} onChange={update("spa_service_id")}>
            <option value="">Select a service</option>
            {services.map((s) => <option key={s.id} value={s.id}>{s.name} — ₹{s.service_price}</option>)}
          </Select>
          <Select label="Therapist (optional)" value={form.therapist_id} onChange={update("therapist_id")}>
            <option value="">Any therapist</option>
            {therapists.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </Select>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <Input label="Date" type="date" required value={form.booking_date} onChange={update("booking_date")} />
          <Input label="Start time" type="time" required value={form.start_time} onChange={update("start_time")} />
          <Input label="Duration (min)" type="number" value={form.duration_minutes} onChange={update("duration_minutes")} />
        </div>
        {error && <p className="text-sm text-wine-700">{error}</p>}
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? "Booking…" : "Create Booking"}
        </Button>
      </form>

      <DataTable
        columns={[
          { key: "booking_code", header: "Booking ID" },
          { key: "booking_date", header: "Date", render: (r) => new Date(r.booking_date).toLocaleDateString() },
          { key: "start_time", header: "Start" },
          { key: "duration_minutes", header: "Duration" },
          { key: "total_amount", header: "Total", render: (r) => `₹${r.total_amount}` },
          { key: "booking_status", header: "Status", render: (r) => <Badge status={r.booking_status} /> },
        ]}
        rows={bookings}
        emptyMessage="No spa bookings yet."
      />
    </div>
  );
}
