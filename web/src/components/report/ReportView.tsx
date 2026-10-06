import type { PaperBundle } from "../../types/contract";
import { Badge } from "../ui/badge";
import { Table, Td, Th } from "../ui/table";
import { buildRows } from "./rows";
import { GradeSeal, Section, TriageNote, VerdictBadge, gradeLabel } from "./shared";

/** Shared by the app (/paper/:id) and the static export. Uses plain anchors only. */
export function ReportView({ bundle, indexHref }: { bundle: PaperBundle; indexHref: string }) {
  const { summary, grade, claims } = bundle;
  const rows = buildRows(bundle);
  const claimText = (id: string) => claims.claims.find((c) => c.id === id)?.claim ?? id;

  return (
    <article>
      <a href={indexHref} className="text-sm text-primary underline">All papers</a>
      <header className="mt-3">
        <h1 className="text-2xl font-semibold sm:text-3xl">{summary.title}</h1>
        <p className="mt-1 flex flex-wrap items-center gap-2 text-sm text-muted">
          <span className="font-mono">{summary.doi}</span>
          {summary.id.startsWith("sample-") && <Badge>Sample data</Badge>}
        </p>
      </header>

      <section aria-labelledby="grade-heading" className="mt-6 flex items-start gap-4 rounded border border-border bg-surface p-4">
        <GradeSeal grade={grade.grade} />
        <div>
          <h2 id="grade-heading" className="text-xl font-semibold">{gradeLabel(grade.grade)}: {grade.rule_fired}</h2>
          <p className="mt-1">{grade.reason}</p>
          <p className="mt-2 text-sm text-muted">
            {grade.expected_grade ? `Expected grade: ${grade.expected_grade}. ` : ""}Claims: {grade.total_claims}, not checkable: {grade.uncheckable_claims.length}.
          </p>
        </div>
      </section>

      {grade.total_claims === 0 && (
        <div className="mt-6 rounded border border-attn border-l-4 bg-attn/10 p-4 text-attn-fg">
          <p className="font-semibold">No claims were extracted</p>
          <p className="mt-1 text-sm">
            This usually happens if an open-access PDF could not be automatically downloaded for the provided DOI, or if the PDF contained no extractable text. If you have the PDF, try starting a new audit and uploading it directly.
          </p>
        </div>
      )}

      <Section title="Checks">
        <Table label="Checks with evidence">
          <thead>
            <tr>
              <Th>Check</Th><Th>Claim or item</Th><Th>Verdict</Th><Th>Page</Th><Th>Quoted evidence</Th><Th>Raw record</Th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.key}>
                <Td><span className="font-medium">{r.check}</span></Td>
                <Td>
                  {r.item}
                  {r.detail && <span className="mt-1 block text-muted">{r.detail}</span>}
                </Td>
                <Td><VerdictBadge verdict={r.verdict} /></Td>
                <Td>{r.page ?? "n/a"}</Td>
                <Td>
                  {r.quote && <blockquote className="border-l-2 border-primary pl-3 font-serif italic">{r.quote}</blockquote>}
                  {r.note && <span className="mt-1 block text-muted">{r.note}</span>}
                </Td>
                <Td>
                  <details>
                    <summary className="cursor-pointer text-primary underline">Show JSON</summary>
                    <pre className="mt-2 max-w-xs whitespace-pre-wrap break-words font-mono text-xs">{JSON.stringify(r.raw, null, 2)}</pre>
                  </details>
                </Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Section>

      <Section title="Not checkable">
        {grade.uncheckable_claims.length === 0 ? (
          <p>No claims were excluded from grading.</p>
        ) : (
          <ul className="space-y-2">
            {grade.uncheckable_claims.map((u) => (
              <li key={u.claim_id} className="rounded border border-border bg-surface p-3">
                <span className="font-medium">{u.claim_id}: {claimText(u.claim_id)}</span>
                <span className="mt-1 block text-muted">Reason: {u.reason}</span>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <TriageNote />
    </article>
  );
}
