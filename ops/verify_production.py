import argparse
import json
import ssl
import sys
import urllib.request


def fetch(
    url: str,
    timeout: int
) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "helios-production-verifier"
        }
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(
        request,
        timeout=timeout,
        context=context
    ) as response:
        return response.status, response.read().decode(
            "utf-8"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify a deployed HELIOS production endpoint."
    )
    parser.add_argument(
        "base_url",
        help="Public API base URL, for example https://helios.example.com/api"
    )
    parser.add_argument(
        "--require-voice",
        action="store_true"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10
    )
    args = parser.parse_args()
    base_url = args.base_url.rstrip(
        "/"
    )
    failures = []

    for path in (
        "/health",
        "/ready",
        "/metrics",
        "/voice/status"
    ):
        try:
            status, body = fetch(
                f"{base_url}{path}",
                args.timeout
            )
            if status != 200:
                failures.append(
                    f"{path} returned {status}"
                )
                continue
            if path == "/ready":
                payload = json.loads(
                    body
                )
                if not payload.get(
                    "ready"
                ):
                    failures.append(
                        "/ready reported not ready"
                    )
            if path == "/metrics" and "helios_requests_total" not in body:
                failures.append(
                    "/metrics did not expose HELIOS counters"
                )
            if path == "/voice/status" and args.require_voice:
                payload = json.loads(
                    body
                )
                if not payload.get(
                    "realtime_available"
                ):
                    failures.append(
                        "voice provider is not available"
                    )
        except Exception as error:
            failures.append(
                f"{path} failed: {error}"
            )

    if failures:
        for failure in failures:
            print(
                f"FAIL: {failure}"
            )
        sys.exit(
            1
        )

    print(
        "HELIOS production verification passed."
    )


if __name__ == "__main__":
    main()
