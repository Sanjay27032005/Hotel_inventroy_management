export function StatCard({ label, value, hint }) {
  return (
    <div className="rounded border border-ink-700/10 bg-white p-5">
      <div className="h-1 w-8 rounded-full bg-brass-500" />
      <p className="mt-3 text-2xl font-semibold text-ink-900">{value}</p>
      <p className="mt-1 text-sm text-ink-700/70">{label}</p>
      {hint && <p className="mt-0.5 text-xs text-ink-700/50">{hint}</p>}
    </div>
  );
}

export function PageHeader({ title, description, actions }) {
  return (
    <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div>
        <h1 className="font-display text-2xl text-ink-900">{title}</h1>
        {description && <p className="mt-1 text-sm text-ink-700/70">{description}</p>}
      </div>
      {actions && <div className="flex gap-2">{actions}</div>}
    </div>
  );
}

export function DataTable({ columns, rows, keyField = "id", emptyMessage = "No records yet." }) {
  if (!rows || rows.length === 0) {
    return (
      <div className="rounded border border-dashed border-ink-700/20 px-6 py-14 text-center text-sm text-ink-700/60">
        {emptyMessage}
      </div>
    );
  }
  return (
    <div className="overflow-x-auto rounded border border-ink-700/10 bg-white">
      <table className="w-full min-w-max text-left text-sm">
        <thead>
          <tr className="border-b border-ink-700/10 bg-linen-100/60">
            {columns.map((col) => (
              <th key={col.key} className="whitespace-nowrap px-4 py-3 font-medium text-ink-700/70">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row[keyField]} className="border-b border-ink-700/5 last:border-0 hover:bg-linen-100/40">
              {columns.map((col) => (
                <td key={col.key} className="whitespace-nowrap px-4 py-3 text-ink-900">
                  {col.render ? col.render(row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
