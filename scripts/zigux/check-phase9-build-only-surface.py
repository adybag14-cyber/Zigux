#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "keep the returned shared runtime-loader allocator/init-flow packet explicit too:",
        "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
        "`zigux/kernel/runtime_loader.zig`",
        "`zigux/kernel/runtime_loader_contract.zig`",
        "`phase9-runtime-loader-shared-tests` shard remain neighboring shared-owner evidence",
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
        "the review-first shared packet still stays neighboring shared-owner evidence through this lane note, the scripts-root reminder, the bounded loader shard, and the direct command/environment boundary guard",
        "keep the Phase 8 command and environment ownership boundary explicit: deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`, while `LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
        "current Phase 9 material still does not prove shipped runtime command or environment activation control; it proves only that the shared runtime-loader packet keeps those Phase 8 control surfaces out of the loader contract",
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
        'const phase9_runtime_loader_command_env_boundary_guard = b.step(',
        'phase9_runtime_loader_command_env_boundary_guard.dependOn(&run_runtime_loader_command_env_boundary_guard_tests.step);',
        'const phase9_runtime_loader_shared = b.step(',
        '"phase9-runtime-loader-shared-tests",',
        'phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);',
        'phase9_runtime_loader_shared.dependOn(&run_runtime_loader_command_env_boundary_guard_tests.step);',
        '&run_runtime_trace_events_loader_substrate_drift_tests.step,',
        'phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);',
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
                write_text(base / rel_path, current.replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

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
        "PHASE9_BUILD_ONLY_SURFACE_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 9 build-only packet keeps the shared "
            "runtime-loader allocator/init-flow shard, the command/environment "
            "boundary guard, and the aligned docs and checklist reminders "
            "explicit across the docs, review checklist, lane sequencing note, "
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

    print(f"PHASE9_BUILD_ONLY_SURFACE_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_BUILD_ONLY_SURFACE_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE9_BUILD_ONLY_SURFACE_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())