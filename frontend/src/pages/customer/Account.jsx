import { useEffect, useState } from "react";
import {
  customerApi, roomApi, restaurantApi, partyHallApi, poolApi, spaApi, laundryApi, membershipApi,
  notificationApi,
} from "../../api/endpoints";
import { Badge, Spinner, EmptyState } from "../../components/ui";

function BookingRow({ code, label, dateText, status }) {
  return (
    <div className="flex items-center justify-between border-b border-ink-700/5 py-3 last:border-0">
      <div>
        <p className="text-sm font-medium text-ink-900">{code}</p>
        <p className="text-xs text-ink-700/60">{label} · {dateText}</p>
      </div>
      <Badge status={status} />
    </div>
  );
}

export default function Account() {
  const [customer, setCustomer] = useState(null);
  const [memberships, setMemberships] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [bookings, setBookings] = useState({ rooms: [], tables: [], events: [], pool: [], spa: [], laundry: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    notificationApi.mine().then((res) => setNotifications(res.data)).catch(() => {});
    customerApi.me().then((res) => {
      const cust = res.data;
      setCustomer(cust);
      const params = { customer_id: cust.id };
      Promise.all([
        roomApi.bookings(params),
        restaurantApi.tableBookings(params),
        partyHallApi.bookings(params),
        poolApi.bookings(params),
        spaApi.bookings(params),
        laundryApi.orders(params),
        membershipApi.forCustomer(cust.id),
      ]).then(([rooms, tables, events, pool, spa, laundry, memb]) => {
        setBookings({
          rooms: rooms.data, tables: tables.data, events: events.data,
          pool: pool.data, spa: spa.data, laundry: laundry.data,
        });
        setMemberships(memb.data);
        setLoading(false);
      });
    });
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Spinner />
      </div>
    );
  }

  const totalBookings =
    bookings.rooms.length + bookings.tables.length + bookings.events.length +
    bookings.pool.length + bookings.spa.length + bookings.laundry.length;

  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="font-display text-4xl text-ink-900">
        Welcome back, {customer.first_name}
      </h1>
      <p className="mt-2 text-sm text-ink-700/70">{customer.customer_code} · {customer.email}</p>

      {memberships.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-2">
          {memberships.map((m) => (
            <span key={m.id} className="rounded-full bg-brass-500/20 px-3 py-1 text-xs font-medium text-brass-600">
              Member since {m.start_date}
            </span>
          ))}
        </div>
      )}

      {notifications.length > 0 && (
        <div className="mt-8 rounded border border-ink-700/10 bg-white p-6">
          <p className="font-display text-lg text-ink-900">Notifications</p>
          <div className="mt-3 space-y-3">
            {notifications.slice(0, 6).map((n) => (
              <div key={n.id} className="border-b border-ink-700/5 pb-3 last:border-0 last:pb-0">
                <p className="text-sm font-medium text-ink-900">{n.title}</p>
                <p className="text-xs text-ink-700/60">{n.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        <div className="rounded border border-ink-700/10 bg-white p-6">
          <p className="font-display text-lg text-ink-900">Room bookings</p>
          {bookings.rooms.length === 0 ? (
            <p className="mt-3 text-sm text-ink-700/50">No room bookings yet.</p>
          ) : (
            bookings.rooms.map((b) => (
              <BookingRow key={b.id} code={b.booking_code} label="Room stay"
                dateText={new Date(b.check_in_date).toLocaleDateString()} status={b.booking_status} />
            ))
          )}
        </div>

        <div className="rounded border border-ink-700/10 bg-white p-6">
          <p className="font-display text-lg text-ink-900">Restaurant reservations</p>
          {bookings.tables.length === 0 ? (
            <p className="mt-3 text-sm text-ink-700/50">No table reservations yet.</p>
          ) : (
            bookings.tables.map((b) => (
              <BookingRow key={b.id} code={b.booking_code} label="Table"
                dateText={new Date(b.reserved_for).toLocaleDateString()} status={b.status} />
            ))
          )}
        </div>

        <div className="rounded border border-ink-700/10 bg-white p-6">
          <p className="font-display text-lg text-ink-900">Events</p>
          {bookings.events.length === 0 ? (
            <p className="mt-3 text-sm text-ink-700/50">No event bookings yet.</p>
          ) : (
            bookings.events.map((b) => (
              <BookingRow key={b.id} code={b.booking_code} label="Party hall"
                dateText={new Date(b.event_date).toLocaleDateString()} status={b.booking_status} />
            ))
          )}
        </div>

        <div className="rounded border border-ink-700/10 bg-white p-6">
          <p className="font-display text-lg text-ink-900">Wellness (Spa & Pool)</p>
          {bookings.spa.length === 0 && bookings.pool.length === 0 ? (
            <p className="mt-3 text-sm text-ink-700/50">No wellness bookings yet.</p>
          ) : (
            <>
              {bookings.spa.map((b) => (
                <BookingRow key={`spa-${b.id}`} code={b.booking_code} label="Spa"
                  dateText={new Date(b.booking_date).toLocaleDateString()} status={b.booking_status} />
              ))}
              {bookings.pool.map((b) => (
                <BookingRow key={`pool-${b.id}`} code={b.booking_code} label="Pool"
                  dateText={new Date(b.booking_date).toLocaleDateString()} status={b.booking_status} />
              ))}
            </>
          )}
        </div>
      </div>

      {totalBookings === 0 && (
        <div className="mt-10">
          <EmptyState title="No bookings yet" description="Once you book a service, it will show up here." />
        </div>
      )}
    </div>
  );
}
