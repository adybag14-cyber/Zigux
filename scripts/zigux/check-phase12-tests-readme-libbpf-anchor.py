#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()

TESTS_README_PATH = "zigux/tests/README.md"
LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
LIBBPF_SNAPSHOT_DETERMINISM_PATH = (
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json"
)

REQUIRED_MARKERS = [
    "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
    "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`Documentation/zigux/phase12-libbpf-segment-survey.md`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
    "`scripts/zigux/check-phase12-release-readiness-packet.py`",
    "`phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / TESTS_README_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_contains(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:missing:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in [
        TESTS_README_PATH,
        LIBBPF_SNAPSHOT_PATH,
        LIBBPF_SNAPSHOT_DETERMINISM_PATH,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    tests_readme = read_text(root, TESTS_README_PATH)
    ensure_contains(failures, "tests_readme", tests_readme, REQUIRED_MARKERS)
    return failures


def minimal_tests_readme() -> str:
    lines = ["# zigux/tests", "", "Phase 12 review packet"]
    lines.extend(f"  * {marker}" for marker in REQUIRED_MARKERS)
    return "\n".join(lines) + "\n"


def minimal_snapshot() -> str:
    return (
        "{\n"
        '  "lane_key": "P12-L17",\n'
        '  "phase": "Phase 12",\n'
        '  "surveyed_commit": "5ccb94e1380d1f2e236c98d09bc52b2b5f6948c7",\n'
        '  "tracked_file_count": 1,\n'
        '  "tracked_paths": [\n'
        '    "tools/lib/bpf/zigux_segments/pin_path.zig"\n'
        "  ]\n"
        "}\n"
    )


def minimal_snapshot_determinism() -> str:
    return minimal_snapshot()


def run_self_test() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        write_text(root / TESTS_README_PATH, minimal_tests_readme())
        write_text(root / LIBBPF_SNAPSHOT_PATH, minimal_snapshot())
        write_text(
            root / LIBBPF_SNAPSHOT_DETERMINISM_PATH, minimal_snapshot_determinism()
        )

        base_failures = validate(root)
        if base_failures:
            failures.append(f"expected clean fixture, got {base_failures}")

        (root / LIBBPF_SNAPSHOT_DETERMINISM_PATH).unlink()
        drift_failures = validate(root)
        expected_missing = (
            "missing_file:zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json"
        )
        if expected_missing not in drift_failures:
            failures.append(
                "expected missing determinism fixture to fail closed, got "
                f"{drift_failures}"
            )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Guard the Phase 12 tests-root libbpf snapshot anchors against "
            "missing companion fixtures."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate (defaults to inferred repository root).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the checker's built-in self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        failures = run_self_test()
    else:
        failures = validate(args.root)

    if failures:
        for failure in failures:
            print(failure)
        return 1

    if args.self_test:
        print("self-test passed")
    else:
        print("phase12 tests README libbpf anchors are aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
