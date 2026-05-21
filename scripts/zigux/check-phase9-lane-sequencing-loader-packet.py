#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

NOTE_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
BUILD_PATH = "zigux/tests/phase9_build.zig"
ALLOCATOR_FLOW_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig"
COMMAND_ENV_GUARD_PATH = "zigux/kernel/runtime_loader_command_env_boundary_guard.zig"

NOTE_REQUIRED_MARKERS = [
    "Trusted mixed rereads on 2026-05-21 confirm three distinct current-master Phase 9 postures.",
    "The shared runtime-loader allocator/init-flow and command/environment boundary packet now survives as a narrower direct-readback shared-owner surface",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "keep the Phase 8 command and environment ownership boundary explicit",
    "deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`",
    "`LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`",
    "the current reminder surfaces still keep the partial runtime bitmap packet visible",
    "treat that docs-root and tests-root overclaim as shared reminder debt to repair one surface at a time",
    "`scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references",
    "`rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence",
]

BUILD_REQUIRED_MARKERS = [
    'b.path("runtime_loader_allocator_init_flow.zig")',
    'b.path("../kernel/runtime_loader_command_env_boundary_guard.zig")',
    '"phase9-runtime-loader-allocator-init-flow-tests"',
    '"phase9-runtime-loader-command-env-boundary-guard-tests"',
    '"phase9-runtime-loader-shared-tests"',
]

ALLOCATOR_FLOW_REQUIRED_MARKERS = [
    "const AllocatorHandoff = contract.AllocatorHandoff;",
    "fn makeInitializedPlan(",
    "runtime_loader.prepareRequest(bitmap_plan)",
    "released_without_substrate",
]

COMMAND_ENV_GUARD_REQUIRED_MARKERS = [
    'test "shared runtime loader surface rejects argv and environment control bleed-through" {',
    '"command_env"',
    '"PERF_EXEC_PATH"',
    '"\\"LINES\\""',
    '"\\"COLUMNS\\""',
]

REQUIRED_MARKERS = {
    NOTE_PATH: NOTE_REQUIRED_MARKERS,
    BUILD_PATH: BUILD_REQUIRED_MARKERS,
    ALLOCATOR_FLOW_PATH: ALLOCATOR_FLOW_REQUIRED_MARKERS,
    COMMAND_ENV_GUARD_PATH: COMMAND_ENV_GUARD_REQUIRED_MARKERS,
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / NOTE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    return failures


def build_fixture_text(rel_path: str) -> str:
    lines = REQUIRED_MARKERS[rel_path]
    if rel_path.endswith(".md"):
        return "# fixture\n\n" + "\n".join(lines) + "\n"
    return "\n".join(lines) + "\n"


def seed_fixture_tree(base: Path) -> None:
    for rel_path in REQUIRED_MARKERS:
        write_text(base / rel_path, build_fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-lane-sequencing-loader-packet-"))
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

        for rel_path in REQUIRED_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_LANE_SEQUENCING_LOADER_PACKET_SELF_TEST=pass")
    print(f"PHASE9_LANE_SEQUENCING_LOADER_PACKET_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_LANE_SEQUENCING_LOADER_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 9 lane-sequencing note stays aligned with the "
            "returned shared runtime-loader allocator/init-flow and command/environment "
            "boundary packet, the bounded build shard, and the narrower shared-owner "
            "release-discipline wording."
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
            print(f"PHASE9_LANE_SEQUENCING_LOADER_PACKET_ERROR={failure}")
        return 1

    print(f"PHASE9_LANE_SEQUENCING_LOADER_PACKET_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_LANE_SEQUENCING_LOADER_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
