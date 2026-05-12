#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

DOCS_ROOT_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
SEQUENCING_PATH = "Documentation/zigux/phase8-tooling-lane-sequencing.md"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
HELP_KALLSYMS_PACKET_CHECKER_PATH = "scripts/zigux/check-phase8-help-kallsyms-packet.py"

REQUIRED_FILES = (
    DOCS_ROOT_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    SEQUENCING_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    VALIDATOR_PATH,
    HELP_KALLSYMS_PACKET_CHECKER_PATH,
)

REQUIRED_MARKERS = {
    DOCS_ROOT_PATH: (
        "Phase 8 notes - `Documentation/zigux/README.md`, `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase8.py`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` now keep the current shared reminder packet reviewable while `tools/lib/subcmd/`, `tools/lib/symbol/`, `tools/lib/bpf/zigux_segments/`, and the older `zigux/tests/phase8_*` shard files remain repo-reality gaps on current `master`.",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the current Phase 8 help-and-kallsyms reminder packet",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "current `master` does not expose `tools/lib/symbol/`",
    ),
    SCRIPTS_README_PATH: (
        "Phase 8 flow - current `master` keeps the shared Phase 8 reminder packet",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`Documentation/zigux/README.md`",
    ),
    TESTS_README_PATH: (
        "Phase 8 reminder packet",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`Documentation/zigux/README.md`",
    ),
    SEQUENCING_PATH: (
        "`PHASE8_STATUS=parked`",
        "### 2. Symbol lane",
        "the default-branch tree read surface does not currently expose `tools/lib/symbol/`",
        "the default-branch tree read surface does not currently expose the older `zigux/tests/phase8_kallsyms*.zig` companions",
        "Do not reopen this lane until the tree again carries explicit symbol-lane files on `master`.",
    ),
    WORKFLOW_PATH: (
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
    ),
    MAKEFILE_PATH: (
        "phase8-validate:",
        "scripts/zigux/check-phase8-help-kallsyms-packet.py",
    ),
}

FIXTURE_OVERRIDES = {
    VALIDATOR_PATH: "# fixture\n",
    HELP_KALLSYMS_PACKET_CHECKER_PATH: "# fixture\n",
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
        ("missing_docs_root", DOCS_ROOT_PATH),
        ("missing_review_checklist", REVIEW_CHECKLIST_PATH),
        ("missing_scripts_readme", SCRIPTS_README_PATH),
        ("missing_tests_readme", TESTS_README_PATH),
        ("missing_sequencing_note", SEQUENCING_PATH),
        ("missing_workflow", WORKFLOW_PATH),
        ("missing_makefile", MAKEFILE_PATH),
        ("missing_help_kallsyms_checker", HELP_KALLSYMS_PACKET_CHECKER_PATH),
    ]
    marker_cases = [
        (
            "docs_root_phase8_reminder_marker",
            DOCS_ROOT_PATH,
            "scripts/zigux/check-phase8-help-kallsyms-packet.py",
            "scripts/zigux/check-phase8-help-symbol-packet.py",
            f"{DOCS_ROOT_PATH}: Phase 8 notes - `Documentation/zigux/README.md`, `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase8.py`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` now keep the current shared reminder packet reviewable while `tools/lib/subcmd/`, `tools/lib/symbol/`, `tools/lib/bpf/zigux_segments/`, and the older `zigux/tests/phase8_*` shard files remain repo-reality gaps on current `master`.",
        ),
        (
            "review_checklist_symbol_gap_marker",
            REVIEW_CHECKLIST_PATH,
            "current `master` does not expose `tools/lib/symbol/`",
            "current `master` still exposes `tools/lib/symbol/`",
            f"{REVIEW_CHECKLIST_PATH}: current `master` does not expose `tools/lib/symbol/`",
        ),
        (
            "scripts_readme_phase8_packet_marker",
            SCRIPTS_README_PATH,
            "Phase 8 flow - current `master` keeps the shared Phase 8 reminder packet",
            "Phase 8 flow - current `master` keeps the old Phase 8 helper packet",
            f"{SCRIPTS_README_PATH}: Phase 8 flow - current `master` keeps the shared Phase 8 reminder packet",
        ),
        (
            "tests_readme_phase8_packet_marker",
            TESTS_README_PATH,
            "Phase 8 reminder packet",
            "Phase 8 helper packet",
            f"{TESTS_README_PATH}: Phase 8 reminder packet",
        ),
        (
            "sequencing_symbol_gap_marker",
            SEQUENCING_PATH,
            "the default-branch tree read surface does not currently expose `tools/lib/symbol/`",
            "the default-branch tree read surface still exposes `tools/lib/symbol/`",
            f"{SEQUENCING_PATH}: the default-branch tree read surface does not currently expose `tools/lib/symbol/`",
        ),
        (
            "workflow_phase8_validate_marker",
            WORKFLOW_PATH,
            "make -C zigux phase8-validate",
            "make -C zigux phase8-verify",
            f"{WORKFLOW_PATH}: make -C zigux phase8-validate",
        ),
        (
            "makefile_checker_marker",
            MAKEFILE_PATH,
            "scripts/zigux/check-phase8-help-kallsyms-packet.py",
            "scripts/zigux/check-phase8-help-symbol-packet.py",
            f"{MAKEFILE_PATH}: scripts/zigux/check-phase8-help-kallsyms-packet.py",
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
    parser = argparse.ArgumentParser(description="Validate the current shared Phase 8 reminder packet.")
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
