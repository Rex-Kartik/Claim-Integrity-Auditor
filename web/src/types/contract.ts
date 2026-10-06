// Data contract for the six files the backend writes to runs/<paper_id>/<stage>.json.
// See DATA_CONTRACT.md for where each field is displayed.

export type Grade = "A" | "B" | "C" | "D" | "withheld";

export interface Claim {
  id: string;
  claim: string;
  quote: string;
  page: number;
}

/** claims.json */
export interface ClaimsFile {
  paper_id: string;
  paper_doi: string;
  claims: Claim[];
  cited_dois: string[];
  code_data_urls: string[];
  statistic_strings: string[];
}

export type RetractionStatus = "retraction record found" | "none found" | "not checkable";

export interface RetractionResult {
  doi: string;
  status: RetractionStatus;
  source_field: string | null;
  raw_record: Record<string, unknown> | null;
}

/** retraction.json */
export interface RetractionFile {
  results: RetractionResult[];
}

export type StatTest = "t" | "F" | "chi-square" | "r";
export type StatVerdict = "reproduced" | "not reproduced" | "not checkable";

export interface StatResult {
  claim_id: string;
  test: StatTest | null; // null when the statistic could not be parsed
  df: string | null; // "28" or "1, 56"
  reported_p: string | null; // kept as text so "< .05" is representable
  recomputed_p: number | null;
  formula: string | null;
  verdict: StatVerdict;
  page: number;
  quote: string;
}

/** stats.json */
export interface StatsFile {
  results: StatResult[];
}

export type CitationVerdict = "supports" | "not supported" | "not checkable";

export interface CitationResult {
  claim_id: string;
  cited_doi: string;
  verdict: CitationVerdict;
  passage: string;
  evidence_label: "abstract only";
  page: number;
  quote: string;
}

/** citations.json */
export interface CitationsFile {
  results: CitationResult[];
}

export type CodeDataStatus = "loads" | "fails" | "absent";

export interface CodeDataResult {
  url: string | null; // null when status is "absent"
  status: CodeDataStatus;
  http_status: number | null;
}

/** code_data.json */
export interface CodeDataFile {
  results: CodeDataResult[];
}

export interface UncheckableClaim {
  claim_id: string;
  reason: string;
}

/** grade.json. The UI renders this file and never computes or changes a grade. */
export interface GradeFile {
  paper_id: string;
  grade: Grade;
  rule_fired: string; // short label shown after the grade, e.g. "retraction record found"
  reason: string; // one or two sentences of detail
  total_claims: number;
  uncheckable_claims: UncheckableClaim[];
  expected_grade: Grade | null;
}

/** mock/index.json (replace with a backend listing). */
export interface PaperSummary {
  id: string;
  title: string;
  doi: string;
}

export interface IndexFile {
  papers: PaperSummary[];
}

/** All six files for one paper, plus its index entry. */
export interface PaperBundle {
  summary: PaperSummary;
  claims: ClaimsFile;
  retraction: RetractionFile;
  stats: StatsFile;
  citations: CitationsFile;
  codeData: CodeDataFile;
  grade: GradeFile;
}
