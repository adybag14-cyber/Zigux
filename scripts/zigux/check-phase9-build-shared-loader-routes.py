#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"

REQUIRED_MARKERS = [
    "const runtime_loader_allocator_init_flow_tests = b.addTest(.{",
    '        .name = "phase9-runtime-loader-allocator-init-flow-tests",',
    "const runtime_loader_command_env_boundary_guard_tests = b.addTest(.{",
    '        .name = "phase9-runtime-loader-command-env-boundary-guard-tests",',
    "const phase9_runtime_loader_shared = b.step(",
    '        "phase9-runtime-loader-shared-tests",',
    "    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
    "    phase9_runtime_loader_shared.dependOn(",
    "        &run_runtime_loader_command_env_boundary_guard_tests.step,",
    "    phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);",
    "    const phase9_first_loadable_runtime_module_parity = b.step(",
    '        "phase9-first-loadable-runtime-module-parity-survey-tests",',
]

EXACT_ONCE_MARKERS = [
    '        .name = "phase9-runtime-loader-allocator-init-flow-tests",',
    '        .name = "phase9-runtime-loader-command-env-boundary-guard-tests",',
    '        "phase9-runtime-loader-shared-tests",',
    '        "phase9-first-loadable-runtime-module-parity-survey-tests",',
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / PHASE9_BUILD_PATH).exists():
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


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    build_path = root / PHASE9_BUILD_PATH
    if not build_path.exists():
        return [f"missing_file:{PHASE9_BUILD_PATH}"]

    content = read_text(root, PHASE9_BUILD_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in content:
            failures.append(f"missing_marker:{PHASE9_BUILD_PATH}:{marker}")

    for marker in EXACT_ONCE_MARKERS:
        count = count_exact_line_occurrences(content, marker)
        if count != 1:
            failures.append(
                f"expected_exact_once:{PHASE9_BUILD_PATH}:{marker}:count={count}"
            )

    return failures


def build_fixture_text() -> str:
    return """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const runtime_loader_allocator_init_flow_tests = b.addTest(.{
        .name = \"phase9-runtime-loader-allocator-init-flow-tests\",
    });

    const runtime_loader_command_env_boundary_guard_tests = b.addTest(.{
        .name = \"phase9-runtime-loader-command-env-boundary-guard-tests\",
    });

    const run_runtime_loader_allocator_init_flow_tests = b.addRunArtifact(
        runtime_loader_allocator_init_flow_tests,
    );
    const run_runtime_loader_command_env_boundary_guard_tests = b.addRunArtifact(
        runtime_loader_command_env_boundary_guard_tests,
    );
    const run_runtime_bitmap_loader_tests = b.addSystemCommand(&.{\"true\"});
    const run_runtime_first_loadable_parity_survey_tests = b.addSystemCommand(&.{\"true\"});

    const phase9_runtime_loader_shared = b.step(
        \"phase9-runtime-loader-shared-tests\",
        \"Run the shared Phase 9 runtime loader handoff parity tests.\",
    );
    phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);
    phase9_runtime_loader_shared.dependOn(
        &run_runtime_loader_command_env_boundary_guard_tests.step,
    );
    phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);

    const phase9_first_loadable_runtime_module_parity = b.step(
        \"phase9-first-loadable-runtime-module-parity-survey-tests\",
        \"Run the Phase 9 first-loadable runtime-module parity survey tests.\",
    );
    phase9_first_loadable_runtime_module_parity.dependOn(
        &run_runtime_first_loadable_parity_survey_tests.step,
    );
}
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-build-shared-loader-routes-"))
    try:
        write_text(base / PHASE9_BUILD_PATH, build_fixture_text())

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in REQUIRED_MARKERS:
            write_text(base / PHASE9_BUILD_PATH, build_fixture_text())
            current = read_text(base, PHASE9_BUILD_PATH)
            if current.count(marker) != 1:
                continue
            write_text(base / PHASE9_BUILD_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{PHASE9_BUILD_PATH}:{marker}")

        for marker in EXACT_ONCE_MARKERS:
            write_text(base / PHASE9_BUILD_PATH, build_fixture_text())
            current = read_text(base, PHASE9_BUILD_PATH)
            write_text(
                base / PHASE9_BUILD_PATH,
                duplicate_marker_occurrence(current, marker),
            )
            expect_failure(
                base,
                f"expected_exact_once:{PHASE9_BUILD_PATH}:{marker}:count=2",
            )

        write_text(base / PHASE9_BUILD_PATH, build_fixture_text())
        (base / PHASE9_BUILD_PATH).unlink()
        expect_failure(base, f"missing_file:{PHASE9_BUILD_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_BUILD_SHARED_LOADER_ROUTES_SELF_TEST=pass")
    print("PHASE9_BUILD_SHARED_LOADER_ROUTES_FILE_COUNT=1")
    print(f"PHASE9_BUILD_SHARED_LOADER_ROUTES_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_BUILD_SHARED_LOADER_ROUTES_EXACT_ONCE_MARKER_COUNT="
        f"{len(EXACT_ONCE_MARKERS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the bounded Phase 9 build bundle keeps the shared loader "
            "allocator/init-flow shard, the command/environment boundary guard shard, "
            "the shared aggregate step, and the first-loadable parity-survey route "
            "explicit on current master."
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
            print(f"PHASE9_BUILD_SHARED_LOADER_ROUTES_ERROR={failure}")
        return 1

    print("PHASE9_BUILD_SHARED_LOADER_ROUTES_FILE_COUNT=1")
    print(f"PHASE9_BUILD_SHARED_LOADER_ROUTES_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_BUILD_SHARED_LOADER_ROUTES_EXACT_ONCE_MARKER_COUNT="
        f"{len(EXACT_ONCE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
