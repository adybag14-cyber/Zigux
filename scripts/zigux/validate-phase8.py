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
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
TESTS_ALIGNMENT_CHECKER_PATH = "scripts/zigux/check-phase8-tests-readme-alignment.py"
HELP_KALLSYMS_PACKET_CHECKER_PATH = "scripts/zigux/check-phase8-help-kallsyms-packet.py"
PERF_BUFFER_POLL_CHECKER_PATH = "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"
HELP_SLICE_PATH = "Documentation/zigux/phase8-help-slice.md"
KALLSYMS_SLICE_PATH = "Documentation/zigux/phase8-kallsyms-slice.md"
HELP_ZIG_PATH = "tools/lib/subcmd/help.zig"
KALLSYMS_ZIG_PATH = "tools/lib/symbol/kallsyms.zig"
HELP_TEST_PATH = "zigux/tests/phase8_help.zig"
HELP_ONLY_BUILD_PATH = "zigux/tests/phase8_help_only_build.zig"
HELP_KALLSYMS_ONLY_BUILD_PATH = "zigux/tests/phase8_help_kallsyms_only_build.zig"
KALLSYMS_TEST_PATH = "zigux/tests/phase8_kallsyms.zig"
KALLSYMS_ONLY_BUILD_PATH = "zigux/tests/phase8_kallsyms_only_build.zig"
CPU_MASK_SLICE_PATH = "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md"
LIBBPF_SEGMENT_GATE_PATH = "scripts/zigux/check-phase8-libbpf-segment-gate.py"
LIBBPF_SHARD_ROUTES_PATH = "scripts/zigux/check-phase8-libbpf-shard-routes.py"

REQUIRED_FILES = [
    WORKFLOW_PATH,
    COMMAND_GAP_SURVEY_PATH,
    SEQUENCING_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    VALIDATOR_PATH,
    TESTS_ALIGNMENT_CHECKER_PATH,
    HELP_KALLSYMS_PACKET_CHECKER_PATH,
    PERF_BUFFER_POLL_CHECKER_PATH,
    HELP_SLICE_PATH,
    KALLSYMS_SLICE_PATH,
    HELP_ZIG_PATH,
    KALLSYMS_ZIG_PATH,
    HELP_TEST_PATH,
    HELP_ONLY_BUILD_PATH,
    HELP_KALLSYMS_ONLY_BUILD_PATH,
    KALLSYMS_TEST_PATH,
    KALLSYMS_ONLY_BUILD_PATH,
    CPU_MASK_SLICE_PATH,
    LIBBPF_SEGMENT_GATE_PATH,
    LIBBPF_SHARD_ROUTES_PATH,
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
        "### 1. Command lane",
        "### 4. Shared wording lane",
        "runtime readback caution: authenticated contents reads for some Phase 8 files are inconsistent from this environment, so public default-branch tree evidence plus exact readable blob content should win over older absent-file assumptions",
        "The next honest shared-surface reopen cue now starts with `Documentation/zigux/README.md`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "if the change touches the shared parked Phase 8 libbpf packet",
        "if the change touches the shared Phase 8 help-and-kallsyms packet",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/validate-phase8.py`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase8.py`",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-shard-routes.py`",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
        "`make -C zigux phase8-validate`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ],
    TESTS_README_PATH: [
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
    ],
    MAKEFILE_PATH: [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-help-kallsyms-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-help-kallsyms-packet.py",
        "phase8-help-test:",
        "phase8-help-kallsyms-test:",
        "phase8-kallsyms-test:",
        "phase8-cpu-mask-test:",
        "phase8-file-path-handle-bridge-test:",
        "phase8-libbpf-segments-test:",
        "phase8-perf-buffer-poll-test:",
        "phase8: phase8-validate",
    ],
    CPU_MASK_SLICE_PATH: [
        "PHASE8_SLICE=libbpf-cpu-mask-starter",
        "repeated comma and newline delimiter skipping for sysfs-style CPU mask strings",
        "anchor-faithful acceptance of carriage returns, tabs, and other ASCII whitespace that `parse_cpu_mask_str()` reaches through `sscanf()`-driven range parsing",
        "direct and chunked carriage-return or tab-delimited fragments that must keep matching the live libbpf helper",
        "deferred `perf-buffer-online-cpu-routing` setup or the broader interrupt-routing-sensitive timing boundary",
    ],
    LIBBPF_SEGMENT_GATE_PATH: [
        "PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass",
        "PHASE8_LIBBPF_SEGMENT_GATE=pass",
        "parked_wording_packet",
    ],
    LIBBPF_SHARD_ROUTES_PATH: [
        "PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass",
        "PHASE8_LIBBPF_SHARD_ROUTES=pass",
        "### 4. Shared wording lane",
    ],
}

FIXTURE_OVERRIDES = {
    VALIDATOR_PATH: "# fixture\n",
    TESTS_ALIGNMENT_CHECKER_PATH: "# fixture\n",
    HELP_KALLSYMS_PACKET_CHECKER_PATH: "# fixture\n",
    PERF_BUFFER_POLL_CHECKER_PATH: "# fixture\n",
    HELP_SLICE_PATH: "# fixture\n",
    KALLSYMS_SLICE_PATH: "# fixture\n",
    HELP_ZIG_PATH: "// fixture\n",
    KALLSYMS_ZIG_PATH: "// fixture\n",
    HELP_TEST_PATH: "// fixture\n",
    HELP_ONLY_BUILD_PATH: "// fixture\n",
    HELP_KALLSYMS_ONLY_BUILD_PATH: "// fixture\n",
    KALLSYMS_TEST_PATH: "// fixture\n",
    KALLSYMS_ONLY_BUILD_PATH: "// fixture\n",
    LIBBPF_SEGMENT_GATE_PATH: "\n".join(REQUIRED_MARKERS[LIBBPF_SEGMENT_GATE_PATH]) + "\n",
    LIBBPF_SHARD_ROUTES_PATH: "\n".join(REQUIRED_MARKERS[LIBBPF_SHARD_ROUTES_PATH]) + "\n",
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
        ("missing_validator", VALIDATOR_PATH),
        ("missing_tests_alignment_checker", TESTS_ALIGNMENT_CHECKER_PATH),
        ("missing_help_kallsyms_packet_checker", HELP_KALLSYMS_PACKET_CHECKER_PATH),
        ("missing_perf_buffer_poll_checker", PERF_BUFFER_POLL_CHECKER_PATH),
        ("missing_help_slice_note", HELP_SLICE_PATH),
        ("missing_kallsyms_slice_note", KALLSYMS_SLICE_PATH),
        ("missing_help_source", HELP_ZIG_PATH),
        ("missing_kallsyms_source", KALLSYMS_ZIG_PATH),
        ("missing_help_test", HELP_TEST_PATH),
        ("missing_help_only_build", HELP_ONLY_BUILD_PATH),
        ("missing_help_kallsyms_only_build", HELP_KALLSYMS_ONLY_BUILD_PATH),
        ("missing_kallsyms_test", KALLSYMS_TEST_PATH),
        ("missing_kallsyms_only_build", KALLSYMS_ONLY_BUILD_PATH),
        ("missing_cpu_mask_slice_note", CPU_MASK_SLICE_PATH),
        ("missing_libbpf_segment_gate_checker", LIBBPF_SEGMENT_GATE_PATH),
        ("missing_libbpf_shard_routes_checker", LIBBPF_SHARD_ROUTES_PATH),
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
            "sequencing_command_gap_marker",
            SEQUENCING_PATH,
            "### 1. Command lane",
            "### 1. Command packet",
            f"{SEQUENCING_PATH}: ### 1. Command lane",
        ),
        (
            "review_checklist_help_checker_marker",
            REVIEW_CHECKLIST_PATH,
            "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
            "`scripts/zigux/check-phase8-help-kallsyms.py`",
            f"{REVIEW_CHECKLIST_PATH}: `scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        ),
        (
            "review_checklist_shared_help_route_marker",
            REVIEW_CHECKLIST_PATH,
            "`make -C zigux phase8-help-kallsyms-test`",
            "`make -C zigux phase8-help-shared-test`",
            f"{REVIEW_CHECKLIST_PATH}: `make -C zigux phase8-help-kallsyms-test`",
        ),
        (
            "review_checklist_kallsyms_only_build_marker",
            REVIEW_CHECKLIST_PATH,
            "`zigux/tests/phase8_kallsyms_only_build.zig`",
            "`zigux/tests/phase8_kallsyms_review_build.zig`",
            f"{REVIEW_CHECKLIST_PATH}: `zigux/tests/phase8_kallsyms_only_build.zig`",
        ),
        (
            "scripts_readme_help_checker_marker",
            SCRIPTS_README_PATH,
            "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
            "`scripts/zigux/check-phase8-help-kallsyms.py`",
            f"{SCRIPTS_README_PATH}: `scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        ),
        (
            "scripts_readme_help_route_marker",
            SCRIPTS_README_PATH,
            "`make -C zigux phase8-help-test`",
            "`make -C zigux phase8-help-route`",
            f"{SCRIPTS_README_PATH}: `make -C zigux phase8-help-test`",
        ),
        (
            "tests_readme_help_packet_marker",
            TESTS_README_PATH,
            "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
            "`zigux/tests/phase8_help_symbol_only_build.zig`",
            f"{TESTS_README_PATH}: `zigux/tests/phase8_help_kallsyms_only_build.zig`",
        ),
        (
            "tests_readme_kallsyms_only_build_marker",
            TESTS_README_PATH,
            "`zigux/tests/phase8_kallsyms_only_build.zig`",
            "`zigux/tests/phase8_kallsyms_review_build.zig`",
            f"{TESTS_README_PATH}: `zigux/tests/phase8_kallsyms_only_build.zig`",
        ),
        (
            "tests_readme_help_checker_marker",
            TESTS_README_PATH,
            "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
            "`scripts/zigux/check-phase8-help-kallsyms.py`",
            f"{TESTS_README_PATH}: `scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        ),
        (
            "makefile_help_checker_self_test_marker",
            MAKEFILE_PATH,
            "scripts/zigux/check-phase8-help-kallsyms-packet.py --self-test",
            "scripts/zigux/check-phase8-help-kallsyms-surface.py --self-test",
            f"{MAKEFILE_PATH}: scripts/zigux/check-phase8-help-kallsyms-packet.py --self-test",
        ),
        (
            "makefile_help_route",
            MAKEFILE_PATH,
            "phase8-help-test:",
            "phase8-help-route:",
            f"{MAKEFILE_PATH}: phase8-help-test:",
        ),
        (
            "makefile_shared_help_route",
            MAKEFILE_PATH,
            "phase8-help-kallsyms-test:",
            "phase8-help-symbol-test:",
            f"{MAKEFILE_PATH}: phase8-help-kallsyms-test:",
        ),
        (
            "cpu_mask_slice_whitespace_marker",
            CPU_MASK_SLICE_PATH,
            "anchor-faithful acceptance of carriage returns, tabs, and other ASCII whitespace that `parse_cpu_mask_str()` reaches through `sscanf()`-driven range parsing",
            "anchor-faithful acceptance of tabs only",
            f"{CPU_MASK_SLICE_PATH}: anchor-faithful acceptance of carriage returns, tabs, and other ASCII whitespace that `parse_cpu_mask_str()` reaches through `sscanf()`-driven range parsing",
        ),
        (
            "libbpf_segment_gate_mode_marker",
            LIBBPF_SEGMENT_GATE_PATH,
            "parked_wording_packet",
            "legacy_only_packet",
            f"{LIBBPF_SEGMENT_GATE_PATH}: parked_wording_packet",
        ),
        (
            "libbpf_shard_routes_heading_marker",
            LIBBPF_SHARD_ROUTES_PATH,
            "### 4. Shared wording lane",
            "### 4. Shared wording packet",
            f"{LIBBPF_SHARD_ROUTES_PATH}: ### 4. Shared wording lane",
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
