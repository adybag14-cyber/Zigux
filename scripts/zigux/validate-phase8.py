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
BOUNDARY_SURVEY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
TESTS_README_ALIGNMENT_CHECKER_PATH = "scripts/zigux/check-phase8-tests-readme-alignment.py"
EXEC_CMD_PACKET_CHECKER_PATH = "scripts/zigux/check-phase8-exec-cmd-packet.py"
HELP_KALLSYMS_PACKET_CHECKER_PATH = "scripts/zigux/check-phase8-help-kallsyms-packet.py"
PERF_BUFFER_POLL_GATE_PATH = "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"
LIBBPF_SEGMENT_GATE_PATH = "scripts/zigux/check-phase8-libbpf-segment-gate.py"
LIBBPF_SHARD_ROUTES_PATH = "scripts/zigux/check-phase8-libbpf-shard-routes.py"
LIBBPF_SEGMENT_SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
LIBBPF_MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
BRIDGE_SLICE_PATH = "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"
BRIDGE_HELPER_PATH = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
BRIDGE_TEST_PATH = "zigux/tests/phase8_file_path_handle_bridge.zig"
BRIDGE_BUILD_PATH = "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"

REQUIRED_FILES = (
    DOCS_ROOT_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    SEQUENCING_PATH,
    BOUNDARY_SURVEY_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    VALIDATOR_PATH,
    TESTS_README_ALIGNMENT_CHECKER_PATH,
    EXEC_CMD_PACKET_CHECKER_PATH,
    HELP_KALLSYMS_PACKET_CHECKER_PATH,
    PERF_BUFFER_POLL_GATE_PATH,
    LIBBPF_SEGMENT_GATE_PATH,
    LIBBPF_SHARD_ROUTES_PATH,
    LIBBPF_SEGMENT_SURVEY_PATH,
    LIBBPF_MANIFEST_PATH,
    BRIDGE_SLICE_PATH,
    BRIDGE_HELPER_PATH,
    BRIDGE_TEST_PATH,
    BRIDGE_BUILD_PATH,
    PHASE8_BUILD_PATH,
)

REQUIRED_MARKERS = {
    DOCS_ROOT_PATH: (
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-shard-routes.py`",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`zigux/tests/phase8_pin_path.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 8 help-and-kallsyms packet",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "if the change touches the shared Phase 8 libbpf packet",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`scripts/zigux/validate-phase8.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-shard-routes.py`",
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`tools/lib/bpf/zigux_segments/manifest.json`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
    ),
    SCRIPTS_README_PATH: (
        "scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-tests-readme-alignment.py",
        "scripts/zigux/check-phase8-exec-cmd-packet.py",
        "scripts/zigux/check-phase8-help-kallsyms-packet.py",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "make -C zigux phase8-exec-cmd-test",
        "make -C zigux phase8-help-kallsyms-test",
        "make -C zigux phase8-kallsyms-test",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-validate",
    ),
    TESTS_README_PATH: (
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
    ),
    SEQUENCING_PATH: (
        "### 2. Symbol lane",
        "Use this lane for bounded `kallsyms` reminder, compile, or packet-truthfulness work only.",
        "current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`",
        "Exact 2026-05-13 readback closes the earlier docs-root reopen cue instead of reopening it",
        "`Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary",
        "Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.",
    ),
    BOUNDARY_SURVEY_PATH: (
        "PHASE8_USERSPACE_KERNEL_BRIDGE_SHARED_NOTE=Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "`python3 scripts/zigux/validate-phase8.py`",
        "`make -C zigux phase8-validate`",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
    ),
    WORKFLOW_PATH: (
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
    ),
    MAKEFILE_PATH: (
        "phase8-validate:",
        "scripts/zigux/check-phase8-tests-readme-alignment.py",
        "scripts/zigux/check-phase8-exec-cmd-packet.py",
        "scripts/zigux/check-phase8-help-kallsyms-packet.py",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "phase8-help-kallsyms-test",
        "phase8-kallsyms-test",
        "phase8-file-path-handle-bridge-test",
        "scripts/zigux/validate-phase8.py",
    ),
    LIBBPF_SEGMENT_SURVEY_PATH: (
        "`tools/lib/bpf/zigux_segments/manifest.json`",
        "The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.",
        "The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.",
        "The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.",
    ),
    LIBBPF_MANIFEST_PATH: (
        '"slug": "fdinfo-map-info-helpers", "status": "starter_landed"',
        '"slug": "map-reuse-compatibility", "status": "starter_landed"',
        '"slug": "file-path-and-handle-bridge", "status": "deferred_high_risk"',
        '"slug": "perf-buffer-poll-bookkeeping", "status": "starter_landed"',
    ),
    BRIDGE_SLICE_PATH: (
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_build.zig`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`make -C zigux phase8-test`",
        "`zig build test --build-file zigux/tests/phase8_build.zig --summary all`",
    ),
    BRIDGE_HELPER_PATH: (
        "buildProcFdinfoPath(",
        "mapReuseObservationFromFdinfo(",
        "resolveReusePinnedMapAttempt(",
        "planTokenPreparation(",
    ),
    BRIDGE_TEST_PATH: (
        "\"Documentation/zigux/phase8-file-path-handle-bridge-slice.md\"",
        "\"zigux/tests/phase8_file_path_handle_bridge_only_build.zig\"",
        "\"zigux/tests/phase8_build.zig\"",
        "\"phase8-file-path-handle-bridge-tests\"",
        "\"make -C zigux phase8-test\"",
    ),
    BRIDGE_BUILD_PATH: (
        "\"../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig\"",
        "\"phase8_file_path_handle_bridge.zig\"",
        "\"phase8-file-path-handle-bridge-tests\"",
    ),
    PHASE8_BUILD_PATH: (
        "\"../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig\"",
        "\"phase8_file_path_handle_bridge.zig\"",
        "\"phase8-file-path-handle-bridge-tests\"",
    ),
}

FIXTURE_OVERRIDES = {
    VALIDATOR_PATH: "# fixture\n",
    TESTS_README_ALIGNMENT_CHECKER_PATH: "# fixture\n",
    EXEC_CMD_PACKET_CHECKER_PATH: "# fixture\n",
    HELP_KALLSYMS_PACKET_CHECKER_PATH: "# fixture\n",
    PERF_BUFFER_POLL_GATE_PATH: "# fixture\n",
    LIBBPF_SEGMENT_GATE_PATH: "# fixture\n",
    LIBBPF_SHARD_ROUTES_PATH: "# fixture\n",
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
        ("missing_boundary_survey", BOUNDARY_SURVEY_PATH),
        ("missing_workflow", WORKFLOW_PATH),
        ("missing_makefile", MAKEFILE_PATH),
        ("missing_tests_readme_alignment_checker", TESTS_README_ALIGNMENT_CHECKER_PATH),
        ("missing_exec_cmd_packet_checker", EXEC_CMD_PACKET_CHECKER_PATH),
        ("missing_help_kallsyms_packet_checker", HELP_KALLSYMS_PACKET_CHECKER_PATH),
        ("missing_perf_buffer_poll_gate", PERF_BUFFER_POLL_GATE_PATH),
        ("missing_libbpf_segment_gate", LIBBPF_SEGMENT_GATE_PATH),
        ("missing_libbpf_shard_routes", LIBBPF_SHARD_ROUTES_PATH),
        ("missing_libbpf_segment_survey", LIBBPF_SEGMENT_SURVEY_PATH),
        ("missing_libbpf_manifest", LIBBPF_MANIFEST_PATH),
        ("missing_bridge_slice", BRIDGE_SLICE_PATH),
        ("missing_bridge_helper", BRIDGE_HELPER_PATH),
        ("missing_bridge_test", BRIDGE_TEST_PATH),
        ("missing_bridge_build", BRIDGE_BUILD_PATH),
        ("missing_phase8_build", PHASE8_BUILD_PATH),
    ]
    marker_cases = [
        (
            "docs_root_help_slice_marker",
            DOCS_ROOT_PATH,
            "`Documentation/zigux/phase8-help-slice.md`",
            "`Documentation/zigux/phase8-help-outline.md`",
            f"{DOCS_ROOT_PATH}: `Documentation/zigux/phase8-help-slice.md`",
        ),
        (
            "review_checklist_help_kallsyms_packet_marker",
            REVIEW_CHECKLIST_PATH,
            "if the change touches the shared Phase 8 help-and-kallsyms packet",
            "if the change touches the parked Phase 8 help packet",
            f"{REVIEW_CHECKLIST_PATH}: if the change touches the shared Phase 8 help-and-kallsyms packet",
        ),
        (
            "review_checklist_help_kallsyms_checker_marker",
            REVIEW_CHECKLIST_PATH,
            "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
            "`scripts/zigux/check-phase8-help-packet.py`",
            f"{REVIEW_CHECKLIST_PATH}: `scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        ),
        (
            "review_checklist_libbpf_segment_gate_marker",
            REVIEW_CHECKLIST_PATH,
            "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
            "`scripts/zigux/check-phase8-libbpf-gate.py`",
            f"{REVIEW_CHECKLIST_PATH}: `scripts/zigux/check-phase8-libbpf-segment-gate.py`",
        ),
        (
            "scripts_readme_help_kallsyms_checker_marker",
            SCRIPTS_README_PATH,
            "scripts/zigux/check-phase8-help-kallsyms-packet.py",
            "scripts/zigux/check-phase8-help-packet.py",
            f"{SCRIPTS_README_PATH}: scripts/zigux/check-phase8-help-kallsyms-packet.py",
        ),
        (
            "scripts_readme_libbpf_segment_survey_marker",
            SCRIPTS_README_PATH,
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "Documentation/zigux/phase8-libbpf-segment-outline.md",
            f"{SCRIPTS_README_PATH}: Documentation/zigux/phase8-libbpf-segment-survey.md",
        ),
        (
            "tests_readme_help_kallsyms_build_marker",
            TESTS_README_PATH,
            "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
            "`zigux/tests/phase8_help_symbol_only_build.zig`",
            f"{TESTS_README_PATH}: `zigux/tests/phase8_help_kallsyms_only_build.zig`",
        ),
        (
            "sequencing_symbol_lane_marker",
            SEQUENCING_PATH,
            "### 2. Symbol lane",
            "### 2. Symbol reminder lane",
            f"{SEQUENCING_PATH}: ### 2. Symbol lane",
        ),
        (
            "docs_root_tests_readme_alignment_marker",
            DOCS_ROOT_PATH,
            "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
            "`scripts/zigux/check-phase8-tests-alignment.py`",
            f"{DOCS_ROOT_PATH}: `scripts/zigux/check-phase8-tests-readme-alignment.py`",
        ),
        (
            "docs_root_exec_cmd_packet_marker",
            DOCS_ROOT_PATH,
            "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
            "`scripts/zigux/check-phase8-exec-cmd-review.py`",
            f"{DOCS_ROOT_PATH}: `scripts/zigux/check-phase8-exec-cmd-packet.py`",
        ),
        (
            "docs_root_bridge_slice_marker",
            DOCS_ROOT_PATH,
            "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
            "`Documentation/zigux/phase8-file-path-handle-bridge-outline.md`",
            f"{DOCS_ROOT_PATH}: `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        ),
        (
            "docs_root_libbpf_segment_survey_marker",
            DOCS_ROOT_PATH,
            "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
            "`Documentation/zigux/phase8-libbpf-segment-outline.md`",
            f"{DOCS_ROOT_PATH}: `Documentation/zigux/phase8-libbpf-segment-survey.md`",
        ),
        (
            "scripts_readme_tests_readme_alignment_marker",
            SCRIPTS_README_PATH,
            "scripts/zigux/check-phase8-tests-readme-alignment.py",
            "scripts/zigux/check-phase8-tests-alignment.py",
            f"{SCRIPTS_README_PATH}: scripts/zigux/check-phase8-tests-readme-alignment.py",
        ),
        (
            "scripts_readme_exec_cmd_packet_marker",
            SCRIPTS_README_PATH,
            "scripts/zigux/check-phase8-exec-cmd-packet.py",
            "scripts/zigux/check-phase8-exec-cmd-review.py",
            f"{SCRIPTS_README_PATH}: scripts/zigux/check-phase8-exec-cmd-packet.py",
        ),
        (
            "scripts_readme_bridge_boundary_survey_marker",
            SCRIPTS_README_PATH,
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
            "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-note.md",
            f"{SCRIPTS_README_PATH}: Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        ),
        (
            "scripts_readme_bridge_slice_marker",
            SCRIPTS_README_PATH,
            "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
            "Documentation/zigux/phase8-file-path-handle-bridge-outline.md",
            f"{SCRIPTS_README_PATH}: Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        ),
        (
            "tests_readme_exec_cmd_packet_marker",
            TESTS_README_PATH,
            "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
            "`scripts/zigux/check-phase8-exec-cmd-review.py`",
            f"{TESTS_README_PATH}: `scripts/zigux/check-phase8-exec-cmd-packet.py`",
        ),
        (
            "sequencing_exec_cmd_packet_marker",
            SEQUENCING_PATH,
            "current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`",
            "current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-review.py`",
            f"{SEQUENCING_PATH}: current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`",
        ),
        (
            "sequencing_docs_root_reopen_cue_marker",
            SEQUENCING_PATH,
            "Exact 2026-05-13 readback closes the earlier docs-root reopen cue instead of reopening it",
            "Exact 2026-05-13 readback keeps the docs-root summary as the next shared wording reopen cue",
            f"{SEQUENCING_PATH}: Exact 2026-05-13 readback closes the earlier docs-root reopen cue instead of reopening it",
        ),
        (
            "sequencing_docs_root_bridge_note_marker",
            SEQUENCING_PATH,
            "`Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary",
            "`Documentation/zigux/README.md` still omits the live file-path bridge note from the broad Phase 8 docs summary",
            f"{SEQUENCING_PATH}: `Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary",
        ),
        (
            "sequencing_shared_wording_parked_marker",
            SEQUENCING_PATH,
            "Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.",
            "Start with that docs-root addition before widening any other shared reminder surface.",
            f"{SEQUENCING_PATH}: Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.",
        ),
        (
            "boundary_survey_shared_note_marker",
            BOUNDARY_SURVEY_PATH,
            "PHASE8_USERSPACE_KERNEL_BRIDGE_SHARED_NOTE=Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "PHASE8_USERSPACE_KERNEL_BRIDGE_SHARED_NOTE=Documentation/zigux/phase8-tooling-sequencing.md",
            f"{BOUNDARY_SURVEY_PATH}: PHASE8_USERSPACE_KERNEL_BRIDGE_SHARED_NOTE=Documentation/zigux/phase8-tooling-lane-sequencing.md",
        ),
        (
            "boundary_survey_validate_route_marker",
            BOUNDARY_SURVEY_PATH,
            "`python3 scripts/zigux/validate-phase8.py`",
            "`python3 scripts/zigux/phase8_validate.py`",
            f"{BOUNDARY_SURVEY_PATH}: `python3 scripts/zigux/validate-phase8.py`",
        ),
        (
            "makefile_tests_readme_alignment_marker",
            MAKEFILE_PATH,
            "scripts/zigux/check-phase8-tests-readme-alignment.py",
            "scripts/zigux/check-phase8-tests-alignment.py",
            f"{MAKEFILE_PATH}: scripts/zigux/check-phase8-tests-readme-alignment.py",
        ),
        (
            "makefile_exec_cmd_packet_marker",
            MAKEFILE_PATH,
            "scripts/zigux/check-phase8-exec-cmd-packet.py",
            "scripts/zigux/check-phase8-exec-cmd-review.py",
            f"{MAKEFILE_PATH}: scripts/zigux/check-phase8-exec-cmd-packet.py",
        ),
        (
            "makefile_help_kallsyms_checker_marker",
            MAKEFILE_PATH,
            "scripts/zigux/check-phase8-help-kallsyms-packet.py",
            "scripts/zigux/check-phase8-help-packet.py",
            f"{MAKEFILE_PATH}: scripts/zigux/check-phase8-help-kallsyms-packet.py",
        ),
        (
            "makefile_libbpf_segment_gate_marker",
            MAKEFILE_PATH,
            "scripts/zigux/check-phase8-libbpf-segment-gate.py",
            "scripts/zigux/check-phase8-libbpf-gate.py",
            f"{MAKEFILE_PATH}: scripts/zigux/check-phase8-libbpf-segment-gate.py",
        ),
        (
            "makefile_libbpf_shard_routes_marker",
            MAKEFILE_PATH,
            "scripts/zigux/check-phase8-libbpf-shard-routes.py",
            "scripts/zigux/check-phase8-libbpf-route-checks.py",
            f"{MAKEFILE_PATH}: scripts/zigux/check-phase8-libbpf-shard-routes.py",
        ),
        (
            "workflow_phase8_validate_marker",
            WORKFLOW_PATH,
            "make -C zigux phase8-validate",
            "make -C zigux phase8-verify",
            f"{WORKFLOW_PATH}: make -C zigux phase8-validate",
        ),
        (
            "libbpf_segment_survey_manifest_marker",
            LIBBPF_SEGMENT_SURVEY_PATH,
            "`tools/lib/bpf/zigux_segments/manifest.json`",
            "`tools/lib/bpf/zigux_segments/manifest.lock`",
            f"{LIBBPF_SEGMENT_SURVEY_PATH}: `tools/lib/bpf/zigux_segments/manifest.json`",
        ),
        (
            "libbpf_segment_survey_landed_slices_marker",
            LIBBPF_SEGMENT_SURVEY_PATH,
            "The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.",
            "The six landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, and `perf-buffer-poll-bookkeeping`.",
            f"{LIBBPF_SEGMENT_SURVEY_PATH}: The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.",
        ),
        (
            "libbpf_manifest_map_reuse_status_marker",
            LIBBPF_MANIFEST_PATH,
            '"slug": "map-reuse-compatibility", "status": "starter_landed"',
            '"slug": "map-reuse-compatibility", "status": "ready_next"',
            f"{LIBBPF_MANIFEST_PATH}: \"slug\": \"map-reuse-compatibility\", \"status\": \"starter_landed\"",
        ),
        (
            "bridge_slice_shared_build_marker",
            BRIDGE_SLICE_PATH,
            "`zigux/tests/phase8_build.zig`",
            "`zigux/tests/phase8_bridge_build.zig`",
            f"{BRIDGE_SLICE_PATH}: `zigux/tests/phase8_build.zig`",
        ),
        (
            "bridge_slice_shared_replay_marker",
            BRIDGE_SLICE_PATH,
            "`make -C zigux phase8-test`",
            "`make -C zigux phase8-bridge-test`",
            f"{BRIDGE_SLICE_PATH}: `make -C zigux phase8-test`",
        ),
        (
            "bridge_helper_token_planning_marker",
            BRIDGE_HELPER_PATH,
            "planTokenPreparation(",
            "planTokenGate(",
            f"{BRIDGE_HELPER_PATH}: planTokenPreparation(",
        ),
        (
            "bridge_test_shared_build_marker",
            BRIDGE_TEST_PATH,
            "\"zigux/tests/phase8_build.zig\"",
            "\"zigux/tests/phase8_bridge_build.zig\"",
            f"{BRIDGE_TEST_PATH}: \"zigux/tests/phase8_build.zig\"",
        ),
        (
            "bridge_focused_build_test_name_marker",
            BRIDGE_BUILD_PATH,
            "\"phase8-file-path-handle-bridge-tests\"",
            "\"phase8-file-path-handle-bridge-shard-tests\"",
            f"{BRIDGE_BUILD_PATH}: \"phase8-file-path-handle-bridge-tests\"",
        ),
        (
            "phase8_build_bridge_test_name_marker",
            PHASE8_BUILD_PATH,
            "\"phase8-file-path-handle-bridge-tests\"",
            "\"phase8-file-path-handle-bridge-shard-tests\"",
            f"{PHASE8_BUILD_PATH}: \"phase8-file-path-handle-bridge-tests\"",
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
