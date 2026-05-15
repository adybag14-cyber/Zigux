#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "Documentation/zigux/phase7-roadmap-integration-survey.md",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 7 runtime helper gates",
        "make -C zigux phase7-validate",
        "Run Phase 7 runtime helper tests",
        "make -C zigux phase7-test",
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_build.zig",
        "make -C zigux phase7-validate",
        "shared Phase 7 control surface",
    ],
    "Documentation/zigux/phase7-roadmap-integration-survey.md": [
        "PHASE7_STATUS=parked",
        "PHASE7_SLICE=roadmap-integration-shared-control-surface",
        "PHASE7_LANE_KEY=P7-L01",
        "lib/string_helpers.zig",
        "lib/cmdline.zig",
        "lib/argv_split.zig",
        "lib/rbtree.zig",
        "runtime-safe leaf helpers",
        "stronger ownership and pointer discipline",
        "integration with validation substrate",
        "scripts/zigux/check-phase7-roadmap-integration.py --self-test",
        "scripts/zigux/check-phase7-roadmap-integration.py",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_build.zig",
        "make -C zigux phase7-validate",
        "make -C zigux phase7-test",
        "This survey does not claim the whole shared Phase 7 helper bundle is green on current `master`.",
    ],
    "zigux/tests/phase7_build.zig": [
        "\"../../lib/string_helpers.zig\"",
        "\"../../lib/cmdline.zig\"",
        "\"../../lib/argv_split.zig\"",
        "\"../../lib/rbtree.zig\"",
        "\"phase7-string-helpers-survey\"",
        "\"phase7-cmdline-survey\"",
        "\"phase7-argv-split-survey\"",
        "\"phase7-rbtree-survey\"",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "scripts/zigux/check-phase7-build-wiring.py --self-test",
        "phase7-test:",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
        "phase7: phase7-validate phase7-test",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "# fixture\n"), encoding="utf-8")


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_phase7_workflow", ".github/workflows/zigux-bootstrap.yml"),
        ("missing_phase7_roadmap_note", "Documentation/zigux/phase7-roadmap-integration-survey.md"),
        ("missing_phase7_build", "zigux/tests/phase7_build.zig"),
    ]

    marker_cases = [
        (
            "roadmap_note_lane_marker",
            "Documentation/zigux/phase7-roadmap-integration-survey.md",
            "PHASE7_LANE_KEY=P7-L01",
            "PHASE7_LANE_KEY=P7-LXX",
            "Documentation/zigux/phase7-roadmap-integration-survey.md: PHASE7_LANE_KEY=P7-L01",
        ),
        (
            "roadmap_note_validation_substrate_marker",
            "Documentation/zigux/phase7-roadmap-integration-survey.md",
            "integration with validation substrate",
            "integration with ad hoc reminders",
            "Documentation/zigux/phase7-roadmap-integration-survey.md: integration with validation substrate",
        ),
        (
            "alignment_note_shared_surface_marker",
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
            "shared Phase 7 control surface",
            "",
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: shared Phase 7 control surface",
        ),
        (
            "roadmap_note_build_wiring_marker",
            "Documentation/zigux/phase7-roadmap-integration-survey.md",
            "scripts/zigux/check-phase7-build-wiring.py",
            "scripts/zigux/check-phase7-build-drift.py",
            "Documentation/zigux/phase7-roadmap-integration-survey.md: scripts/zigux/check-phase7-build-wiring.py",
        ),
        (
            "build_rbtree_survey_marker",
            "zigux/tests/phase7_build.zig",
            "\"phase7-rbtree-survey\"",
            "\"phase7-rbtree-survey-drift\"",
            "zigux/tests/phase7_build.zig: \"phase7-rbtree-survey\"",
        ),
        (
            "makefile_phase7_test_route",
            "zigux/Makefile",
            "phase7-test:",
            "",
            "zigux/Makefile: phase7-test:",
        ),
        (
            "workflow_phase7_validate_step",
            ".github/workflows/zigux-bootstrap.yml",
            "Validate Phase 7 runtime helper gates",
            "Validate Phase 7 helper gates",
            ".github/workflows/zigux-bootstrap.yml: Validate Phase 7 runtime helper gates",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_roadmap_integration_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            assert validate(tmp_root) == ([rel], []), case
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            assert validate(tmp_root) == ([], [expected]), case
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases)
    print("PHASE7_ROADMAP_INTEGRATION_SELF_TEST=pass")
    print(f"PHASE7_ROADMAP_INTEGRATION_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 7 roadmap-backed integration packet stays aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_ROADMAP_INTEGRATION=fail")
        print("MISSING_PHASE7_ROADMAP_INTEGRATION_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_ROADMAP_INTEGRATION_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_ROADMAP_INTEGRATION=fail")
        print("MISSING_PHASE7_ROADMAP_INTEGRATION_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_ROADMAP_INTEGRATION_MARKERS_END")
        return 1

    print("PHASE7_ROADMAP_INTEGRATION=pass")
    print(f"PHASE7_ROADMAP_INTEGRATION_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_ROADMAP_INTEGRATION_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
