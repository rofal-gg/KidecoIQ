import { clsx } from "clsx";

interface BadgeProps {
  variant?: "default" | "success" | "warning" | "danger" | "info";
  children: React.ReactNode;
  className?: string;
}

const variantStyles: Record<string, string> = {
  default: "bg-gray-100 text-gray-700",
  success: "bg-emerald-100 text-emerald-700",
  warning: "bg-amber-100 text-amber-700",
  danger: "bg-red-100 text-red-700",
  info: "bg-blue-100 text-blue-700",
};

export default function Badge({ variant = "default", children, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

export function statusBadgeVariant(status: string) {
  switch (status) {
    case "vegetasi_sehat": return "success";
    case "vegetasi_stres": return "warning";
    case "lahan_kosong": return "danger";
    case "air": return "info";
    default: return "default";
  }
}

export function statusLabel(status: string) {
  switch (status) {
    case "vegetasi_sehat": return "Vegetasi Sehat";
    case "vegetasi_stres": return "Vegetasi Stres";
    case "lahan_kosong": return "Lahan Kosong";
    case "air": return "Air";
    default: return status;
  }
}
