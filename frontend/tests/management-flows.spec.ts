import { expect, test } from "@playwright/test";

test("schedules a mission from the mission composer", async ({ page }) => {
  let scheduledPayload: Record<string, unknown> | undefined;

  await page.route("http://localhost:8000/missions/schedule", async (route) => {
    scheduledPayload = route.request().postDataJSON() as Record<string, unknown>;
    expect(scheduledPayload).toMatchObject({
      title: "Review scheduled runtime",
      module: "planning",
      agent: "Orion",
    });
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        mission: {
          id: "scheduled-1",
          title: "Review scheduled runtime",
          status: "pending",
        },
      }),
    });
  });

  await page.goto("/");
  await page.locator(".mission-launch-row").getByRole("button", { name: "Plan" }).click();
  await page.getByPlaceholder("What should HELIOS accomplish?").fill("Review scheduled runtime");
  await page.locator("input[type='datetime-local']").fill("2030-01-01T09:30");
  await page.getByRole("button", { name: "Schedule Mission" }).click();

  await expect.poll(() => scheduledPayload?.title).toBe("Review scheduled runtime");
  expect(scheduledPayload?.scheduled_at).toEqual(expect.any(Number));
});

test("manages plugins from the plugin marketplace", async ({ page }) => {
  await page.route("http://localhost:8000/plugins", async (route) => {
    if (route.request().method() === "POST") {
      expect(route.request().postDataJSON()).toMatchObject({
        name: "sample_tool",
        version: "1.0.0",
      });
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({ message: "Plugin sample_tool.py uploaded and loaded." }),
      });
      return;
    }
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        plugins: [
          {
            name: "sample_tool",
            filename: "sample_tool.py",
            version: "1.0.0",
            verified: true,
          },
        ],
      }),
    });
  });
  await page.route("http://localhost:8000/plugins/upload", async (route) => {
    expect(route.request().postDataJSON()).toMatchObject({
      name: "sample_tool",
    });
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ message: "Plugin sample_tool.py uploaded and loaded." }),
    });
  });

  await page.goto("/");
  await page.locator(".module-tabs").getByRole("button", { name: "Plugins" }).click();
  await page.getByPlaceholder("Plugin name").fill("sample_tool");
  await page.getByPlaceholder("Description").fill("demo");
  await page.getByPlaceholder(/def register_plugin/).fill("def register_plugin(registry):\n    registry['demo'] = lambda: 'ok'");
  await page.getByRole("button", { name: "Upload signed plugin" }).click();

  await expect(page.getByText("Plugin sample_tool.py uploaded and loaded.")).toBeVisible();
});

test("reindexes and removes indexed sources", async ({ page }) => {
  await page.route("http://localhost:8000/sources", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        sources: [
          {
            id: "src-1",
            name: "ops.md",
            type: "MD",
            size: "1 KB",
            status: "Indexed",
          },
        ],
      }),
    });
  });
  await page.route("http://localhost:8000/sources/src-1/reindex", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        source: {
          id: "src-1",
          name: "ops.md",
          type: "MD",
          size: "1 KB",
          status: "Indexed",
        },
      }),
    });
  });
  await page.route("http://localhost:8000/sources/src-1", async (route) => {
    expect(route.request().method()).toBe("DELETE");
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ deleted: true }),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: /Knowledge Sources/ }).click();
  const sourceRow = page.locator(".source-row").filter({ hasText: "ops.md" });
  await sourceRow.getByRole("button", { name: "Reindex", exact: true }).click();
  await expect(page.getByText("ops.md")).toBeVisible();
  page.once("dialog", (dialog) => dialog.accept());
  await sourceRow.getByRole("button", { name: "Remove", exact: true }).click();
  await expect(page.getByText("ops.md")).toHaveCount(0);
});

test("deploy uses durable approval before executing the tool", async ({ page }) => {
  let executeCalls = 0;
  await page.route("http://localhost:8000/tools/execute", async (route) => {
    executeCalls += 1;
    const body = route.request().postDataJSON();
    if (executeCalls === 1) {
      expect(body).toMatchObject({ tool: "deploy_project" });
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          status: "approval_required",
          approval: {
            approval_id: "approval-1",
          },
        }),
      });
      return;
    }
    expect(body).toMatchObject({
      tool: "deploy_project",
      approval_id: "approval-1",
    });
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        status: "success",
        result: {
          stdout: "deployed",
        },
      }),
    });
  });
  await page.route("http://localhost:8000/approvals/approval-1", async (route) => {
    expect(route.request().postDataJSON()).toMatchObject({ status: "approved" });
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        approval: {
          id: "approval-1",
          status: "approved",
        },
      }),
    });
  });

  await page.goto("/");
  await page.getByLabel("Open deploy panel").click();
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Deploy HELIOS" }).click();

  await expect.poll(() => executeCalls).toBe(2);
});
