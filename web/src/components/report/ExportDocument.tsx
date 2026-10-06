import type { ReactNode } from "react";

/** Page shell for the static export: inline CSS, no scripts, no external resources. */
export const ExportDocument = ({ title, css, children }: { title: string; css: string; children: ReactNode }) => (
  <html lang="en">
    <head>
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>{title}</title>
      <style dangerouslySetInnerHTML={{ __html: css }} />
    </head>
    <body>
      <main className="mx-auto max-w-[1100px] px-4 py-8">{children}</main>
    </body>
  </html>
);
