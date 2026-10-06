import type { HTMLAttributes, TdHTMLAttributes, ThHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

/** Wide tables scroll inside this region, never the page. */
export function Table({ label, minWidth = "min-w-[56rem]", ...props }: HTMLAttributes<HTMLTableElement> & { label: string; minWidth?: string }) {
  return (
    <div className="overflow-x-auto rounded border border-border bg-surface" role="region" aria-label={label} tabIndex={0}>
      <table className={cn("w-full border-collapse text-left text-sm", minWidth)} {...props} />
    </div>
  );
}

export const Th = ({ scope = "col", className, ...props }: ThHTMLAttributes<HTMLTableCellElement>) => (
  <th scope={scope} className={cn("border-b border-border bg-paper px-3 py-2 font-semibold align-top", className)} {...props} />
);

export const Td = ({ className, ...props }: TdHTMLAttributes<HTMLTableCellElement>) => (
  <td className={cn("border-b border-border px-3 py-3 align-top", className)} {...props} />
);
