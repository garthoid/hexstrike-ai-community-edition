// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
//
// screenshot-url.mjs — screenshot a single page of the NyxStrike dashboard,
// for quick visual checks while iterating on UI changes. Optionally click an
// element and/or press a key first, to capture interactive states (modals,
// sheets, dropdowns) rather than just the page's initial load state.
//
// Usage:
//   node scripts/screenshot-url.mjs <hash-route-or-url> [output.png] [--theme=<id>] [--no-demo] [--click=<selector>] [--press=<key>] [--wait-for=<selector>]
//
// Examples:
//   node scripts/screenshot-url.mjs '#/tools'
//   node scripts/screenshot-url.mjs '#/tools' tools.png --theme=synthwave
//   node scripts/screenshot-url.mjs http://localhost:5173/#/loot loot.png
//   node scripts/screenshot-url.mjs '#/settings' --no-demo
//   # Click the first tool card and capture the detail Sheet that slides in:
//   node scripts/screenshot-url.mjs '#/tools' sheet.png --click=".registry-card--clickable" --wait-for=".sheet"
//   # Then close it and confirm Escape works (chain a second invocation with --press=Escape).
//
// Env vars (all optional):
//   BASE_URL             default http://localhost:5173
//   NYXSTRIKE_API_TOKEN  if set (and --no-demo passed), seeds this token
//   FULL_PAGE            default true; set to "false" for viewport-only capture

import { chromium } from "playwright";
import path from "path";
import { fileURLToPath } from "url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));

const BASE_URL = process.env.BASE_URL ?? "http://localhost:5173";
const API_TOKEN = process.env.NYXSTRIKE_API_TOKEN ?? null;
const FULL_PAGE = process.env.FULL_PAGE !== "false";

// Keep in sync with ui/src/app/themes.ts THEME_OPTIONS.
const THEME_IDS = [
  "dark", "unicorn", "forest", "solarized", "ocean-glass",
  "crimson-night", "retro-crt", "nord",
  "dracula", "gruvbox", "folio", "tokyo", "catppuccin", "synthwave", "rose", "frost",
];
const THEME_STORAGE_KEY = "nyxstrike_theme";

const rawArgs = process.argv.slice(2);
const themeArg = rawArgs.find((a) => a.startsWith("--theme="));
const clickArg = rawArgs.find((a) => a.startsWith("--click="));
const pressArg = rawArgs.find((a) => a.startsWith("--press="));
const waitForArg = rawArgs.find((a) => a.startsWith("--wait-for="));
const noDemo = rawArgs.includes("--no-demo");
const positional = rawArgs.filter((a) =>
  !a.startsWith("--theme=") && !a.startsWith("--click=") && !a.startsWith("--press=") &&
  !a.startsWith("--wait-for=") && a !== "--no-demo"
);
const clickSelector = clickArg ? clickArg.slice("--click=".length) : null;
const pressKey = pressArg ? pressArg.slice("--press=".length) : null;
const waitForSelector = waitForArg ? waitForArg.slice("--wait-for=".length) : null;

const target = positional[0];
if (!target) {
  console.error("Usage: node scripts/screenshot-url.mjs <hash-route-or-url> [output.png] [--theme=<id>] [--no-demo]");
  process.exit(1);
}

let themeId = null;
if (themeArg) {
  themeId = themeArg.slice("--theme=".length);
  if (!THEME_IDS.includes(themeId)) {
    console.error(`Unknown theme "${themeId}". Valid ids: ${THEME_IDS.join(", ")}`);
    process.exit(1);
  }
}

const isFullUrl = /^https?:\/\//.test(target);
const demoFlag = !noDemo && !API_TOKEN ? "?demo=1" : "";
const url = isFullUrl
  ? target
  : `${BASE_URL}/${demoFlag}${target.startsWith("#") ? target : `#/${target.replace(/^\/+/, "")}`}`;

const outPath = positional[1]
  ? path.resolve(positional[1])
  : path.join(SCRIPT_DIR, "screenshots", "url-shot.png");

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });

if (API_TOKEN && noDemo) {
  await page.addInitScript((token) => {
    sessionStorage.setItem("nyxstrike_token", token);
  }, API_TOKEN);
}

if (themeId) {
  await page.addInitScript(([key, id]) => {
    localStorage.setItem(key, id);
  }, [THEME_STORAGE_KEY, themeId]);
}

const consoleErrors = [];
page.on("console", (msg) => { if (msg.type() === "error") consoleErrors.push(msg.text()); });
page.on("pageerror", (err) => consoleErrors.push("pageerror: " + err.message));

await page.goto(url, { waitUntil: "networkidle" });
await page.waitForTimeout(600);

if (clickSelector) {
  await page.locator(clickSelector).first().click();
}
if (waitForSelector) {
  await page.waitForSelector(waitForSelector, { timeout: 5000 });
}
if (pressKey) {
  await page.keyboard.press(pressKey);
}
if (clickSelector || pressKey) {
  await page.waitForTimeout(300);
}

await page.screenshot({ path: outPath, fullPage: FULL_PAGE });
await browser.close();

console.log("Saved screenshot to", outPath);
if (consoleErrors.length > 0) {
  console.log("console/page errors:", consoleErrors.length);
  console.log(consoleErrors.join("\n"));
  process.exit(1);
}
