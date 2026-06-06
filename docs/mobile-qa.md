# HELIOS Mobile QA

## Automated Matrix

The Playwright suite runs the HELIOS dashboard against:

- Desktop Chromium
- Pixel 5 / Mobile Chrome
- iPhone 12 / Mobile Safari

Dedicated responsive assertions verify that primary module navigation, Code controls, Knowledge URL ingestion, and the dashboard viewport remain usable without horizontal overflow.

Run:

```sh
cd frontend
npm run test:e2e
```

## Manual Checklist

- Sign in and confirm the account control remains accessible.
- Create, run, review, and archive a mission.
- Open Code Intelligence and use repair, diff, git, and terminal controls.
- Open Knowledge Sources and index a web or GitHub URL.
- Open Voice and use the provider-independent fallback.
- Open the execution drawer and filter events.
- Rotate the device and confirm no control is clipped or unreachable.
