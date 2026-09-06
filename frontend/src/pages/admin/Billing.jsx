import { useEffect, useState } from "react";
import { billingApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Button, Input, Select, Badge, Spinner } from "../../components/ui";

const SERVICE_TYPES = [
  ["restaurant", "Restaurant order"],
  ["accommodation", "Room booking"],
  ["party_hall", "Event booking"],
  ["swimming_pool", "Pool booking"],
  ["spa", "Spa booking"],
  ["club_bar", "Club order"],
  ["laundry", "Laundry order"],
];

const PAYMENT_METHODS = ["cash", "card", "upi", "bank_transfer", "online"];

export default function Billing() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [genForm, setGenForm] = useState({ service_type: "accommodation", reference_id: "" });
  const [payForm, setPayForm] = useState({ invoice_id: "", amount_paid: "", payment_method: "cash" });
  const [error, setError] = useState("");
  const [payError, setPayError] = useState("");

  function load() {
    setLoading(true);
    billingApi.invoices().then((res) => setInvoices(res.data)).finally(() => setLoading(false));
  }
  useEffect(load, []);

  async function generate(e) {
    e.preventDefault();
    setError("");
    try {
      await billingApi.generateInvoice(genForm.service_type, Number(genForm.reference_id));
      setGenForm({ ...genForm, reference_id: "" });
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't generate this invoice."));
    }
  }

  async function pay(e) {
    e.preventDefault();
    setPayError("");
    try {
      await billingApi.pay({
        invoice_id: Number(payForm.invoice_id),
        amount_paid: Number(payForm.amount_paid),
        payment_method: payForm.payment_method,
      });
      setPayForm({ invoice_id: "", amount_paid: "", payment_method: "cash" });
      load();
    } catch (err) {
      setPayError(apiErrorMessage(err, "Couldn't record this payment."));
    }
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader title="Billing & Invoices" description="Generate invoices from any service booking and record payments." />

      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <form onSubmit={generate} className="space-y-4 rounded border border-ink-700/10 bg-white p-6">
          <p className="font-medium text-ink-900">Generate invoice</p>
          <Select label="Service" value={genForm.service_type} onChange={(e) => setGenForm((f) => ({ ...f, service_type: e.target.value }))}>
            {SERVICE_TYPES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </Select>
          <Input label="Booking / Order ID (numeric)" required type="number" value={genForm.reference_id}
            onChange={(e) => setGenForm((f) => ({ ...f, reference_id: e.target.value }))} />
          {error && <p className="text-sm text-wine-700">{error}</p>}
          <Button type="submit" variant="primary">Generate Invoice</Button>
        </form>

        <form onSubmit={pay} className="space-y-4 rounded border border-ink-700/10 bg-white p-6">
          <p className="font-medium text-ink-900">Record payment</p>
          <Input label="Invoice ID" required type="number" value={payForm.invoice_id}
            onChange={(e) => setPayForm((f) => ({ ...f, invoice_id: e.target.value }))} />
          <Input label="Amount paid" required type="number" value={payForm.amount_paid}
            onChange={(e) => setPayForm((f) => ({ ...f, amount_paid: e.target.value }))} />
          <Select label="Payment method" value={payForm.payment_method} onChange={(e) => setPayForm((f) => ({ ...f, payment_method: e.target.value }))}>
            {PAYMENT_METHODS.map((m) => <option key={m} value={m}>{m.replace(/_/g, " ")}</option>)}
          </Select>
          {payError && <p className="text-sm text-wine-700">{payError}</p>}
          <Button type="submit" variant="brass">Record Payment</Button>
        </form>
      </div>

      <DataTable
        columns={[
          { key: "invoice_number", header: "Invoice #" },
          { key: "booking_code", header: "Booking" },
          { key: "service_type", header: "Service", render: (r) => <span className="capitalize">{r.service_type.replace(/_/g, " ")}</span> },
          { key: "grand_total", header: "Total", render: (r) => `₹${r.grand_total}` },
          { key: "payment_status", header: "Payment", render: (r) => <Badge status={r.payment_status} /> },
          {
            key: "pdf", header: "", render: (r) => (
              <a href={billingApi.invoicePdfUrl(r.id)} target="_blank" rel="noreferrer" className="text-brass-600 hover:underline">
                View PDF
              </a>
            ),
          },
        ]}
        rows={invoices}
        emptyMessage="No invoices generated yet."
      />
    </div>
  );
}
