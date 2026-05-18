#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parent.parent.parent if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_CLOSURE_CHECKLIST_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
LIBBPF_VERIFY_SHARD_NOTE_PATH = "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
LIBBPF_SNAPSHOT_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-snapshot.py"
LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
LIBBPF_SNAPSHOT_DETERMINISM_PATH = (
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json"
)

REQUIRED_FILES = [
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    LIBBPF_VERIFY_SHARD_NOTE_PATH,
    LIBBPF_SNAPSHOT_CHECKER_PATH,
    LIBBPF_SNAPSHOT_PATH,
    LIBBPF_SNAPSHOT_DETERMINISM_PATH,
]

REQUIRED_MARKERS = {
    RELEASE_READINESS_SURVEY_PATH: [
        "the parked verify-shard note still governs the shared libbpf packet",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "The deterministic libbpf fixture pair stays explicit: `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remain required before the shared release packet can be described as ready for closure review.",
        "The parked libbpf heavy-consumer packet stays explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being rounded up into a shipped shared replay claim.",
    ],
    LIBBPF_VERIFY_SHARD_NOTE_PATH: [
        "snapshot checker: `scripts/zigux/check-phase12-libbpf-snapshot.py`",
        "snapshot anchor: `zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
        "the snapshot anchor remains the truthful bounded signal here while those direct replay files stay absent from the shipped checkout",
    ],
    LIBBPF_SNAPSHOT_CHECKER_PATH: [
        'SNAPSHOT_PATH = Path("zigux/tests/fixtures/phase12_libbpf_snapshot.json")',
        'EXPECTED_LANE_KEY = "P12-Y04"',
        'EXPECTED_PHASE = "Phase 12"',
    ],
}

SNAPSHOT_EXPECTATIONS = {
    "lane_key": "P12-Y04",
    "phase": "Phase 12",
    "tracked_file_count": 4,
    "tracked_paths": [
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
        "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
        "Documentation/zigux/phase12-release-coordination-matrix.md",
    ],
    "supporting_notes": [
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
        "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
        "Documentation/zigux/phase12-release-coordination-matrix.md",
    ],
}

SNAPSHOT_DETERMINISM_EXPECTATIONS = {
    "lane_key": "P12-L17",
    "phase": "Phase 12",
    "tracked_file_count": 1,
    "tracked_paths": [
        "tools/lib/bpf/zigux_segments/pin_path.zig",
    ],
}


def load_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> dict[str, object]:
    return json.loads(load_text(root, rel_path))


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = load_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    snapshot = load_json(root, LIBBPF_SNAPSHOT_PATH)
    for field, expected in SNAPSHOT_EXPECTATIONS.items():
        if snapshot.get(field) != expected:
            failures.append(f"snapshot:{field}:{expected}")

    snapshot_determinism = load_json(root, LIBBPF_SNAPSHOT_DETERMINISM_PATH)
    for field, expected in SNAPSHOT_DETERMINISM_EXPECTATIONS.items():
        if snapshot_determinism.get(field) != expected:
            failures.append(f"snapshot_determinism:{field}:{expected}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(
        root / RELEASE_READINESS_SURVEY_PATH,
        marker_fixture(
            "# Phase 12 Release Readiness Survey",
            REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH],
        ),
    )
    write_text(
        root / RELEASE_CLOSURE_CHECKLIST_PATH,
        marker_fixture(
            "# Phase 12 Release Closure Checklist",
            REQUIRED_MARKERS[RELEASE_CLOSURE_CHECKLIST_PATH],
        ),
    )
    write_text(
        root / LIBBPF_VERIFY_SHARD_NOTE_PATH,
        marker_fixture(
            "# Phase 12 Libbpf Verify Shard Note",
            REQUIRED_MARKERS[LIBBPF_VERIFY_SHARD_NOTE_PATH],
        ),
    )
    write_text(
        root / LIBBPF_SNAPSHOT_CHECKER_PATH,
        "\n".join(REQUIRED_MARKERS[LIBBPF_SNAPSHOT_CHECKER_PATH]) + "\n",
    )
    write_text(
        root / LIBBPF_SNAPSHOT_PATH,
        json.dumps(SNAPSHOT_EXPECTATIONS, indent=2) + "\n",
    )
    write_text(
        root / LIBBPF_SNAPSHOT_DETERMINISM_PATH,
        json.dumps(SNAPSHOT_DETERMINISM_EXPECTATIONS, indent=2) + "\n",
    )


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-libbpf-readiness-snapshot-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        file_cases = [
            RELEASE_READINESS_SURVEY_PATH,
            RELEASE_CLOSURE_CHECKLIST_PATH,
            LIBBPF_VERIFY_SHARD_NOTE_PATH,
            LIBBPF_SNAPSHOT_CHECKER_PATH,
            LIBBPF_SNAPSHOT_PATH,
            LIBBPF_SNAPSHOT_DETERMINISM_PATH,
        ]
        for rel_path in file_cases:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (
                RELEASE_READINESS_SURVEY_PATH,
                REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][0],
            ),
            (
                RELEASE_CLOSURE_CHECKLIST_PATH,
                REQUIRED_MARKERS[RELEASE_CLOSURE_CHECKLIST_PATH][0],
            ),
            (
                LIBBPF_VERIFY_SHARD_NOTE_PATH,
                REQUIRED_MARKERS[LIBBPF_VERIFY_SHARD_NOTE_PATH][0],
            ),
            (
                LIBBPF_SNAPSHOT_CHECKER_PATH,
                REQUIRED_MARKERS[LIBBPF_SNAPSHOT_CHECKER_PATH][0],
            ),
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        write_fixture_tree(base)
        write_text(
            base / LIBBPF_SNAPSHOT_PATH,
            json.dumps(
                {
                    **SNAPSHOT_EXPECTATIONS,
                    "lane_key": "P12-X99",
                },
                indent=2,
            )
            + "\n",
        )
        expect_failure(base, "snapshot:lane_key:P12-Y04")

        write_fixture_tree(base)
        write_text(
            base / LIBBPF_SNAPSHOT_DETERMINISM_PATH,
            json.dumps(
                {
                    **SNAPSHOT_DETERMINISM_EXPECTATIONS,
                    "tracked_paths": [],
                },
                indent=2,
            )
            + "\n",
        )
        expect_failure(
            base,
            "snapshot_determinism:tracked_paths:['tools/lib/bpf/zigux_segments/pin_path.zig']",
        )

        case_count = len(file_cases) + len(marker_cases) + 2
        print("PHASE12_LIBBPF_READINESS_SNAPSHOT_SELF_TEST=pass")
        print(f"PHASE12_LIBBPF_READINESS_SNAPSHOT_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed when the shared Phase 12 libbpf readiness packet drifts from "
            "its deterministic snapshot anchors."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE12_LIBBPF_READINESS_SNAPSHOT=fail")
        print("PHASE12_LIBBPF_READINESS_SNAPSHOT_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_LIBBPF_READINESS_SNAPSHOT_FAILURES_END")
        return 1

    print("PHASE12_LIBBPF_READINESS_SNAPSHOT=pass")
    print(f"PHASE12_LIBBPF_READINESS_SNAPSHOT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_LIBBPF_READINESS_SNAPSHOT_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
