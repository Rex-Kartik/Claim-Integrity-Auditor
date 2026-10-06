import { STAGES, initialStages, type RunClient, type RunState } from "./runClient";

type Listener = (state: RunState) => void;

/** Simulated progress only. Nothing is uploaded and no network call is made. */
export class MockRunClient implements RunClient {
  private runs = new Map<string, { state: RunState; listeners: Set<Listener> }>();
  private counter = 0;

  async start() {
    const runId = `simulated-${++this.counter}`;
    const run = { state: { runId, stages: initialStages(), finished: false }, listeners: new Set<Listener>() };
    this.runs.set(runId, run);
    const set = (i: number, status: RunState["stages"][keyof RunState["stages"]]) => {
      run.state = { ...run.state, stages: { ...run.state.stages, [STAGES[i]]: status }, finished: i === STAGES.length - 1 && status !== "running" };
      run.listeners.forEach((l) => l(run.state));
    };
    STAGES.forEach((name, i) => {
      setTimeout(() => set(i, "running"), i * 1100 + 100);
      // Shows the "not checkable" state in the demo; no real result is behind it.
      setTimeout(() => set(i, name === "Citation check" ? "not checkable" : "done"), i * 1100 + 900);
    });
    return { runId };
  }

  subscribe(runId: string, listener: Listener) {
    const run = this.runs.get(runId);
    if (!run) return () => {};
    run.listeners.add(listener);
    listener(run.state);
    return () => run.listeners.delete(listener);
  }
}
