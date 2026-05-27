#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase14-end-to-end-smoke-survey.md").exists() and (
            candidate / "zigux/Makefile"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SMOKE_SURVEY_PATH = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
RELEASE_BOUNDARY_PATH = "Documentation/zigux/phase14-release-boundary-survey.md"
PRODUCTIZATION_GAP_PATH = "Documentation/zigux/phase14-productization-gap-survey.md"
SHARED_SMOKE_GAP_PATH = "Documentation/zigux/phase14-shared-smoke-current-master-gap.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
ATTACHED_TOOLCHAIN_GUIDANCE_PATH = "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md"
CORE_BOUNDARY_TRACEABILITY_PATH = "Documentation/zigux/phase14-core-boundary-traceability.md"
COMPILE_SHARD_MATRIX_SURVEY_PATH = "Documentation/zigux/phase14-compile-shard-matrix-survey.md"
WORKQUEUE_SLICE_PATH = "Documentation/zigux/phase14-workqueue-bridge-slice.md"
WORKQUEUE_SURVEY_PATH = "Documentation/zigux/phase14-workqueue-bridge-survey.md"
RING_BUFFER_SURVEY_PATH = "Documentation/zigux/phase14-ring-buffer-survey.md"
SKBUFF_SURVEY_PATH = "Documentation/zigux/phase14-skbuff-bridge-survey.md"
RCU_TREE_SURVEY_PATH = "Documentation/zigux/phase14-rcu-tree-survey.md"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SHARED_SMOKE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-shared-smoke-route.py"
RELEASE_BOUNDARY_CHECKER_PATH = "scripts/zigux/check-phase14-release-boundary-exact-counts.py"
ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH = (
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
)
SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH = (
    "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py"
)
SKBUFF_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-skbuff-compile-route.py"
RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = (
    "scripts/zigux/check-phase14-ring-buffer-compile-route.py"
)
RCU_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-rcu-compile-route.py"
RCU_ROLLBACK_GUARDRAIL_CHECKER_PATH = "scripts/zigux/check-phase14-rcu-rollback-guardrail.py"
TESTS_README_CHECKER_PATH = "scripts/zigux/check-phase14-tests-readme-smoke-summary.py"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
END_TO_END_SMOKE_MANIFEST_PATH = "zigux/tests/phase14_end_to_end_smoke_manifest.json"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
WORKQUEUE_BRIDGE_PATH = "kernel/workqueue_bridge.zig"
WORKQUEUE_BRIDGE_TEST_PATH = "zigux/tests/phase14_workqueue_bridge.zig"
WORKQUEUE_REVIEWABILITY_PATH = "zigux/tests/phase14_workqueue_reviewability.zig"
WORKQUEUE_MANIFEST_PATH = "zigux/tests/phase14_workqueue_bridge_manifest.json"
RING_BUFFER_MANIFEST_PATH = "zigux/tests/phase14_ring_buffer_manifest.json"
VALIDATOR_PATH = "scripts/zigux/validate-phase14.py"

REQUIRED_FILES = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    SMOKE_SURVEY_PATH,
    RELEASE_BOUNDARY_PATH,
    PRODUCTIZATION_GAP_PATH,
    SHARED_SMOKE_GAP_PATH,
    FREEZE_MAP_PATH,
    ATTACHED_TOOLCHAIN_GUIDANCE_PATH,
    CORE_BOUNDARY_TRACEABILITY_PATH,
    COMPILE_SHARD_MATRIX_SURVEY_PATH,
    WORKQUEUE_SLICE_PATH,
    WORKQUEUE_SURVEY_PATH,
    RING_BUFFER_SURVEY_PATH,
    SKBUFF_SURVEY_PATH,
    RCU_TREE_SURVEY_PATH,
    STUDY_ONLY_ACCOUNTING_PATH,
    SCRIPTS_README_PATH,
    SHARED_SMOKE_ROUTE_CHECKER_PATH,
    RELEASE_BOUNDARY_CHECKER_PATH,
    ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH,
    SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH,
    SKBUFF_COMPILE_ROUTE_CHECKER_PATH,
    RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,
    RCU_COMPILE_ROUTE_CHECKER_PATH,
    RCU_ROLLBACK_GUARDRAIL_CHECKER_PATH,
    TESTS_README_CHECKER_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
    END_TO_END_SMOKE_MANIFEST_PATH,
    WORKFLOW_PATH,
    WORKQUEUE_BRIDGE_PATH,
    WORKQUEUE_BRIDGE_TEST_PATH,
    WORKQUEUE_REVIEWABILITY_PATH,
    WORKQUEUE_MANIFEST_PATH,
    RING_BUFFER_MANIFEST_PATH,
    VALIDATOR_PATH,
]

SUBCHECKER_PATHS = [
    SHARED_SMOKE_ROUTE_CHECKER_PATH,
    TESTS_README_CHECKER_PATH,
    ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH,
    SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH,
    SKBUFF_COMPILE_ROUTE_CHECKER_PATH,
    RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,
    RCU_COMPILE_ROUTE_CHECKER_PATH,
    RCU_ROLLBACK_GUARDRAIL_CHECKER_PATH,
    RELEASE_BOUNDARY_CHECKER_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
        "scripts/zigux/validate-phase14.py",
        "zigux/tests/phase14_workqueue_reviewability.zig",
        "while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors",
    ],
    REVIEW_CHECKLIST_PATH: [
        "Use this checklist before opening or merging Zigux product work.",
        "if the change touches the shared Phase 14 smoke packet",
        "`scripts/zigux/validate-phase14.py` and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
        "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, and `zigux/tests/phase14_ring_buffer_survey.zig` explicit as the directly readable study-only workqueue-and-ring-buffer companions",
        "`zigux/Makefile` framed as readable current evidence for the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with the returned `make -C zigux phase14-validate` gate while `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
        "`zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` framed as exact-readback gaps",
    ],
    SMOKE_SURVEY_PATH: [
        "  * rollback owner: `Repo Tooling Pod`",
        "  * status bucket: `study_only`",
        "  * rollback threshold: `0` tolerated same-packet drifts",
        "`phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`",
        "  * directly readable ring-buffer survey companion:",
        "    * `zigux/tests/phase14_ring_buffer_survey.zig`",
        "  * executable packet members still unrecovered through this lane's exact contents path:",
        "    * `zigux/tests/phase14_build.zig`",
        "    * `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    ],
    RELEASE_BOUNDARY_PATH: [
        "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` now returns through the current contents path and keeps the release-facing exact-count posture aligned with the current shared reminder packet",
        "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
        "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
    ],
    PRODUCTIZATION_GAP_PATH: [
        "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py` now returns through the current contents path and keeps the tests-root reminder aligned with the same recovered study-only split without promoting the broader `phase14-smoke`, `phase14-test`, or `phase14` wrappers",
        "the directly readable release-boundary exact-count guard",
        "the readable non-owner Makefile body with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
        "`zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
    ],
    SHARED_SMOKE_GAP_PATH: [
        "current public raw-file readback of `zigux/tests/phase14_end_to_end_smoke_manifest.json` keeps the shared smoke surface inventory and compile-shard catalog visible, and its live body now matches the narrowed single-gate posture too: `make -C zigux phase14-validate` stays the only shared smoke Makefile command, `smoke_shard_commands` now records the raw focused build-file route `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`, and the manifest still does not advertise the older `make -C zigux phase14-test`, `make -C zigux phase14`, `make -C zigux phase14-smoke`, or workflow-backed build or smoke coverage that the readable current Makefile body and readable bootstrap workflow still omit",
        "the now-aligned raw-manifest posture",
        "and the continued absence of the broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers on current `master`",
        "`zigux/tests/phase14_ring_buffer_survey.zig` is directly readable again through the current contents path as a ring-buffer-local survey companion",
    ],
    FREEZE_MAP_PATH: [
        "## Study / Boundary Only",
        "- `kernel/workqueue.c`",
        "- `kernel/trace/ring_buffer.c`",
        "shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set",
        "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file",
    ],
    CORE_BOUNDARY_TRACEABILITY_PATH: [
        "`kernel/workqueue.c`: `Study / Boundary Only`",
        "`net/core/skbuff.c`: `Freeze In C Initially`",
        "Documentation/zigux/phase14-workqueue-bridge-survey.md",
        "public GitHub web readback confirms the returned bridge, focused gate, manifest, and build shard",
    ],
    COMPILE_SHARD_MATRIX_SURVEY_PATH: [
        "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
        "- shared gate: `make -C zigux phase14-validate`",
        "- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
        "- checker: `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
        "- skbuff compile-route checker: `scripts/zigux/check-phase14-skbuff-compile-route.py`",
        "- ring-buffer compile-route checker: `scripts/zigux/check-phase14-ring-buffer-compile-route.py`",
        "- rcu compile-route checker: `scripts/zigux/check-phase14-rcu-compile-route.py`",
    ],
    WORKQUEUE_SLICE_PATH: [
        "  * `PHASE14_LANE_KEY=P14-L04`",
        "  * `PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`",
        "  * `PHASE14_DIRECT_ZIG_TEST=zigux/tests/phase14_workqueue_bridge.zig`",
    ],
    WORKQUEUE_SURVEY_PATH: [
        "`PHASE14_ANCHOR=kernel/workqueue.c`",
        "`PHASE14_BLOCKER=phase14-workqueue-live-execution-blocker`",
        "`zig test zigux/tests/phase14_workqueue_reviewability.zig`",
    ],
    RING_BUFFER_SURVEY_PATH: [
        "`PHASE14_STATUS=study_only`",
        "`phase14-ring-buffer-maintenance-handoff`",
        "`phase14-ring-buffer-tracefs-reader-serialization-followup`",
        "`zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    ],
    SKBUFF_SURVEY_PATH: [
        "`PHASE14_LANE_KEY=P14-L11`",
        "`PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`",
        "current `master` ships the bounded skbuff anchor packet again through `net/core/skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, and `zigux/tests/phase14_build.zig`",
        "`zigux/tests/phase14_build.zig` wires `../../net/core/skbuff_bridge.zig` and `phase14_skbuff_bridge.zig` into the dedicated Phase 14 build shard, so there is now a live skbuff-local review route on current `master`",
    ],
    RCU_TREE_SURVEY_PATH: [
        "`PHASE14_LANE_KEY=P14-L16`",
        "`PHASE14_STATUS_BUCKET=freeze_in_c`",
        "`PHASE14_ANCHOR=kernel/rcu/tree.c`",
        "`PHASE14_BLOCKED_GAP=phase14-rcu-tree-bridge-blocker`",
        "`phase14-rcu-tree-rollback-threshold-guardrail`",
        "rollback owner: `Repo Tooling Pod`",
        "`Architecture Council` reopen record",
        "parity scorecard evidence and benchmark notes",
        "validation replay command and evidence archive path",
    ],
    STUDY_ONLY_ACCOUNTING_PATH: [
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only",
        "`kernel/workqueue.c` remains a boundary-study target first, not a rewrite target",
        "`kernel/trace/ring_buffer.c` remains a boundary-study target first, not a rewrite target",
    ],
    SCRIPTS_README_PATH: [
        "## Phase 14",
        "Phase 14 flow - the current scripts-root shared smoke packet stays reviewable",
        "`scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, and `zigux/Makefile` keep the directly readable shared-smoke route proof",
        "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` keep the directly readable workqueue reviewability shard explicit",
        "shared reminder truthfulness around the returned study-only packet and the single `make -C zigux phase14-validate` gate",
    ],
    SHARED_SMOKE_ROUTE_CHECKER_PATH: [
        "PHASE14_CHECK_PACKET=shared_smoke_route",
        "PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass",
        "run: make -C zigux phase14-validate",
    ],
    RELEASE_BOUNDARY_CHECKER_PATH: [
        "PHASE14_CHECK_PACKET=release_boundary_exact_counts",
        "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass",
        'SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")',
    ],
    ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH: [
        "PHASE14_CHECK_PACKET=rollback_threshold_sequencing",
        "PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass",
        "phase14 rollback-threshold sequencing packet validated",
    ],
    SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH: [
        "PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_SELF_TEST=pass",
        "`PHASE14_LANE_KEY=P14-L11`",
        "`phase14-skbuff-live-ownership-blocker`",
        "Check that the dedicated Phase 14 skbuff survey stays aligned with the current review-only stay-in-C guardrail wording.",
    ],
    SKBUFF_COMPILE_ROUTE_CHECKER_PATH: [
        "PHASE14_CHECK_PACKET=skbuff_compile_route",
        "PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=pass",
        '"phase14-skbuff-bridge-tests"',
        '"phase14-skbuff-live-ownership-blocker"',
    ],
    RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH: [
        "PHASE14_CHECK_PACKET=ring_buffer_compile_route",
        "PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST=pass",
        '"phase14-ring-buffer-survey-tests"',
        '"phase14-ring-buffer-zig-port-blocker"',
    ],
    RCU_COMPILE_ROUTE_CHECKER_PATH: [
        "PHASE14_CHECK_PACKET=rcu_compile_route",
        "PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=pass",
        '"phase14-rcu-tree-survey-tests"',
        '"phase14-rcu-tree-bridge-blocker"',
    ],
    RCU_ROLLBACK_GUARDRAIL_CHECKER_PATH: [
        "PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST=pass",
        "`PHASE14_LANE_KEY=P14-L16`",
        "`phase14-rcu-tree-rollback-threshold-guardrail`",
        "Check that the dedicated Phase 14 RCU rollback note stays aligned",
    ],
    TESTS_README_CHECKER_PATH: [
        "Check that the shared Phase 14 tests-root reminder stays aligned with repo reality.",
        "PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST=pass",
        'SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")',
    ],
    TESTS_README_PATH: [
        "## Phase 14 shared smoke packet",
        "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
        "`scripts/zigux/validate-phase14.py`",
        "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
        "`zigux/tests/phase14_workqueue_reviewability.zig`",
    ],
    MAKEFILE_PATH: [
        "phase14-validate:",
        "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
        "scripts/zigux/check-phase14-shared-smoke-route.py",
        "scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
        "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
        "scripts/zigux/validate-phase14.py --self-test",
        "scripts/zigux/validate-phase14.py",
        "scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
        "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
        "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py --self-test",
        "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py",
        "scripts/zigux/check-phase14-rcu-rollback-guardrail.py --self-test",
        "scripts/zigux/check-phase14-rcu-rollback-guardrail.py",
        "scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
        "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    ],
    END_TO_END_SMOKE_MANIFEST_PATH: [
        '"shared_smoke_surfaces": [',
        '"scripts/zigux/check-phase14-rollback-threshold-sequencing.py"',
        '"phase14_validate_runs_rollback_threshold_sequencing": true',
        '"scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py"',
        '"phase14_validate_runs_skbuff_stay_in_c_guardrail": true',
        '"scripts/zigux/check-phase14-skbuff-compile-route.py"',
        '"shared_manifest_records_skbuff_compile_route_checker": true',
        '"scripts/zigux/check-phase14-ring-buffer-compile-route.py"',
        '"Documentation/zigux/phase14-core-boundary-traceability.md"',
        '"scripts/zigux/check-phase14-release-boundary-exact-counts.py"',
        '"smoke_commands": [',
        '"smoke_shard_commands": [',
        '"zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"',
        '"phase14_make_smoke_target_present": false',
        '"smoke_note_records_rollback_threshold": true',
        '"scripts/zigux/check-phase14-rcu-compile-route.py"',
        '"phase14_validate_runs_rcu_compile_route_checker": true',
        '"shared_manifest_records_rcu_compile_route_checker": true',
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 14 shared smoke route checker",
        "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
        "- name: Run current Phase 14 validate route",
        "run: make -C zigux phase14-validate",
    ],
    WORKQUEUE_BRIDGE_PATH: [
        'return "phase14-workqueue-scheduler-visible-worker-state-refinement";',
        '.posture = "blocked_maintenance",',
        "zigux/tests/phase14_workqueue_reviewability.zig",
    ],
    WORKQUEUE_BRIDGE_TEST_PATH: [
        'try std.testing.expectEqualStrings("phase14-workqueue-scheduler-visible-worker-state-refinement", workqueue_bridge.WorkqueueBridgeLab.currentSliceId());',
        'try std.testing.expect(std.mem.indexOf(u8, handoff.next_future_target, "blocked maintenance") != null);',
    ],
    WORKQUEUE_REVIEWABILITY_PATH: [
        'try std.testing.expectEqualStrings("P14-L04", manifest.lane_key);',
        '"zig test zigux/tests/phase14_workqueue_reviewability.zig"',
        '"blocked maintenance"',
    ],
    WORKQUEUE_MANIFEST_PATH: [
        '"lane_key": "P14-L04"',
        '"current_lane_posture": "blocked_maintenance"',
        '"zig test zigux/tests/phase14_workqueue_reviewability.zig"',
        '"phase14-workqueue-live-execution-blocker"',
    ],
    RING_BUFFER_MANIFEST_PATH: [
        '"lane_key": "P14-L08"',
        '"current_lane_posture": "maintenance_mode"',
        '"phase14-ring-buffer-maintenance-handoff"',
        '"zig test zigux/tests/phase14_ring_buffer_survey.zig"',
    ],
    VALIDATOR_PATH: [
        "PHASE14_VALIDATION=pass",
        "PHASE14_VALIDATOR_SELF_TEST=pass",
        "REQUIRED_FILES = [",
        "REQUIRED_MARKERS = {",
    ],
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: str) -> str:
    titles = {
        DOCS_README_PATH: "# Zigux Documentation",
        REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
        SMOKE_SURVEY_PATH: "# Phase 14 End-to-End Smoke Survey",
        RELEASE_BOUNDARY_PATH: "# Phase 14 Release Boundary Survey",
        PRODUCTIZATION_GAP_PATH: "# Phase 14 Productization Gap Survey",
        SHARED_SMOKE_GAP_PATH: "# Phase 14 Shared Smoke Current-Master Gap",
        FREEZE_MAP_PATH: "# Zigux Freeze Map",
        ATTACHED_TOOLCHAIN_GUIDANCE_PATH: "# Phase 14 Attached Toolchain Guidance Gap",
        CORE_BOUNDARY_TRACEABILITY_PATH: "# Phase 14 Core Boundary Traceability",
        COMPILE_SHARD_MATRIX_SURVEY_PATH: "# Phase 14 Compile Shard Matrix Survey",
        WORKQUEUE_SLICE_PATH: "# Phase 14 Workqueue Bridge Slice",
        WORKQUEUE_SURVEY_PATH: "# Phase 14 Workqueue Bridge Survey",
        RING_BUFFER_SURVEY_PATH: "# Phase 14 Ring Buffer Survey",
        SKBUFF_SURVEY_PATH: "# Phase 14 Skbuff Bridge Survey",
        RCU_TREE_SURVEY_PATH: "# Phase 14 RCU Tree Survey",
        STUDY_ONLY_ACCOUNTING_PATH: "# Phase 15 Study-Only Anchor Accounting",
        SCRIPTS_README_PATH: "# scripts/zigux",
        TESTS_README_PATH: "# zigux/tests",
    }
    if rel_path == SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH:
        return (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "# PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_SELF_TEST=pass\n"
            "# `PHASE14_LANE_KEY=P14-L11`\n"
            "# `phase14-skbuff-live-ownership-blocker`\n"
            "# Check that the dedicated Phase 14 skbuff survey stays aligned with the current review-only stay-in-C guardrail wording.\n"
            'if "--self-test" in sys.argv:\n'
            '    print("PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_SELF_TEST=pass")\n'
            "else:\n"
            '    print("PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL=pass")\n'
        )
    if rel_path == SKBUFF_COMPILE_ROUTE_CHECKER_PATH:
        return (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "# PHASE14_CHECK_PACKET=skbuff_compile_route\n"
            "# PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=pass\n"
            '# "phase14-skbuff-bridge-tests"\n'
            '# "phase14-skbuff-live-ownership-blocker"\n'
            'if "--self-test" in sys.argv:\n'
            '    print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=pass")\n'
            "else:\n"
            '    print("PHASE14_SKBUFF_COMPILE_ROUTE=pass")\n'
        )
    if rel_path == RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH:
        return (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "# PHASE14_CHECK_PACKET=ring_buffer_compile_route\n"
            "# PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST=pass\n"
            '# "phase14-ring-buffer-survey-tests"\n'
            '# "phase14-ring-buffer-zig-port-blocker"\n'
            'if "--self-test" in sys.argv:\n'
            '    print("PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST=pass")\n'
            "else:\n"
            '    print("PHASE14_RING_BUFFER_COMPILE_ROUTE=pass")\n'
        )
    if rel_path == RCU_COMPILE_ROUTE_CHECKER_PATH:
        return (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "# PHASE14_CHECK_PACKET=rcu_compile_route\n"
            "# PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=pass\n"
            '# "phase14-rcu-tree-survey-tests"\n'
            '# "phase14-rcu-tree-bridge-blocker"\n'
            'if "--self-test" in sys.argv:\n'
            '    print("PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=pass")\n'
            "else:\n"
            '    print("PHASE14_RCU_COMPILE_ROUTE=pass")\n'
        )
    if rel_path == RCU_ROLLBACK_GUARDRAIL_CHECKER_PATH:
        return (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "# PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST=pass\n"
            "# `PHASE14_LANE_KEY=P14-L16`\n"
            "# `phase14-rcu-tree-rollback-threshold-guardrail`\n"
            "# Check that the dedicated Phase 14 RCU rollback note stays aligned\n"
            'if "--self-test" in sys.argv:\n'
            '    print("PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST=pass")\n'
            "else:\n"
            '    print("PHASE14_RCU_ROLLBACK_GUARDRAIL=pass")\n'
        )
    if rel_path in REQUIRED_MARKERS:
        title = titles.get(rel_path)
        if title is not None:
            return marker_fixture(title, REQUIRED_MARKERS[rel_path])
        return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n"
    if rel_path.endswith(".json"):
        return "{}\n"
    return ""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def checker_script_path(root: Path, rel_path: str) -> Path:
    candidate = root / rel_path
    if candidate.exists():
        return candidate
    return ROOT / rel_path


def run_guardrail_checker(root: Path, rel_path: str, *, self_test: bool) -> list[str]:
    command = [sys.executable, str(checker_script_path(root, rel_path))]
    if self_test:
        command.append("--self-test")
    else:
        command.extend(["--root", str(root)])

    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode == 0:
        return []

    output = [line for line in (completed.stdout + completed.stderr).splitlines() if line.strip()]
    if not output:
        output = ["checker exited with no output"]
    return [f"subcheck_fail:{rel_path}:{line}" for line in output]


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-validator-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")
        for rel_path in SUBCHECKER_PATHS:
            checker_failures = run_guardrail_checker(base, rel_path, self_test=True)
            if checker_failures:
                raise SystemExit(
                    "fixture tree should pass the dedicated Phase 14 checker self-tests "
                    f"but failed: {checker_failures!r}"
                )

        missing_file_cases = [
            SHARED_SMOKE_ROUTE_CHECKER_PATH,
            RELEASE_BOUNDARY_CHECKER_PATH,
            RING_BUFFER_SURVEY_PATH,
            ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH,
            SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH,
            SKBUFF_COMPILE_ROUTE_CHECKER_PATH,
            RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,
            RCU_COMPILE_ROUTE_CHECKER_PATH,
            RCU_TREE_SURVEY_PATH,
            RCU_ROLLBACK_GUARDRAIL_CHECKER_PATH,
            TESTS_README_CHECKER_PATH,
            END_TO_END_SMOKE_MANIFEST_PATH,
            FREEZE_MAP_PATH,
            WORKFLOW_PATH,
            WORKQUEUE_MANIFEST_PATH,
            RING_BUFFER_MANIFEST_PATH,
            COMPILE_SHARD_MATRIX_SURVEY_PATH,
        ]
        for rel_path in missing_file_cases:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][0]),
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][7]),
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][9]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][2]),
            (RELEASE_BOUNDARY_PATH, REQUIRED_MARKERS[RELEASE_BOUNDARY_PATH][1]),
            (PRODUCTIZATION_GAP_PATH, REQUIRED_MARKERS[PRODUCTIZATION_GAP_PATH][3]),
            (SHARED_SMOKE_GAP_PATH, REQUIRED_MARKERS[SHARED_SMOKE_GAP_PATH][3]),
            (FREEZE_MAP_PATH, REQUIRED_MARKERS[FREEZE_MAP_PATH][3]),
            (SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][2]),
            (COMPILE_SHARD_MATRIX_SURVEY_PATH, REQUIRED_MARKERS[COMPILE_SHARD_MATRIX_SURVEY_PATH][4]),
            (COMPILE_SHARD_MATRIX_SURVEY_PATH, REQUIRED_MARKERS[COMPILE_SHARD_MATRIX_SURVEY_PATH][5]),
            (COMPILE_SHARD_MATRIX_SURVEY_PATH, REQUIRED_MARKERS[COMPILE_SHARD_MATRIX_SURVEY_PATH][6]),
            (RING_BUFFER_SURVEY_PATH, REQUIRED_MARKERS[RING_BUFFER_SURVEY_PATH][2]),
            (
                RELEASE_BOUNDARY_CHECKER_PATH,
                REQUIRED_MARKERS[RELEASE_BOUNDARY_CHECKER_PATH][2],
            ),
            (
                ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH,
                REQUIRED_MARKERS[ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH][0],
            ),
            (
                SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH,
                REQUIRED_MARKERS[SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH][3],
            ),
            (
                SKBUFF_COMPILE_ROUTE_CHECKER_PATH,
                REQUIRED_MARKERS[SKBUFF_COMPILE_ROUTE_CHECKER_PATH][3],
            ),
            (
                RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,
                REQUIRED_MARKERS[RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH][3],
            ),
            (
                RCU_COMPILE_ROUTE_CHECKER_PATH,
                REQUIRED_MARKERS[RCU_COMPILE_ROUTE_CHECKER_PATH][3],
            ),
            (RCU_TREE_SURVEY_PATH, REQUIRED_MARKERS[RCU_TREE_SURVEY_PATH][4]),
            (WORKQUEUE_MANIFEST_PATH, REQUIRED_MARKERS[WORKQUEUE_MANIFEST_PATH][0]),
            (RING_BUFFER_MANIFEST_PATH, REQUIRED_MARKERS[RING_BUFFER_MANIFEST_PATH][0]),
            (SHARED_SMOKE_ROUTE_CHECKER_PATH, REQUIRED_MARKERS[SHARED_SMOKE_ROUTE_CHECKER_PATH][0]),
            (CORE_BOUNDARY_TRACEABILITY_PATH, REQUIRED_MARKERS[CORE_BOUNDARY_TRACEABILITY_PATH][3]),
            (SMOKE_SURVEY_PATH, REQUIRED_MARKERS[SMOKE_SURVEY_PATH][4]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][1]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][2]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][3]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][4]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][5]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][6]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][7]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][10]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][13]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][15]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][16]),
            (END_TO_END_SMOKE_MANIFEST_PATH, REQUIRED_MARKERS[END_TO_END_SMOKE_MANIFEST_PATH][17]),
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        case_count = len(missing_file_cases) + len(marker_cases)
        print("PHASE14_VALIDATOR_SELF_TEST=pass")
        print(f"PHASE14_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current bounded Phase 14 shared smoke packet around the live "
            "`phase14-validate` route, the shared route checker, the shared smoke manifest, "
            "the freeze-map study-only inventory, the release-boundary exact-count guard, "
            "the compile-shard matrix survey, the ring-buffer study-only packet, the dedicated "
            "rollback-threshold sequencing checker, the dedicated skbuff stay-in-C "
            "guardrail, the dedicated skbuff compile-route checker, the dedicated ring-buffer "
            "compile-route checker, the dedicated RCU compile-route checker, the dedicated "
            "RCU rollback guardrail, and the returned workqueue reviewability shard."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if not failures:
        for rel_path in SUBCHECKER_PATHS:
            failures.extend(
                run_guardrail_checker(
                    args.root,
                    rel_path,
                    self_test=False,
                )
            )
            if failures:
                break
    if failures:
        print("PHASE14_VALIDATION=fail")
        print("PHASE14_PACKET_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_PACKET_DRIFT_END")
        return 1

    print("PHASE14_VALIDATION=pass")
    print(f"PHASE14_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE14_REQUIRED_MARKER_COUNT={sum(len(m) for m in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
