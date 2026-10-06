// Static export: dist-reports/index.html and dist-reports/<id>/report.html.
// Run via `npm run export:reports` (builds first so the compiled CSS exists in dist/assets).
import { mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { ExportDocument } from "../src/components/report/ExportDocument";
import { IndexView } from "../src/components/report/IndexView";
import { ReportView } from "../src/components/report/ReportView";
import { assembleBundle } from "../src/lib/bundle";
import type { IndexFile } from "../src/types/contract";

const OUT = "dist-reports";
const cssFile = readdirSync("dist/assets").find((f) => f.endsWith(".css"));
if (!cssFile) throw new Error("No compiled CSS in dist/assets. Run vite build first.");
const css = readFileSync(join("dist/assets", cssFile), "utf8");

const readJson = (path: string) => JSON.parse(readFileSync(path, "utf8"));
const { papers } = readJson("mock/index.json") as IndexFile;
const bundles = papers.map((p) => assembleBundle(p, (name) => readJson(`mock/${p.id}/${name}.json`)));

const render = (title: string, body: JSX.Element) => {
  const html = "<!doctype html>" + renderToStaticMarkup(<ExportDocument title={title} css={css}>{body}</ExportDocument>);
  // Self-containment guard: fail loudly rather than ship a page that loads anything.
  if (/<script|<link|https?:\/\/|\burl\(/i.test(html)) throw new Error(`${title}: export is not self-contained`);
  return html;
};

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
writeFileSync(
  join(OUT, "index.html"),
  render("Audited papers", <IndexView entries={bundles.map((b) => ({ summary: b.summary, grade: b.grade }))} hrefFor={(id) => `${id}/report.html`} />),
);
for (const b of bundles) {
  mkdirSync(join(OUT, b.summary.id), { recursive: true });
  writeFileSync(join(OUT, b.summary.id, "report.html"), render(b.summary.title, <ReportView bundle={b} indexHref="../index.html" />));
}
console.log(`wrote ${bundles.length + 1} files to ${OUT}/`);
