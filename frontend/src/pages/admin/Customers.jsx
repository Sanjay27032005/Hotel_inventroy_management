import { useEffect, useState } from "react";
import { customerApi } from "../../api/endpoints";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Input, Badge, Spinner } from "../../components/ui";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setLoading(true);
      customerApi.list(search || undefined).then((res) => setCustomers(res.data)).finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timeout);
  }, [search]);

  return (
    <div>
      <PageHeader title="Customers" description="Everyone who has registered or booked with the property." />

      <div className="mb-6 max-w-sm">
        <Input placeholder="Search by name, email, phone or code" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <DataTable
          columns={[
            { key: "customer_code", header: "ID" },
            { key: "name", header: "Name", render: (r) => `${r.first_name} ${r.last_name}` },
            { key: "email", header: "Email" },
            { key: "phone", header: "Phone" },
            { key: "city", header: "City" },
            { key: "status", header: "Status", render: (r) => <Badge status={r.status} /> },
          ]}
          rows={customers}
          emptyMessage="No customers match this search yet."
        />
      )}
    </div>
  );
}
