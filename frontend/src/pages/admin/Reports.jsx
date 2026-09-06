import { useEffect, useState } from "react";
import { reportsApi } from "../../api/endpoints";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Spinner } from "../../components/ui";

const REPORT_GROUPS = [
  {
    label: "Accommodation",
    reports: [
      { key: "accommodation/occupancy", label: "Room occupancy" },
      { key: "accommodation/revenue", label: "Room revenue" },
      { key: "accommodation/check-in", label: "Check-in report" },
      { key: "accommodation/check-out", label: "Check-out report" },
    ],
  },
  {
    label: "Restaurant",
    reports: [
      { key: "restaurant/food-sales", label: "Food sales" },
      { key: "restaurant/category-wise-sales", label: "Category-wise sales" },
      { key: "restaurant/daily-revenue", label: "Daily revenue" },
    ],
  },
  {
    label: "Events",
    reports: [
      { key: "events/upcoming", label: "Upcoming events" },
      { key: "events/revenue", label: "Event revenue" },
    ],
  },
  {
    label: "Spa",
    reports: [
      { key: "spa/therapist-sessions", label: "Therapist sessions" },
      { key: "spa/service-report", label: "Massage service report" },
      { key: "spa/revenue", label: "Spa revenue" },
    ],
  },
  {
    label: "Pool",
    reports: [
      { key: "pool/package-sales", label: "Package sales" },
      { key: "pool/customer-type-report", label: "Child/Adult/Couple report" },
      { key: "pool/trainer-package-report", label: "Trainer package report" },
    ],
  },
  {
    label: "Laundry",
    reports: [
      { key: "laundry/cloth-wise-sales", label: "Cloth-wise sales" },
      { key: "laundry/quantity-wise-sales", label: "Quantity-wise sales" },
      { key: "laundry/pending", label: "Pending laundry" },
      { key: "laundry/revenue", label: "Laundry revenue" },
    ],
  },
  {
    label: "Financial",
    reports: [
      { key: "financial/summary", label: "Revenue summary" },
      { key: "financial/daily-revenue", label: "Daily revenue" },
      { key: "financial/monthly-revenue", label: "Monthly revenue" },
      { key: "financial/invoices", label: "Invoice report" },
      { key: "financial/discounts", label: "Discount report" },
      { key: "financial/payments", label: "Payment report" },
    ],
  },
  {
    label: "Employees",
    reports: [
      { key: "employees/department-wise", label: "Department-wise headcount" },
      { key: "employees/activity", label: "Employee activity" },
      { key: "employees/login-activity", label: "User login activity" },
    ],
  },
];

function renderRows(key, data) {
  if (key === "financial/summary") {
    const rows = Object.entries(data.service_wise_revenue || {}).map(([service, revenue]) => ({ service, revenue }));
    return {
      rows,
      columns: [
        { key: "service", header: "Service", render: (r) => <span className="capitalize">{r.service.replace(/_/g, " ")}</span> },
        { key: "revenue", header: "Revenue", render: (r) => `₹${r.revenue.toLocaleString()}` },
      ],
      footer: `Pending payments: ₹${data.pending_payments_total.toLocaleString()} · Discounts given: ₹${data.total_discounts_given.toLocaleString()}`,
    };
  }
  if (key === "accommodation/occupancy") {
    const rows = Object.entries(data.by_status || {}).map(([status, count]) => ({ status, count }));
    return {
      rows,
      columns: [
        { key: "status", header: "Status", render: (r) => <span className="capitalize">{r.status.replace(/_/g, " ")}</span> },
        { key: "count", header: "Rooms" },
      ],
      footer: `Total rooms: ${data.total_rooms}`,
    };
  }
  if (["accommodation/revenue", "events/revenue", "spa/revenue", "laundry/revenue"].includes(key)) {
    const value = Object.values(data)[0];
    return { rows: [{ id: 1, label: Object.keys(data)[0].replace(/_/g, " "), value }], columns: [
      { key: "label", header: "Metric", render: (r) => <span className="capitalize">{r.label}</span> },
      { key: "value", header: "Amount", render: (r) => `₹${r.value.toLocaleString()}` },
    ] };
  }
  if (key === "financial/discounts") {
    const rows = (data.by_service || []).map((r, i) => ({ ...r, id: i }));
    return {
      rows,
      columns: [
        { key: "service_type", header: "Service", render: (r) => <span className="capitalize">{r.service_type.replace(/_/g, " ")}</span> },
        { key: "invoice_count", header: "Invoices" },
        { key: "total_discount", header: "Total discount", render: (r) => `₹${r.total_discount.toLocaleString()}` },
      ],
      footer: data.top_discounted_invoices?.length
        ? `Top discount: ${data.top_discounted_invoices[0].invoice_number} (₹${data.top_discounted_invoices[0].discount.toLocaleString()})`
        : undefined,
    };
  }
  if (Array.isArray(data)) {
    if (data.length === 0) return { rows: [], columns: [] };
    const sample = data[0];
    const columns = Object.keys(sample)
      .filter((k) => typeof sample[k] !== "object")
      .slice(0, 6)
      .map((k) => ({ key: k, header: k.replace(/_/g, " ") }));
    return { rows: data.map((row, i) => ({ ...row, id: row.id ?? i })), columns };
  }
  return { rows: [], columns: [] };
}

export default function Reports() {
  const [active, setActive] = useState(REPORT_GROUPS[0].reports[0]);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    reportsApi.get(active.key).then((res) => setData(res.data)).finally(() => setLoading(false));
  }, [active]);

  const view = data ? renderRows(active.key, data) : { rows: [], columns: [] };

  return (
    <div>
      <PageHeader title="Reports" description="Operational and financial reports across every module." />

      <div className="grid gap-6 lg:grid-cols-[220px_1fr]">
        <nav className="space-y-5">
          {REPORT_GROUPS.map((group) => (
            <div key={group.label}>
              <p className="px-1 text-xs font-medium text-ink-700/50">{group.label}</p>
              <div className="mt-1 flex flex-col gap-0.5">
                {group.reports.map((r) => (
                  <button
                    key={r.key}
                    onClick={() => setActive(r)}
                    className={`rounded px-3 py-1.5 text-left text-sm ${active.key === r.key ? "bg-ink-900 text-linen-50" : "text-ink-700/80 hover:bg-linen-200"}`}
                  >
                    {r.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div>
          <p className="mb-3 font-display text-lg text-ink-900">{active.label}</p>
          {loading ? (
            <Spinner />
          ) : (
            <>
              <DataTable columns={view.columns} rows={view.rows} emptyMessage="No data for this report yet." />
              {view.footer && <p className="mt-3 text-sm text-ink-700/60">{view.footer}</p>}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
