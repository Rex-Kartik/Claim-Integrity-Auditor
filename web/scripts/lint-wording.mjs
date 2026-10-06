// Exits 1 if any file under src/, mock/ or dist-reports/ contains a listed substring (case-insensitive).
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const BANNED = ["fraud", "fabricat", "misconduct", "cheat", "fake", "dishonest", "guilty"];
const DIRS = ["src", "mock", "dist-reports"];

const walk = (dir) =>
  readdirSync(dir).flatMap((n) => {
    const p = join(dir, n);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });

let hits = 0;
for (const dir of DIRS) {
  if (!existsSync(dir)) {
    console.log(`skip: ${dir}/ not found`);
    continue;
  }
  for (const file of walk(dir)) {
    const text = readFileSync(file, "utf8").toLowerCase();
    for (const word of BANNED) {
      if (text.includes(word)) {
        console.error(`${file}: contains "${word}"`);
        hits++;
      }
    }
  }
}
console.log(hits ? `${hits} hit(s)` : "wording lint passed");
process.exit(hits ? 1 : 0);
