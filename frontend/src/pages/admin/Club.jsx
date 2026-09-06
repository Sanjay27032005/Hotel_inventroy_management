import { useEffect, useState } from "react";
import { clubApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Button, Input, Select, Badge, Spinner } from "../../components/ui";

export default function Club() {
  const [foodItems, setFoodItems] = useState([]);
  const [drinkItems, setDrinkItems] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({ customer_id: "", entry_fee: 0, tips: 0, service_charges: 0, tax: 0 });
  const [lines, setLines] = useState([{ item_type: "food", item_id: "", quantity: 1 }]);

  function load() {
    setLoading(true);
    Promise.all([clubApi.foodItems(), clubApi.drinkItems(), clubApi.orders()])
      .then(([f, d, o]) => { setFoodItems(f.data); setDrinkItems(d.data); setOrders(o.data); })
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
      await clubApi.createOrder({
        customer_id: Number(form.customer_id),
        entry_fee: Number(form.entry_fee),
        tips: Number(form.tips),
        service_charges: Number(form.service_charges),
        tax: Number(form.tax),
        lines: lines.filter((l) => l.item_id).map((l) => ({ ...l, item_id: Number(l.item_id), quantity: Number(l.quantity) })),
      });
      setForm({ customer_id: "", entry_fee: 0, tips: 0, service_charges: 0, tax: 0 });
      setLines([{ item_type: "food", item_id: "", quantity: 1 }]);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create this order."));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader title="Club & Bar" description="Entry, food, drinks and membership discounts." />

      <form onSubmit={submit} className="mb-8 space-y-4 rounded border border-ink-700/10 bg-white p-6">
        <p className="font-medium text-ink-900">New club order</p>
        <div className="grid gap-4 sm:grid-cols-4">
          <Input label="Customer ID" required type="number" value={form.customer_id}
            onChange={(e) => setForm((f) => ({ ...f, customer_id: e.target.value }))} />
          <Input label="Entry fee" type="number" value={form.entry_fee}
            onChange={(e) => setForm((f) => ({ ...f, entry_fee: e.target.value }))} />
          <Input label="Tips" type="number" value={form.tips}
            onChange={(e) => setForm((f) => ({ ...f, tips: e.target.value }))} />
          <Input label="Service charges" type="number" value={form.service_charges}
            onChange={(e) => setForm((f) => ({ ...f, service_charges: e.target.value }))} />
        </div>

        <div className="space-y-2">
          <p className="text-sm font-medium text-ink-800">Food & drinks</p>
          {lines.map((line, i) => (
            <div key={i} className="flex gap-3">
              <Select value={line.item_type} onChange={(e) => updateLine(i, "item_type", e.target.value)} className="w-28">
                <option value="food">Food</option>
                <option value="drink">Drink</option>
              </Select>
              <Select value={line.item_id} onChange={(e) => updateLine(i, "item_id", e.target.value)} className="flex-1">
                <option value="">Select an item</option>
                {(line.item_type === "food" ? foodItems : drinkItems).map((it) => (
                  <option key={it.id} value={it.id}>{it.name} — ₹{it.unit_price}</option>
                ))}
              </Select>
              <Input type="number" min="1" className="w-24" value={line.quantity}
                onChange={(e) => updateLine(i, "quantity", e.target.value)} />
            </div>
          ))}
          <Button type="button" variant="ghost" size="sm" onClick={() => setLines((ls) => [...ls, { item_type: "food", item_id: "", quantity: 1 }])}>
            + Add item
          </Button>
        </div>
        {error && <p className="text-sm text-wine-700">{error}</p>}
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? "Placing order…" : "Create Order"}
        </Button>
      </form>

      <DataTable
        columns={[
          { key: "order_code", header: "Order ID" },
          { key: "food_total", header: "Food", render: (r) => `₹${r.food_total}` },
          { key: "drinks_total", header: "Drinks", render: (r) => `₹${r.drinks_total}` },
          { key: "membership_discount", header: "Membership discount", render: (r) => `₹${r.membership_discount}` },
          { key: "total_amount", header: "Total", render: (r) => `₹${r.total_amount}` },
          { key: "payment_status", header: "Payment", render: (r) => <Badge status={r.payment_status} /> },
        ]}
        rows={orders}
        emptyMessage="No club orders yet."
      />
    </div>
  );
}
