import type { Config } from "tailwindcss";

// Palette: no hue between 340 and 20 degrees. Every bg/fg pair below is at least 4.5:1.
const pair = (bg: string, fg: string) => ({ bg, fg });

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#EFF3F4",
        surface: "#FFFFFF",
        ink: "#15232B",
        muted: "#4A5A63",
        border: "#C3CFD4",
        primary: { DEFAULT: "#0B5F66", foreground: "#FFFFFF" },
        ok: pair("#D6EEE9", "#0B4A44"),
        info: pair("#DCE8F7", "#163E73"),
        attn: pair("#F6E7C1", "#5E4000"),
        record: pair("#E6E0F5", "#3F2B7A"),
        neutral: pair("#E3E7E9", "#2F3C43"),
      },
      fontFamily: {
        serif: ['"Iowan Old Style"', '"Palatino Linotype"', "Palatino", '"Book Antiqua"', "Georgia", "serif"],
        sans: ["ui-sans-serif", "system-ui", "-apple-system", '"Segoe UI"', "Roboto", '"Helvetica Neue"', "Arial", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", '"Liberation Mono"', "monospace"],
      },
    },
  },
} satisfies Config;
