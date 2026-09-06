import { useEffect, useState } from "react";
import { restaurantApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Button, Input, Select, Badge, Spinner } from "../../components/ui";

const ORDER_STATUSES = ["new", "preparing", "ready", "served", "completed", "cancelled"];

export default function Restaurant() {
  const [tab, setTab] = useState("orders");
  const [tables, setTables] = useState([]);
  const [menu, setMenu] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [orderForm, setOrderForm] = useState({ customer_id: "", table_id: "", discount: 0 });
  const [lines, setLines] = useState([{ food_item_id: "", quantity: 1 }]);

  function load() {
    setLoading(true);
    Promise.all([restaurantApi.tables(), restaurantApi.menu(), restaurantApi.orders()])
      .then(([t, m, o]) => {
        setTables(t.data);
        setMenu(m.data);
        setOrders(o.data);
      })
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  function updateLine(index, field, value) {
    setLines((ls) => ls.map((l, i) => (i === index ? { ...l, [field]: value } : l)));
  }

  async function submitOrder(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await restaurantApi.createOrder({
        customer_id: Number(orderForm.customer_id),
        table_id: orderForm.table_id ? Number(orderForm.table_id) : null,
        discount: Number(orderForm.discount),
        items: lines.filter((l) => l.food_item_id).map((l) => ({
          food_item_id: Number(l.food_item_id), quantity: Number(l.quantity),
        })),
      });
      setOrderForm({ customer_id: "", table_id: "", discount: 0 });
      setLines([{ food_item_id: "", quantity: 1 }]);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create this order."));
    } finally {
      setSubmitting(false);
    }
  }

  async function updateStatus(id, status) {
    await restaurantApi.updateOrderStatus(id, status);
    load();
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader title="Restaurant" description="Tables, menu and food orders." />

      <div className="mb-6 flex gap-2">
        {["orders", "tables", "menu"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-full px-4 py-1.5 text-sm capitalize ${tab === t ? "bg-ink-900 text-linen-50" : "bg-white text-ink-700/70"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "orders" && (
        <>
          <form onSubmit={submitOrder} className="mb-8 space-y-4 rounded border border-ink-700/10 bg-white p-6">
            <p className="font-medium text-ink-900">New food order</p>
            <div className="grid gap-4 sm:grid-cols-3">
              <Input label="Customer ID" required type="number" value={orderForm.customer_id}
                onChange={(e) => setOrderForm((f) => ({ ...f, customer_id: e.target.value }))} />
              <Select label="Table (optional)" value={orderForm.table_id}
                onChange={(e) => setOrderForm((f) => ({ ...f, table_id: e.target.value }))}>
                <option value="">Takeaway / no table</option>
                {tables.map((t) => <option key={t.id} value={t.id}>Table {t.table_number}</option>)}
              </Select>
              <Input label="Discount" type="number" value={orderForm.discount}
                onChange={(e) => setOrderForm((f) => ({ ...f, discount: e.target.value }))} />
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium text-ink-800">Items</p>
              {lines.map((line, i) => (
                <div key={i} className="flex gap-3">
                  <Select value={line.food_item_id} onChange={(e) => updateLine(i, "food_item_id", e.target.value)} className="flex-1">
                    <option value="">Select a food item</option>
                    {menu.map((m) => <option key={m.id} value={m.id}>{m.name} — ₹{m.price}</option>)}
                  </Select>
                  <Input type="number" min="1" className="w-24" value={line.quantity}
                    onChange={(e) => updateLine(i, "quantity", e.target.value)} />
                </div>
              ))}
              <Button type="button" variant="ghost" size="sm" onClick={() => setLines((ls) => [...ls, { food_item_id: "", quantity: 1 }])}>
                + Add item
              </Button>
            </div>
            {error && <p className="text-sm text-wine-700">{error}</p>}
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? "Placing order…" : "Place Order"}
            </Button>
          </form>

          <DataTable
            columns={[
              { key: "order_code", header: "Order ID" },
              { key: "items", header: "Items", render: (r) => r.items.map((i) => `${i.quantity}× item#${i.food_item_id}`).join(", ") },
              { key: "total_amount", header: "Total", render: (r) => `₹${r.total_amount}` },
              { key: "payment_status", header: "Payment", render: (r) => <Badge status={r.payment_status} /> },
              {
                key: "status", header: "Status", render: (r) => (
                  <Select value={r.status} onChange={(e) => updateStatus(r.id, e.target.value)} className="!py-1 text-xs">
                    {ORDER_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </Select>
                ),
              },
            ]}
            rows={orders}
            emptyMessage="No orders placed yet."
          />
        </>
      )}

      {tab === "tables" && (
        <DataTable
          columns={[
            { key: "table_number", header: "Table" },
            { key: "capacity", header: "Capacity" },
            { key: "table_type", header: "Type" },
            { key: "status", header: "Status", render: (r) => <Badge status={r.status} /> },
          ]}
          rows={tables}
        />
      )}

      {tab === "menu" && (
        <DataTable
          columns={[
            { key: "name", header: "Item" },
            { key: "price", header: "Price", render: (r) => `₹${r.price}` },
            { key: "tax_percentage", header: "Tax %" },
            { key: "is_available", header: "Available", render: (r) => (r.is_available ? "Yes" : "No") },
          ]}
          rows={menu}
        />
      )}
    </div>
  );
}
