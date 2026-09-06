import { useEffect, useState } from "react";
import { bookingApi } from "../../api/endpoints";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Select, Input, Button, Badge, Spinner } from "../../components/ui";

const ENQUIRY_STATUSES = ["new", "in_progress", "resolved"];

export default function Bookings() {
  const [stayRequests, setStayRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lookupCode, setLookupCode] = useState("");
  const [lookupResults, setLookupResults] = useState(null);

  function load() {
    setLoading(true);
    bookingApi.stayRequests().then((res) => setStayRequests(res.data)).finally(() => setLoading(false));
  }
  useEffect(load, []);

  async function updateStatus(id, status) {
    await bookingApi.updateStayRequestStatus(id, status);
    load();
  }

  async function lookup(e) {
    e.preventDefault();
    const res = await bookingApi.lookup({ booking_code: lookupCode });
    setLookupResults(res.data);
  }

  return (
    <div>
      <PageHeader title="Bookings & Stay Requests" description="Book a Stay enquiries and booking lookups." />

      <form onSubmit={lookup} className="mb-8 flex items-end gap-3 rounded border border-ink-700/10 bg-white p-6">
        <Input label="Look up any booking by ID" placeholder="BK-2026-000001" value={lookupCode}
          onChange={(e) => setLookupCode(e.target.value)} className="flex-1" />
        <Button type="submit" variant="primary">Search</Button>
      </form>

      {lookupResults && (
        <div className="mb-8">
          <DataTable
            columns={[
              { key: "booking_code", header: "Booking ID" },
              { key: "booking_type", header: "Type", render: (r) => <span className="capitalize">{r.booking_type.replace(/_/g, " ")}</span> },
              { key: "status", header: "Status", render: (r) => <Badge status={r.status} /> },
            ]}
            rows={lookupResults}
            emptyMessage="No booking found with that ID."
          />
        </div>
      )}

      <p className="mb-3 font-medium text-ink-900">Book a Stay requests</p>
      {loading ? (
        <Spinner />
      ) : (
        <DataTable
          columns={[
            { key: "name", header: "Name", render: (r) => `${r.first_name} ${r.last_name}` },
            { key: "email", header: "Email" },
            { key: "phone", header: "Phone" },
            { key: "requirement_text", header: "Requirement", render: (r) => <span className="line-clamp-2 max-w-xs">{r.requirement_text}</span> },
            {
              key: "status", header: "Status", render: (r) => (
                <Select value={r.status} onChange={(e) => updateStatus(r.id, e.target.value)} className="!py-1 text-xs">
                  {ENQUIRY_STATUSES.map((s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
                </Select>
              ),
            },
          ]}
          rows={stayRequests}
          emptyMessage="No Book a Stay requests yet."
        />
      )}
    </div>
  );
}
