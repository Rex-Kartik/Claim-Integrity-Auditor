import type { GradeFile, PaperSummary } from "../../types/contract";
import { Badge } from "../ui/badge";
import { Table, Td, Th } from "../ui/table";
import { GradeSeal, TriageNote, gradeLabel } from "./shared";

export interface IndexEntry {
  summary: PaperSummary;
  grade: GradeFile;
}

// Compares two grade strings from grade.json for display. It does not derive a grade.
function matchText(g: GradeFile) {
  if (g.grade === "withheld") return "grade withheld";
  if (!g.expected_grade) return "not recorded";
  return g.grade === g.expected_grade ? "matches expected" : "differs from expected";
}

export function IndexView({ entries, hrefFor }: { entries: IndexEntry[]; hrefFor: (id: string) => string }) {
  return (
    <section>
      <h1 className="text-2xl font-semibold sm:text-3xl">Audited papers</h1>
      <p className="mt-2 max-w-prose">Each row shows what the automated checks found for one paper. Results are automated triage, not a final judgement.</p>
      <div className="mt-6">
        <Table label="Audited papers" minWidth="min-w-[48rem]">
          <thead>
            <tr><Th>Paper</Th><Th>DOI</Th><Th>Expected grade</Th><Th>Actual grade</Th><Th>Match</Th></tr>
          </thead>
          <tbody>
            {entries.map(({ summary, grade }) => (
              <tr key={summary.id}>
                <Th scope="row" className="bg-surface font-normal">
                  <a href={hrefFor(summary.id)} className="font-medium text-primary underline">{summary.title}</a>
                  {summary.id.startsWith("sample-") && <Badge className="ml-2">Sample data</Badge>}
                </Th>
                <Td><span className="font-mono text-xs">{summary.doi}</span></Td>
                <Td>{grade.expected_grade ? gradeLabel(grade.expected_grade) : "not recorded"}</Td>
                <Td>
                  <span className="flex items-center gap-2">
                    <GradeSeal grade={grade.grade} className="h-8 w-8 text-lg" />
                    {gradeLabel(grade.grade)}
                  </span>
                </Td>
                <Td>{matchText(grade)}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
      <TriageNote />
    </section>
  );
}
