import { NavLink, Outlet } from "react-router-dom";
import { cn } from "../lib/utils";

const links = [
  { to: "/", label: "Papers", end: true },
  { to: "/run", label: "Run an audit", end: false },
  { to: "/evaluation", label: "Evaluation", end: false },
];

export function Layout() {
  return (
    <>
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:bg-surface focus:p-2">Skip to content</a>
      <header className="border-b border-border bg-surface">
        <div className="mx-auto flex max-w-[1100px] flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-3">
          <span className="font-serif text-lg font-semibold">Claim Integrity Auditor</span>
          <nav aria-label="Main" className="flex gap-4 text-sm">
            {links.map((l) => (
              <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => cn("py-1 text-primary hover:underline", isActive && "font-semibold underline underline-offset-4")}>
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main id="main" className="mx-auto max-w-[1100px] px-4 py-8">
        <Outlet />
      </main>
    </>
  );
}
