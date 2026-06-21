"use strict";

const path = require("path");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const chromePath =
  process.env.CHROME_PATH ||
  path.join(process.env.PROGRAMFILES || "C:\\Program Files", "Google", "Chrome", "Application", "chrome.exe");

async function main() {
  const browser = await chromium.launch({ executablePath: chromePath, headless: true });
  const page = await browser.newPage({ viewport: { width: 1728, height: 1000 }, deviceScaleFactor: 1 });
  await page.goto("http://127.0.0.1:8051", { waitUntil: "networkidle" });

  const views = [
    ["Overview", "Overview.png"],
    ["State Review", "State_Review.png"],
    ["Reliability Check", "Reliability_Check.png"],
  ];
  for (const [label, filename] of views) {
    await page.getByText(label, { exact: true }).last().click();
    await page.waitForTimeout(1200);
    await page.screenshot({
      path: path.join(root, "dashboard_stakeholder", "assets", filename),
      fullPage: true,
    });
    console.log(`PASS ${filename}`);
  }
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
