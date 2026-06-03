import os
import time
from pathlib import Path

from backup_runtime import backup_runtime


def main() -> None:
    source = Path(
        os.getenv(
            "HELIOS_BACKUP_SOURCE",
            "/data/memory"
        )
    )
    destination = Path(
        os.getenv(
            "HELIOS_BACKUP_DESTINATION",
            "/data/backups"
        )
    )
    keep = int(
        os.getenv(
            "HELIOS_BACKUP_KEEP",
            "7"
        )
    )
    interval = max(
        60,
        int(
            os.getenv(
                "HELIOS_BACKUP_INTERVAL_SECONDS",
                "86400"
            )
        )
    )

    while True:
        if source.exists():
            target = backup_runtime(
                source,
                destination,
                keep
            )
            print(
                f"Created HELIOS backup: {target}",
                flush=True
            )
        else:
            print(
                f"Backup source does not exist: {source}",
                flush=True
            )
        time.sleep(
            interval
        )


if __name__ == "__main__":
    main()
