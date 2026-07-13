import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "FactoryMind — Industrial Intelligence",
  description: "Multimodal Industrial Intelligence Platform",
};

const nav = [
  { href: "/", label: "Dashboard" },
  { href: "/machine-health", label: "Machine Health" },
  { href: "/defect-inspector", label: "Defect Inspector" },
  { href: "/shift-reports", label: "Shift Reports" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen">
          <aside className="w-56 border-r border-border bg-surface p-5">
            <div className="mb-8">
              <span className="font-display text-xl font-bold text-orange">Factory</span>
              <span className="font-display text-xl font-bold text-txt">Mind</span>
            </div>
            <nav className="flex flex-col gap-1">
              {nav.map((n) => (
                <Link
                  key={n.href}
                  href={n.href}
                  className="rounded px-3 py-2 text-sm text-txt2 hover:bg-orange/10 hover:text-orange"
                >
                  {n.label}
                </Link>
              ))}
            </nav>
          </aside>
          <main className="flex-1 p-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
