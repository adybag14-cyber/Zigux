#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase14-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")

FILES = [
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-workqueue-bridge-survey.md",
    "Documentation/zigux/phase14-skbuff-bridge-survey.md",
    "Documentation/zigux/phase14-ring-buffer-survey.md",
    "Documentation/zigux/phase14-rcu-tree-survey.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase14_build.zig",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig",
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
    "zigux/tests/phase14_ring_buffer_manifest.json",
    "zigux/tests/phase14_rcu_tree_manifest.json",
    "zigux/tests/phase14_workqueue_reviewability.zig",
]

MAKE_MARKERS = [
    "PHONY += phase14-validate phase14-smoke phase14-test phase14",
    "phase14-validate:",
    "scripts/zigux/validate-phase14.py",
    "phase14-smoke:",
    "$(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14-test:",
    "$(ZIG) build test --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14: phase14-validate phase14-smoke phase14-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 14 shared smoke packet",
    "make -C zigux phase14-validate",
    "Run Phase 14 smoke shard",
    "make -C zigux phase14-smoke",
    "Run Phase 14 internal bridge tests",
    "make -C zigux phase14-test",
]

SCRIPT_README_MARKERS = [
    "Current bootstrap helpers",
    "`validate-phase14.py`",
    "Phase 14 flow",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/freeze-map.md`",
    "`make -C zigux phase14-validate`",
    "`make -C zigux phase14-smoke`",
    "`zigux/tests/phase14_build.zig`",
    "shared Phase 14 smoke packet",
    "focused smoke-shard replay contract",
    "stay-in-C boundary",
]

RELEASE_MARKERS = [
    "PHASE14_STATUS=active",
    "PHASE14_SLICE=end-to-end-smoke-verification",
    "PHASE14_SMOKE_VALIDATOR=present",
    "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
    "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14",
    "PHASE14_ANCHOR_PACKET_COUNT=4",
    "PHASE14_STAY_IN_C_BOUNDARY=explicit",
    "PHASE14_STATUS_CHANGE_CLAIM=no",
    "compile shard matrix captured in the current shared packet",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "phase14_workqueue_bridge_manifest.json",
    "phase14_skbuff_bridge_manifest.json",
    "phase14_ring_buffer_manifest.json",
    "phase14_rcu_tree_manifest.json",
    "phase14-workqueue-reviewability-tests",
    "phase14_workqueue_reviewability.zig",
]

SKBUFF_SURVEY_MARKERS = [
    "`PHASE14_LANE_KEY=P14-L11`",
    "`phase14-skbuff-live-ownership-blocker`",
    "explicit stay-in-C wording for `segs->prev`, `tail->next`, and `validate_xmit_skb_list()`",
    "explicit wording that qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, and destructor coordination remain in C",
    "After the roadmap-alignment helper and the exported-tail checkpoint, no smaller review-only skbuff follow-up remains before the live ownership blocker.",
]

REQUIRED_SKBUFF_DECISION_CHECKLIST = {
    "shared-info-refcount-ownership": [
        "struct skb_shared_info",
        "dataref",
        "skb_header_cloned",
    ],
    "destructor-and-free-path": [
        "skb_release_head_state",
        "skb_release_data",
        "consume_skb",
    ],
    "segmentation-partial-tail-owner-transfer": [
        "skb_segment",
        "SKB_GSO_PARTIAL",
        "sock_wfree",
    ],
    "segmentation-checksum-data-offset-crossover": [
        "skb_segment",
        "SKB_GSO_CB",
        "remcsum_offload",
    ],
    "segmentation-tail-publication-consumer-contract": [
        "skb_segment",
        "segs->prev",
        "validate_xmit_skb_list",
    ],
}

CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 14 smoke packet, do `scripts/zigux/validate-phase14.py`, `scripts/zigux/README.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_build.zig`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, and the four Phase 14 anchor-local manifests plus survey notes still agree on the same exact validator-backed smoke commands, the same focused `phase14-smoke` shard commands, ready-next versus blocked posture, stay-in-C boundary, named owner, validation gate, rollback owner, and explicit ZAR-to-product transfer rationale?",
]

BUILD_MARKERS = [
    "phase14-workqueue-bridge-tests",
    "phase14-workqueue-reviewability-tests",
    "phase14-skbuff-bridge-tests",
    "phase14-ring-buffer-survey-tests",
    "phase14-rcu-tree-survey-tests",
    "phase14-end-to-end-smoke-tests",
    "test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
    "test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);",
    "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
    "test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
    "test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
    "test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
]

COMPILE_MATRIX_ROWS = [
    ("phase14-workqueue-bridge-tests", "phase14_workqueue_bridge.zig", "full_bundle_only"),
    ("phase14-workqueue-reviewability-tests", "phase14_workqueue_reviewability.zig", "full_bundle_only"),
    ("phase14-skbuff-bridge-tests", "phase14_skbuff_bridge.zig", "full_bundle_only"),
    ("phase14-ring-buffer-survey-tests", "phase14_ring_buffer_survey.zig", "full_bundle_only"),
    ("phase14-rcu-tree-survey-tests", "phase14_rcu_tree_survey.zig", "full_bundle_only"),
    ("phase14-end-to-end-smoke-tests", "phase14_end_to_end_smoke_survey.zig", "focused_and_full_bundle"),
]

EXPECTED_BUILD_TEST_NAMES = [label for label, _, _ in COMPILE_MATRIX_ROWS]
EXPECTED_COMPILE_SHARDS = [
    {"label": label, "root_source": root_source, "coverage": coverage}
    for label, root_source, coverage in COMPILE_MATRIX_ROWS
]
ANCHOR_PACKET_LABELS = {
    "kernel/workqueue.c": "workqueue",
    "net/core/skbuff.c": "skbuff",
    "kernel/trace/ring_buffer.c": "ring buffer",
    "kernel/rcu/tree.c": "RCU tree",
}


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(
    path: str,
    json_decode_errors: list[str],
    *,
    base_root: Path | None = None,
) -> dict[str, object] | None:
    root = ROOT if base_root is None else base_root
    source = (root / path).read_text(encoding="utf-8")
    try:
        loaded = json.loads(source)
    except json.JSONDecodeError as exc:
        json_decode_errors.append(
            f"{path}:{exc.lineno}:{exc.colno}:{exc.msg}"
        )
        return None
    if not isinstance(loaded, dict):
        json_decode_errors.append(f"{path}:top_level_type={type(loaded).__name__}")
        return None
    return loaded


def summarize_gap_ids(manifest: dict[str, object]) -> tuple[str, str]:
    ready_next_gap = ""
    blocked_gap = ""
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return ready_next_gap, blocked_gap

    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        gap_id = gap.get("id")
        status = gap.get("status")
        if not isinstance(gap_id, str) or not isinstance(status, str):
            continue
        if status == "ready_next":
            ready_next_gap = gap_id
        elif status.startswith("blocked"):
            blocked_gap = gap_id

    return ready_next_gap, blocked_gap


def format_anchor_packet_survey_line(packet: dict[str, object]) -> str:
    anchor = packet.get("anchor")
    manifest_path = packet.get("manifest_path")
    packet_lane_key = packet.get("lane_key")
    packet_commit = packet.get("surveyed_commit")
    ready_next_gap = packet.get("ready_next_gap")
    blocked_gap = packet.get("blocked_gap")
    label = ANCHOR_PACKET_LABELS.get(anchor, anchor)
    ready_next_text = ready_next_gap if ready_next_gap else "none currently recorded"
    return (
        f"- {label}: `{manifest_path}`, lane `{packet_lane_key}`, surveyed commit `{packet_commit}`, "
        f"ready-next `{ready_next_text}`, blocked `{blocked_gap}`"
    )


def run_self_test() -> int:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        bad_manifest = tmp_root / "bad.json"
        bad_manifest.write_text('{"lane_key": "P14-L11",\n', encoding="utf-8")
        result = load_json("bad.json", errors, base_root=tmp_root)
    if result is not None:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=load_json_returned_value_for_invalid_json")
        return 1
    if errors != ["bad.json:2:1:Expecting property name enclosed in double quotes"]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_json_error_marker")
        print("SELF_TEST_MARKERS_START")
        for item in errors:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    missing_reviewability_build = "\n".join(
        [f'.name = "{name}"' for name in EXPECTED_BUILD_TEST_NAMES]
        + [
            f"test_step.dependOn(&{step}.step);"
            for step in [
                "run_phase14_workqueue_bridge_tests",
                "run_phase14_skbuff_bridge_tests",
                "run_phase14_ring_buffer_survey_tests",
                "run_phase14_rcu_tree_survey_tests",
                "run_phase14_end_to_end_smoke_tests",
            ]
        ]
    )
    missing_build_markers = [
        marker for marker in BUILD_MARKERS if marker not in missing_reviewability_build
    ]
    if missing_build_markers != [
        "test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_reviewability_dependency_gap_markers")
        print("SELF_TEST_MARKERS_START")
        for item in missing_build_markers:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1
    if BUILD_TEST_NAME_RE.findall(missing_reviewability_build) != EXPECTED_BUILD_TEST_NAMES:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_reviewability_dependency_test_names")
        return 1
    if BUILD_DEPEND_STEP_RE.findall(missing_reviewability_build) != [
        "run_phase14_workqueue_bridge_tests",
        "run_phase14_skbuff_bridge_tests",
        "run_phase14_ring_buffer_survey_tests",
        "run_phase14_rcu_tree_survey_tests",
        "run_phase14_end_to_end_smoke_tests",
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_reviewability_dependency_parse_result")
        return 1

    print("PHASE14_SELF_TEST=pass")
    print("PHASE14_SELF_TEST_JSON_ERROR_MARKER=bad.json:2:1:Expecting property name enclosed in double quotes")
    print("PHASE14_SELF_TEST_MISSING_REVIEWABILITY_MARKER=test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);")
    return 0


def run_validation() -> int:
    missing_files = [path for path in FILES if not (ROOT / path).exists()]
    if missing_files:
        print("PHASE14_VALIDATION=fail")
        print("MISSING_PHASE14_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_PHASE14_FILES_END")
        return 1

    survey_text = text("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
    skbuff_survey_text = text("Documentation/zigux/phase14-skbuff-bridge-survey.md")
    missing: list[str] = []
    json_decode_errors: list[str] = []
    for name, source, markers in [
        ("scripts_readme", text("scripts/zigux/README.md"), SCRIPT_README_MARKERS),
        ("make", text("zigux/Makefile"), MAKE_MARKERS),
        ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
        ("survey", survey_text, RELEASE_MARKERS),
        ("skbuff_survey", skbuff_survey_text, SKBUFF_SURVEY_MARKERS),
        ("checklist", text("Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS),
        ("build", text("zigux/tests/phase14_build.zig"), BUILD_MARKERS),
    ]:
        for marker in markers:
            if marker not in source:
                missing.append(f"{name}:{marker}")

    freeze_map_text = text("Documentation/zigux/freeze-map.md")
    for marker in [
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
        "net/core/skbuff.c",
        "kernel/rcu/tree.c",
        "Architecture Council",
    ]:
        if marker not in freeze_map_text:
            missing.append(f"freeze_map:{marker}")

    manifest = load_json(
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        json_decode_errors,
    )
    if manifest is not None:
        lane_key = manifest.get("lane_key")
        if not isinstance(lane_key, str) or not lane_key.startswith("P14-"):
            missing.append(f"manifest:lane_key={lane_key}")
        if manifest.get("phase") != "Phase 14":
            missing.append(f'manifest:phase={manifest.get("phase")}')
        surveyed_commit = manifest.get("surveyed_commit")
        if not isinstance(surveyed_commit, str) or not HEX40_RE.fullmatch(surveyed_commit):
            missing.append(f"manifest:surveyed_commit={surveyed_commit}")

        shared_smoke_surfaces = manifest.get("shared_smoke_surfaces")
        if not isinstance(shared_smoke_surfaces, list):
            missing.append("manifest:shared_smoke_surfaces")
        else:
            for required_surface in [
                "scripts/zigux/validate-phase14.py",
                "scripts/zigux/check-phase14-docs-root-smoke-summary.py",
                "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
                "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
                "scripts/zigux/README.md",
                "zigux/tests/phase14_end_to_end_smoke_manifest.json",
                "zigux/tests/phase14_end_to_end_smoke_survey.zig",
                "zigux/tests/phase14_build.zig",
                "zigux/tests/phase14_workqueue_reviewability.zig",
                "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
                "Documentation/zigux/review-checklist.md",
                "Documentation/zigux/freeze-map.md",
            ]:
                if required_surface not in shared_smoke_surfaces:
                    missing.append(f"manifest:shared_smoke_surface:{required_surface}")

        anchor_packets = manifest.get("anchor_packets")
        expected_survey_anchor_lines: list[tuple[str, str]] = []
        if not isinstance(anchor_packets, list) or len(anchor_packets) != 4:
            missing.append("manifest:anchor_packets")
        else:
            for packet in anchor_packets:
                if not isinstance(packet, dict):
                    missing.append("manifest:anchor_packet")
                    continue
                packet_lane_key = packet.get("lane_key")
                anchor = packet.get("anchor")
                packet_commit = packet.get("surveyed_commit")
                manifest_path = packet.get("manifest_path")
                survey_note_path = packet.get("survey_note_path")
                ready_next_gap = packet.get("ready_next_gap")
                blocked_gap = packet.get("blocked_gap")
                if not isinstance(packet_lane_key, str) or not packet_lane_key.startswith("P14-"):
                    missing.append(f"manifest:anchor_packet:lane_key={packet_lane_key}")
                    continue
                if not isinstance(anchor, str) or not anchor:
                    missing.append(f"manifest:{packet_lane_key}:anchor={anchor}")
                if not isinstance(packet_commit, str) or not HEX40_RE.fullmatch(packet_commit):
                    missing.append(f"manifest:{packet_lane_key}:surveyed_commit={packet_commit}")
                    continue
                if not isinstance(manifest_path, str) or not manifest_path:
                    missing.append(f"manifest:{packet_lane_key}:manifest_path={manifest_path}")
                    continue
                if not isinstance(survey_note_path, str) or not survey_note_path:
                    missing.append(f"manifest:{packet_lane_key}:survey_note_path={survey_note_path}")
                if not isinstance(ready_next_gap, str):
                    missing.append(f"manifest:{packet_lane_key}:ready_next_gap={ready_next_gap}")
                if not isinstance(blocked_gap, str) or not blocked_gap:
                    missing.append(f"manifest:{packet_lane_key}:blocked_gap={blocked_gap}")
                    continue

                anchor_manifest = load_json(manifest_path, json_decode_errors)
                if anchor_manifest is None:
                    continue
                if anchor_manifest.get("phase") != "Phase 14":
                    missing.append(f"{manifest_path}:phase")
                if anchor_manifest.get("lane_key") != packet_lane_key:
                    missing.append(f"{manifest_path}:lane_key")
                if anchor_manifest.get("anchor") != anchor:
                    missing.append(f"{manifest_path}:anchor")
                if anchor_manifest.get("surveyed_commit") != packet_commit:
                    missing.append(f"{manifest_path}:surveyed_commit")

                expected_ready_next_gap, expected_blocked_gap = summarize_gap_ids(anchor_manifest)
                if ready_next_gap != expected_ready_next_gap:
                    missing.append(f"{manifest_path}:ready_next_gap")
                if blocked_gap != expected_blocked_gap:
                    missing.append(f"{manifest_path}:blocked_gap")

                if manifest_path == "zigux/tests/phase14_skbuff_bridge_manifest.json":
                    decision_checklist = anchor_manifest.get("decision_checklist")
                    if not isinstance(decision_checklist, list):
                        missing.append(f"{manifest_path}:decision_checklist")
                    else:
                        checklist_by_id: dict[str, dict[str, object]] = {}
                        for item in decision_checklist:
                            if not isinstance(item, dict):
                                missing.append(f"{manifest_path}:decision_checklist:item")
                                continue
                            item_id = item.get("id")
                            if not isinstance(item_id, str):
                                missing.append(
                                    f"{manifest_path}:decision_checklist:id={item_id}"
                                )
                                continue
                            checklist_by_id[item_id] = item

                        for decision_id, required_symbols in (
                            REQUIRED_SKBUFF_DECISION_CHECKLIST.items()
                        ):
                            entry = checklist_by_id.get(decision_id)
                            if entry is None:
                                missing.append(
                                    f"{manifest_path}:decision_checklist:{decision_id}"
                                )
                                continue
                            if entry.get("ownership") != "stay_in_c":
                                missing.append(
                                    f"{manifest_path}:decision_checklist:{decision_id}:ownership={entry.get('ownership')}"
                                )
                            anchor_symbols = entry.get("anchor_symbols")
                            if not isinstance(anchor_symbols, list):
                                missing.append(
                                    f"{manifest_path}:decision_checklist:{decision_id}:anchor_symbols"
                                )
                                continue
                            for symbol in required_symbols:
                                if symbol not in anchor_symbols:
                                    missing.append(
                                        f"{manifest_path}:decision_checklist:{decision_id}:anchor_symbol:{symbol}"
                                    )

                expected_survey_anchor_lines.append(
                    (packet_lane_key, format_anchor_packet_survey_line(packet))
                )

        for packet_lane_key, survey_line in expected_survey_anchor_lines:
            if survey_line not in survey_text:
                missing.append(f"survey:anchor_packet:{packet_lane_key}")

        smoke_commands = manifest.get("smoke_commands")
        expected_smoke_commands = [
            "make -C zigux phase14-validate",
            "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
            "make -C zigux phase14",
        ]
        if smoke_commands != expected_smoke_commands:
            missing.append("manifest:smoke_commands")

        smoke_shard_commands = manifest.get("smoke_shard_commands")
        expected_smoke_shard_commands = [
            "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
            "make -C zigux phase14-smoke",
        ]
        if smoke_shard_commands != expected_smoke_shard_commands:
            missing.append("manifest:smoke_shard_commands")

        compile_shards = manifest.get("compile_shards")
        if compile_shards != EXPECTED_COMPILE_SHARDS:
            missing.append("manifest:compile_shards")

        summary = manifest.get("survey_summary")
        if not isinstance(summary, dict):
            missing.append("manifest:survey_summary")
        else:
            for key in [
                "phase14_validate_script_present",
                "phase14_validate_entrypoint_present",
                "phase14_build_has_shared_smoke_step",
                "phase14_build_has_smoke_shard_step",
                "phase14_make_target_present",
                "phase14_make_smoke_target_present",
                "workflow_runs_phase14_validate",
                "workflow_runs_phase14_build",
                "workflow_runs_phase14_smoke_shard",
                "review_checklist_has_phase14_smoke_prompt",
                "review_checklist_has_productization_prompt",
                "smoke_note_records_owner_and_rollback",
                "smoke_note_records_transfer_rationale",
                "freeze_map_lists_workqueue_c",
                "freeze_map_lists_skbuff_c",
                "freeze_map_lists_ring_buffer_c",
                "freeze_map_lists_tree_c",
            ]:
                if summary.get(key) is not True:
                    missing.append(f"manifest:survey_summary:{key}={summary.get(key)}")

    build_text = text("zigux/tests/phase14_build.zig")
    build_names = BUILD_TEST_NAME_RE.findall(build_text)
    if build_names != EXPECTED_BUILD_TEST_NAMES:
        missing.append("build:test_names")

    depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
    if len(depend_steps) != 6:
        missing.append(f"build:depend_step_count={len(depend_steps)}")

    if json_decode_errors or missing:
        print("PHASE14_VALIDATION=fail")
        if json_decode_errors:
            print("PHASE14_JSON_DECODE_ERRORS_START")
            for item in json_decode_errors:
                print(item)
            print("PHASE14_JSON_DECODE_ERRORS_END")
        if missing:
            print("PHASE14_VALIDATION_MISSING_START")
            for item in missing:
                print(item)
            print("PHASE14_VALIDATION_MISSING_END")
        return 1

    print("PHASE14_VALIDATION=pass")
    print(f"PHASE14_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "PHASE14_REQUIRED_MARKER_COUNT="
        f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(SCRIPT_README_MARKERS) + len(RELEASE_MARKERS) + len(SKBUFF_SURVEY_MARKERS) + len(CHECKLIST_MARKERS) + len(BUILD_MARKERS)}"
    )
    print(f"PHASE14_BUILD_TEST_COUNT={len(build_names)}")
    print(f"PHASE14_BUILD_DEPEND_STEP_COUNT={len(depend_steps)}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the validator's internal self-test coverage checks",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()
    return run_validation()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
