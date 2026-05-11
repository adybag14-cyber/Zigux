#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase8.py",
    "scripts/zigux/check-phase8-libbpf-segment-gate.py",
    "scripts/zigux/check-phase8-libbpf-shard-routes.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
    ],
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": [
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8",
    ],
    "Documentation/zigux/review-checklist.md": [
        "scripts/zigux/validate-phase8.py",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "make -C zigux phase8-validate",
        "make -C zigux phase8-libbpf-segments-test",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "phase8-libbpf-segments-test:",
        "phase8: phase8-validate",
    ],
    "zigux/tests/README.md": [
        "make -C zigux phase8-libbpf-segments-test",
        "make -C zigux phase8",
    ],
}

FIXTURE_OVERRIDES = {
    "scripts/zigux/validate-phase8.py": "# fixture\n",
    "scripts/zigux/check-phase8-libbpf-segment-gate.py": "# fixture\n",
    "scripts/zigux/check-phase8-libbpf-shard-routes.py": "# fixture\n",
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
    fixture_text.update(FIXTURE_OVERRIDES)
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "# fixture\n"), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_validator", "scripts/zigux/validate-phase8.py"),
        ("missing_segment_gate", "scripts/zigux/check-phase8-libbpf-segment-gate.py"),
        ("missing_shard_routes", "scripts/zigux/check-phase8-libbpf-shard-routes.py"),
        ("missing_lane_note", "Documentation/zigux/phase8-tooling-lane-sequencing.md"),
        ("missing_makefile", "zigux/Makefile"),
    ]
    marker_cases = [
        (
            "scripts_readme_validator_marker",
            "scripts/zigux/README.md",
            "scripts/zigux/validate-phase8.py",
            "scripts/zigux/validate-phase8-lane.py",
            "scripts/zigux/README.md: scripts/zigux/validate-phase8.py",
        ),
        (
            "lane_note_shard_routes_marker",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "scripts/zigux/check-phase8-libbpf-shard-routes.py",
            "scripts/zigux/check-phase8-libbpf-routes.py",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: scripts/zigux/check-phase8-libbpf-shard-routes.py",
        ),
        (
            "review_checklist_validator_marker",
            "Documentation/zigux/review-checklist.md",
            "scripts/zigux/validate-phase8.py",
            "scripts/zigux/validate-phase8-lane.py",
            "Documentation/zigux/review-checklist.md: scripts/zigux/validate-phase8.py",
        ),
        (
            "tests_readme_segments_route",
            "zigux/tests/README.md",
            "make -C zigux phase8-libbpf-segments-test",
            "make -C zigux phase8-libbpf-segment-test",
            "zigux/tests/README.md: make -C zigux phase8-libbpf-segments-test",
        ),
        (
            "makefile_phase8_validate_hook",
            "zigux/Makefile",
            "scripts/zigux/validate-phase8.py",
            "scripts/zigux/validate-phase8-lane.py",
            "zigux/Makefile: scripts/zigux/validate-phase8.py",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases)
    print("PHASE8_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE8_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shared Phase 8 tooling packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_VALIDATION=fail")
        print("MISSING_PHASE8_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_VALIDATION=fail")
        print("MISSING_PHASE8_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_MARKERS_END")
        return 1

    print("PHASE8_VALIDATION=pass")
    print(f"PHASE8_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
