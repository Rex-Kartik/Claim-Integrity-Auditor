import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Check, Circle, Loader2, Minus, X } from "lucide-react";
import { Badge, type BadgeVariant } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { TriageNote } from "../components/report/shared";
import { runClient } from "../lib/clients";
import { STAGES, initialStages, type RunState, type StageStatus } from "../lib/runClient";

const DOI_PATTERN = /^10\.\d{4,9}\/\S+$/;

const STATUS_STYLE: Record<StageStatus, { variant: BadgeVariant; icon: JSX.Element }> = {
  waiting:        { variant: "neutral", icon: <Circle className="h-4 w-4" /> },
  running:        { variant: "info",    icon: <Loader2 className="h-4 w-4 animate-spin" /> },
  done:           { variant: "ok",      icon: <Check className="h-4 w-4" /> },
  "not checkable":{ variant: "neutral", icon: <Minus className="h-4 w-4" /> },
  failed:         { variant: "attn",    icon: <X className="h-4 w-4" /> },
};

function persistAuditId(id: string) {
  const ids: string[] = JSON.parse(localStorage.getItem("__audit_ids__") ?? "[]");
  if (!ids.includes(id)) {
    ids.unshift(id);
    localStorage.setItem("__audit_ids__", JSON.stringify(ids.slice(0, 50)));
  }
}

export function RunPage() {
  const navigate = useNavigate();
  const [runId, setRunId] = useState<string | null>(null);
  const [state, setState] = useState<RunState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [announce, setAnnounce] = useState("");

  useEffect(() => (runId ? runClient.subscribe(runId, setState) : undefined), [runId]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const stages = state?.stages ?? initialStages();
  const running = isSubmitting || (runId !== null && !state?.finished);

  useEffect(() => {
    const active = STAGES.find((s) => stages[s] === "running");
    if (active) setAnnounce(`${active}: running`);
    else if (state?.finished) setAnnounce("Run finished");
  }, [stages, state?.finished]);

  // When finished, navigate to the report page
  useEffect(() => {
    if (state?.finished && runId) {
      navigate(`/paper/${runId}`);
    }
  }, [state?.finished, runId, navigate]);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const file = form.get("pdf") as File;
    const doi  = String(form.get("doi") ?? "").trim();
    const hasFile = file && file.size > 0;
    if (hasFile === Boolean(doi))
      return setError(hasFile ? "Provide either a PDF or a DOI, not both." : "Provide a PDF file or a DOI.");
    if (!hasFile && !DOI_PATTERN.test(doi))
      return setError("Enter a DOI in the form 10.NNNN/identifier.");
    setError(null);
    setState(null);
    setIsSubmitting(true);
    try {
      const { runId } = await runClient.start(hasFile ? { kind: "pdf", file } : { kind: "doi", doi });
      persistAuditId(runId);
      setRunId(runId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect to the backend.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section>
      <h1 className="text-2xl font-semibold sm:text-3xl">Run an audit</h1>
      <p className="mt-2 max-w-prose text-muted">
        Enter a DOI or upload a PDF. The pipeline checks retraction records, recomputes
        statistics, verifies citations and checks code/data availability.
      </p>

      <form onSubmit={onSubmit} className="mt-6 grid max-w-xl gap-4" noValidate>
        <div className="grid gap-1">
          <Label htmlFor="pdf">PDF file</Label>
          <Input id="pdf" name="pdf" type="file" accept="application/pdf" />
        </div>
        <div className="grid gap-1">
          <Label htmlFor="doi">or DOI</Label>
          <Input id="doi" name="doi" type="text" placeholder="10.NNNN/identifier" autoComplete="off" />
        </div>
        {error && <p role="alert" className="text-sm font-medium text-attn-fg">{error}</p>}
        <div><Button type="submit" disabled={running}>Start audit</Button></div>
      </form>

      {runId && (
        <>
          <h2 className="mt-10 text-xl font-semibold">Stages</h2>
          <p className="sr-only" role="status" aria-live="polite">{announce}</p>
          <ol aria-label="Audit stages" className="mt-3 max-w-xl border-l-2 border-border pl-4">
            {STAGES.map((name) => {
              const st = stages[name];
              return (
                <li key={name} className="flex items-center justify-between gap-3 py-2">
                  <span>{name}</span>
                  <Badge variant={STATUS_STYLE[st].variant} className="gap-1.5">
                    <span aria-hidden="true">{STATUS_STYLE[st].icon}</span>
                    {st}
                  </Badge>
                </li>
              );
            })}
          </ol>
        </>
      )}
      <TriageNote />
    </section>
  );
}
