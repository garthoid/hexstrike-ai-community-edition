import { chromium } from "playwright";

const BASE_URL = "http://localhost:5173";
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
const errors = [];
page.on("console", msg => { if (msg.type() === "error") errors.push(msg.text()); });
page.on("pageerror", err => errors.push(String(err)));

await page.goto(`${BASE_URL}/#/sessions/sess_d0014619f2`, { waitUntil: "networkidle" });
await page.waitForTimeout(500);
await page.click("text=Notes");
await page.waitForTimeout(300);
await page.locator(".session-notes-header-actions button", { hasText: "New Note" }).click();
await page.waitForTimeout(300);
await page.fill("input[name='new-note-name']", "test-note");
await page.locator(".session-notes-new-row button.session-action-btn--primary").click();
await page.waitForSelector(".sheet", { timeout: 5000 });
await page.waitForTimeout(500);
await page.screenshot({ path: "/tmp/claude-1000/-home-morten-DEV-nyxstrike/67b0f51b-1291-4587-b637-5b0487a3059e/scratchpad/note-modal2.png", fullPage: true });
console.log("note modal errors:", errors);

await browser.close();
