import { IndexView } from "../components/report/IndexView";
import { dataSource } from "../lib/datasource";
import { useAsync } from "../lib/useAsync";

export function IndexPage() {
  const s = useAsync(async () => {
    const papers = await dataSource.listPapers();
    return Promise.all(papers.map(async (p) => ({ summary: p, grade: (await dataSource.getPaper(p.id)).grade })));
  }, []);
  if (s.status === "loading") return <p role="status">Loading papers.</p>;
  if (s.status === "error") return <p role="alert">Papers could not be loaded: {s.message}</p>;
  return <IndexView entries={s.data} hrefFor={(id) => `#/paper/${id}`} />;
}
