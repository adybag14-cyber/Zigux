#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

DOCS_README_PATH = "Documentation/zigux/README.md"
PHASE9_BITMAP_SURVEY_PATH = "Documentation/zigux/phase9-runtime-bitmap-survey.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig"
RUNTIME_LOADER_CONTRACT_PATH = "zigux/kernel/runtime_loader_contract.zig"
RUNTIME_LOADER_ALLOCATOR_INIT_FLOW_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig"

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "keep the returned shared runtime-loader allocator/init-flow packet explicit too:",
        "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
        "`zigux/kernel/runtime_loader.zig`",
        "`zigux/kernel/runtime_loader_contract.zig`",
        "`phase9-runtime-loader-shared-tests` shard remain neighboring shared-owner evidence",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "the runtime bitmap sample, cold-stage guard, survey, module, diff, loader, and top-bit companion packet members",
    ],
    PHASE9_BITMAP_SURVEY_PATH: [
        "`samples/zigux/runtime_bitmap_direct_init_contract.zig`",
        "Keep the direct-init companion explicit when reminder text summarizes sample-local init normalization, unsorted duplicate input collapse, nth-set ordering, and formatted sparse-summary stability.",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage sample-root guard companion;",
        "`phase9-runtime-bitmap-cold-stage-guard-tests`",
        "`phase9-runtime-bitmap-tests`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "if the change touches the shared Phase 9 runtime-pilot packet",
        "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
        "`zigux/tests/runtime_loader_gap_survey.zig`",
        "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
        "`zigux/kernel/runtime_loader.zig`",
        "`zigux/kernel/runtime_loader_contract.zig`",
        "`samples/zigux/runtime_*_loader.zig`",
        "the returned shared runtime-loader allocator/init-flow packet remains neighboring shared-owner evidence",
    ],
    LANE_SEQUENCING_PATH: [
        "The shared runtime-loader allocator/init-flow and command/environment boundary packet now survives as a narrower direct-readback shared-owner surface",
        "Trusted GitHub rereads on 2026-05-21 directly recover the still-live shared loader packet through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the still-returned `samples/zigux/runtime_bitmap_loader.zig` scaffold, and the bounded `zigux/tests/phase9_build.zig` shard.",
        "`zigux/tests/phase9_build.zig` still exposes `phase9-runtime-atomic64-diff`, `phase9-runtime-bitmap-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-first-loadable-runtime-module-parity-survey-tests`",
        "`zigux/tests/phase9_build.zig` now also names `phase9-runtime-loader-command-env-boundary-guard-tests`",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig` now also returns on the trusted path as sample-root-only cold-stage selftest, exit, mutation, and source-lifecycle guard proof",
        "`phase9-runtime-bitmap-cold-stage-guard-tests` route plus the aggregate `phase9-runtime-bitmap-tests` handle",
        "the review-first shared packet still stays neighboring shared-owner evidence through the aligned docs-root, scripts-root, and tests-root reminders, the bounded loader shard, and the direct command/environment boundary guard",
        "keep the Phase 8 command and environment ownership boundary explicit: deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`, while `LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
        "current Phase 9 material still does not prove shipped runtime command or environment activation control; it proves only that the shared runtime-loader packet keeps those Phase 8 control surfaces out of the loader contract",
    ],
    SAMPLES_README_PATH: [
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter.",
        "`zigux/tests/runtime_bitmap_module.zig`",
        "`zigux/tests/runtime_bitmap_diff.zig`",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 9 reminder packet explicit from the scripts root",
        "there is still no dedicated shared `validate-phase9.py` rerun path for this loader packet on current `master`",
        "`zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold keep the narrower shared runtime-loader allocator/init-flow and command/environment boundary packet explicit beside the still-blocked module-metadata, install-root, and depmod-publication boundary",
        "keep `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` framed as historical wider-family vocabulary until trusted direct rereads return them",
    ],
    TESTS_README_PATH: [
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "the partial runtime bitmap reminder packet including the returned cold-stage guard, module, and diff witnesses",
        "Keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` reruns the atomic64 diff, bitmap survey, bitmap module, bitmap diff, bitmap cold-stage guard, bitmap top-bit companion, shared loader allocator/init-flow, shared loader command/environment boundary guard, the shared trace-events loader-substrate-drift shard, and the first-loadable parity-survey handle, but it is not proof that blocked publication boundaries or deeper runtime substrate work are complete.",
    ],
    PHASE9_BUILD_PATH: [
        'const runtime_loader_allocator_init_flow_module = b.createModule(.{',
        '.root_source_file = b.path("runtime_loader_allocator_init_flow.zig"),',
        'const runtime_loader_allocator_init_flow_tests = b.addTest(.{',
        '"phase9-runtime-loader-allocator-init-flow-tests",',
        'const runtime_loader_command_env_boundary_guard_module = b.createModule(.{',
        '.root_source_file = b.path("../kernel/runtime_loader_command_env_boundary_guard.zig"),',
        'const runtime_loader_command_env_boundary_guard_tests = b.addTest(.{',
        '"phase9-runtime-loader-command-env-boundary-guard-tests",',
        'const runtime_bitmap_direct_init_contract_module = b.createModule(.{',
        '.root_source_file = b.path("../../samples/zigux/runtime_bitmap_direct_init_contract.zig"),',
        'const runtime_bitmap_direct_init_contract_tests = b.addTest(.{',
        '"phase9-runtime-bitmap-direct-init-contract-tests",',
        'const runtime_bitmap_cold_stage_guard_module = b.createModule(.{',
        '.root_source_file = b.path("../../samples/zigux/runtime_bitmap_cold_stage_guard.zig"),',
        'const runtime_bitmap_cold_stage_guard_tests = b.addTest(.{',
        '"phase9-runtime-bitmap-cold-stage-guard-tests",',
        'const phase9_runtime_bitmap_direct_init_contract = b.step(',
        'phase9_runtime_bitmap_direct_init_contract.dependOn(',
        'const phase9_runtime_bitmap_cold_stage_guard = b.step(',
        'phase9_runtime_bitmap_cold_stage_guard.dependOn(',
        'const phase9_runtime_loader_command_env_boundary_guard = b.step(',
        'phase9_runtime_loader_command_env_boundary_guard.dependOn(\n        &run_runtime_loader_command_env_boundary_guard_tests.step,\n    );',
        'const phase9_runtime_loader_shared = b.step(',
        '"phase9-runtime-loader-shared-tests",',
        'phase9_runtime_loader_shared.dependOn(&run_runtime_loader_kernel_tests.step);',
        'phase9_runtime_loader_shared.dependOn(&run_runtime_loader_contract_tests.step);',
        'phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);',
        'phase9_runtime_loader_shared.dependOn(\n        &run_runtime_loader_command_env_boundary_guard_tests.step,\n    );',
        'phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);',
        'phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_direct_init_contract_tests.step);',
        'phase9_runtime_bitmap.dependOn(&run_runtime_bitmap_cold_stage_guard_tests.step);',
    ],
    RUNTIME_LOADER_PATH: [
        "pub const PreparedRequest = struct {",
        "pub fn keepsAllocatorInitFlowConsistent(",
        "pub fn prepareRequest(plan: LoadPlan) !PreparedRequest {",
        'test "prepareRequest enforces the bounded runtime loader contract"',
        'test "PreparedRequest.requestRuntimeLoad preserves the prepared snapshot on drift"',
        'test "releaseWithoutSubstrate preserves the waiting snapshot on drift"',
    ],
    RUNTIME_LOADER_CONTRACT_PATH: [
        'test "LoadPlan keeps blocked publication and depmod surfaces out of the shared request contract"',
        '"modinfo"',
        '"module_alias"',
        '"modules_alias_path"',
        '"module_install_root"',
        '"modules_order_path"',
        '"modules_builtin_path"',
        '"module_symvers_path"',
        '"depmod_script"',
        '"depmod_manifest"',
        '"depmod_aliases"',
    ],
    RUNTIME_LOADER_ALLOCATOR_INIT_FLOW_PATH: [
        'test "shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned"',
        'test "shared runtime loader keeps selftest-complete trace-events and atomic64 request shape aligned"',
        'test "shared runtime loader keeps rejected release-order transitions fail-closed across loader families"',
    ],
}

FORBIDDEN_MARKERS = {
    DOCS_README_PATH: [
        "blocked publication, install-root, or module-metadata boundaries are already solved",
    ],
    LANE_SEQUENCING_PATH: [
        "full publication completion",
    ],
}

EXACT_ONCE_MARKERS = {
    SCRIPTS_README_PATH: [
        "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 9 reminder packet explicit from the scripts root",
    ],
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / DOCS_README_PATH).exists():
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


def break_marker(marker: str) -> str:
    if len(marker) == 1:
        return "_"
    replacement_tail = "_" if marker[-1] != "_" else "-"
    return marker[:-1] + replacement_tail


def tamper_marker_occurrences(content: str, marker: str) -> str:
    return content.replace(marker, break_marker(marker))


def build_fixture_text(rel_path: str) -> str:
    markers = REQUIRED_MARKERS[rel_path]
    prefix = "# fixture\n\n" if rel_path.endswith(".md") else ""
    return prefix + "\n".join(markers) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_MARKERS:
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

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")

    return failures


def seed_fixture_tree(base: Path) -> None:
    for rel_path in REQUIRED_MARKERS:
        write_text(base / rel_path, build_fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-build-only-surface-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, tamper_marker_occurrences(current, marker))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path, markers in EXACT_ONCE_MARKERS.items():
            for marker in markers:
                seed_fixtureTree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, duplicate_marker_occurrence(current, marker))
                expect_failure(base, f"expected_exact_once:{rel_path}:{marker}:count=2")

        for rel_path, markers in FORBIDDEN_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, current + f"\n{marker}\n")
                expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        for rel_path in REQUIRED_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_BUILD_ONLY_SURFACE_SELF_TEST=pass")
    print(f"PHASE9_BUILD_ONLY_SURFACE_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_BUILD_ONLY_SURFACE_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE9_BUILD_ONLY_SURFACE_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    print(
        "PHASE9_BUILD_ONLY_SURFACE_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 9 build-only packet keeps the shared "
            "runtime-loader allocator/init-flow shard, the command/environment "
            "boundary guard, the returned runtime bitmap direct-init and cold-stage "
            "guard packet, the scripts-root reminder, the blocked depmod-boundary "
            "contract, the live loader facade, the dedicated allocator/init-flow "
            "replay, and the aligned docs, samples, tests, and sequencing reminders "
            "explicit across the docs, scripts, review checklist, lane sequencing "
            "note, survey, samples README, tests README, contract, facade, replay, "
            "and phase9_build rerun surface."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_BUILD_ONLY_SURFACE_ERROR={failure}")
        return 1

    print("PHASE9_BUILD_ONLY_SURFACE=pass")
    print(f"PHASE9_BUILD_ONLY_SURFACE_ROOT={args.repo_root}")
    print(f"PHASE9_BUILD_ONLY_SURFACE_FILES_CHECKED={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_BUILD_ONLY_SURFACE_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE9_BUILD_ONLY_SURFACE_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    print(
        "PHASE9_BUILD_ONLY_SURFACE_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
