import { useEffect, useState } from "react";
import { dashboardApi } from "../../api/endpoints";
import { PageHeader, StatCard } from "../../components/admin-ui";
import { Spinner } from "../../components/ui";

export default function Dashboard() {
  const [kpis, setKpis] = useState(null);
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([dashboardApi.kpis(), dashboardApi.revenueTrend(14)])
      .then(([k, t]) => {
        setKpis(k.data);
        setTrend(t.data);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Spinner />
      </div>
    );
  }

  const maxRevenue = Math.max(1, ...trend.map((t) => t.revenue));

  return (
    <div>
      <PageHeader title="Dashboard" description="A live snapshot of the property right now." />

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        <StatCard label="Total customers" value={kpis.total_customers} />
        <StatCard label="Total employees" value={kpis.total_employees} />
        <StatCard label="Total bookings" value={kpis.total_bookings} />
        <StatCard label="Today's bookings" value={kpis.todays_bookings} />
        <StatCard label="Available rooms" value={kpis.available_rooms} />
        <StatCard label="Occupied rooms" value={kpis.occupied_rooms} />
        <StatCard label="Restaurant orders today" value={kpis.restaurant_orders_today} />
        <StatCard label="Upcoming spa sessions" value={kpis.spa_sessions_upcoming} />
        <StatCard label="Pool bookings today" value={kpis.pool_bookings_today} />
        <StatCard label="Upcoming events" value={kpis.upcoming_events} />
        <StatCard label="Pending payments" value={kpis.pending_payments} />
        <StatCard label="Today's revenue" value={`₹${kpis.todays_revenue.toLocaleString()}`} />
      </div>

      <div className="mt-8 rounded border border-ink-700/10 bg-white p-6">
        <p className="font-display text-lg text-ink-900">Revenue — last 14 days</p>
        <p className="text-sm text-ink-700/60">Monthly total so far: ₹{kpis.monthly_revenue.toLocaleString()}</p>
        <div className="mt-6 flex h-40 items-end gap-2">
          {trend.length === 0 ? (
            <p className="text-sm text-ink-700/50">No paid invoices in this window yet.</p>
          ) : (
            trend.map((point) => (
              <div key={point.date} className="flex flex-1 flex-col items-center gap-1">
                <div
                  className="w-full rounded-t bg-brass-500"
                  style={{ height: `${Math.max(4, (point.revenue / maxRevenue) * 100)}%` }}
                  title={`₹${point.revenue.toLocaleString()}`}
                />
                <span className="text-[10px] text-ink-700/50">{point.date.slice(5)}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
