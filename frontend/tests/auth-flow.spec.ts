import { expect, test } from "@playwright/test";

test("signs in and restores the authenticated account", async ({ page }) => {
  let signedIn = false;
  const user = {
    id: "admin-1",
    username: "admin",
    role: "admin",
    active: true,
  };

  await page.route("http://localhost:8000/health", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        status: "online",
        security: {
          token_auth_enabled: true,
        },
      }),
    });
  });

  await page.route("http://localhost:8000/auth/login", async (route) => {
    signedIn = true;
    await route.fulfill({
      contentType: "application/json",
      headers: {
        "Set-Cookie": "helios_session=test-token; Path=/; HttpOnly; SameSite=Strict",
      },
      body: JSON.stringify({
        token: "test-token",
        user,
      }),
    });
  });

  await page.route("http://localhost:8000/auth/me", async (route) => {
    if (!signedIn) {
      await route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Session required" }),
      });
      return;
    }
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ user }),
    });
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
  await page.getByLabel("Username").fill("admin");
  await page.getByLabel("Password").fill("strong-password");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page.getByRole("button", { name: /admin/i }).first()).toBeVisible();
  await expect.poll(async () => (await page.context().cookies()).some((cookie) => cookie.name === "helios_session")).toBe(true);
  await expect.poll(() => page.evaluate(() => window.localStorage.getItem("helios-auth-session"))).toBeNull();
});
