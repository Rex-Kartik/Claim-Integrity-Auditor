import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter, Route, Routes } from "react-router-dom";
import "./index.css";
import { Layout } from "./components/Layout";
import { IndexPage } from "./pages/IndexPage";
import { ReportPage } from "./pages/ReportPage";
import { RunPage } from "./pages/RunPage";
import { EvaluationPage } from "./pages/EvaluationPage";

// HashRouter keeps plain-anchor links (shared with the static export) working on any static host.
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <HashRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<IndexPage />} />
          <Route path="/paper/:id" element={<ReportPage />} />
          <Route path="/run" element={<RunPage />} />
          <Route path="/evaluation" element={<EvaluationPage />} />
          <Route path="*" element={<p>Page not found. Go back to the list of papers.</p>} />
        </Route>
      </Routes>
    </HashRouter>
  </StrictMode>,
);
