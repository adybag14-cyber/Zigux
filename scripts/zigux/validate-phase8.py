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
DOCS_ROOT_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
EXEC_CMD_PACKET_CHECKER_PATH = "scripts/zigux/check-phase8-exec-cmd-packet.py"
TESTS_ALIGNMENT_CHECKER_PATH = "scripts/zigux/check-phase8-tests-readme-alignment.py"
HELP_KALLSYMS_PACKET_CHECKER_PATH = "scripts/zigux/check-phase8-help-kallsyms-packet.py"
PERF_BUFFER_POLL_CHECKER_PATH = "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"
EXEC_CMD_SLICE_PATH = "Documentation/zigux/phase8-exec-cmd-slice.md"
HELP_SLICE_PATH = "Documentation/zigux/phase8-help-slice.md"
KALLSYMS_SLICE_PATH = "Documentation/zigux/phase8-kallsyms-slice.md"
EXEC_CMD_ZIG_PATH = "tools/lib/subcmd/exec-cmd.zig"
HELP_ZIG_PATH = "tools/lib/subcmd/help.zig"
KALLSYMS_ZIG_PATH = "tools/lib/symbol/kallsyms.zig"
EXEC_CMD_TEST_PATH = "zigux/tests/phase8_exec_cmd.zig"
EXEC_CMD_ONLY_BUILD_PATH = "zigux/tests/phase8_exec_cmd_only_build.zig"
HELP_TEST_PATH = "zigux/tests/phase8_help.zig"
HELP_ONLY_BUILD_PATH = "zigux/tests/phase8_help_only_build.zig"
HELP_KALLSYMS_ONLY_BUILD_PATH = "zigux/tests/phase8_help_kallsyms_only_build.zig"
KALLSYMS_TEST_PATH = "zigux/tests/phase8_kallsyms.zig"
KALLSYMS_ONLY_BUILD_PATH = "zigux/tests/phase8_kallsyms_only_build.zig"
CPU_MASK_SLICE_PATH = "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md"
LOGGING_SLICE_PATH = "Documentation/zigux/phase8-logging-slice.md"
FILE_PATH_HANDLE_BRIDGE_SLICE_PATH = "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"
FILE_PATH_HANDLE_BRIDGE_ZIG_PATH = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
FILE_PATH_HANDLE_BRIDGE_TEST_PATH = "zigux/tests/phase8_file_path_handle_bridge.zig"
FILE_PATH_HANDLE_BRIDGE_ONLY_BUILD_PATH = "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"
LIBBPF_SEGMENTS_MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
LIBBPF_SEGMENT_GATE_PATH = "scripts/zigux/check-phase8-libbpf-segment-gate.py"
LIBBPF_SHARD_ROUTES_PATH = "scripts/zigux/check-phase8-libbpf-shard-routes.py"

REQUIRED_FILES = [
    WORKFLOW_PATH,
    COMMAND_GAP_SURVEY_PATH,
    SEQUENCING_PATH,
    DOCS_ROOT_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    VALIDATOR_PATH,
    EXEC_CMD_PACKET_CHECKER_PATH,
    TESTS_ALIGNMENT_CHECKER_PATH,
    HELP_KALLSYMS_PACKET_CHECKER_PATH,
    PERF_BUFFER_POLL_CHECKER_PATH,
    EXEC_CMD_SLICE_PATH,
    HELP_SLICE_PATH,
    KALLSYMS_SLICE_PATH,
    EXEC_CMD_ZIG_PATH,
    HELP_ZIG_PATH,
    KALLSYMS_ZIG_PATH,
    EXEC_CMD_TEST_PATH,
    EXEC_CMD_ONLY_BUILD_PATH,
    HELP_TEST_PATH,
    HELP_ONLY_BUILD_PATH,
    HELP_KALLSYMS_ONLY_BUILD_PATH,
    KALLSYMS_TEST_PATH,
    KALLSYMS_ONLY_BUILD_PATH,
    CPU_MASK_SLICE_PATH,
    LOGGING_SLICE_PATH,
    FILE_PATH_HANDLE_BRIDGE_SLICE_PATH,
    FILE_PATH_HANDLE_BRIDGE_ZIG_PATH,
    FILE_PATH_HANDLE_BRIDGE_TEST_PATH,
    FILE_PATH_HANDLE_BRIDGE_ONLY_BUILD_PATH,
    PHASE8_BUILD_PATH,
    LIBBPF_SEGMENTS_MANIFEST_PATH,
    LIBBPF_SEGMENT_GATE_PATH,
    LIBBPF_SHARD_ROUTES_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
]

REQUIRED_MARKERS = {
    WORKFLOW_PATH: [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
        "Run focused Phase 8 exec-cmd tests",
        "make -C zigux phase8-exec-cmd-test",
    ],
    COMMAND_GAP_SURVEY_PATH: [
        "PHASE8_USERSPACE_KERNEL_BRIDGE_STATUS=parked_gap_packet_landed",
        "PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P8-L01",
        "PHASE8_USERSPACE_KERNEL_BRIDGE_SCOPE=runtime-command-and-environment-plumbing",
        "tools/lib/subcmd/exec-cmd.c",
        "tools/lib/subcmd/help.c",
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "python3 scripts/zigux/validate-phase8.py",
        "make -C zigux phase8-validate",
        "Current public default-branch tree readback shows the parked command and help",
        "Authenticated contents reads for some Phase 8 files are inconsistent from this",
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
    DOCS_ROOT_PATH: [
        "`Documentation/zigux/phase8-exec-cmd-slice.md`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "if the change touches the parked Phase 8 `exec-cmd` packet",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "helper-first, output-stable deferred-exec planning packet",
        "separate `kernel/workqueue.c` Phase 14 boundary-study target",
        "if the change touches the shared parked Phase 8 libbpf packet",
        "if the change touches the shared Phase 8 help-and-kallsyms packet",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/validate-phase8.py`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_build.zig`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-test`",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase8.py`",
        "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-shard-routes.py`",
        "`Documentation/zigux/phase8-exec-cmd-slice.md`",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`Documentation/zigux/phase8-logging-slice.md`",
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`make -C zigux phase8-validate`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-test`",
    ],
    TESTS_README_PATH: [
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
        "`make -C zigux phase8`",
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-cpu-mask-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-test`",
    ],
    MAKEFILE_PATH: [
        "phase8-validate:",
        "phase8-exec-cmd-test:",
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
        "phase8-test:",
        "phase8: phase8-validate",
    ],
    EXEC_CMD_PACKET_CHECKER_PATH: [
        "PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass",
        "phase8 exec-cmd packet ok",
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        "zigux/tests/phase8_exec_cmd.zig",
        "tools/lib/subcmd/exec-cmd.zig",
    ],
    EXEC_CMD_SLICE_PATH: [
        "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        "pure deferred `execv_cmd()`-style handoff planning",
        "pure `execl_cmd()`-style argv collection and handoff planning only",
        "make -C zigux phase8-validate",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
    ],
    EXEC_CMD_TEST_PATH: [
        'test "phase 8 exec-cmd slice note keeps the helper-vs-phase ownership boundary explicit" {',
        'test "phase 8 exec-cmd checklist hook keeps the parked deferred-exec packet explicit" {',
        'test "phase 8 exec-cmd workflow keeps the focused replay ahead of sibling help shards" {',
        'test "phase 8 exec-cmd docs root summary keeps the focused replay route explicit" {',
        'test "phase 8 exec-cmd scripts root summary keeps the focused replay route explicit" {',
        'test "phase 8 exec-cmd tests root summary keeps the focused replay route explicit" {',
    ],
    FILE_PATH_HANDLE_BRIDGE_SLICE_PATH: [
        "PHASE8_SLICE=libbpf-file-path-handle-bridge",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`zig build test --build-file zigux/tests/phase8_build.zig --summary all`",
        "`make -C zigux phase8-test`",
        "planTokenPreparation()",
        "no direct procfs reads",
        "no actual bpffs opens or `bpf_obj_get()` reopen calls",
        "no fd duplication or `F_DUPFD_CLOEXEC` handling",
        "no token materialization or handle transfer",
    ],
    FILE_PATH_HANDLE_BRIDGE_ZIG_PATH: [
        "mapReuseObservationFromFdinfo",
        "resolveReusePinnedMapAttempt",
        "planTokenPreparation",
    ],
    FILE_PATH_HANDLE_BRIDGE_TEST_PATH: [
        'test "phase 8 file-path handle bridge helper stays wired into its focused Phase 8 build shard" {',
        'test "phase 8 file-path handle bridge helper stays wired into the shared Phase 8 build shard" {',
        'test "phase 8 file-path handle bridge helper keeps fdinfo observations reusable for planning-only compatibility" {',
        'test "phase 8 file-path handle bridge helper keeps planning-only reopen attempts explicit" {',
        'test "phase 8 file-path-handle bridge keeps token acquisition ownership planning explicit" {',
        'try expectContains(note, "no actual bpffs opens or `bpf_obj_get()` reopen calls");',
        'try expectContains(note, "no token materialization or handle transfer");',
        'try expectContains(survey, "fd close or ownership semantics");',
    ],
    FILE_PATH_HANDLE_BRIDGE_ONLY_BUILD_PATH: [
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge.zig",
        "phase8-file-path-handle-bridge-tests",
    ],
    PHASE8_BUILD_PATH: [
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge.zig",
        "phase8-file-path-handle-bridge-tests",
    ],
    LIBBPF_SEGMENTS_MANIFEST_PATH: [
        '"slug": "fdinfo-map-info-helpers", "status": "starter_landed"',
        '"slug": "map-reuse-compatibility", "status": "starter_landed"',
        '"slug": "file-path-and-handle-bridge", "status": "deferred_high_risk"',
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
    EXEC_CMD_PACKET_CHECKER_PATH: "\n".join(REQUIRED_MARKERS[EXEC_CMD_PACKET_CHECKER_PATH]) + "\n",
    TESTS_ALIGNMENT_CHECKER_PATH: "# fixture\n",
    HELP_KALLSYMS_PACKET_CHECKER_PATH: "# fixture\n",
    PERF_BUFFER_POLL_CHECKER_PATH: "# fixture\n",
    DOCS_ROOT_PATH: "\n".join(REQUIRED_MARKERS[DOCS_ROOT_PATH]) + "\n",
    EXEC_CMD_SLICE_PATH: "\n".join(REQUIRED_MARKERS[EXEC_CMD_SLICE_PATH]) + "\n",
    HELP_SLICE_PATH: "# fixture\n",
    KALLSYMS_SLICE_PATH: "# fixture\n",
    LOGGING_SLICE_PATH: "# fixture\n",
    FILE_PATH_HANDLE_BRIDGE_SLICE_PATH: "\n".join(REQUIRED_MARKERS[FILE_PATH_HANDLE_BRIDGE_SLICE_PATH]) + "\n",
    FILE_PATH_HANDLE_BRIDGE_ZIG_PATH: "\n".join(REQUIRED_MARKERS[FILE_PATH_HANDLE_BRIDGE_ZIG_PATH]) + "\n",
    FILE_PATH_HANDLE_BRIDGE_TEST_PATH: "\n".join(REQUIRED_MARKERS[FILE_PATH_HANDLE_BRIDGE_TEST_PATH]) + "\n",
    FILE_PATH_HANDLE_BRIDGE_ONLY_BUILD_PATH: "\n".join(REQUIRED_MARKERS[FILE_PATH_HANDLE_BRIDGE_ONLY_BUILD_PATH]) + "\n",
    PHASE8_BUILD_PATH: "\n".join(REQUIRED_MARKERS[PHASE8_BUILD_PATH]) + "\n",
    LIBBPF_SEGMENTS_MANIFEST_PATH: "\n".join(REQUIRED_MARKERS[LIBBPF_SEGMENTS_MANIFEST_PATH]) + "\n",
    EXEC_CMD_ZIG_PATH: "// fixture\n",
    HELP_ZIG_PATH: "// fixture\n",
    KALLSYMS_ZIG_PATH: "// fixture\n",
    EXEC_CMD_TEST_PATH: "\n".join(REQUIRED_MARKERS[EXEC_CMD_TEST_PATH]) + "\n",
    EXEC_CMD_ONLY_BUILD_PATH: "// fixture\n",
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
        ("missing_exec_cmd_packet_checker", EXEC_CMD_PACKET_CHECKER_PATH),
        ("missing_tests_alignment_checker", TESTS_ALIGNMENT_CHECKER_PATH),
        ("missing_help_kallsyms_packet_checker", HELP_KALLSYMS_PACKET_CHECKER_PATH),
        ("missing_perf_buffer_poll_checker", PERF_BUFFER_POLL_CHECKER_PATH),
        ("missing_docs_root", DOCS_ROOT_PATH),
        ("missing_exec_cmd_slice_note", EXEC_CMD_SLICE_PATH),
        ("missing_help_slice_note", HELP_SLICE_PATH),
        ("missing_kallsyms_slice_note", KALLSYMS_SLICE_PATH),
        ("missing_exec_cmd_source", EXEC_CMD_ZIG_PATH),
        ("missing_help_source", HELP_ZIG_PATH),
        ("missing_kallsyms_source", KALLSYMS_ZIG_PATH),
        ("missing_exec_cmd_test", EXEC_CMD_TEST_PATH),
        ("missing_exec_cmd_only_build", EXEC_CMD_ONLY_BUILD_PATH),
        ("missing_help_test", HELP_TEST_PATH),
        ("missing_help_only_build", HELP_ONLY_BUILD_PATH),
        ("missing_help_kallsyms_only_build", HELP_KALLSYMS_ONLY_BUILD_PATH),
        ("missing_kallsyms_test", KALLSYMS_TEST_PATH),
        ("missing_kallsyms_only_build", KALLSYMS_ONLY_BUILD_PATH),
        ("missing_cpu_mask_slice_note", CPU_MASK_SLICE_PATH),
        ("missing_logging_slice_note", LOGGING_SLICE_PATH),
        ("missing_file_path_handle_bridge_slice_note", FILE_PATH_HANDLE_BRIDGE_SLICE_PATH),
        ("missing_file_path_handle_bridge_source", FILE_PATH_HANDLE_BRIDGE_ZIG_PATH),
        ("missing_file_path_handle_bridge_test", FILE_PATH_HANDLE_BRIDGE_TEST_PATH),
        ("missing_file_path_handle_bridge_only_build", FILE_PATH_HANDLE_BRIDGE_ONLY_BUILD_PATH),
        ("missing_phase8_shared_build", PHASE8_BUILD_PATH),
        ("missing_libbpf_segments_manifest", LIBBPF_SEGMENTS_MANIFEST_PATH),
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
            "workflow_exec_cmd_route_marker",
            WORKFLOW_PATH,
            "make -C zigux phase8-exec-cmd-test",
            "make -C zigux phase8-exec-cmd-replay",
            f"{WORKFLOW_PATH}: make -C zigux phase8-exec-cmd-test",
        ),
        (
            "command_gap_lane_key_marker",
            COMMAND_GAP_SURVEY_PATH,
            "PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P8-L01",
            "PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P8-L02",
            f"{COMMAND_GAP_SURVEY_PATH}: PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P8-L01",
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
            "docs_root_exec_cmd_route_marker",
            DOCS_ROOT_PATH,
            "`make -C zigux phase8-exec-cmd-test`",
            "`make -C zigux phase8-exec-cmd-replay`",
            f"{DOCS_ROOT_PATH}: `make -C zigux phase8-exec-cmd-test`",
        ),
        (
            "review_checklist_exec_cmd_packet_marker",
            REVIEW_CHECKLIST_PATH,
            "if the change touches the parked Phase 8 `exec-cmd` packet",
            "if the change touches the Phase 8 exec packet",
            f"{REVIEW_CHECKLIST_PATH}: if the change touches the parked Phase 8 `exec-cmd` packet",
        ),
        (
            "review_checklist_bridge_slice_marker",
            REVIEW_CHECKLIST_PATH,
            "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
            "`Documentation/zigux/phase8-file-path-bridge-slice.md`",
            f"{REVIEW_CHECKLIST_PATH}: `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        ),
        (
            "scripts_readme_exec_cmd_checker_marker",
            SCRIPTS_README_PATH,
            "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
            "`scripts/zigux/check-phase8-exec-cmd.py`",
            f"{SCRIPTS_README_PATH}: `scripts/zigux/check-phase8-exec-cmd-packet.py`",
        ),
        (
            "scripts_readme_bridge_only_build_marker",
            SCRIPTS_README_PATH,
            "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
            "`zigux/tests/phase8_file_path_bridge_only_build.zig`",
            f"{SCRIPTS_README_PATH}: `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        ),
        (
            "scripts_readme_logging_slice_marker",
            SCRIPTS_README_PATH,
            "`Documentation/zigux/phase8-logging-slice.md`",
            "`Documentation/zigux/phase8-libbpf-logging-slice.md`",
            f"{SCRIPTS_README_PATH}: `Documentation/zigux/phase8-logging-slice.md`",
        ),
        (
            "tests_readme_exec_cmd_route_marker",
            TESTS_README_PATH,
            "`make -C zigux phase8-exec-cmd-test`",
            "`make -C zigux phase8-exec-cmd-replay`",
            f"{TESTS_README_PATH}: `make -C zigux phase8-exec-cmd-test`",
        ),
        (
            "tests_readme_bridge_only_build_marker",
            TESTS_README_PATH,
            "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
            "`zigux/tests/phase8_file_path_bridge_only_build.zig`",
            f"{TESTS_README_PATH}: `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        ),
        (
            "makefile_exec_cmd_route",
            MAKEFILE_PATH,
            "phase8-exec-cmd-test:",
            "phase8-exec-cmd-replay:",
            f"{MAKEFILE_PATH}: phase8-exec-cmd-test:",
        ),
        (
            "makefile_phase8_test_route",
            MAKEFILE_PATH,
            "phase8-test:",
            "phase8-shared-test:",
            f"{MAKEFILE_PATH}: phase8-test:",
        ),
        (
            "exec_cmd_packet_checker_self_test_marker",
            EXEC_CMD_PACKET_CHECKER_PATH,
            "PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass",
            "PHASE8_EXEC_CMD_PACKET_SELF_TEST=broken",
            f"{EXEC_CMD_PACKET_CHECKER_PATH}: PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass",
        ),
        (
            "exec_cmd_slice_marker",
            EXEC_CMD_SLICE_PATH,
            "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
            "PHASE8_SLICE=exec-cmd-starter-packet",
            f"{EXEC_CMD_SLICE_PATH}: PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        ),
        (
            "bridge_slice_shared_route_marker",
            FILE_PATH_HANDLE_BRIDGE_SLICE_PATH,
            "`make -C zigux phase8-test`",
            "`make -C zigux phase8-shared-test`",
            f"{FILE_PATH_HANDLE_BRIDGE_SLICE_PATH}: `make -C zigux phase8-test`",
        ),
        (
            "bridge_slice_resource_boundary_marker",
            FILE_PATH_HANDLE_BRIDGE_SLICE_PATH,
            "no actual bpffs opens or `bpf_obj_get()` reopen calls",
            "no actual bpffs opens",
            f"{FILE_PATH_HANDLE_BRIDGE_SLICE_PATH}: no actual bpffs opens or `bpf_obj_get()` reopen calls",
        ),
        (
            "bridge_source_token_planning_marker",
            FILE_PATH_HANDLE_BRIDGE_ZIG_PATH,
            "planTokenPreparation",
            "planTokenBridgePreparation",
            f"{FILE_PATH_HANDLE_BRIDGE_ZIG_PATH}: planTokenPreparation",
        ),
        (
            "bridge_test_shared_build_marker",
            FILE_PATH_HANDLE_BRIDGE_TEST_PATH,
            'test "phase 8 file-path handle bridge helper stays wired into the shared Phase 8 build shard" {',
            'test "phase 8 file-path handle bridge shared build drifted" {',
            f'{FILE_PATH_HANDLE_BRIDGE_TEST_PATH}: test "phase 8 file-path handle bridge helper stays wired into the shared Phase 8 build shard" {{',
        ),
        (
            "bridge_test_ownership_marker",
            FILE_PATH_HANDLE_BRIDGE_TEST_PATH,
            'test "phase 8 file-path-handle bridge keeps token acquisition ownership planning explicit" {',
            'test "phase 8 file-path-handle bridge ownership planning drifted" {',
            f'{FILE_PATH_HANDLE_BRIDGE_TEST_PATH}: test "phase 8 file-path-handle bridge keeps token acquisition ownership planning explicit" {{',
        ),
        (
            "bridge_only_build_target_marker",
            FILE_PATH_HANDLE_BRIDGE_ONLY_BUILD_PATH,
            "phase8-file-path-handle-bridge-tests",
            "phase8-file-path-bridge-tests",
            f"{FILE_PATH_HANDLE_BRIDGE_ONLY_BUILD_PATH}: phase8-file-path-handle-bridge-tests",
        ),
        (
            "phase8_build_bridge_target_marker",
            PHASE8_BUILD_PATH,
            "phase8-file-path-handle-bridge-tests",
            "phase8-file-path-bridge-tests",
            f"{PHASE8_BUILD_PATH}: phase8-file-path-handle-bridge-tests",
        ),
        (
            "manifest_deferred_boundary_marker",
            LIBBPF_SEGMENTS_MANIFEST_PATH,
            '"slug": "file-path-and-handle-bridge", "status": "deferred_high_risk"',
            '"slug": "file-path-and-handle-bridge", "status": "starter_landed"',
            f'{LIBBPF_SEGMENTS_MANIFEST_PATH}: "slug": "file-path-and-handle-bridge", "status": "deferred_high_risk"',
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
