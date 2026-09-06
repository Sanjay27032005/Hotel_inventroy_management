import { useEffect, useState } from "react";
import { contactApi } from "../../api/endpoints";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Select, Spinner } from "../../components/ui";

const STATUSES = ["new", "in_progress", "resolved"];

export default function Enquiries() {
  const [enquiries, setEnquiries] = useState([]);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    contactApi.list().then((res) => setEnquiries(res.data)).finally(() => setLoading(false));
  }
  useEffect(load, []);

  async function updateStatus(id, status) {
    await contactApi.updateStatus(id, status);
    load();
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader title="Enquiries" description="Contact Us submissions from the customer website." />
      <DataTable
        columns={[
          { key: "name", header: "Name" },
          { key: "email", header: "Email" },
          { key: "subject", header: "Subject" },
          { key: "message", header: "Message", render: (r) => <span className="line-clamp-2 max-w-xs">{r.message}</span> },
          {
            key: "status", header: "Status", render: (r) => (
              <Select value={r.status} onChange={(e) => updateStatus(r.id, e.target.value)} className="!py-1 text-xs">
                {STATUSES.map((s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
              </Select>
            ),
          },
        ]}
        rows={enquiries}
        emptyMessage="No enquiries submitted yet."
      />
    </div>
  );
}
