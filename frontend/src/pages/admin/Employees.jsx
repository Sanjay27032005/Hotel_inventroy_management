import { useEffect, useState } from "react";
import { employeeApi } from "../../api/endpoints";
import { apiErrorMessage } from "../../api/client";
import { PageHeader, DataTable } from "../../components/admin-ui";
import { Button, Input, Select, Badge, Spinner } from "../../components/ui";

const ROLES = [
  "manager", "general_manager", "billing_person", "room_servant", "food_servant", "chef",
];

const EMPTY_FORM = {
  first_name: "", last_name: "", email: "", phone: "", role: "billing_person",
  department_id: "", create_login: false, username: "", password: "",
};

export default function Employees() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    setLoading(true);
    Promise.all([employeeApi.list(), employeeApi.listDepartments()])
      .then(([emp, dept]) => {
        setEmployees(emp.data);
        setDepartments(dept.data);
      })
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  function update(field) {
    return (e) => {
      const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
      setForm((f) => ({ ...f, [field]: value }));
    };
  }

  async function submit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const payload = { ...form, department_id: form.department_id || null };
      await employeeApi.create(payload);
      setForm(EMPTY_FORM);
      setShowForm(false);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create this employee."));
    } finally {
      setSubmitting(false);
    }
  }

  async function deactivate(id) {
    if (!window.confirm("Deactivate this employee? Their login will also be disabled.")) return;
    await employeeApi.deactivate(id);
    load();
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <PageHeader
        title="Employees"
        description="Create staff accounts and manage roles across the hotel hierarchy."
        actions={
          <Button variant="brass" size="sm" onClick={() => setShowForm((v) => !v)}>
            {showForm ? "Cancel" : "Add Employee"}
          </Button>
        }
      />

      {showForm && (
        <form onSubmit={submit} className="mb-8 space-y-4 rounded border border-ink-700/10 bg-white p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="First Name" required value={form.first_name} onChange={update("first_name")} />
            <Input label="Last Name" required value={form.last_name} onChange={update("last_name")} />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="Email" type="email" required value={form.email} onChange={update("email")} />
            <Input label="Phone" value={form.phone} onChange={update("phone")} />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Select label="Role" value={form.role} onChange={update("role")}>
              {ROLES.map((r) => (
                <option key={r} value={r}>{r.replace(/_/g, " ")}</option>
              ))}
            </Select>
            <Select label="Department" value={form.department_id} onChange={update("department_id")}>
              <option value="">Unassigned</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </Select>
          </div>
          <label className="flex items-center gap-2 text-sm text-ink-800">
            <input type="checkbox" checked={form.create_login} onChange={update("create_login")} />
            Create a login account for this employee now
          </label>
          {form.create_login && (
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Username" required={form.create_login} value={form.username} onChange={update("username")} />
              <Input label="Password" type="password" required={form.create_login} value={form.password} onChange={update("password")} />
            </div>
          )}
          {error && <p className="text-sm text-wine-700">{error}</p>}
          <Button type="submit" variant="primary" disabled={submitting}>
            {submitting ? "Creating…" : "Create Employee"}
          </Button>
        </form>
      )}

      <DataTable
        columns={[
          { key: "employee_code", header: "ID" },
          { key: "name", header: "Name", render: (r) => `${r.first_name} ${r.last_name}` },
          { key: "email", header: "Email" },
          { key: "role", header: "Role", render: (r) => <span className="capitalize">{r.role.replace(/_/g, " ")}</span> },
          { key: "status", header: "Status", render: (r) => <Badge status={r.status} /> },
          { key: "login", header: "Login", render: (r) => (r.has_login ? "Yes" : "No") },
          {
            key: "actions", header: "", render: (r) => (
              r.status === "active" && (
                <Button variant="ghost" size="sm" onClick={() => deactivate(r.id)}>Deactivate</Button>
              )
            ),
          },
        ]}
        rows={employees}
        emptyMessage="No employees yet — add your first team member above."
      />
    </div>
  );
}
