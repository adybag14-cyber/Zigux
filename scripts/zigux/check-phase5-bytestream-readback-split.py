#!/usr/bin/env python3
"""Guard the shared Phase 5 bytestream readback split."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


SURFACES = {
    "Documentation/zigux/phase5-sample-review-guide.md": (
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        "zigux/tests/phase5_bytestream_fifo.zig",
        "zigux/tests/phase5_bytestream_fifo_survey.zig",
        "zigux/tests/phase5_build.zig",
    ),
    "samples/zigux/README.md": (
        "Fresh authenticated contents readback in this run now recovers this bytestream companion path too:",
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        "zigux/tests/phase5_bytestream_fifo.zig",
        "zigux/tests/phase5_bytestream_fifo_survey.zig",
        "zigux/tests/phase5_build.zig",
    ),
    "scripts/zigux/README.md": (
        "the directly readable companion manifest `zigux/tests/phase5_bytestream_fifo_manifest.json`",
        "authenticated contents readback in this environment still fails for `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and the shared `zigux/tests/phase5_build.zig` route",
    ),
    "zigux/tests/README.md": (
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        "current public-tree-backed Phase 5 bytestream companions: `zigux/tests/phase5_bytestream_fifo.zig` and `zigux/tests/phase5_bytestream_fifo_survey.zig`",
        "current public-tree-backed Phase 5 shared-build companion: `zigux/tests/phase5_build.zig`",
    ),
}


def check_repo(repo_root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, markers in SURFACES.items():
        path = repo_root / relative_path
        if not path.exists():
            failures.append(f"missing file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"{relative_path}: missing marker: {marker}")
    return failures


def expect_failure(repo_root: Path, relative_path: str, marker: str, case_id: str) -> None:
    path = repo_root / relative_path
    original = path.read_text(encoding="utf-8")
    if marker not in original:
        raise AssertionError(f"{case_id}: seeded self-test file is missing marker")
    mutated = original.replace(marker, "", 1)
    path.write_text(mutated, encoding="utf-8")
    failures = check_repo(repo_root)
    if not any(relative_path in failure and "missing marker" in failure for failure in failures):
        raise AssertionError(f"{case_id}: checker did not fail after removing marker")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase5_bytestream_readback_") as tmpdir:
        repo_root = Path(tmpdir)
        case_count = 0
        for relative_path, markers in SURFACES.items():
            path = repo_root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(markers) + "\n", encoding="utf-8")

        failures = check_repo(repo_root)
        if failures:
            raise AssertionError(f"seeded self-test repo should pass: {failures}")

        for relative_path, markers in SURFACES.items():
            for index, marker in enumerate(markers, start=1):
                case_count += 1
                expect_failure(repo_root, relative_path, marker, f"{relative_path}#{index}")

    print("PHASE5_BYTESTREAM_READBACK_SPLIT_SELF_TEST=pass")
    print(f"PHASE5_BYTESTREAM_READBACK_SPLIT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that shared Phase 5 reminders keep the bytestream direct-readback split explicit."
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in checker self-tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    repo_root = Path(__file__).resolve().parents[1]
    failures = check_repo(repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE5_BYTESTREAM_READBACK_SPLIT_FAIL={failure}")
        return 1

    print("PHASE5_BYTESTREAM_READBACK_SPLIT=pass")
    print(f"PHASE5_BYTESTREAM_READBACK_SPLIT_SURFACE_COUNT={len(SURFACES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
