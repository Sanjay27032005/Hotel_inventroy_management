import { useEffect, useState } from "react";
import { laundryApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Button, Input, Select, Badge, Spinner } from "../../components/ui";

const STATUSES = ["received", "washing", "drying", "ironing", "ready", "delivered", "cancelled"];

export default function Laundry() {
  const [prices, setPrices] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({ customer_id: "", room_number: "", pricing_method: "quantity_based", discount: 0, tax: 0 });
  const [lines, setLines] = useState([{ cloth_type: "", quantity: 1 }]);

  function load() {
    setLoading(true);
    Promise.all([laundryApi.prices(), laundryApi.orders()])
      .then(([p, o]) => { setPrices(p.data); setOrders(o.data); })
      .finally(() => setLoading(false));
  }
  useEffect(load, []);

  function updateLine(i, field, value) {
    setLines((ls) => ls.map((l, idx) => (idx === i ? { ...l, [field]: value } : l)));
  }

  async function submit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await laundryApi.createOrder({
        ...form,
        customer_id: Number(form.customer_id),
        discount: Number(form.discount),
        tax: Number(form.tax),
        items: lines.filter((l) => l.cloth_type).map((l) => ({ ...l, quantity: Number(l.quantity) })),
      });
      setForm({ customer_id: "", room_number: "", pricing_method: "quantity_based", discount: 0, tax: 0 });
      setLines([{ cloth_type: "", quantity: 1 }]);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create this laundry order."));
    } finally {
      setSubmitting(false);
    }
  }

  async function updateStatus(id, status) {
    await laundryApi.updateStatus(id, status);
    load();
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader title="Laundry" description="Cloth pricing and laundry orders, tracked from pickup to delivery." />

      <form onSubmit={submit} className="mb-8 space-y-4 rounded border border-ink-700/10 bg-white p-6">
        <p className="font-medium text-ink-900">New laundry order</p>
        <div className="grid gap-4 sm:grid-cols-3">
          <Input label="Customer ID" required type="number" value={form.customer_id}
            onChange={(e) => setForm((f) => ({ ...f, customer_id: e.target.value }))} />
          <Input label="Room number" value={form.room_number}
            onChange={(e) => setForm((f) => ({ ...f, room_number: e.target.value }))} />
          <Select label="Pricing method" value={form.pricing_method}
            onChange={(e) => setForm((f) => ({ ...f, pricing_method: e.target.value }))}>
            <option value="quantity_based">Quantity-based</option>
            <option value="cloth_based">Cloth-based</option>
          </Select>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-medium text-ink-800">Items</p>
          {lines.map((line, i) => (
            <div key={i} className="flex gap-3">
              <Select value={line.cloth_type} onChange={(e) => updateLine(i, "cloth_type", e.target.value)} className="flex-1">
                <option value="">Select cloth type</option>
                {prices.map((p) => <option key={p.id} value={p.cloth_type}>{p.cloth_type} — ₹{p.unit_price}</option>)}
              </Select>
              <Input type="number" min="1" className="w-24" value={line.quantity}
                onChange={(e) => updateLine(i, "quantity", e.target.value)} />
            </div>
          ))}
          <Button type="button" variant="ghost" size="sm" onClick={() => setLines((ls) => [...ls, { cloth_type: "", quantity: 1 }])}>
            + Add item
          </Button>
        </div>
        {error && <p className="text-sm text-wine-700">{error}</p>}
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? "Creating…" : "Create Order"}
        </Button>
      </form>

      <DataTable
        columns={[
          { key: "order_code", header: "Order ID" },
          { key: "room_number", header: "Room" },
          { key: "total_amount", header: "Total", render: (r) => `₹${r.total_amount}` },
          { key: "payment_status", header: "Payment", render: (r) => <Badge status={r.payment_status} /> },
          {
            key: "status", header: "Status", render: (r) => (
              <Select value={r.status} onChange={(e) => updateStatus(r.id, e.target.value)} className="!py-1 text-xs">
                {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </Select>
            ),
          },
        ]}
        rows={orders}
        emptyMessage="No laundry orders yet."
      />
    </div>
  );
}
