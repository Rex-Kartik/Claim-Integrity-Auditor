import { API_BASE } from "./apiBase";
import { STAGES, initialStages, type RunClient, type RunInput, type RunState, type StageName, type StageStatus } from "./runClient";

// Maps the backend SSE stage names to the UI's stage labels.
const STAGE_MAP: Record<string, StageName> = {
  claims:     "Claim extraction",
  retraction: "Retraction check",
  stats:      "Statistics recomputation",
  citations:  "Citation check",
  code_data:  "Code/data check",
  grade:      "Grading",
};

function backendStatusToUI(status: string): StageStatus {
  if (status === "done")           return "done";
  if (status === "running")        return "running";
  if (status === "not checkable")  return "not checkable";
  if (status === "error")          return "failed";
  return "waiting";
}

type Listener = (state: RunState) => void;

export class HttpRunClient implements RunClient {
  private runs = new Map<string, { state: RunState; listeners: Set<Listener> }>();

  async start(input: RunInput): Promise<{ runId: string }> {
    const form = new FormData();
    if (input.kind === "doi") {
      form.append("doi_or_link", input.doi);
    } else {
      form.append("file", input.file);
    }

    const resp = await fetch(`${API_BASE}/api/audit`, { method: "POST", body: form });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(err.detail ?? "Failed to start audit");
    }
    const { audit_id } = await resp.json();
    const runId: string = audit_id;

    const run = {
      state: { runId, stages: initialStages(), finished: false },
      listeners: new Set<Listener>(),
    };
    this.runs.set(runId, run);

    // Connect to SSE stream
    this._streamEvents(runId, run);

    return { runId };
  }

  private _streamEvents(
    runId: string,
    run: { state: RunState; listeners: Set<Listener> },
  ) {
    const es = new EventSource(`${API_BASE}/api/audit/${runId}/events`);

    es.onmessage = (ev) => {
      try {
        const event: { stage: string; status: string } = JSON.parse(ev.data);
        const uiStage = STAGE_MAP[event.stage];

        if (uiStage) {
          const newStages = {
            ...run.state.stages,
            [uiStage]: backendStatusToUI(event.status),
          };
          run.state = { ...run.state, stages: newStages };
          run.listeners.forEach((l) => l(run.state));
        }

        if (event.stage === "done" || event.stage === "error") {
          run.state = { ...run.state, finished: true };
          run.listeners.forEach((l) => l(run.state));
          es.close();
        }
      } catch {
        // ignore parse errors
      }
    };

    es.onerror = () => {
      run.state = { ...run.state, finished: true };
      run.listeners.forEach((l) => l(run.state));
      es.close();
    };
  }

  subscribe(runId: string, listener: Listener): () => void {
    const run = this.runs.get(runId);
    if (!run) return () => {};
    run.listeners.add(listener);
    listener(run.state);
    return () => run.listeners.delete(listener);
  }
}
