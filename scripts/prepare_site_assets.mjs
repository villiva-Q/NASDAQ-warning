import { cp, mkdir, rm } from "node:fs/promises";
import { resolve } from "node:path";

const root = process.cwd();
const docs = resolve(root, "docs");
const publicDir = resolve(root, "public");

await mkdir(publicDir, { recursive: true });
await rm(resolve(publicDir, "data"), { recursive: true, force: true });

await Promise.all([
  cp(resolve(docs, "index.html"), resolve(publicDir, "dashboard.html")),
  cp(resolve(docs, "app.js"), resolve(publicDir, "app.js")),
  cp(resolve(docs, "styles.css"), resolve(publicDir, "styles.css")),
  cp(resolve(docs, "og.png"), resolve(publicDir, "og.png")),
  cp(resolve(docs, "og-evergreen.png"), resolve(publicDir, "og-evergreen.png")),
  cp(resolve(docs, "data"), resolve(publicDir, "data"), { recursive: true }),
]);
