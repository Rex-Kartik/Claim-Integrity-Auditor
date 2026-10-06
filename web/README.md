# Claim Integrity Auditor UI

Visual direction: an evidence ledger. Cool grey-teal paper (#EFF3F4), ink text (#15232B), teal accent (#0B5F66).
Grade tints are teal, blue, ochre, violet and slate. No hue between 340 and 20 degrees is used anywhere.
Type: system stacks only. Serif (Iowan Old Style, Palatino, Georgia) for headings and quoted evidence; system sans for body; system mono for raw JSON.
Spacing: 4px base scale, 1100px content width. The grade seal is the one bold element; everything else stays quiet.
Every grade is a letter plus a text label, and color is never the only signal.

All data in this build is invented sample data. Nothing here has been evaluated.

## Install and run

```
npm install
npm run dev        # development server
npm run build      # type-check and production build
```

## Static export and wording lint

```
npm run export:reports   # builds, then writes dist-reports/index.html and dist-reports/<id>/report.html
npm run lint:wording     # scans src/, mock/ and dist-reports/; exit code 1 on any hit
```

Each exported file is self-contained: inline CSS, no scripts, no external URLs, system fonts. Raw-record rows use native `<details>`. The export renders the same `ReportView` and `IndexView` components as the app.

## Handoff to Antigravity

Swap points:

1. `src/lib/datasource.ts`: replace `MockDataSource` with a class that reads `runs/<paper_id>/<stage>.json` from the backend and builds each paper with `assembleBundle()`.
2. `src/lib/clients.ts`: replace `MockRunClient` with an HTTP client implementing `RunClient` (`start(input)` and `subscribe(runId, listener)`). A base URL could come from a Vite environment variable such as `VITE_API_BASE_URL`.
3. `mock/`: delete once the backend writes the six files. `DATA_CONTRACT.md` has the field list and a mapping checklist.
4. `scripts/export-reports.tsx`: it reads `mock/` with `fs`. Point it at `runs/` to export real reports.

The UI renders `grade.json` and never computes a grade.

## Packages beyond the listed set

- `class-variance-authority`, `clsx`, `tailwind-merge`, `@radix-ui/react-slot`, `@radix-ui/react-label`: required by the shadcn/ui components in `src/components/ui`.
- `postcss` and `autoprefixer`: required by Tailwind CSS 3.
- `@vitejs/plugin-react`: lets Vite compile React.
- `tsx`: runs `scripts/export-reports.tsx` in Node.
- `@types/node`: types for the Node file functions used by the scripts.
