import { expect, test } from "@playwright/test";

test("creates, runs, reviews, and archives a mission", async ({ page }) => {
  const errors: string[] = [];

  page.on("console", (message) => {
    if (message.type() === "error") {
      errors.push(message.text());
    }
  });

  page.on("pageerror", (error) => {
    errors.push(error.message);
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Command Center" })).toBeVisible();
  await page.getByLabel("Mission presets").getByRole("button", { name: "Plan", exact: true }).click();

  const missionName = `playwright mission ${Date.now()}`;
  await page.getByPlaceholder("What should HELIOS accomplish?").fill(missionName);
  await page.getByRole("button", { name: "Create Mission" }).last().click();

  await expect(page.getByText(missionName).first()).toBeVisible();
  await page.getByRole("button", { name: "⌘ Command Center" }).click();
  await expect(page.getByText(missionName).first()).toBeVisible();

  await page.getByRole("button", { name: "Run" }).click();
  await expect(page.getByText(/converted mission into/i).first()).toBeVisible();

  await page.getByRole("button", { name: "Reviewed" }).click();
  await expect(page.getByText("Reviewed").first()).toBeVisible();

  await page.getByRole("button", { name: "Archived" }).click();
  await expect(page.getByText("Archived").first()).toBeVisible();

  expect(errors).toEqual([]);
});
