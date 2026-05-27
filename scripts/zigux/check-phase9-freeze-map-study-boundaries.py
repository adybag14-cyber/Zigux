#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

ROADMAP_STUDY_ONLY_ANCHORS = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
)

PATH_REQUIREMENTS = {
    FREEZE_MAP_PATH: [
        "# Zigux Freeze Map",
        "`kernel/workqueue.c`",
        "`kernel/trace/ring_buffer.c`",
        "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
        "`Documentation/zigux/README.md`",
        "`Documentation/zigux/review-checklist.md`",
        "`scripts/zigux/README.md`",
        "`samples/zigux/README.md`",
        "`zigux/tests/README.md`",
        "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`",
        "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`",
        "`scripts/zigux/check-phase9-freeze-map-study-boundaries.py`",
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
        "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`",
        "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
        "`zigux/tests/runtime_loader_gap_manifest.json`",
        "`zigux/tests/runtime_loader_gap_survey.zig`",
        "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
        "`zigux/tests/phase9_build.zig`",
        "`zigux/kernel/runtime_loader.zig`",
        "`zigux/kernel/runtime_loader_contract.zig`",
        "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
        "`samples/zigux/runtime_bitmap_loader.zig`",
        "`samples/zigux/runtime_trace_events_loader.zig`",
        "`zigux/Makefile` explicit only as a readable non-owner surface whose live body now exposes bounded `phase9-runtime-atomic64-test`, `phase9-runtime-bitmap-test`, `phase9-runtime-loader-shared-test`, `phase9-runtime-loader-command-env-boundary-guard-test`, `phase9-runtime-trace-events-test`, `phase9-runtime-kretprobe-test`, and `phase9-test` routes",
    ],
    STUDY_ONLY_ACCOUNTING_PATH: [
        "# Phase 15 Study-Only Anchor Accounting",
        "PHASE15_STATUS=study_only_accounting_slice_landed",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "`kernel/workqueue.c`",
        "`kernel/trace/ring_buffer.c`",
        "`study_only`",
        "tracked outside the freeze-in-C scorecard",
        "this note is an inventory and handoff surface, not an approval record",
        "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
        "the freeze-map governance note, the parity scorecard, the handoff-next-steps survey, and the shared-summary gap note",
        "boundary-study target first, not a rewrite target",
        "remain future-only and not current product claims",
        "no Architecture Council approval is currently recorded for a deep-core status change",
        "a direct Zigux bridge for `kernel/workqueue.c`",
        "a direct Zigux bridge for `kernel/trace/ring_buffer.c`",
        "any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together",
    ],
    REVIEW_CHECKLIST_PATH: [
        "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
    ],
    DOCS_README_PATH: [
        "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-trace-events-runtime-packet.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
        "keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
        "keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.",
        "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.",
    ],
    LANE_SEQUENCING_PATH: [
        "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness",
    ],
    SCRIPTS_README_PATH: [
        "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
    ],
    SAMPLES_README_PATH: [
        "Keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit as the rejected re-init rollback companion for initialized, selftest-complete, and exited lifecycle checkpoints in the same direct runtime packet.",
        "Keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit as the paired rejected re-init plus rejected re-exit rollback companion after initialized direct activity and selftest-ready replay in the same direct runtime packet.",
        "Current `master` also keeps a narrower returned runtime kretprobe sample-side packet explicit through `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes in `zigux/tests/phase9_build.zig`.",
        "Keep `samples/zigux/runtime_bitmap_direct_init_contract.zig` explicit as the returned direct-init normalization companion proof for the same runtime bitmap starter, covering unsorted duplicate input collapse, nth-set ordering, formatted sparse-summary stability, and lifecycle-summary stability through selftest and exit.",
        "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
    ],
    TESTS_README_PATH: [
        "Keep the current bounded Phase 9 reminder packet explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`.",
        "keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` remain the current shipped runtime-pilot proof rather than a claim that broader runtime-loader or publication boundaries are solved",
        "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests` routes, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete",
        "keep the returned runtime kretprobe pilot packet distinct from those shared loader and bitmap reminders too: `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes are current family-local pilot evidence, but they still must not be used to imply that the broader shared runtime-loader packet, blocked publication boundaries, or install-root surfaces are complete",
        "without implying any Architecture Council approval for a freeze-map status change",
    ],
    WORKFLOW_PATH: [
        "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
        "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
        "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test",
        "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
        "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py",
        "zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig",
        "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
        "zig test samples/zigux/runtime_trace_events.zig",
        "zig test zigux/tests/runtime_trace_events_survey.zig",
    ],
}

CURRENT_PHASE9_MAKE_ROUTES = [
    "phase9-runtime-atomic64-test",
    "phase9-runtime-bitmap-test",
    "phase9-runtime-loader-shared-test",
    "phase9-runtime-loader-command-env-boundary-guard-test",
    "phase9-runtime-trace-events-test",
    "phase9-runtime-kretprobe-test",
    "phase9-first-loadable-runtime-module-parity-test",
    "phase9-test",
]

FORBIDDEN_PHASE9_MAKE_ROUTES = [
    "phase9",
    "phase9-validate",
    "phase9-runtime-trace-events-sample-tests",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / FREEZE_MAP_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_section_lines(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    collected: list[str] = []
    in_section = False
    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            collected.append(line)
    return collected


def extract_freeze_map_study_only_anchors(text: str) -> list[str]:
    anchors: list[str] = []
    for line in extract_section_lines(text, "## Study / Boundary Only"):
        stripped = line.strip()
        if stripped.startswith("- `") and stripped.endswith("`"):
            anchors.append(stripped[3:-1])
    return anchors


def extract_study_only_accounting_anchors(text: str) -> list[str]:
    anchors: list[str] = []
    for line in extract_section_lines(text, "## Study-Only Anchor Inventory"):
        stripped = line.strip()
        if stripped.startswith("### `") and stripped.endswith("`"):
            anchors.append(stripped[5:-1])
    return anchors


def find_makefile_phase9_routes(text: str) -> list[str]:
    routes: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(".PHONY:"):
            continue
        if stripped.startswith("phase9") and ":" in stripped:
            routes.append(stripped.split(":", 1)[0])
    return routes


def remove_makefile_route_definition(content: str, route: str) -> str:
    lines = content.splitlines()
    kept: list[str] = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{route}:"):
            skipping = True
            continue
        if skipping:
            if line.startswith("\t"):
                continue
            skipping = False
        kept.append(line)
    return "\n".join(kept) + "\n"


def validate_exact_study_only_anchor_inventory(
    failures: list[str], rel_path: str, actual: list[str]
) -> None:
    expected = list(ROADMAP_STUDY_ONLY_ANCHORS)
    if actual != expected:
        failures.append(
            f"study_only_anchor_mismatch:{rel_path}:expected={expected}:actual={actual}"
        )


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = list(PATH_REQUIREMENTS) + [MAKEFILE_PATH]
    for rel_path in required_paths:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in PATH_REQUIREMENTS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    freeze_map = read_text(root, FREEZE_MAP_PATH)
    validate_exact_study_only_anchor_inventory(
        failures, FREEZE_MAP_PATH, extract_freeze_map_study_only_anchors(freeze_map)
    )

    study_only_accounting = read_text(root, STUDY_ONLY_ACCOUNTING_PATH)
    validate_exact_study_only_anchor_inventory(
        failures,
        STUDY_ONLY_ACCOUNTING_PATH,
        extract_study_only_accounting_anchors(study_only_accounting),
    )

    makefile = read_text(root, MAKEFILE_PATH)
    makefile_routes = find_makefile_phase9_routes(makefile)
    for route in CURRENT_PHASE9_MAKE_ROUTES:
        if route not in makefile_routes:
            failures.append(f"missing_phase9_route:{MAKEFILE_PATH}:{route}")
    for route in FORBIDDEN_PHASE9_MAKE_ROUTES:
        if route in makefile_routes:
            failures.append(f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

    return failures


def build_freeze_map_fixture_text() -> str:
    return """# Zigux Freeze Map

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- shared reminder surfaces that summarize freeze posture must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- shared Phase 9 runtime-pilot freeze-boundary packet must keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`, `.github/workflows/zigux-bootstrap.yml`, `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit together, keep `zigux/Makefile` explicit only as a readable non-owner surface whose live body now exposes bounded `phase9-runtime-atomic64-test`, `phase9-runtime-bitmap-test`, `phase9-runtime-loader-shared-test`, `phase9-runtime-loader-command-env-boundary-guard-test`, `phase9-runtime-trace-events-test`, `phase9-runtime-kretprobe-test`, and `phase9-test` routes without treating those wrappers as proof that blocked publication, install-root, or deeper runtime-substrate work is complete, keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold, and must treat `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` as historical blocked-boundary vocabulary.
"""


def build_study_only_accounting_fixture_text() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- current companions: the freeze-map governance note, the parity scorecard, the handoff-next-steps survey, and the shared-summary gap note
- roadmap reason: boundary-study target first, not a rewrite target
- speculative direct ports remain future-only and not current product claims
- no Architecture Council approval is currently recorded for a deep-core status change

## Study-Only Anchor Inventory

### `kernel/workqueue.c`
- posture: `study_only`
- current Phase 15 role: tracked outside the freeze-in-C scorecard

### `kernel/trace/ring_buffer.c`
- posture: `study_only`
- current Phase 15 role: tracked outside the freeze-in-C scorecard

## Accounting Rules

- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
- any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together

## Non-Goals

- a direct Zigux bridge for `kernel/workqueue.c`
- a direct Zigux bridge for `kernel/trace/ring_buffer.c`
"""


def build_review_checklist_fixture_text() -> str:
    return """# Zigux Review Checklist

- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
"""


def build_docs_readme_fixture_text() -> str:
    return """# Zigux Documentation

- Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-trace-events-runtime-packet.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.
- keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.
- keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.
- keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.
"""


def build_lane_sequencing_fixture_text() -> str:
    return """# Phase 9 Runtime Pilot Lane Sequencing

- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness
"""


def build_scripts_readme_fixture_text() -> str:
    return """# scripts/zigux

- keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues
"""


def build_samples_readme_fixture_text() -> str:
    return """# samples/zigux

- Keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit as the rejected re-init rollback companion for initialized, selftest-complete, and exited lifecycle checkpoints in the same direct runtime packet.
- Keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit as the paired rejected re-init plus rejected re-exit rollback companion after initialized direct activity and selftest-ready replay in the same direct runtime packet.
- Current `master` also keeps a narrower returned runtime kretprobe sample-side packet explicit through `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes in `zigux/tests/phase9_build.zig`.
- Keep `samples/zigux/runtime_bitmap_direct_init_contract.zig` explicit as the returned direct-init normalization companion proof for the same runtime bitmap starter, covering unsorted duplicate input collapse, nth-set ordering, formatted sparse-summary stability, and lifecycle-summary stability through selftest and exit.
- Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.
"""


def build_tests_readme_fixture_text() -> str:
    return """# zigux/tests

Keep the current bounded Phase 9 reminder packet explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`.

Keep the current bounded Phase 15 governance reminder explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.

- keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` remain the current shipped runtime-pilot proof rather than a claim that broader runtime-loader or publication boundaries are solved
- keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests` routes, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete
- keep the returned runtime kretprobe pilot packet distinct from those shared loader and bitmap reminders too: `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes are current family-local pilot evidence, but they still must not be used to imply that the broader shared runtime-loader packet, blocked publication boundaries, or install-root surfaces are complete
- without implying any Architecture Council approval for a freeze-map status change
"""


def build_workflow_fixture_text() -> str:
    return """name: zigux-bootstrap

- python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test
- python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py
- python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test
- python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py
- python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test
- python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py
- zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig
- zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig
- zig test samples/zigux/runtime_trace_events.zig
- zig test zigux/tests/runtime_trace_events_survey.zig
"""


def build_makefile_fixture_text() -> str:
    return """PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := ..

.PHONY: phase8-test phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-loader-command-env-boundary-guard-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test phase9-test phase10-test phase12-test

phase8-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase9-runtime-atomic64-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-bitmap-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-loader-shared-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-loader-command-env-boundary-guard-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-trace-events-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-kretprobe-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-first-loadable-runtime-module-parity-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-test: phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-loader-command-env-boundary-guard-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test
"""


FIXTURE_BUILDERS = {
    FREEZE_MAP_PATH: build_freeze_map_fixture_text,
    STUDY_ONLY_ACCOUNTING_PATH: build_study_only_accounting_fixture_text,
    REVIEW_CHECKLIST_PATH: build_review_checklist_fixture_text,
    DOCS_README_PATH: build_docs_readme_fixture_text,
    LANE_SEQUENCING_PATH: build_lane_sequencing_fixture_text,
    SCRIPTS_README_PATH: build_scripts_readme_fixture_text,
    SAMPLES_README_PATH: build_samples_readme_fixture_text,
    TESTS_README_PATH: build_tests_readme_fixture_text,
    WORKFLOW_PATH: build_workflow_fixture_text,
    MAKEFILE_PATH: build_makefile_fixture_text,
}


def seed_fixture_tree(base: Path) -> None:
    for rel_path, builder in FIXTURE_BUILDERS.items():
        write_text(base / rel_path, builder())


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-freeze-map-study-boundaries-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in PATH_REQUIREMENTS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                if current.count(marker) != 1:
                    continue
                write_text(base / rel_path, current.replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        seed_fixture_tree(base)
        write_text(
            base / FREEZE_MAP_PATH,
            build_freeze_map_fixture_text().replace(
                "- `kernel/trace/ring_buffer.c`",
                "- `kernel/trace/ring_buffer.c`\n- `kernel/sched/core.c`",
                1,
            ),
        )
        expect_failure(
            base,
            "study_only_anchor_mismatch:Documentation/zigux/freeze-map.md:expected=['kernel/workqueue.c', 'kernel/trace/ring_buffer.c']:actual=['kernel/workqueue.c', 'kernel/trace/ring_buffer.c', 'kernel/sched/core.c']",
        )

        seed_fixture_tree(base)
        write_text(
            base / STUDY_ONLY_ACCOUNTING_PATH,
            build_study_only_accounting_fixture_text().replace(
                "## Accounting Rules",
                "### `kernel/sched/core.c`\n- posture: `study_only`\n\n## Accounting Rules",
                1,
            ),
        )
        expect_failure(
            base,
            "study_only_anchor_mismatch:Documentation/zigux/phase15-study-only-anchor-accounting.md:expected=['kernel/workqueue.c', 'kernel/trace/ring_buffer.c']:actual=['kernel/workqueue.c', 'kernel/trace/ring_buffer.c', 'kernel/sched/core.c']",
        )

        for route in CURRENT_PHASE9_MAKE_ROUTES:
            seed_fixture_tree(base)
            current = read_text(base, MAKEFILE_PATH)
            write_text(base / MAKEFILE_PATH, remove_makefile_route_definition(current, route))
            expect_failure(base, f"missing_phase9_route:{MAKEFILE_PATH}:{route}")

        for route in FORBIDDEN_PHASE9_MAKE_ROUTES:
            seed_fixture_tree(base)
            current = read_text(base, MAKEFILE_PATH)
            write_text(base / MAKEFILE_PATH, current + f"\n{route}:\n\t@true\n")
            expect_failure(base, f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

        for rel_path in FIXTURE_BUILDERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_FREEZE_MAP_STUDY_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE9_ROADMAP_STUDY_ONLY_ANCHOR_COUNT={len(ROADMAP_STUDY_ONLY_ANCHORS)}")
    print(f"PHASE9_REQUIRED_PATH_COUNT={len(PATH_REQUIREMENTS) + 1}")
    print(f"PHASE9_REQUIRED_MAKE_ROUTE_COUNT={len(CURRENT_PHASE9_MAKE_ROUTES)}")
    print(f"PHASE9_FORBIDDEN_MAKE_ROUTE_COUNT={len(FORBIDDEN_PHASE9_MAKE_ROUTES)}")
    print(f"PHASE9_SAMPLES_README_MARKER_COUNT={len(PATH_REQUIREMENTS[SAMPLES_README_PATH])}")
    print(f"PHASE9_TESTS_README_MARKER_COUNT={len(PATH_REQUIREMENTS[TESTS_README_PATH])}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 9 freeze-map boundary packet keeps the roadmap-backed "
            "study-only anchors, the reviewer-facing route-back wording, and the richer "
            "current-master runtime reminder packet explicit together across shared docs."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_FREEZE_MAP_STUDY_BOUNDARIES_ERROR={failure}")
        return 1

    print(f"PHASE9_ROADMAP_STUDY_ONLY_ANCHOR_COUNT={len(ROADMAP_STUDY_ONLY_ANCHORS)}")
    print(f"PHASE9_REQUIRED_PATH_COUNT={len(PATH_REQUIREMENTS) + 1}")
    print(f"PHASE9_REQUIRED_MAKE_ROUTE_COUNT={len(CURRENT_PHASE9_MAKE_ROUTES)}")
    print(f"PHASE9_FORBIDDEN_MAKE_ROUTE_COUNT={len(FORBIDDEN_PHASE9_MAKE_ROUTES)}")
    print(f"PHASE9_SAMPLES_README_MARKER_COUNT={len(PATH_REQUIREMENTS[SAMPLES_README_PATH])}")
    print(f"PHASE9_TESTS_README_MARKER_COUNT={len(PATH_REQUIREMENTS[TESTS_README_PATH])}")
    print("PHASE9_FREEZE_MAP_STUDY_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())