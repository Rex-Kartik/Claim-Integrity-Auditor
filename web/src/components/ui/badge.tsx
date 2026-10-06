import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";
import { cn } from "../../lib/utils";

const badgeVariants = cva("inline-flex items-center rounded border px-2 py-0.5 text-sm font-medium whitespace-nowrap", {
  variants: {
    variant: {
      ok: "bg-ok-bg text-ok-fg border-ok-fg/40",
      info: "bg-info-bg text-info-fg border-info-fg/40",
      attn: "bg-attn-bg text-attn-fg border-attn-fg/40",
      record: "bg-record-bg text-record-fg border-record-fg/40",
      neutral: "bg-neutral-bg text-neutral-fg border-neutral-fg/40",
    },
  },
  defaultVariants: { variant: "neutral" },
});

export type BadgeVariant = NonNullable<VariantProps<typeof badgeVariants>["variant"]>;

export function Badge({ className, variant, ...props }: HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
