import type { IndexFile, PaperBundle, PaperSummary } from "../types/contract";
import { assembleBundle } from "./bundle";
import { HttpDataSource } from "./httpDataSource";

/** The only way pages read data. */
export interface DataSource {
  listPapers(): Promise<PaperSummary[]>;
  getPaper(id: string): Promise<PaperBundle>;
}

const files = import.meta.glob("../../mock/**/*.json", { eager: true, import: "default" }) as Record<string, unknown>;

export class MockDataSource implements DataSource {
  async listPapers() {
    return (files["../../mock/index.json"] as IndexFile).papers;
  }
  async getPaper(id: string) {
    const summary = (await this.listPapers()).find((p) => p.id === id);
    if (!summary) throw new Error(`No paper with id "${id}"`);
    return assembleBundle(summary, (name) => files[`../../mock/${id}/${name}.json`]);
  }
}

// Live backend data source — reads from /api/audit/{id}
export const dataSource: DataSource = new HttpDataSource();
