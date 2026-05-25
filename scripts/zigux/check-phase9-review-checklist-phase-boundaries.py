#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
CONTRACT_PATH = "zigux/kernel/runtime_loader_contract.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"
PHASE2_BOUNDARY_MARKER = "remain Phase 2 config-surface bridge references"
PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references rather than runtime-pilot evidence"

REVIEW_CHECKLIST_REQUIRED_MARKERS = [
    "if the change touches the shared Phase 9 runtime-pilot packet",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`",
    "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`",
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    ".provides_selftest_hook = true",
    "initialized, selftest_complete, and exited lifecycle tracking",
    "failed-exit rollback explicit after reusable selftest replay",
    "balanced registration re-entry companion that keeps function-thread registration reusable before and after selftest",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`samples/zigux/runtime_*_loader.zig`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "the older `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` stay historical wider-family vocabulary",
    "older blocked module-metadata and depmod-publication vocabulary such as `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, `Module.symvers`, module install-root, and depmod script or manifest state stays historical blocked-boundary vocabulary until a fresh repo reread restores a current shared owner surface for that packet",
    "the partial separate runtime bitmap reminder packet stays explicit in `samples/zigux/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md`",
    "the shared `zigux/tests/phase9_build.zig` bundle now reruns that partial bitmap packet through `phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle",
    "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

DOCS_README_REQUIRED_MARKERS = [
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` - `scripts/zigux/check-phase9-trace-events-runtime-packet.py` - `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.",
    "keep the partial runtime bitmap reminder packet distinct from that returned loader shard too:",
]

LANE_SEQUENCING_REQUIRED_MARKERS = [
    "Trusted mixed rereads on 2026-05-21 confirm three distinct current-master Phase 9 postures.",
    "The shared runtime-loader allocator/init-flow and command/environment boundary packet now survives as a narrower direct-readback shared-owner surface",
    "`zigux/tests/phase9_build.zig` still exposes `phase9-runtime-atomic64-diff`, `phase9-runtime-bitmap-tests`, `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-first-loadable-runtime-module-parity-survey-tests`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "the review-first shared packet still stays neighboring shared-owner evidence through the aligned docs-root, scripts-root, and tests-root reminders, the bounded loader shard, and the direct command/environment boundary guard",
    "keep the Phase 8 command and environment ownership boundary explicit",
    "deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`",
    "`LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
    "current `master` therefore supports a partial runtime bitmap reminder packet plus the returned shared allocator/init-flow and command/environment boundary packet",
    "keep `modules.order`, `modules.builtin`, `Module.symvers`, and module install-root wording framed as blocked wider-family vocabulary too",
    "keep blocked depmod script, depmod manifest, and depmod alias-output wording framed as historical wider-family vocabulary too until trusted direct rereads return a current shared owner surface for that publication packet",
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
    "Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.",
]

MODULE_SLICE_REQUIRED_MARKERS = [
    "The adjacent shared build shard in `zigux/tests/phase9_build.zig` now names `phase9-runtime-trace-events-tests`, `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, the dedicated `phase9-runtime-trace-events-loader-substrate-drift-tests` replay, aggregate `phase9-runtime-loader-shared-tests`, and the broader `phase9-first-loadable-runtime-module-parity-survey-tests` route, but those rerun routes remain neighboring shared-owner evidence instead of expanding this module slice into returned family-local runtime-loader parity.",
    "Current `master` does now expose the shared loader-backed surfaces `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold through the adjacent `phase9-runtime-loader-shared-tests` shard plus the dedicated `phase9-runtime-trace-events-loader-substrate-drift-tests` replay in `zigux/tests/phase9_build.zig`, but those neighboring routes still stay shared-owner evidence rather than returned family-local trace-events proof.",
    "Current `master` still keeps the separate Phase 9 runtime bitmap reminder packet visible through `Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    "- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references.",
    "- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.",
    "- Those earlier-phase anchors stay adjacent context for the narrow trace-events packet rather than shared runtime-pilot evidence.",
]

SCRIPTS_README_REQUIRED_MARKERS = [
    "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 9 reminder packet explicit from the scripts root",
    "- `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold keep the narrower shared runtime-loader allocator/init-flow and command/environment boundary packet explicit beside the still-blocked module-metadata, install-root, and depmod-publication boundary",
]

SAMPLES_README_REQUIRED_MARKERS = [
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    "Keep the earlier non-owner boundary split explicit here too: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot sample evidence.",
]

TESTS_README_REQUIRED_MARKERS = [
    "Keep the current shared review-checklist and trace-events checker packet explicit through `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md`, while keeping the shared loader and command/environment boundary packet distinct from the trace-events direct sample family.",
    "Keep the Phase 8 and earlier non-owner boundaries explicit too: `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` remain the command and environment owners, `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface references, and `rust/exports.c` plus `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence.",
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

WORKFLOW_REQUIRED_MARKERS = [
    "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
    "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test",
    "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
    "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test",
    "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py",
    "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py --self-test",
    "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py",
]

CONTRACT_REQUIRED_MARKERS = [
    "test \\\"LoadPlan keeps blocked publication and depmod surfaces out of the shared request contract\\\" {",
    "const blocked_publication_fields = [_][]const u8{",
    "\\\"modinfo\\\",",
    "\\\"module_alias\\\",",
    "\\\"module_aliases\\\",",
    "\\\"modules_alias_path\\\",",
    "\\\"module_install_root\\\",",
    "\\\"modules_order_path\\\",",
    "\\\"modules_builtin_path\\\",",
    "\\\"module_symvers_path\\\",",
    "\\\"depmod_script\\\",",
    "\\\"depmod_manifest\\\",",
    "\\\"depmod_aliases\\\",",
    "try std.testing.expect(!@hasField(LoadPlan, field));",
]

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_PATH: REVIEW_CHECKLIST_REQUIRED_MARKERS,
    DOCS_README_PATH: DOCS_README_REQUIRED_MARKERS,
    LANE_SEQUENCING_PATH: LANE_SEQUENCING_REQUIRED_MARKERS,
    MODULE_SLICE_PATH: MODULE_SLICE_REQUIRED_MARKERS,
    SCRIPTS_README_PATH: SCRIPTS_README_REQUIRED_MARKERS,
    SAMPLES_README_PATH: SAMPLES_README_REQUIRED_MARKERS,
    TESTS_README_PATH: TESTS_README_REQUIRED_MARKERS,
    CONTRACT_PATH: CONTRACT_REQUIRED_MARKERS,
    WORKFLOW_PATH: WORKFLOW_REQUIRED_MARKERS,
}

EXACT_ONCE_MARKERS = {
    REVIEW_CHECKLIST_PATH: [
        "if the change touches the shared Phase 9 runtime-pilot packet",
        "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned",
    ],
}

CURRENT_PHASE9_MAKE_ROUTES = [
    "phase9-runtime-atomic64-test",
    "phase9-runtime-bitmap-test",
    "phase9-runtime-loader-shared-test",
    "phase9-runtime-trace-events-test",
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
        if (candidate / REVIEW_CHECKLIST_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_line_occurrences(content: str, marker: str) -> int:
    return sum(1 for line in content.splitlines() if line == marker)


def duplicate_marker_occurrence(content: str, marker: str) -> str:
    return content.replace(marker, f"{marker}\n{marker}", 1)


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
            if line.startswith("	"):
                continue
            skipping = False
        kept.append(line)
    return "\n".join(kept) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in EXACT_ONCE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            count = count_exact_line_occurrences(text, marker)
            if count != 1:
                failures.append(f"expected_exact_once:{rel_path}:{marker}:count={count}")

    makefile = read_text(root, MAKEFILE_PATH)
    makefile_routes = find_makefile_phase9_routes(makefile)
    for route in CURRENT_PHASE9_MAKE_ROUTES:
        if route not in makefile_routes:
            failures.append(f"missing_phase9_route:{MAKEFILE_PATH}:{route}")
    for route in FORBIDDEN_PHASE9_MAKE_ROUTES:
        if route in makefile_routes:
            failures.append(f"unexpected_phase9_route:{MAKEFILE_PATH}:{route}")

    return failures


def build_fixture_text(rel_path: str) -> str:
    if rel_path == WORKFLOW_PATH:
        return """name: fixture

jobs:
  bootstrap:
    steps:
      - run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test
      - run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py
      - run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test
      - run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py
      - run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test
      - run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py
      - run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test
      - run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py
      - run: python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py --self-test
      - run: python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py
"""
    if rel_path == MAKEFILE_PATH:
        return """PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := ..

.PHONY: phase8-test phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-trace-events-test phase9-first-loadable-runtime-module-parity-test phase9-test phase10-test phase12-test

phase8-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase9-runtime-atomic64-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-bitmap-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-loader-shared-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-runtime-trace-events-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-first-loadable-runtime-module-parity-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase9-first-loadable-runtime-module-parity-survey-tests --build-file zigux/tests/phase9_build.zig --summary all

phase9-test: phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-trace-events-test phase9-first-loadable-runtime-module-parity-test

phase10-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all

phase12-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all
"""
    if rel_path.endswith(".md"):
        return "# fixture\n\n" + "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
    return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"


def seed_fixture_tree(base: Path) -> None:
    for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
        write_text(base / rel_path, build_fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-review-checklist-boundaries-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                if current.count(marker) != 1:
                    continue
                write_text(base / rel_path, current.replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path, markers in EXACT_ONCE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, duplicate_marker_occurrence(current, marker))
                expect_failure(base, f"expected_exact_once:{rel_path}:{marker}:count=2")

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

        for rel_path in [*REQUIRED_MARKERS, MAKEFILE_PATH]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FILE_COUNT={len(REQUIRED_MARKERS) + 1}")
    print(
        "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    print(
        "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_REQUIRED_MAKEFILE_ROUTE_COUNT="
        f"{len(CURRENT_PHASE9_MAKE_ROUTES)}"
    )
    print(
        "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FORBIDDEN_MAKEFILE_ROUTE_COUNT="
        f"{len(FORBIDDEN_PHASE9_MAKE_ROUTES)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 9 reviewer-facing packet keeps the surviving "
            "trace-events runtime family, the returned shared loader packet, the "
            "command/environment boundary guard, the blocked-publication contract "
            "boundary, and the bounded current Makefile route packet explicit across the "
            "key reviewer-facing surfaces without making neighboring bitmap reminder "
            "details the responsibility of this shared-loader lane."
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
            print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_ERROR={failure}")
        return 1

    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FILE_COUNT={len(REQUIRED_MARKERS) + 1}")
    print(
        "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    print(
        "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_REQUIRED_MAKEFILE_ROUTE_COUNT="
        f"{len(CURRENT_PHASE9_MAKE_ROUTES)}"
    )
    print(
        "PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_FORBIDDEN_MAKEFILE_ROUTE_COUNT="
        f"{len(FORBIDDEN_PHASE9_MAKE_ROUTES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())