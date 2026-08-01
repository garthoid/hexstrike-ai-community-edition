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
await page.click("text=Upload .md");
await page.waitForSelector(".sheet", { timeout: 5000 });
await page.waitForTimeout(300);
await page.screenshot({ path: "/tmp/claude-1000/-home-morten-DEV-nyxstrike/67b0f51b-1291-4587-b637-5b0487a3059e/scratchpad/upload-modal.png", fullPage: true });
console.log("upload errors:", errors.filter(e => !e.includes('hydration') && !e.includes('cannot contain')));

await page.goto(`${BASE_URL}/#/sessions/sess_d0014619f2`, { waitUntil: "networkidle" });
await page.waitForTimeout(500);
await page.click("text=Findings");
await page.waitForTimeout(300);
await page.click("text=Add Finding");
await page.waitForSelector(".sheet", { timeout: 5000 });
await page.waitForTimeout(300);
await page.screenshot({ path: "/tmp/claude-1000/-home-morten-DEV-nyxstrike/67b0f51b-1291-4587-b637-5b0487a3059e/scratchpad/finding-modal.png", fullPage: true });
console.log("finding errors:", errors.filter(e => !e.includes('hydration') && !e.includes('cannot contain')));

await browser.close();
