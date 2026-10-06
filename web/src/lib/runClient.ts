export const STAGES = [
  "Claim extraction",
  "Retraction check",
  "Statistics recomputation",
  "Citation check",
  "Code/data check",
  "Grading",
] as const;

export type StageName = (typeof STAGES)[number];
export type StageStatus = "waiting" | "running" | "done" | "not checkable" | "failed";

export type RunInput = { kind: "pdf"; file: File } | { kind: "doi"; doi: string };

export interface RunState {
  runId: string;
  stages: Record<StageName, StageStatus>;
  finished: boolean;
}

export interface RunClient {
  start(input: RunInput): Promise<{ runId: string }>;
  /** Calls listener now and on every change. Returns an unsubscribe function. */
  subscribe(runId: string, listener: (state: RunState) => void): () => void;
}

export const initialStages = (): Record<StageName, StageStatus> =>
  Object.fromEntries(STAGES.map((s) => [s, "waiting"])) as Record<StageName, StageStatus>;
