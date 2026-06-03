import argparse
import shutil
import time
from pathlib import Path


def backup_runtime(
    source: Path,
    destination: Path,
    keep: int
) -> Path:
    destination.mkdir(
        parents=True,
        exist_ok=True
    )
    target = destination / f"helios-runtime-{int(time.time())}"
    shutil.copytree(
        source,
        target
    )
    backups = sorted(
        destination.glob(
            "helios-runtime-*"
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )
    for stale in backups[
        max(
            1,
            keep
        ):
    ]:
        shutil.rmtree(
            stale
        )
    return target


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Back up HELIOS runtime state."
    )
    parser.add_argument(
        "--source",
        default="backend/memory"
    )
    parser.add_argument(
        "--destination",
        default="backups"
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=7
    )
    args = parser.parse_args()
    target = backup_runtime(
        Path(
            args.source
        ),
        Path(
            args.destination
        ),
        args.keep
    )
    print(
        target
    )


if __name__ == "__main__":
    main()
