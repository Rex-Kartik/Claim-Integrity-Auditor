import { useParams } from "react-router-dom";
import { ReportView } from "../components/report/ReportView";
import { dataSource } from "../lib/datasource";
import { useAsync } from "../lib/useAsync";

export function ReportPage() {
  const { id = "" } = useParams();
  const s = useAsync(() => dataSource.getPaper(id), [id]);
  if (s.status === "loading") return <p role="status">Loading report.</p>;
  if (s.status === "error") return <p role="alert">This report could not be loaded: {s.message}</p>;
  return <ReportView bundle={s.data} indexHref="#/" />;
}
