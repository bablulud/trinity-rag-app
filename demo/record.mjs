import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.BASE_URL || "http://localhost:8000";
const W = 1440;
const H = 900;
const REC_DIR = "recordings";

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

async function smoothScrollThread(page, to) {
  await page.evaluate((target) => {
    const el = document.querySelector("#thread");
    if (el) el.scrollTo({ top: target === "bottom" ? el.scrollHeight : 0, behavior: "smooth" });
  }, to);
}

async function waitForAnswer(page) {
  // Wait for the API call to resolve, then for the DOM to settle.
  await page.waitForResponse(
    (r) => r.url().includes("/api/chat") && r.status() === 200,
    { timeout: 60000 }
  );
  await wait(2200);
}

async function main() {
  mkdirSync(REC_DIR, { recursive: true });

  const browser = await chromium.launch({ args: ["--force-color-profile=srgb"] });
  const context = await browser.newContext({
    viewport: { width: W, height: H },
    deviceScaleFactor: 2,
    recordVideo: { dir: REC_DIR, size: { width: W, height: H } },
  });
  const page = await context.newPage();

  try {
    await page.goto(BASE, { waitUntil: "networkidle" });
    await wait(2200); // land on the welcome screen

    // 1) Ask via a suggested prompt
    const chip = page.getByRole("button", {
      name: /tank cars does TrinityRail offer/i,
    });
    await chip.hover();
    await wait(500);
    await chip.click();

    await waitForAnswer(page);
    await smoothScrollThread(page, "bottom");
    await wait(3800); // read the answer + sources + performance panel

    // 2) Open the config.py drawer
    await page.locator("#cfgBtn").click();
    await wait(1400);

    // 3) Switch the LLM model
    await page.locator("#cfgLlm").selectOption("gpt-4o");
    await wait(900);

    // 4) Bump TOP_K up with the keyboard so the slider animates
    await page.locator("#cfgTopk").click();
    for (let i = 0; i < 4; i++) {
      await page.keyboard.press("ArrowRight");
      await wait(220);
    }
    await wait(900);

    // 5) Apply & re-run the same question to compare performance
    await page.locator("#rerunBtn").click();
    await waitForAnswer(page);
    await smoothScrollThread(page, "bottom");
    await wait(4200); // compare the two performance panels

    await wait(1500);
  } finally {
    await context.close(); // flushes the video file
    await browser.close();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
