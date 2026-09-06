import { useEffect, useState } from "react";
import { partyHallApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Button, Input, Select, Badge, Spinner } from "../../components/ui";

const EMPTY = {
  customer_id: "", hall_id: "", event_type_id: "", event_date: "", rate_type: "daily",
  duration: 1, additional_services_charge: 0, discount: 0, tax: 0,
};

export default function PartyHall() {
  const [halls, setHalls] = useState([]);
  const [eventTypes, setEventTypes] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    setLoading(true);
    Promise.all([partyHallApi.halls(), partyHallApi.eventTypes(), partyHallApi.bookings()])
      .then(([h, e, b]) => {
        setHalls(h.data);
        setEventTypes(e.data);
        setBookings(b.data);
      })
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
      await partyHallApi.book({
        ...form,
        customer_id: Number(form.customer_id),
        hall_id: Number(form.hall_id),
        event_type_id: Number(form.event_type_id),
        duration: Number(form.duration),
        additional_services_charge: Number(form.additional_services_charge),
        discount: Number(form.discount),
        tax: Number(form.tax),
      });
      setForm(EMPTY);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create this event booking."));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader title="Party Hall" description="Halls, event types, and event bookings." />

      <form onSubmit={submit} className="mb-8 space-y-4 rounded border border-ink-700/10 bg-white p-6">
        <p className="font-medium text-ink-900">New event booking</p>
        <div className="grid gap-4 sm:grid-cols-3">
          <Input label="Customer ID" required type="number" value={form.customer_id} onChange={update("customer_id")} />
          <Select label="Hall" required value={form.hall_id} onChange={update("hall_id")}>
            <option value="">Select a hall</option>
            {halls.map((h) => <option key={h.id} value={h.id}>{h.name}</option>)}
          </Select>
          <Select label="Event type" required value={form.event_type_id} onChange={update("event_type_id")}>
            <option value="">Select an event type</option>
            {eventTypes.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
          </Select>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <Input label="Event date/time" type="datetime-local" required value={form.event_date} onChange={update("event_date")} />
          <Select label="Rate type" value={form.rate_type} onChange={update("rate_type")}>
            <option value="hourly">Hourly</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </Select>
          <Input label="Duration" type="number" min="1" value={form.duration} onChange={update("duration")} />
        </div>
        {error && <p className="text-sm text-wine-700">{error}</p>}
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? "Booking…" : "Create Booking"}
        </Button>
      </form>

      <DataTable
        columns={[
          { key: "booking_code", header: "Booking ID" },
          { key: "hall_id", header: "Hall", render: (r) => halls.find((h) => h.id === r.hall_id)?.name || r.hall_id },
          { key: "event_date", header: "Date", render: (r) => new Date(r.event_date).toLocaleString() },
          { key: "total_amount", header: "Total", render: (r) => `₹${r.total_amount}` },
          { key: "payment_status", header: "Payment", render: (r) => <Badge status={r.payment_status} /> },
          { key: "booking_status", header: "Status", render: (r) => <Badge status={r.booking_status} /> },
          {
            key: "actions", header: "", render: (r) => (
              r.booking_status === "confirmed" && (
                <Button variant="ghost" size="sm" onClick={async () => { await partyHallApi.cancel(r.id); load(); }}>
                  Cancel
                </Button>
              )
            ),
          },
        ]}
        rows={bookings}
        emptyMessage="No event bookings yet."
      />
    </div>
  );
}
