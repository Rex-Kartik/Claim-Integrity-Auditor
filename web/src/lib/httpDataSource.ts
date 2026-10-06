import { API_BASE } from "./apiBase";
import type {
  ClaimsFile, CitationsFile, CodeDataFile, GradeFile,
  PaperBundle, PaperSummary, RetractionFile, StatsFile,
} from "../types/contract";
import { assembleBundle } from "./bundle";
import type { DataSource } from "./datasource";

// ---------------------------------------------------------------------------
// Backend → contract adapters (field name mismatches)
// ---------------------------------------------------------------------------

function adaptClaims(raw: Record<string, unknown>): ClaimsFile {
  const outputs = (raw.outputs ?? raw) as Record<string, unknown>;
  const claims = ((outputs.claims ?? []) as Record<string, unknown>[]).map((c, i) => ({
    id: String(c.claim_id ?? c.id ?? i),
    claim: String(c.claim ?? ""),
    quote: String(c.quote ?? ""),
    page: Number(c.page ?? 0),
  }));
  return {
    paper_id:          String(outputs.paper_doi ?? raw.audit_id ?? ""),
    paper_doi:         String(outputs.paper_doi ?? ""),
    claims,
    cited_dois:        (outputs.cited_dois ?? []) as string[],
    code_data_urls:    (outputs.code_data_urls ?? []) as string[],
    statistic_strings: (outputs.apa_statistics ?? []) as string[],
  };
}

function adaptRetraction(raw: Record<string, unknown>): RetractionFile {
  const outputs = (raw.outputs ?? raw) as Record<string, unknown>;
  // Backend writes doi_results[]
  const doiResults = ((outputs.doi_results ?? []) as Record<string, unknown>[]).map((r) => ({
    doi:          String(r.doi ?? ""),
    status:       (r.verdict ?? "not checkable") as RetractionFile["results"][number]["status"],
    source_field: (r.retraction_watch_hit ? "retraction_watch_csv" : null) as string | null,
    raw_record:   (r.evidence ?? null) as Record<string, unknown> | null,
  }));
  return { results: doiResults };
}

function adaptStats(raw: Record<string, unknown>): StatsFile {
  const outputs = (raw.outputs ?? raw) as Record<string, unknown>;
  const results = ((outputs.results ?? []) as Record<string, unknown>[]).map((r, i) => ({
    claim_id:    String(r.claim_id ?? i),
    test:        (r.test ?? null) as StatsFile["results"][number]["test"],
    df:          r.df !== undefined ? String(r.df)
               : r.df1 !== undefined ? `${r.df1}, ${r.df2}` : null,
    reported_p:  r.reported_p !== undefined ? String(r.reported_p) : null,
    recomputed_p: r.recomputed_p !== undefined ? Number(r.recomputed_p) : null,
    formula:     (r.formula ?? null) as string | null,
    verdict:     (r.verdict ?? "not checkable") as StatsFile["results"][number]["verdict"],
    page:        Number(r.page ?? 0),
    quote:       String(r.raw_string ?? r.quote ?? ""),
  }));
  return { results };
}

function adaptCitations(raw: Record<string, unknown>): CitationsFile {
  const outputs = (raw.outputs ?? raw) as Record<string, unknown>;
  const results = ((outputs.results ?? []) as Record<string, unknown>[]).map((r, i) => ({
    claim_id:       String(r.claim_id ?? i),
    cited_doi:      String(r.cited_doi ?? ""),
    verdict:        (r.verdict ?? "not checkable") as CitationsFile["results"][number]["verdict"],
    passage:        String(r.retrieved_passage ?? r.passage ?? ""),
    evidence_label: "abstract only" as const,
    page:           Number(r.page ?? 0),
    quote:          String(r.quote ?? ""),
  }));
  return { results };
}

function adaptCodeData(raw: Record<string, unknown>): CodeDataFile {
  const outputs = (raw.outputs ?? raw) as Record<string, unknown>;
  const results = ((outputs.results ?? []) as Record<string, unknown>[]).map((r) => ({
    url:         (r.url ?? null) as string | null,
    status:      (r.verdict ?? "absent") as CodeDataFile["results"][number]["status"],
    http_status: r.status_code !== undefined ? Number(r.status_code) : null,
  }));
  // If no results at all, represent as a single "absent" entry
  if (results.length === 0) {
    return { results: [{ url: null, status: "absent", http_status: null }] };
  }
  return { results };
}

function adaptGrade(raw: Record<string, unknown>, auditId: string): GradeFile {
  const outputs = (raw.outputs ?? raw) as Record<string, unknown>;
  const inputs = (raw.inputs ?? {}) as Record<string, unknown>;
  const grade = String(outputs.grade ?? "withheld").replace("grade withheld", "withheld") as GradeFile["grade"];
  return {
    paper_id:          auditId,
    grade,
    rule_fired:        String(outputs.rule ?? ""),
    reason:            String(outputs.rule ?? ""),
    total_claims:      Number(inputs.total_claims ?? 0),
    uncheckable_claims: ((outputs.uncheckable_items ?? []) as Record<string, unknown>[]).map((u, i) => ({
      claim_id: String(u.claim ?? u.raw_string ?? i),
      reason:   String(u.reason ?? "not checkable"),
    })),
    expected_grade:    null, // backend doesn't track expected
  };
}

// ---------------------------------------------------------------------------
// HttpDataSource
// ---------------------------------------------------------------------------

export class HttpDataSource implements DataSource {
  async listPapers(): Promise<PaperSummary[]> {
    // Discover completed runs from the backend by reading runs/<id>/grade.json
    // The backend exposes /api/audit/{id} but has no listing endpoint.
    // We maintain an index in localStorage to remember audit IDs from this session.
    const ids: string[] = JSON.parse(localStorage.getItem("__audit_ids__") ?? "[]");
    const papers: PaperSummary[] = [];

    for (const id of ids) {
      try {
        const resp = await fetch(`${API_BASE}/api/audit/${id}`);
        if (!resp.ok) continue;
        const data = await resp.json();
        if (!data?.grade) continue;
        papers.push({
          id,
          title: data.metadata?.title ?? id,
          doi:   data.metadata?.doi   ?? "",
        });
      } catch {
        // skip stale IDs
      }
    }
    return papers;
  }

  async getPaper(id: string): Promise<PaperBundle> {
    const resp = await fetch(`${API_BASE}/api/audit/${id}`);
    if (!resp.ok) throw new Error(`Audit ${id} not found`);
    const data = await resp.json();

    const summary: PaperSummary = {
      id,
      title: data.metadata?.title ?? id,
      doi:   data.metadata?.doi   ?? "",
    };

    const stages = data.stages ?? {};

    return assembleBundle(summary, (name) => {
      switch (name) {
        case "claims":    return adaptClaims(stages.claims ?? {});
        case "retraction":return adaptRetraction(stages.retraction ?? {});
        case "stats":     return adaptStats(stages.stats ?? {});
        case "citations": return adaptCitations(stages.citations ?? {});
        case "code_data": return adaptCodeData(stages.code_data ?? {});
        case "grade":     return adaptGrade(stages.grade ?? {}, id);
        default:          return {};
      }
    });
  }
}
