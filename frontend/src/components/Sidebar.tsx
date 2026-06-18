"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import { Sprout, Truck, LayoutDashboard, AlertTriangle, Map, BarChart3 } from "lucide-react";

const navItems = [
  {
    label: "Reklamasi",
    href: "/reklamasi",
    icon: Sprout,
    children: [
      { label: "Dashboard", href: "/reklamasi", icon: LayoutDashboard },
    ],
  },
  {
    label: "Operasional",
    href: "/operasional",
    icon: Truck,
    children: [
      { label: "Dashboard", href: "/operasional", icon: BarChart3 },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-60 bg-white border-r border-gray-200 flex flex-col">
      <div className="flex items-center gap-2 px-5 h-16 border-b border-gray-200">
        <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
          <Map className="w-4 h-4 text-white" />
        </div>
        <span className="font-bold text-lg text-gray-900">KidecoIQ</span>
      </div>

      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {navItems.map((group) => (
          <div key={group.label}>
            <div className="flex items-center gap-2 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-gray-400">
              <group.icon className="w-3.5 h-3.5" />
              {group.label}
            </div>
            <div className="mt-1 space-y-0.5">
              {group.children.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={clsx(
                      "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                      isActive
                        ? "bg-emerald-50 text-emerald-700"
                        : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                    )}
                  >
                    <item.icon className="w-4 h-4" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-gray-200">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <AlertTriangle className="w-3 h-3" />
          <span>MVP Demo v0.1</span>
        </div>
      </div>
    </aside>
  );
}
