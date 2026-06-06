import { expect, test } from "@playwright/test";

test("queues a durable autonomous run from the loop workspace", async ({ page }) => {
  const run = {
    id: "run-1",
    objective: "Plan memory, research citations, and debate implementation",
    status: "queued",
    plan: {
      primary_route: "planning",
      tasks: [
        { agent: "planning", route: "planning", objective: "Create a plan", priority: 1 },
        { agent: "research", route: "research", objective: "Gather evidence", priority: 2 },
        { agent: "collaboration", route: "swarm", objective: "Reach consensus", priority: 3 },
      ],
    },
    steps: [],
  };

  await page.route("http://localhost:8000/autonomy/runs?limit=12", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ runs: [] }),
    });
  });
  await page.route("http://localhost:8000/autonomy/runs", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ run }),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: /Autonomous Loop/ }).click();
  await page.getByPlaceholder("Objective for a long-running autonomous run").fill(run.objective);
  await page.getByRole("button", { name: "Queue run" }).click();

  await expect(page.getByText(run.objective)).toBeVisible();
  await expect(page.getByText("collaboration / swarm")).toBeVisible();
});

test("runs automatic code repair from the code workspace", async ({ page }) => {
  await page.route("http://localhost:8000/code/repair/auto", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        status: "completed",
        commit_ready: true,
        attempts: [
          {
            repair: {
              mode: "general_code_repair",
              edits: [{ path: "backend/main.py", status: "applied" }],
              verification: [{ command: "backend/venv/bin/python -m pytest backend", status: "passed" }],
              commit_ready: true,
            },
          },
        ],
      }),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: /Code Intelligence/ }).click();
  await page.getByPlaceholder("Repair objective").fill("Fix the backend health contract");
  await page.getByPlaceholder("Target files, comma separated").fill("backend/main.py");
  await page.getByRole("button", { name: "Edit, test, retry" }).click();

  const verification = page.getByText("backend/venv/bin/python -m pytest backend");
  await verification.scrollIntoViewIfNeeded();
  await expect(verification).toBeVisible();
  await expect(page.getByText("Patch ready for review")).toBeAttached();
});

test("runs guarded git workflow operations from the code workspace", async ({ page }) => {
  await page.route("http://localhost:8000/git/stage", async (route) => {
    expect(route.request().postDataJSON()).toMatchObject({
      paths: ["backend/main.py"],
      confirm: true,
    });
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ status: "success", stdout: "staged" }),
    });
  });
  await page.route("http://localhost:8000/git/diff?staged=true", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ status: "success", staged: true, diff: "+staged" }),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: /Code Intelligence/ }).click();
  await page.getByPlaceholder("Paths to stage, comma separated").fill("backend/main.py");
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Stage" }).click();

  await expect(page.getByText(/success.*staged/)).toBeVisible();
});

test("indexes web and GitHub URLs from the knowledge workspace", async ({ page }) => {
  await page.route("http://localhost:8000/sources", async (route) => {
    if (route.request().method() === "POST") {
      expect(route.request().postDataJSON()).toMatchObject({
        type: "GITHUB",
        content: "https://github.com/openai/openai-python",
      });
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          source: {
            id: "source-github",
            name: "https://github.com/openai/openai-python",
            type: "GITHUB",
            scope: "project",
            status: "Indexed",
          },
        }),
      });
      return;
    }
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ sources: [] }),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: /Knowledge Sources/ }).click();
  await page.getByRole("combobox").selectOption("GITHUB");
  await page.getByPlaceholder("https://github.com/owner/repository").fill("https://github.com/openai/openai-python");
  await page.getByRole("button", { name: "Index URL" }).click();

  await expect(page.getByText("https://github.com/openai/openai-python")).toBeVisible();
});
