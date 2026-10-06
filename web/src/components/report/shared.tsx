import type { ReactNode } from "react";
import type { Grade } from "../../types/contract";
import { Badge, type BadgeVariant } from "../ui/badge";
import { cn } from "../../lib/utils";

export const TRIAGE_LINE = "Automated triage. Human review required.";

export const TriageNote = () => <p className="mt-10 border-t border-border pt-4 text-sm text-muted">{TRIAGE_LINE}</p>;

// Display styling only: maps a verdict phrase to a badge colour. Nothing here decides a grade.
const VERDICT_VARIANT: Record<string, BadgeVariant> = {
  reproduced: "ok",
  supports: "ok",
  "none found": "ok",
  loads: "ok",
  "not reproduced": "attn",
  "not supported": "attn",
  fails: "attn",
  "retraction record found": "record",
  "not checkable": "neutral",
  absent: "neutral",
};

export const VerdictBadge = ({ verdict }: { verdict: string }) => <Badge variant={VERDICT_VARIANT[verdict] ?? "neutral"}>{verdict}</Badge>;

const GRADE_STYLE: Record<Grade, string> = {
  A: "bg-ok-bg text-ok-fg border-ok-fg",
  B: "bg-info-bg text-info-fg border-info-fg",
  C: "bg-attn-bg text-attn-fg border-attn-fg",
  D: "bg-record-bg text-record-fg border-record-fg",
  withheld: "bg-neutral-bg text-neutral-fg border-neutral-fg",
};

/** The one bold element: the grade letter in a bordered seal. Text label always accompanies it. */
export const GradeSeal = ({ grade, className }: { grade: Grade; className?: string }) => (
  <span
    aria-hidden="true"
    className={cn("inline-flex h-14 w-14 shrink-0 items-center justify-center rounded border-2 font-serif text-3xl font-bold", GRADE_STYLE[grade], className)}
  >
    {grade === "withheld" ? "-" : grade}
  </span>
);

export const gradeLabel = (grade: Grade) => (grade === "withheld" ? "Grade withheld" : `Grade ${grade}`);

export const Section = ({ title, children }: { title: string; children: ReactNode }) => (
  <section className="mt-8">
    <h2 className="mb-3 text-xl font-semibold">{title}</h2>
    {children}
  </section>
);
