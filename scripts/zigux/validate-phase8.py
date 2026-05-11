#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

COMMAND_GAP_SURVEY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
SEQUENCING_PATH = "Documentation/zigux/phase8-tooling-lane-sequencing.md"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
TESTS_ALIGNMENT_CHECKER_PATH = "scripts/zigux/check-phase8-tests-readme-alignment.py"
PERF_BUFFER_POLL_CHECKER_PATH = "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"

REQUIRED_FILES = [
    WORKFLOW_PATH,
    COMMAND_GAP_SURVEY_PATH,
    SEQUENCING_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    "scripts/zigux/validate-phase8.py",
    TESTS_ALIGNMENT_CHECKER_PATH,
    PERF_BUFFER_POLL_CHECKER_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
]

REQUIRED_MARKERS = {
    WORKFLOW_PATH: [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
    ],
    COMMAND_GAP_SURVEY_PATH: [
        "PHASE8_USERSPACE_KERNEL_BRIDGE_STATUS=parked_gap_packet_landed",
        "PHASE8_USERSPACE_KERNEL_BRIDGE_SCOPE=runtime-command-and-environment-plumbing",
        "tools/lib/subcmd/exec-cmd.c",
        "tools/lib/subcmd/help.c",
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "python3 scripts/zigux/validate-phase8.py",
        "make -C zigux phase8-validate",
        "Current `master` does not currently expose:",
    ],
    SEQUENCING_PATH: [
        "PHASE8_STATUS=parked",
        "PHASE8_SEQUENCE=tooling-lane-anti-overlap",
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        "scripts/zigux/validate-phase8.py",
        "zigux/tests/README.md",
        "zigux/Makefile",
        "### 4. Shared wording lane",
        "The next honest reopen cue still starts at the docs-root Phase 8 summary in `Documentation/zigux/README.md`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "if the change touches the shared parked Phase 8 libbpf packet",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/validate-phase8.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase8.py`",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-validate`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ],
    TESTS_README_PATH: [
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ],
    MAKEFILE_PATH: [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "phase8-cpu-mask-test:",
        "phase8-file-path-handle-bridge-test:",
        "phase8-libbpf-segments-test:",
        "phase8-perf-buffer-poll-test:",
        "phase8: phase8-validate",
    ],
}

FIXTURE_OVERRIDES = {
    "scripts/zigux/validate-phase8.py": "# fixture\n",
    TESTS_ALIGNMENT_CHECKER_PATH: "# fixture\n",
    PERF_BUFFER_POLL_CHECKER_PATH: "# fixture\n",
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
        ("missing_tests_alignment_checker", TESTS_ALIGNMENT_CHECKER_PATH),
        ("missing_perf_buffer_poll_checker", PERF_BUFFER_POLL_CHECKER_PATH),
        ("missing_command_gap_survey", COMMAND_GAP_SURVEY_PATH),
        ("missing_lane_note", SEQUENCING_PATH),
        ("missing_makefile", MAKEFILE_PATH),
    ]
    marker_cases = [
        (
            "workflow_phase8_validate_marker",
            WORKFLOW_PATH,
            "make -C zigux phase8-validate",
            "make -C zigux phase8-verify",
            f"{WORKFLOW_PATH}: make -C zigux phase8-validate",
        ),
        (
            "command_gap_validation_marker",
            COMMAND_GAP_SURVEY_PATH,
            "python3 scripts/zigux/validate-phase8.py",
            "python3 scripts/zigux/validate-phase8-lane.py",
            f"{COMMAND_GAP_SURVEY_PATH}: python3 scripts/zigux/validate-phase8.py",
        ),
        (
            "sequencing_shared_wording_lane_marker",
            SEQUENCING_PATH,
            "### 4. Shared wording lane",
            "### 4. Shared lane",
            f"{SEQUENCING_PATH}: ### 4. Shared wording lane",
        ),
        (
            "review_checklist_perf_checker_marker",
            REVIEW_CHECKLIST_PATH,
            "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
            "`scripts/zigux/check-phase8-perf-poll-gate.py`",
            f"{REVIEW_CHECKLIST_PATH}: `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        ),
        (
            "scripts_readme_tests_alignment_marker",
            SCRIPTS_README_PATH,
            "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
            "`scripts/zigux/check-phase8-tests-alignment.py`",
            f"{SCRIPTS_README_PATH}: `scripts/zigux/check-phase8-tests-readme-alignment.py`",
        ),
        (
            "tests_readme_perf_route_marker",
            TESTS_README_PATH,
            "`make -C zigux phase8-perf-buffer-poll-test`",
            "`make -C zigux phase8-perf-buffer-test`",
            f"{TESTS_README_PATH}: `make -C zigux phase8-perf-buffer-poll-test`",
        ),
        (
            "makefile_cpu_mask_route",
            MAKEFILE_PATH,
            "phase8-cpu-mask-test:",
            "phase8-cpu-mask-route:",
            f"{MAKEFILE_PATH}: phase8-cpu-mask-test:",
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
