import { TriageNote } from "../components/report/shared";

const METRICS = ["Precision", "Recall", "Quadratic-weighted Cohen's kappa"];

export function EvaluationPage() {
  return (
    <section>
      <h1 className="text-2xl font-semibold sm:text-3xl">Evaluation</h1>
      <p className="mt-2">Evaluation on 20 papers is planned and has not been run.</p>
      <dl className="mt-6 grid gap-3 sm:grid-cols-3">
        {METRICS.map((m) => (
          <div key={m} className="rounded border border-border bg-surface p-4">
            <dt className="text-sm text-muted">{m}</dt>
            <dd className="mt-1 font-serif text-lg font-semibold">not yet evaluated</dd>
          </div>
        ))}
      </dl>
      <TriageNote />
    </section>
  );
}
