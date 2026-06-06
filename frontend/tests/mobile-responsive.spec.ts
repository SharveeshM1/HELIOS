import { expect, test } from "@playwright/test";

test("mobile dashboard exposes primary navigation without horizontal overflow", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Command Center" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Knowledge Sources/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /Code Intelligence/ })).toBeVisible();

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(2);
});

test("mobile code and knowledge controls remain usable", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: /Code Intelligence/ }).click();
  await expect(page.getByPlaceholder("Repair objective")).toBeVisible();
  await expect(page.getByPlaceholder("Paths to stage, comma separated")).toBeVisible();

  await page.getByRole("button", { name: /Knowledge Sources/ }).click();
  await expect(page.getByRole("button", { name: "Index URL" })).toBeVisible();
});
