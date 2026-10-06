import type { PaperBundle } from "../../types/contract";

export interface CheckRow {
  key: string;
  check: string;
  item: string;
  detail?: string;
  verdict: string;
  page: number | null;
  quote?: string;
  note?: string;
  raw: unknown;
}

const S = "S source supports claim";
const R = "R statistic reproduces";
const N = "N no retraction found";
const C = "C code/data loads";

/** Flattens the stage files into table rows, in file order. No verdict is created or changed here. */
export function buildRows(b: PaperBundle): CheckRow[] {
  const claimText = (id: string) => b.claims.claims.find((c) => c.id === id)?.claim ?? id;
  const rows: CheckRow[] = [];

  b.citations.results.forEach((r, i) =>
    rows.push({
      key: `s${i}`, check: S, item: `${r.claim_id}: ${claimText(r.claim_id)}`, detail: `Cited work: ${r.cited_doi}`,
      verdict: r.verdict, page: r.page, quote: r.quote, note: `${r.evidence_label}: ${r.passage}`, raw: r,
    }),
  );
  b.stats.results.forEach((r, i) =>
    rows.push({
      key: `r${i}`, check: R, item: `${r.claim_id}: ${claimText(r.claim_id)}`,
      detail: [r.test && `Test ${r.test}`, r.df && `df ${r.df}`, r.reported_p && `reported p ${r.reported_p}`, r.recomputed_p !== null && `recomputed p ${r.recomputed_p}`].filter(Boolean).join(", ") || "Statistic could not be parsed",
      verdict: r.verdict, page: r.page, quote: r.quote, note: r.formula ? `Formula: ${r.formula}` : undefined, raw: r,
    }),
  );
  b.retraction.results.forEach((r, i) =>
    rows.push({
      key: `n${i}`, check: N, item: `DOI ${r.doi}`, verdict: r.status, page: null,
      note: r.source_field ? `Source field: ${r.source_field}` : "No source field", raw: r,
    }),
  );
  b.codeData.results.forEach((r, i) =>
    rows.push({
      key: `c${i}`, check: C, item: r.url ?? "No code or data link in the paper", verdict: r.status, page: null,
      note: r.http_status !== null ? `HTTP status ${r.http_status}` : undefined, raw: r,
    }),
  );
  return rows;
}
