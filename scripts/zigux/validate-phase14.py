#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase14-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
TESTS_README_CHECKER_PATH = "scripts/zigux/check-phase14-tests-readme-smoke-summary.py"

FILES = [
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    TESTS_README_CHECKER_PATH,
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "Documentation/zigux/phase14-workqueue-bridge-survey.md",
    "Documentation/zigux/phase14-skbuff-bridge-survey.md",
    "Documentation/zigux/phase14-ring-buffer-survey.md",
    "Documentation/zigux/phase14-rcu-tree-survey.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/README.md",
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
    "phase14-smoke:",
    "$(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14-test:",
    "$(ZIG) build test --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14: phase14-validate phase14-smoke phase14-test",
]

MAKE_EXACT_LINES = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py",
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

TESTS_README_PACKET_ANCHOR = "  * `zigux/tests/phase14_build.zig`"
TESTS_README_EXACT_LINES = [
    "  * `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "  * `zigux/tests/phase14_workqueue_reviewability.zig`",
    "  * `zigux/tests/phase14_workqueue_bridge_manifest.json`",
    "  * `zigux/tests/phase14_skbuff_bridge_manifest.json`",
    "  * `zigux/tests/phase14_ring_buffer_manifest.json`",
    "  * `zigux/tests/phase14_rcu_tree_manifest.json`",
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
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "phase14_workqueue_bridge_manifest.json",
    "phase14_skbuff_bridge_manifest.json",
    "phase14_ring_buffer_manifest.json",
    "phase14_rcu_tree_manifest.json",
    "phase14-workqueue-reviewability-tests",
    "phase14_workqueue_reviewability.zig",
]

RELEASE_BOUNDARY_MARKERS = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "make -C zigux phase14-test",
    "PHASE14_SHARED_SMOKE_GATE_COUNT=1",
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0",
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
    "if the change touches the shared Phase 14 smoke packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/freeze-map.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, `zigux/tests/phase14_ring_buffer_manifest.json`, `zigux/tests/phase14_rcu_tree_manifest.json`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, `make -C zigux phase14-test`, `zig build test --build-file zigux/tests/phase14_build.zig --summary all`, and `make -C zigux phase14` still agree on the same study-only stay-in-C posture, with `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` kept explicit as the two boundary-study-only anchors and `kernel/rcu/tree.c` plus `net/core/skbuff.c` kept explicit as the two freeze-in-C-governed anchors, without implying an active deep-core port claim?",
]

BUILD_MARKERS = [
    "phase14-workqueue-bridge-tests",
    "phase14-workqueue-reviewability-tests",
    "phase14-skbuff-bridge-tests",
    "phase14-ring-buffer-survey-tests",
    "phase14-rcu-tree-survey-tests",
    "phase14-end-to-end-smoke-tests",
    "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
    "test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
    "test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);",
    "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
    "test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
    "test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
    "test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
]

FORBIDDEN_SMOKE_DEPENDENCIES = [
    "smoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
    "smoke_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);",
    "smoke_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
    "smoke_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
    "smoke_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
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


def run_python_checker(
    root: Path,
    rel_path: str,
    extra_args: list[str] | None = None,
) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(root / rel_path), *(extra_args or [])],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    output_parts = [part.strip() for part in (result.stdout, result.stderr) if part.strip()]
    return result.returncode, "\n".join(output_parts)


def require_exact_line_once(missing: list[str], name: str, source: str, markers: list[str]) -> None:
    lines = source.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            missing.append(f"{name}:exact_line:{marker}:count={count}")


def require_lines_after_anchor(
    missing: list[str],
    name: str,
    source: str,
    anchor_line: str,
    expected_lines: list[str],
    label: str,
) -> None:
    lines = source.splitlines()
    anchor_count = sum(1 for line in lines if line == anchor_line)
    if anchor_count != 1:
        missing.append(f"{name}:exact_line:{anchor_line}:count={anchor_count}")
        return

    anchor_index = lines.index(anchor_line)
    actual_lines = lines[anchor_index + 1 : anchor_index + 1 + len(expected_lines)]
    if actual_lines != expected_lines:
        missing.append(f"{name}:{label}")


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

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        checker_path = tmp_root / TESTS_README_CHECKER_PATH
        checker_path.parent.mkdir(parents=True, exist_ok=True)
        checker_path.write_text(
            "print('phase14 tests-readme smoke summary validated')\nraise SystemExit(0)\n",
            encoding="utf-8",
        )
        returncode, output = run_python_checker(tmp_root, TESTS_README_CHECKER_PATH)
        if returncode != 0 or output != "phase14 tests-readme smoke summary validated":
            print("PHASE14_SELF_TEST=fail")
            print("SELF_TEST_REASON=unexpected_tests_readme_checker_success_result")
            print(f"SELF_TEST_CHECKER_RETURN_CODE={returncode}")
            print(f"SELF_TEST_CHECKER_OUTPUT={output}")
            return 1

        checker_path.write_text(
            "import sys\nprint(' '.join(sys.argv[1:]) or 'no-args')\nraise SystemExit(0)\n",
            encoding="utf-8",
        )
        returncode, output = run_python_checker(
            tmp_root,
            TESTS_README_CHECKER_PATH,
            ["--self-test"],
        )
        if returncode != 0 or output != "--self-test":
            print("PHASE14_SELF_TEST=fail")
            print("SELF_TEST_REASON=unexpected_tests_readme_checker_arg_replay_result")
            print(f"SELF_TEST_CHECKER_RETURN_CODE={returncode}")
            print(f"SELF_TEST_CHECKER_OUTPUT={output}")
            return 1

        checker_path.write_text(
            "import sys\nprint('phase14 tests-readme smoke summary failed', file=sys.stderr)\nraise SystemExit(1)\n",
            encoding="utf-8",
        )
        returncode, output = run_python_checker(tmp_root, TESTS_README_CHECKER_PATH)
        if returncode != 1 or output != "phase14 tests-readme smoke summary failed":
            print("PHASE14_SELF_TEST=fail")
            print("SELF_TEST_REASON=unexpected_tests_readme_checker_failure_result")
            print(f"SELF_TEST_CHECKER_RETURN_CODE={returncode}")
            print(f"SELF_TEST_CHECKER_OUTPUT={output}")
            return 1

    missing_reviewability_build = "\n".join(
        [f'.name = "{name}"' for name in EXPECTED_BUILD_TEST_NAMES]
        + ["smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);"]
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

    good_scripts_readme = "\n".join(SCRIPT_README_MARKERS) + "\n"
    missing_scripts_readme_markers = [
        marker
        for marker in SCRIPT_README_MARKERS
        if marker not in good_scripts_readme.replace("`make -C zigux phase14-smoke`", "", 1)
    ]
    if missing_scripts_readme_markers != ["`make -C zigux phase14-smoke`"]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_scripts_readme_marker_gap")
        print("SELF_TEST_MARKERS_START")
        for item in missing_scripts_readme_markers:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    good_tests_readme = "\n".join(
        [
            "# zigux/tests",
            "",
            "Key entrypoints",
            TESTS_README_PACKET_ANCHOR,
            *TESTS_README_EXACT_LINES,
            "  * `zigux/tests/phase14_ring_buffer_survey.zig`",
        ]
    ) + "\n"
    exact_line_missing = []
    require_exact_line_once(
        exact_line_missing,
        "tests_readme",
        good_tests_readme.replace(f"{TESTS_README_EXACT_LINES[0]}\n", "", 1),
        TESTS_README_EXACT_LINES,
    )
    if exact_line_missing != [
        f"tests_readme:exact_line:{TESTS_README_EXACT_LINES[0]}:count=0"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_tests_readme_exact_line_gap")
        print("SELF_TEST_MARKERS_START")
        for item in exact_line_missing:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    packet_after_anchor_missing = []
    require_lines_after_anchor(
        packet_after_anchor_missing,
        "tests_readme",
        good_tests_readme.replace(
            "\n".join(
                [
                    TESTS_README_PACKET_ANCHOR,
                    TESTS_README_EXACT_LINES[0],
                    TESTS_README_EXACT_LINES[1],
                ]
            ),
            "\n".join(
                [
                    TESTS_README_PACKET_ANCHOR,
                    TESTS_README_EXACT_LINES[1],
                    TESTS_README_EXACT_LINES[0],
                ]
            ),
            1,
        ),
        TESTS_README_PACKET_ANCHOR,
        TESTS_README_EXACT_LINES,
        "phase14_smoke_packet_after_anchor",
    )
    if packet_after_anchor_missing != [
        "tests_readme:phase14_smoke_packet_after_anchor"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_tests_readme_packet_after_anchor_gap")
        print("SELF_TEST_MARKERS_START")
        for item in packet_after_anchor_missing:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    good_phase14_make = "\n".join(["phase14-validate:", *MAKE_EXACT_LINES]) + "\n"
    exact_line_missing: list[str] = []
    require_exact_line_once(
        exact_line_missing,
        "make",
        good_phase14_make.replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test\n",
            "",
            1,
        ),
        MAKE_EXACT_LINES,
    )
    if exact_line_missing != [
        "make:exact_line:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test:count=0"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_makefile_docs_root_selftest_gap_markers")
        print("SELF_TEST_MARKERS_START")
        for item in exact_line_missing:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    exact_line_missing = []
    require_exact_line_once(
        exact_line_missing,
        "make",
        good_phase14_make.replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test\n",
            "",
            1,
        ),
        MAKE_EXACT_LINES,
    )
    if exact_line_missing != [
        "make:exact_line:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test:count=0"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_makefile_rollback_selftest_gap_markers")
        print("SELF_TEST_MARKERS_START")
        for item in exact_line_missing:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    exact_line_missing = []
    require_exact_line_once(
        exact_line_missing,
        "make",
        good_phase14_make.replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py\n",
            "",
            1,
        ),
        MAKE_EXACT_LINES,
    )
    if exact_line_missing != [
        "make:exact_line:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py:count=0"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_makefile_rollback_route_gap_markers")
        print("SELF_TEST_MARKERS_START")
        for item in exact_line_missing:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    exact_line_missing = []
    require_exact_line_once(
        exact_line_missing,
        "make",
        good_phase14_make.replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test\n",
            "",
            1,
        ),
        MAKE_EXACT_LINES,
    )
    if exact_line_missing != [
        "make:exact_line:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test:count=0"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_makefile_release_boundary_selftest_gap_markers")
        print("SELF_TEST_MARKERS_START")
        for item in exact_line_missing:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    exact_line_missing = []
    require_exact_line_once(
        exact_line_missing,
        "make",
        good_phase14_make.replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py\n",
            "",
            1,
        ),
        MAKE_EXACT_LINES,
    )
    if exact_line_missing != [
        "make:exact_line:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py:count=0"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_makefile_release_boundary_route_gap_markers")
        print("SELF_TEST_MARKERS_START")
        for item in exact_line_missing:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    good_release_boundary = "\n".join(RELEASE_BOUNDARY_MARKERS) + "\n"
    missing_release_boundary_markers = [
        marker
        for marker in RELEASE_BOUNDARY_MARKERS
        if marker
        not in good_release_boundary.replace("make -C zigux phase14-test", "", 1)
    ]
    if missing_release_boundary_markers != ["make -C zigux phase14-test"]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_release_boundary_marker_gap")
        print("SELF_TEST_MARKERS_START")
        for item in missing_release_boundary_markers:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    forbidden_smoke_dependency_build = "\n".join(
        [
            "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
            "smoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
        ]
    )
    forbidden_smoke_markers = [
        marker for marker in FORBIDDEN_SMOKE_DEPENDENCIES if marker in forbidden_smoke_dependency_build
    ]
    if forbidden_smoke_markers != [
        "smoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_forbidden_smoke_dependency_markers")
        print("SELF_TEST_MARKERS_START")
        for item in forbidden_smoke_markers:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    forbidden_reviewability_smoke_dependency_build = "\n".join(
        [
            "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
            "smoke_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);",
        ]
    )
    forbidden_reviewability_smoke_markers = [
        marker
        for marker in FORBIDDEN_SMOKE_DEPENDENCIES
        if marker in forbidden_reviewability_smoke_dependency_build
    ]
    if forbidden_reviewability_smoke_markers != [
        "smoke_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);"
    ]:
        print("PHASE14_SELF_TEST=fail")
        print("SELF_TEST_REASON=unexpected_reviewability_forbidden_smoke_dependency_markers")
        print("SELF_TEST_MARKERS_START")
        for item in forbidden_reviewability_smoke_markers:
            print(item)
        print("SELF_TEST_MARKERS_END")
        return 1

    print("PHASE14_SELF_TEST=pass")
    print("PHASE14_SELF_TEST_JSON_ERROR_MARKER=bad.json:2:1:Expecting property name enclosed in double quotes")
    print("PHASE14_SELF_TEST_TESTS_README_CHECKER_PASS_MARKER=phase14 tests-readme smoke summary validated")
    print("PHASE14_SELF_TEST_TESTS_README_CHECKER_ARG_MARKER=--self-test")
    print("PHASE14_SELF_TEST_TESTS_README_CHECKER_FAIL_MARKER=phase14 tests-readme smoke summary failed")
    print("PHASE14_SELF_TEST_MISSING_REVIEWABILITY_MARKER=test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);")
    print("PHASE14_SELF_TEST_MISSING_SCRIPTS_README_SMOKE_ROUTE_MARKER=`make -C zigux phase14-smoke`")
    print(
        "PHASE14_SELF_TEST_TESTS_README_PACKET_LINE_COUNT="
        f"{len(TESTS_README_EXACT_LINES)}"
    )
    print(
        "PHASE14_SELF_TEST_TESTS_README_AFTER_ANCHOR_MARKER="
        "tests_readme:phase14_smoke_packet_after_anchor"
    )
    print("PHASE14_SELF_TEST_MISSING_DOCS_ROOT_SELFTEST_MARKER=\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test")
    print("PHASE14_SELF_TEST_MISSING_ROLLBACK_SELFTEST_MARKER=\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test")
    print("PHASE14_SELF_TEST_MISSING_ROLLBACK_ROUTE_MARKER=\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py")
    print("PHASE14_SELF_TEST_MISSING_RELEASE_BOUNDARY_SELFTEST_MARKER=\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test")
    print("PHASE14_SELF_TEST_MISSING_RELEASE_BOUNDARY_ROUTE_LINE_MARKER=\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py")
    print("PHASE14_SELF_TEST_MISSING_RELEASE_BOUNDARY_ROUTE_MARKER=make -C zigux phase14-test")
    print("PHASE14_SELF_TEST_FORBIDDEN_SMOKE_MARKER=smoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);")
    print("PHASE14_SELF_TEST_FORBIDDEN_REVIEWABILITY_SMOKE_MARKER=smoke_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);")
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

    tests_readme_checker_selftest_returncode, tests_readme_checker_selftest_output = run_python_checker(
        ROOT,
        TESTS_README_CHECKER_PATH,
        ["--self-test"],
    )
    if tests_readme_checker_selftest_returncode != 0:
        print("PHASE14_VALIDATION=fail")
        print("PHASE14_TESTS_README_CHECKER_SELF_TEST_OUTPUT_START")
        print(
            tests_readme_checker_selftest_output
            or "tests-readme smoke checker self-test exited without output"
        )
        print("PHASE14_TESTS_README_CHECKER_SELF_TEST_OUTPUT_END")
        return 1

    tests_readme_checker_returncode, tests_readme_checker_output = run_python_checker(
        ROOT, TESTS_README_CHECKER_PATH
    )
    if tests_readme_checker_returncode != 0:
        print("PHASE14_VALIDATION=fail")
        print("PHASE14_TESTS_README_CHECKER_OUTPUT_START")
        print(tests_readme_checker_output or "tests-readme smoke checker exited without output")
        print("PHASE14_TESTS_README_CHECKER_OUTPUT_END")
        return 1

    survey_text = text("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
    release_boundary_text = text("Documentation/zigux/phase14-release-boundary-survey.md")
    skbuff_survey_text = text("Documentation/zigux/phase14-skbuff-bridge-survey.md")
    missing: list[str] = []
    json_decode_errors: list[str] = []
    make_text = text("zigux/Makefile")
    tests_readme_text = text("zigux/tests/README.md")
    for name, source, markers in [
        ("scripts_readme", text("scripts/zigux/README.md"), SCRIPT_README_MARKERS),
        ("make", make_text, MAKE_MARKERS),
        ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
        ("survey", survey_text, RELEASE_MARKERS),
        ("release_boundary", release_boundary_text, RELEASE_BOUNDARY_MARKERS),
        ("skbuff_survey", skbuff_survey_text, SKBUFF_SURVEY_MARKERS),
        ("checklist", text("Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS),
        ("build", text("zigux/tests/phase14_build.zig"), BUILD_MARKERS),
        ]:
        for marker in markers:
            if marker not in source:
                missing.append(f"{name}:{marker}")
    require_exact_line_once(missing, "make", make_text, MAKE_EXACT_LINES)
    require_exact_line_once(
        missing,
        "tests_readme",
        tests_readme_text,
        TESTS_README_EXACT_LINES,
    )
    require_lines_after_anchor(
        missing,
        "tests_readme",
        tests_readme_text,
        TESTS_README_PACKET_ANCHOR,
        TESTS_README_EXACT_LINES,
        "phase14_smoke_packet_after_anchor",
    )

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
                "zigux/tests/README.md",
                "Documentation/zigux/README.md",
                "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
                "Documentation/zigux/phase14-release-boundary-survey.md",
                "Documentation/zigux/phase14-core-boundary-traceability.md",
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
            "make -C zigux phase14-test",
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

    forbidden_smoke_dependencies = [
        marker for marker in FORBIDDEN_SMOKE_DEPENDENCIES if marker in build_text
    ]
    for marker in forbidden_smoke_dependencies:
        missing.append(f"build:forbidden_smoke_dependency:{marker}")

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
        f"{len(MAKE_MARKERS) + len(MAKE_EXACT_LINES) + len(WORKFLOW_MARKERS) + len(SCRIPT_README_MARKERS) + len(TESTS_README_EXACT_LINES) + 1 + len(RELEASE_MARKERS) + len(RELEASE_BOUNDARY_MARKERS) + len(SKBUFF_SURVEY_MARKERS) + len(CHECKLIST_MARKERS) + len(BUILD_MARKERS)}"
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
