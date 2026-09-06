import { useEffect, useState } from "react";
import { roomApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Button, Input, Select, Badge, Spinner } from "../../components/ui";

const RATE_TYPES = ["hourly", "daily", "weekly", "monthly"];

const EMPTY_BOOKING = {
  customer_id: "", room_id: "", check_in_date: "", check_out_date: "",
  adults: 1, children: 0, rate_type: "daily", discount: 0, tax: 0,
};

export default function Rooms() {
  const [tab, setTab] = useState("bookings");
  const [roomTypes, setRoomTypes] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(EMPTY_BOOKING);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    setLoading(true);
    Promise.all([roomApi.types(), roomApi.list(), roomApi.bookings()])
      .then(([t, r, b]) => {
        setRoomTypes(t.data);
        setRooms(r.data);
        setBookings(b.data);
      })
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function submitBooking(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await roomApi.book({
        ...form,
        customer_id: Number(form.customer_id),
        room_id: Number(form.room_id),
        adults: Number(form.adults),
        children: Number(form.children),
        discount: Number(form.discount),
        tax: Number(form.tax),
      });
      setForm(EMPTY_BOOKING);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create this booking."));
    } finally {
      setSubmitting(false);
    }
  }

  async function action(fn, id) {
    await fn(id);
    load();
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader title="Accommodation" description="Room types, rooms, and stay bookings." />

      <div className="mb-6 flex gap-2">
        {["bookings", "rooms"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-full px-4 py-1.5 text-sm capitalize ${tab === t ? "bg-ink-900 text-linen-50" : "bg-white text-ink-700/70"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "bookings" && (
        <>
          <form onSubmit={submitBooking} className="mb-8 space-y-4 rounded border border-ink-700/10 bg-white p-6">
            <p className="font-medium text-ink-900">New room booking</p>
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Customer ID" required type="number" value={form.customer_id} onChange={update("customer_id")} />
              <Select label="Room" required value={form.room_id} onChange={update("room_id")}>
                <option value="">Select a room</option>
                {rooms.filter((r) => r.status === "available").map((r) => (
                  <option key={r.id} value={r.id}>Room {r.room_number}</option>
                ))}
              </Select>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Check-in" type="datetime-local" required value={form.check_in_date} onChange={update("check_in_date")} />
              <Input label="Check-out" type="datetime-local" required value={form.check_out_date} onChange={update("check_out_date")} />
            </div>
            <div className="grid gap-4 sm:grid-cols-4">
              <Input label="Adults" type="number" min="1" value={form.adults} onChange={update("adults")} />
              <Input label="Children" type="number" min="0" value={form.children} onChange={update("children")} />
              <Select label="Rate type" value={form.rate_type} onChange={update("rate_type")}>
                {RATE_TYPES.map((r) => <option key={r} value={r}>{r}</option>)}
              </Select>
              <Input label="Discount" type="number" value={form.discount} onChange={update("discount")} />
            </div>
            {error && <p className="text-sm text-wine-700">{error}</p>}
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? "Booking…" : "Create Booking"}
            </Button>
          </form>

          <DataTable
            columns={[
              { key: "booking_code", header: "Booking ID" },
              { key: "room_id", header: "Room", render: (r) => rooms.find((x) => x.id === r.room_id)?.room_number || r.room_id },
              { key: "check_in_date", header: "Check-in", render: (r) => new Date(r.check_in_date).toLocaleString() },
              { key: "check_out_date", header: "Check-out", render: (r) => new Date(r.check_out_date).toLocaleString() },
              { key: "total_amount", header: "Total", render: (r) => `₹${r.total_amount}` },
              { key: "payment_status", header: "Payment", render: (r) => <Badge status={r.payment_status} /> },
              { key: "booking_status", header: "Status", render: (r) => <Badge status={r.booking_status} /> },
              {
                key: "actions", header: "", render: (r) => (
                  <div className="flex gap-2">
                    {r.booking_status === "confirmed" && (
                      <Button variant="ghost" size="sm" onClick={() => action(roomApi.checkIn, r.id)}>Check In</Button>
                    )}
                    {r.booking_status === "checked_in" && (
                      <Button variant="ghost" size="sm" onClick={() => action(roomApi.checkOut, r.id)}>Check Out</Button>
                    )}
                    {["pending", "confirmed"].includes(r.booking_status) && (
                      <Button variant="ghost" size="sm" onClick={() => action(roomApi.cancel, r.id)}>Cancel</Button>
                    )}
                  </div>
                ),
              },
            ]}
            rows={bookings}
            emptyMessage="No room bookings yet."
          />
        </>
      )}

      {tab === "rooms" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <p className="mb-3 font-medium text-ink-900">Room Types</p>
            <DataTable
              columns={[
                { key: "name", header: "Type" },
                { key: "customer_category", header: "Category" },
                { key: "daily_rate", header: "Daily Rate", render: (r) => `₹${r.daily_rate}` },
              ]}
              rows={roomTypes}
            />
          </div>
          <div>
            <p className="mb-3 font-medium text-ink-900">Rooms</p>
            <DataTable
              columns={[
                { key: "room_number", header: "Room #" },
                { key: "floor", header: "Floor" },
                { key: "status", header: "Status", render: (r) => <Badge status={r.status} /> },
              ]}
              rows={rooms}
            />
          </div>
        </div>
      )}
    </div>
  );
}
