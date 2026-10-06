import type { PaperBundle, PaperSummary } from "../types/contract";

/** Pure helper shared by the app loader and the static export (which reads files with fs). */
export function assembleBundle(summary: PaperSummary, read: (file: string) => unknown): PaperBundle {
  return {
    summary,
    claims: read("claims") as PaperBundle["claims"],
    retraction: read("retraction") as PaperBundle["retraction"],
    stats: read("stats") as PaperBundle["stats"],
    citations: read("citations") as PaperBundle["citations"],
    codeData: read("code_data") as PaperBundle["codeData"],
    grade: read("grade") as PaperBundle["grade"],
  };
}
