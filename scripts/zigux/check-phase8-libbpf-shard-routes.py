#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    "Documentation/zigux/phase8-bpf-type-names-slice.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase8.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
    ],
    "Documentation/zigux/README.md": [
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
        "`scripts/zigux/check-phase8-libbpf-shard-routes.py`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "while the docs-root summary stays aligned with the live scripts-root and tests-root reminder packet on `master`",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the shared parked Phase 8 libbpf packet",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`tools/lib/bpf/zigux_segments/manifest.json`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "`make -C zigux phase8-libbpf-segments-test`",
    ],
    "Documentation/zigux/phase8-tooling-lane-sequencing.md": [
        "the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`",
        "`zigux/tests/phase8_cpu_mask.zig`",
        "`zigux/tests/phase8_cpu_mask_only_build.zig`",
        "`zigux/tests/phase8_logging.zig`",
        "`zigux/tests/phase8_pin_path.zig`",
        "`zigux/tests/phase8_bpf_type_names.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "do not let older absent-file assumptions overrule current tree evidence",
        "### 4. Shared wording lane",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md` now carries the refreshed mixed 2026-05-12 libbpf readback",
        "current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`",
        "Exact 2026-05-13 readback closes the earlier docs-root reopen cue instead of reopening it",
        "`Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary",
        "Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.",
    ],
    "Documentation/zigux/phase8-libbpf-segment-survey.md": [
        "`Documentation/zigux/README.md` now names the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` note in the broad Phase 8 docs summary, public Phase 8 readback still serves `Documentation/zigux/phase8-bpf-type-names-slice.md`, and `scripts/zigux/README.md` keeps the broader Phase 8 libbpf helper packet visible through the shared sequencing, bridge-boundary, bridge-slice, checker, and build-surface reminders.",
        "`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet",
        "`phase8_pin_path.zig`",
        "`phase8_bpf_type_names.zig`",
        "`phase8_file_path_handle_bridge.zig`",
        "`phase8_perf_buffer_poll.zig`",
        "`phase8_perf_buffer_poll_only_build.zig`",
        "`phase8_libbpf_segments.zig`",
        "`phase8_libbpf_segments_only_build.zig`",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`",
        "`make -C zigux phase8-test`",
        "`zig build test --build-file zigux/tests/phase8_build.zig --summary all`",
        "targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`",
        "Current `master` no longer matches that wording: the manifest and the shared file-path bridge packet now treat those two bridge-adjacent helpers as landed helper-first slices while keeping the heavier `file-path-and-handle-bridge` destination deferred.",
        "Exact 2026-05-13 readback closes the earlier docs-root reopen cue: public Phase 8 readback still serves both `Documentation/zigux/phase8-bpf-type-names-slice.md` and `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, and `Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary.",
        "The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.",
        "The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.",
        "Keep the libbpf survey packet parked after this survey-and-checker sync unless a fresh shared reminder-surface drift reappears against the current readable helper-plus-build evidence.",
    ],
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md": [
        "PHASE8_SLICE=libbpf-perf-buffer-poll",
        "make -C zigux phase8-perf-buffer-poll-test",
        "no standalone timer helper behavior",
        "no standalone clockevent helper behavior",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "make -C zigux phase8-validate",
    ],
    "scripts/zigux/validate-phase8.py": [
        "Documentation/zigux/phase8-tooling-lane-sequencing.md",
        "scripts/zigux/check-phase8-libbpf-shard-routes.py",
        "zigux/Makefile",
        "zigux/tests/README.md",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
    ],
    "zigux/tests/README.md": [
        "scripts/zigux/validate-phase8.py",
        "make -C zigux phase8-validate",
        "`zigux/tests/phase8_cpu_mask_only_build.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "`make -C zigux phase8-libbpf-segments-test`",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def fixture_text(rel: str) -> str:
    markers = REQUIRED_MARKERS.get(rel)
    if markers is None:
        return "# fixture\n"
    return "\n".join(markers) + "\n"


def write_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text(rel), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [expected], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_docs_root", "Documentation/zigux/README.md"),
        ("missing_review_checklist", "Documentation/zigux/review-checklist.md"),
        ("missing_lane_note", "Documentation/zigux/phase8-tooling-lane-sequencing.md"),
        ("missing_segment_survey", "Documentation/zigux/phase8-libbpf-segment-survey.md"),
        ("missing_perf_buffer_poll_slice", "Documentation/zigux/phase8-perf-buffer-poll-slice.md"),
        ("missing_file_path_handle_bridge_slice", "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"),
        ("missing_bpf_type_names_slice", "Documentation/zigux/phase8-bpf-type-names-slice.md"),
        ("missing_scripts_readme", "scripts/zigux/README.md"),
        ("missing_validator", "scripts/zigux/validate-phase8.py"),
        ("missing_workflow", ".github/workflows/zigux-bootstrap.yml"),
        ("missing_makefile", "zigux/Makefile"),
    ]
    marker_cases = [
        (
            "docs_root_segment_survey_anchor",
            "Documentation/zigux/README.md",
            "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
            "`Documentation/zigux/phase8-libbpf-segment-note.md`",
            "Documentation/zigux/README.md: `Documentation/zigux/phase8-libbpf-segment-survey.md`",
        ),
        (
            "docs_root_segment_gate_checker_anchor",
            "Documentation/zigux/README.md",
            "`scripts/zigux/check-phase8-libbpf-segment-gate.py`",
            "`scripts/zigux/check-phase8-libbpf-segment.py`",
            "Documentation/zigux/README.md: `scripts/zigux/check-phase8-libbpf-segment-gate.py`",
        ),
        (
            "docs_root_checker_anchor",
            "Documentation/zigux/README.md",
            "`scripts/zigux/check-phase8-libbpf-shard-routes.py`",
            "`scripts/zigux/check-phase8-libbpf-routes.py`",
            "Documentation/zigux/README.md: `scripts/zigux/check-phase8-libbpf-shard-routes.py`",
        ),
        (
            "review_checklist_manifest_anchor",
            "Documentation/zigux/review-checklist.md",
            "`tools/lib/bpf/zigux_segments/manifest.json`",
            "`tools/lib/bpf/zigux_segments/index.json`",
            "Documentation/zigux/review-checklist.md: `tools/lib/bpf/zigux_segments/manifest.json`",
        ),
        (
            "review_checklist_route_anchor",
            "Documentation/zigux/review-checklist.md",
            "`make -C zigux phase8-libbpf-segments-test`",
            "`make -C zigux phase8-libbpf-shared-test`",
            "Documentation/zigux/review-checklist.md: `make -C zigux phase8-libbpf-segments-test`",
        ),
        (
            "lane_note_manifest_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`",
            "the current tree exposes `tools/lib/bpf/zigux_segments/verify.zig`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`",
        ),
        (
            "lane_note_pin_path_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`zigux/tests/phase8_pin_path.zig`",
            "`zigux/tests/phase8_pin_path_review.zig`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `zigux/tests/phase8_pin_path.zig`",
        ),
        (
            "lane_note_logging_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`zigux/tests/phase8_logging.zig`",
            "`zigux/tests/phase8_logging_review.zig`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `zigux/tests/phase8_logging.zig`",
        ),
        (
            "lane_note_type_names_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`zigux/tests/phase8_bpf_type_names.zig`",
            "`zigux/tests/phase8_type_names_review.zig`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `zigux/tests/phase8_bpf_type_names.zig`",
        ),
        (
            "lane_note_file_path_handle_bridge_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`zigux/tests/phase8_file_path_handle_bridge.zig`",
            "`zigux/tests/phase8_file_path_bridge_review.zig`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `zigux/tests/phase8_file_path_handle_bridge.zig`",
        ),
        (
            "lane_note_file_path_handle_bridge_only_build_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
            "`zigux/tests/phase8_file_path_handle_bridge_review_build.zig`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        ),
        (
            "lane_note_perf_buffer_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`zigux/tests/phase8_perf_buffer_poll.zig`",
            "`zigux/tests/phase8_perf_buffer_review.zig`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `zigux/tests/phase8_perf_buffer_poll.zig`",
        ),
        (
            "lane_note_perf_buffer_only_build_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
            "`zigux/tests/phase8_perf_buffer_poll_review_build.zig`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        ),
        (
            "lane_note_libbpf_segments_only_build_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
            "`zigux/tests/phase8_libbpf_segments_review_build.zig`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `zigux/tests/phase8_libbpf_segments_only_build.zig`",
        ),
        (
            "lane_note_shared_wording_heading",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "### 4. Shared wording lane",
            "### 4. Shared wording packet",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: ### 4. Shared wording lane",
        ),
        (
            "lane_note_shared_survey_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`Documentation/zigux/phase8-libbpf-segment-survey.md` now carries the refreshed mixed 2026-05-12 libbpf readback",
            "`Documentation/zigux/phase8-libbpf-segment-survey.md` already carries the refreshed mixed 2026-05-12 libbpf readback",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `Documentation/zigux/phase8-libbpf-segment-survey.md` now carries the refreshed mixed 2026-05-12 libbpf readback",
        ),
        (
            "lane_note_shared_wording_scope_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.",
            "Keep the shared wording lane active until a fresh one-file reminder-surface drift appears.",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.",
        ),
        (
            "lane_note_scripts_readme_case_closure_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`",
            "current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-review.py`",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`",
        ),
        (
            "lane_note_docs_root_reopen_closed_anchor",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "Exact 2026-05-13 readback closes the earlier docs-root reopen cue instead of reopening it",
            "Exact 2026-05-13 readback now makes the docs-root summary the next shared wording reopen cue instead of closing it",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: Exact 2026-05-13 readback closes the earlier docs-root reopen cue instead of reopening it",
        ),
        (
            "lane_note_docs_root_bridge_note_marker",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "`Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary",
            "`Documentation/zigux/README.md` still omits the live file-path bridge note from the broad Phase 8 docs summary",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md: `Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary",
        ),
        (
            "segment_survey_docs_root_readback_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`Documentation/zigux/README.md` now names the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` note in the broad Phase 8 docs summary, public Phase 8 readback still serves `Documentation/zigux/phase8-bpf-type-names-slice.md`, and `scripts/zigux/README.md` keeps the broader Phase 8 libbpf helper packet visible through the shared sequencing, bridge-boundary, bridge-slice, checker, and build-surface reminders.",
            "`Documentation/zigux/README.md` still exposes the broader Phase 8 libbpf helper packet through a stale `Documentation/zigux/phase8-bpf-type-names-slice.md` note path while omitting the live file-path bridge note.",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `Documentation/zigux/README.md` now names the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` note in the broad Phase 8 docs summary, public Phase 8 readback still serves `Documentation/zigux/phase8-bpf-type-names-slice.md`, and `scripts/zigux/README.md` keeps the broader Phase 8 libbpf helper packet visible through the shared sequencing, bridge-boundary, bridge-slice, checker, and build-surface reminders.",
        ),
        (
            "segment_survey_build_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet",
            "`zigux/tests/phase8_build.zig` no longer wires the current libbpf helper-first shard packet",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet",
        ),
        (
            "segment_survey_type_names_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`phase8_bpf_type_names.zig`",
            "`phase8_type_names_review.zig`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `phase8_bpf_type_names.zig`",
        ),
        (
            "segment_survey_bridge_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`phase8_file_path_handle_bridge.zig`",
            "`phase8_file_path_bridge_review.zig`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `phase8_file_path_handle_bridge.zig`",
        ),
        (
            "segment_survey_perf_buffer_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`phase8_perf_buffer_poll.zig`",
            "`phase8_perf_buffer_review.zig`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `phase8_perf_buffer_poll.zig`",
        ),
        (
            "segment_survey_perf_buffer_only_build_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`phase8_perf_buffer_poll_only_build.zig`",
            "`phase8_perf_buffer_poll_review_build.zig`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `phase8_perf_buffer_poll_only_build.zig`",
        ),
        (
            "segment_survey_libbpf_segments_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`phase8_libbpf_segments.zig`",
            "`phase8_libbpf_segments_review.zig`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `phase8_libbpf_segments.zig`",
        ),
        (
            "segment_survey_libbpf_segments_only_build_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`phase8_libbpf_segments_only_build.zig`",
            "`phase8_libbpf_segments_review_build.zig`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `phase8_libbpf_segments_only_build.zig`",
        ),
        (
            "segment_survey_verify_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`tools/lib/bpf/zigux_segments/verify.zig`",
            "`tools/lib/bpf/zigux_segments/review_verify.zig`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `tools/lib/bpf/zigux_segments/verify.zig`",
        ),
        (
            "segment_survey_libbpf_segments_route_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`make -C zigux phase8-libbpf-segments-test`",
            "`make -C zigux phase8-libbpf-segments-review`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `make -C zigux phase8-libbpf-segments-test`",
        ),
        (
            "segment_survey_libbpf_segments_build_route_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`",
            "`zig build test --build-file zigux/tests/phase8_libbpf_segments_review_build.zig --summary all`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`",
        ),
        (
            "segment_survey_perf_buffer_route_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`make -C zigux phase8-perf-buffer-poll-test`",
            "`make -C zigux phase8-perf-buffer-poll-review`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `make -C zigux phase8-perf-buffer-poll-test`",
        ),
        (
            "segment_survey_phase8_test_route_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`make -C zigux phase8-test`",
            "`make -C zigux phase8-review`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `make -C zigux phase8-test`",
        ),
        (
            "segment_survey_phase8_build_route_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "`zig build test --build-file zigux/tests/phase8_build.zig --summary all`",
            "`zig build test --build-file zigux/tests/phase8_review_build.zig --summary all`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: `zig build test --build-file zigux/tests/phase8_build.zig --summary all`",
        ),
        (
            "segment_survey_pin_path_split_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`",
            "targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, and `tools/lib/bpf/zigux_segments/pin_path.zig`",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`",
        ),
        (
            "segment_survey_current_master_bridge_state_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "Current `master` no longer matches that wording: the manifest and the shared file-path bridge packet now treat those two bridge-adjacent helpers as landed helper-first slices while keeping the heavier `file-path-and-handle-bridge` destination deferred.",
            "Current `master` now matches that wording: the manifest and the shared file-path bridge packet still treat those two bridge-adjacent helpers as queued helper-first slices while the heavier `file-path-and-handle-bridge` destination stays deferred.",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: Current `master` no longer matches that wording: the manifest and the shared file-path bridge packet now treat those two bridge-adjacent helpers as landed helper-first slices while keeping the heavier `file-path-and-handle-bridge` destination deferred.",
        ),
        (
            "segment_survey_docs_root_gap_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "Exact 2026-05-13 readback closes the earlier docs-root reopen cue: public Phase 8 readback still serves both `Documentation/zigux/phase8-bpf-type-names-slice.md` and `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, and `Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary.",
            "Exact 2026-05-13 readback reopens the earlier docs-root cue because the broad Phase 8 docs summary still omits the live file-path bridge note.",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: Exact 2026-05-13 readback closes the earlier docs-root reopen cue: public Phase 8 readback still serves both `Documentation/zigux/phase8-bpf-type-names-slice.md` and `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, and `Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary.",
        ),
        (
            "segment_survey_landed_slice_catalog_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.",
            "The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-online-cpu-routing`.",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.",
        ),
        (
            "segment_survey_deferred_slice_catalog_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.",
            "The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-poll-bookkeeping`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.",
        ),
        (
            "segment_survey_follow_through_anchor",
            "Documentation/zigux/phase8-libbpf-segment-survey.md",
            "Keep the libbpf survey packet parked after this survey-and-checker sync unless a fresh shared reminder-surface drift reappears against the current readable helper-plus-build evidence.",
            "Keep the shared wording lane active after this survey-and-checker sync even without a fresh shared reminder-surface drift.",
            "Documentation/zigux/phase8-libbpf-segment-survey.md: Keep the libbpf survey packet parked after this survey-and-checker sync unless a fresh shared reminder-surface drift reappears against the current readable helper-plus-build evidence.",
        ),
        (
            "perf_buffer_poll_slice_route_anchor",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
            "make -C zigux phase8-perf-buffer-poll-test",
            "make -C zigux phase8-perf-buffer-review",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md: make -C zigux phase8-perf-buffer-poll-test",
        ),
        (
            "perf_buffer_poll_slice_timer_anchor",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
            "no standalone timer helper behavior",
            "standalone timer helper behavior",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md: no standalone timer helper behavior",
        ),
        (
            "perf_buffer_poll_slice_clockevent_anchor",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
            "no standalone clockevent helper behavior",
            "standalone clockevent helper behavior",
            "Documentation/zigux/phase8-perf-buffer-poll-slice.md: no standalone clockevent helper behavior",
        ),
        (
            "scripts_readme_segment_gate_checker_anchor",
            "scripts/zigux/README.md",
            "scripts/zigux/check-phase8-libbpf-segment-gate.py",
            "scripts/zigux/check-phase8-libbpf-segment.py",
            "scripts/zigux/README.md: scripts/zigux/check-phase8-libbpf-segment-gate.py",
        ),
        (
            "scripts_readme_checker_anchor",
            "scripts/zigux/README.md",
            "scripts/zigux/check-phase8-libbpf-shard-routes.py",
            "scripts/zigux/check-phase8-libbpf-routes.py",
            "scripts/zigux/README.md: scripts/zigux/check-phase8-libbpf-shard-routes.py",
        ),
        (
            "validator_lane_note_anchor",
            "scripts/zigux/validate-phase8.py",
            "Documentation/zigux/phase8-tooling-lane-sequencing.md",
            "Documentation/zigux/phase8-tooling-sequencing.md",
            "scripts/zigux/validate-phase8.py: Documentation/zigux/phase8-tooling-lane-sequencing.md",
        ),
        (
            "workflow_phase8_validate_route",
            ".github/workflows/zigux-bootstrap.yml",
            "make -C zigux phase8-validate",
            "make -C zigux phase8",
            ".github/workflows/zigux-bootstrap.yml: make -C zigux phase8-validate",
        ),
        (
            "makefile_phase8_validator_hook",
            "zigux/Makefile",
            "scripts/zigux/validate-phase8.py",
            "scripts/zigux/validate-phase8-lane.py",
            "zigux/Makefile: scripts/zigux/validate-phase8.py",
        ),
        (
            "tests_readme_cpu_mask_only_build_anchor",
            "zigux/tests/README.md",
            "`zigux/tests/phase8_cpu_mask_only_build.zig`",
            "`zigux/tests/phase8_cpu_mask_review_build.zig`",
            "zigux/tests/README.md: `zigux/tests/phase8_cpu_mask_only_build.zig`",
        ),
        (
            "tests_readme_file_path_handle_bridge_only_build_anchor",
            "zigux/tests/README.md",
            "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
            "`zigux/tests/phase8_file_path_handle_bridge_review_build.zig`",
            "zigux/tests/README.md: `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        ),
        (
            "tests_readme_perf_buffer_poll_only_build_anchor",
            "zigux/tests/README.md",
            "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
            "`zigux/tests/phase8_perf_buffer_poll_review_build.zig`",
            "zigux/tests/README.md: `zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_shard_routes_") as tmp_dir_str:
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

    print("PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass")
    print(
        "PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current parked Phase 8 libbpf wording and route packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_FILES_END")
        return 1
    if missing_markers:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_LIBBPF_SHARD_ROUTE_MARKERS_END")
        return 1

    print("PHASE8_LIBBPF_SHARD_ROUTES=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTE_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_LIBBPF_SHARD_ROUTE_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
