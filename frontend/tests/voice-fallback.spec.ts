import { expect, test } from "@playwright/test";

test("uses provider-independent voice fallback and shows the transcript", async ({ page }) => {
  await page.route("http://localhost:8000/voice/fallback", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        response: "Provider-independent voice is ready.",
        provider_independent: true,
      }),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: /Voice AI/ }).click();
  await page.getByPlaceholder("Ask HELIOS to speak...").fill("Give me a voice status.");
  await page.getByRole("button", { name: "Speak reply" }).click();
  await page.getByRole("button", { name: "Transcript" }).click();

  await expect(page.getByText("Provider-independent voice is ready.")).toBeVisible();
});
