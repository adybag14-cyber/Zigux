#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "scripts/zigux/validate-phase12.py").exists() and (
            candidate / "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
TESTS_README_PATH = "zigux/tests/README.md"

EXPECTED_SNAPSHOT = {
    "lane_key": "P12-L16",
    "phase": "Phase 12",
    "surveyed_commit": "c0ae127363e3d4e5feeb36efb665a12ece3392c7",
    "tracked_file_count": 5,
    "tracked_paths": [
        "tools/lib/bpf/zigux_segments/type_names.zig",
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
        "tools/lib/bpf/zigux_segments/logging.zig",
        "tools/lib/bpf/zigux_segments/pin_path.zig",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    ],
}

RELEASE_READINESS_MARKERS = [
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json` is the public anchor",
    "parked libbpf reviewability packet",
    "the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` remain note-owned or snapshot-backed boundaries",
]

TESTS_README_MARKERS = [
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
]

BUILD_ONLY_CHECKER_MARKERS = [
    'PHASE12_LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"',
]

REQUIRED_FILES = [
    SNAPSHOT_PATH,
    BUILD_ONLY_CHECKER_PATH,
    RELEASE_READINESS_PATH,
    TESTS_README_PATH,
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate_snapshot(root: Path) -> list[str]:
    snapshot_path = root / SNAPSHOT_PATH
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    failures: list[str] = []

    for key in ["lane_key", "phase", "surveyed_commit", "tracked_file_count", "tracked_paths"]:
        if key not in snapshot:
            failures.append(f"snapshot:missing_key:{key}")

    if failures:
        return failures

    for key in ["lane_key", "phase", "surveyed_commit", "tracked_file_count"]:
        if snapshot[key] != EXPECTED_SNAPSHOT[key]:
            failures.append(
                f"snapshot:{key}:expected={EXPECTED_SNAPSHOT[key]!r}:actual={snapshot[key]!r}"
            )

    tracked_paths = snapshot["tracked_paths"]
    if tracked_paths != EXPECTED_SNAPSHOT["tracked_paths"]:
        failures.append("snapshot:tracked_paths:exact_match_required")

    if len(tracked_paths) != snapshot["tracked_file_count"]:
        failures.append(
            "snapshot:tracked_file_count_mismatch:"
            f"expected_list_len={len(tracked_paths)}:declared={snapshot['tracked_file_count']}"
        )

    if len(set(tracked_paths)) != len(tracked_paths):
        failures.append("snapshot:tracked_paths:duplicate_entries")

    for path in tracked_paths:
        if not path.startswith("tools/lib/bpf/zigux_segments/"):
            failures.append(f"snapshot:tracked_path_prefix:{path}")

    return failures


def validate_markers(root: Path, rel_path: str, markers: list[str], prefix: str) -> list[str]:
    text = read_text(root, rel_path)
    failures: list[str] = []
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:{marker}")
    return failures


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    failures.extend(validate_snapshot(root))
    failures.extend(
        validate_markers(
            root,
            RELEASE_READINESS_PATH,
            RELEASE_READINESS_MARKERS,
            "release_readiness",
        )
    )
    failures.extend(
        validate_markers(
            root,
            TESTS_README_PATH,
            TESTS_README_MARKERS,
            "tests_readme",
        )
    )
    failures.extend(
        validate_markers(
            root,
            BUILD_ONLY_CHECKER_PATH,
            BUILD_ONLY_CHECKER_MARKERS,
            "build_only_checker",
        )
    )
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root / SNAPSHOT_PATH, json.dumps(EXPECTED_SNAPSHOT, indent=2) + "\n")
    write_text(
        root / BUILD_ONLY_CHECKER_PATH,
        "\n".join(BUILD_ONLY_CHECKER_MARKERS) + "\n",
    )
    write_text(
        root / RELEASE_READINESS_PATH,
        "# Phase 12 Release Readiness Survey\n\n" + "\n".join(RELEASE_READINESS_MARKERS) + "\n",
    )
    write_text(
        root / TESTS_README_PATH,
        "# zigux/tests\n\n" + "\n".join(TESTS_README_MARKERS) + "\n",
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-libbpf-snapshot-support-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        (base / SNAPSHOT_PATH).unlink()
        expect_failure(base, f"missing_file:{SNAPSHOT_PATH}")

        write_fixture_tree(base)
        snapshot_path = base / SNAPSHOT_PATH
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot["lane_key"] = "P12-L99"
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_failure(base, "snapshot:lane_key:expected='P12-L16':actual='P12-L99'")

        write_fixture_tree(base)
        snapshot_path = base / SNAPSHOT_PATH
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot["tracked_paths"][-1] = "tools/lib/bpf/zigux_segments/missing.zig"
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        expect_failure(base, "snapshot:tracked_paths:exact_match_required")

        write_fixture_tree(base)
        readiness_path = base / RELEASE_READINESS_PATH
        readiness_path.write_text(
            read_text(base, RELEASE_READINESS_PATH).replace(
                RELEASE_READINESS_MARKERS[0], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"release_readiness:{RELEASE_READINESS_MARKERS[0]}")

        write_fixture_tree(base)
        tests_readme_path = base / TESTS_README_PATH
        tests_readme_path.write_text(
            read_text(base, TESTS_README_PATH).replace(TESTS_README_MARKERS[1], "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"tests_readme:{TESTS_README_MARKERS[1]}")

        write_fixture_tree(base)
        checker_path = base / BUILD_ONLY_CHECKER_PATH
        checker_path.write_text(
            read_text(base, BUILD_ONLY_CHECKER_PATH).replace(
                BUILD_ONLY_CHECKER_MARKERS[0], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"build_only_checker:{BUILD_ONLY_CHECKER_MARKERS[0]}")

        print("PHASE12_LIBBPF_SNAPSHOT_SUPPORT_SELF_TEST=pass")
        print("PHASE12_LIBBPF_SNAPSHOT_SUPPORT_SELF_TEST_CASE_COUNT=6")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the surviving Phase 12 libbpf deterministic-snapshot support packet "
            "around the committed snapshot anchor and the reminder surfaces that still "
            "frame it as a parked boundary rather than a direct replay route."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_LIBBPF_SNAPSHOT_SUPPORT=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_LIBBPF_SNAPSHOT_SUPPORT=pass")
    print(f"PHASE12_LIBBPF_SNAPSHOT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE12_LIBBPF_SNAPSHOT_TRACKED_FILE_COUNT={EXPECTED_SNAPSHOT['tracked_file_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
