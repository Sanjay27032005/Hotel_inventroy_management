export function Button({ variant = "primary", size = "md", className = "", as: As = "button", ...props }) {
  const base = "inline-flex items-center justify-center gap-2 rounded font-medium transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed";
  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-5 py-2.5 text-sm",
    lg: "px-7 py-3 text-base",
  };
  const variants = {
    primary: "bg-ink-800 text-linen-50 hover:bg-ink-900",
    brass: "bg-brass-500 text-ink-900 hover:bg-brass-600",
    outline: "border border-ink-800 text-ink-800 hover:bg-ink-800 hover:text-linen-50",
    ghost: "text-ink-800 hover:bg-linen-200",
    danger: "bg-wine-700 text-linen-50 hover:bg-wine-600",
  };
  return (
    <As className={`${base} ${sizes[size]} ${variants[variant]} ${className}`} {...props} />
  );
}

export function Input({ label, error, className = "", labelClassName = "text-ink-800", id, ...props }) {
  const inputId = id || props.name;
  return (
    <label className="block" htmlFor={inputId}>
      {label && <span className={`mb-1.5 block text-sm font-medium ${labelClassName}`}>{label}</span>}
      <input
        id={inputId}
        className={`w-full rounded border border-ink-700/20 bg-linen-50 px-3.5 py-2.5 text-sm text-ink-900 placeholder:text-ink-700/40 focus:border-brass-500 focus:outline-none ${className}`}
        {...props}
      />
      {error && <span className="mt-1 block text-xs text-wine-700">{error}</span>}
    </label>
  );
}

export function Textarea({ label, error, className = "", id, ...props }) {
  const inputId = id || props.name;
  return (
    <label className="block" htmlFor={inputId}>
      {label && <span className="mb-1.5 block text-sm font-medium text-ink-800">{label}</span>}
      <textarea
        id={inputId}
        className={`w-full rounded border border-ink-700/20 bg-linen-50 px-3.5 py-2.5 text-sm text-ink-900 placeholder:text-ink-700/40 focus:border-brass-500 focus:outline-none ${className}`}
        {...props}
      />
      {error && <span className="mt-1 block text-xs text-wine-700">{error}</span>}
    </label>
  );
}

export function Select({ label, error, className = "", id, children, ...props }) {
  const inputId = id || props.name;
  return (
    <label className="block" htmlFor={inputId}>
      {label && <span className="mb-1.5 block text-sm font-medium text-ink-800">{label}</span>}
      <select
        id={inputId}
        className={`w-full rounded border border-ink-700/20 bg-linen-50 px-3.5 py-2.5 text-sm text-ink-900 focus:border-brass-500 focus:outline-none ${className}`}
        {...props}
      >
        {children}
      </select>
      {error && <span className="mt-1 block text-xs text-wine-700">{error}</span>}
    </label>
  );
}

const STATUS_TONES = {
  available: "bg-ink-700/10 text-ink-700",
  active: "bg-ink-700/10 text-ink-700",
  confirmed: "bg-ink-700/10 text-ink-700",
  paid: "bg-ink-700/10 text-ink-700",
  completed: "bg-ink-700/10 text-ink-700",
  delivered: "bg-ink-700/10 text-ink-700",
  pending: "bg-brass-500/20 text-brass-600",
  reserved: "bg-brass-500/20 text-brass-600",
  occupied: "bg-brass-500/20 text-brass-600",
  partially_paid: "bg-brass-500/20 text-brass-600",
  preparing: "bg-brass-500/20 text-brass-600",
  cancelled: "bg-wine-700/10 text-wine-700",
  rejected: "bg-wine-700/10 text-wine-700",
  not_available: "bg-wine-700/10 text-wine-700",
  refunded: "bg-wine-700/10 text-wine-700",
};

export function Badge({ status, children }) {
  const key = (status || "").toLowerCase();
  const tone = STATUS_TONES[key] || "bg-ink-700/10 text-ink-700";
  const text = children || (status ? status.replace(/_/g, " ") : "");
  return <span className={`inline-block rounded-full px-2.5 py-1 text-xs font-medium capitalize ${tone}`}>{text}</span>;
}

export function Card({ className = "", children }) {
  return <div className={`rounded border border-ink-700/10 bg-white p-6 ${className}`}>{children}</div>;
}

export function Spinner({ className = "" }) {
  return (
    <div className={`h-5 w-5 animate-spin rounded-full border-2 border-ink-700/20 border-t-brass-500 ${className}`} />
  );
}

export function EmptyState({ title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center rounded border border-dashed border-ink-700/20 px-6 py-16 text-center">
      <p className="font-display text-lg text-ink-800">{title}</p>
      {description && <p className="mt-2 max-w-sm text-sm text-ink-700/70">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
