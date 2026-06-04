#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

OWNERSHIP_MAP_PATH = Path("Documentation/zigux/phase9-runtime-pilot-ownership-map.md")
SAMPLE_PATH = Path("samples/zigux/runtime_kretprobe.zig")
LOADER_PATH = Path("samples/zigux/runtime_kretprobe_loader.zig")
INITIALIZED_SNAPSHOT_GUARD_PATH = Path(
    "samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig"
)
REGISTRATION_REENTRY_GATE_PATH = Path(
    "samples/zigux/runtime_kretprobe_registration_reentry_gate.zig"
)
REINIT_REEXIT_GUARD_PATH = Path("samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig")
SURVEY_PATH = Path("zigux/tests/runtime_kretprobe_survey.zig")
MODULE_PATH = Path("zigux/tests/runtime_kretprobe_module.zig")
BUILD_PATH = Path("zigux/tests/phase9_build.zig")

REQUIRED_FILES = (
    OWNERSHIP_MAP_PATH,
    SAMPLE_PATH,
    LOADER_PATH,
    INITIALIZED_SNAPSHOT_GUARD_PATH,
    REGISTRATION_REENTRY_GATE_PATH,
    REINIT_REEXIT_GUARD_PATH,
    SURVEY_PATH,
    MODULE_PATH,
    BUILD_PATH,
)

FILE_MARKERS = {
    OWNERSHIP_MAP_PATH: (
        "## Runtime Kretprobe Family Owner",
        "`samples/zigux/runtime_kretprobe.zig`",
        "`samples/zigux/runtime_kretprobe_loader.zig`",
        "`samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`",
        "`samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`",
        "`samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig`",
        "`zigux/tests/runtime_kretprobe_survey.zig`",
        "`zigux/tests/runtime_kretprobe_module.zig`",
        "`zigux/tests/runtime_first_loadable_parity_behavior.zig`",
        "`scripts/zigux/check-phase9-kretprobe-runtime-packet.py`",
        "bounded `phase9-runtime-kretprobe-sample-tests`",
        "bounded `phase9-runtime-kretprobe-loader-tests`",
        "bounded `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`",
        "bounded `phase9-runtime-kretprobe-registration-reentry-gate-tests`",
        "bounded `phase9-runtime-kretprobe-reinit-reexit-guard-tests`",
        "bounded `phase9-runtime-kretprobe-survey-tests`",
        "bounded `phase9-runtime-kretprobe-module-tests`",
        "bounded `phase9-runtime-kretprobe-tests`",
        "bounded `phase9-first-loadable-runtime-module-parity-behavior-tests`",
    ),
    SAMPLE_PATH: (
        '.name = "runtime_kretprobe"',
        '.anchor = "samples/kprobes/kretprobe_example.c"',
        '.requires_runtime_substrate = true',
        '.provides_selftest_hook = true',
        'pub fn runSelftest(self: *Self) !SelftestSummary {',
        'pub fn exit(self: *Self) !void {',
        'test "runtime kretprobe sample keeps selftest hook and return replay explicit" {',
    ),
    LOADER_PATH: (
        'const runtime_loader = @import("runtime_loader");',
        'pub const LoaderStage = enum(u8) {',
        'pub fn requestSharedRuntimeLoad(',
        'pub fn releaseSharedWithoutSubstrate(',
        'released_without_substrate',
        'waiting_on_runtime_substrate',
        'error.InvalidLoaderState',
        'test "runtime kretprobe loader keeps initialized-stage shared contract plans explicit" {',
        'test "runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity" {',
    ),
    INITIALIZED_SNAPSHOT_GUARD_PATH: (
        'const RuntimeKretprobeSample = kretprobe.RuntimeKretprobeSample;',
        'test "phase9 kretprobe sample keeps captured initialized snapshot replay explicit across later selftest and exit" {',
        'test "phase9 kretprobe sample keeps captured initialized direct-activity snapshot replay explicit across later selftest and exit" {',
    ),
    REGISTRATION_REENTRY_GATE_PATH: (
        'const RuntimeKretprobeSample = runtime_kretprobe_sample.RuntimeKretprobeSample;',
        'test "runtime kretprobe registration reentry stays reusable before selftest" {',
        'test "runtime kretprobe registration reentry stays reusable after selftest" {',
        'test "runtime kretprobe registration reentry stays fail-closed after exit" {',
    ),
    REINIT_REEXIT_GUARD_PATH: (
        'const RuntimeKretprobeSample = kretprobe.RuntimeKretprobeSample;',
        'test "phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after initialized direct activity" {',
        'test "phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after selftest-ready replay" {',
    ),
    SURVEY_PATH: (
        'test "phase9 runtime kretprobe survey gate matches the roadmap-backed sample and module packet" {',
        'try std.testing.expectEqualStrings("runtime_kretprobe", descriptor.name);',
        'try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);',
        'try expectContains(phase9_build, "\\"phase9-runtime-kretprobe-tests\\"");',
        "phase9-first-loadable-runtime-module-parity-behavior-tests",
        'test "phase9 runtime kretprobe survey keeps captured initialized snapshot replay explicit across later selftest and exit" {',
    ),
    MODULE_PATH: (
        'test "runtime kretprobe sample advertises the bounded pilot-module contract" {',
        'test "runtime kretprobe sample keeps selftest summary replay explicit at the module boundary" {',
        'test "runtime kretprobe sample keeps lifecycle snapshot replay explicit at the module boundary" {',
        'test "runtime kretprobe sample keeps initialized-stage exit replay explicit at the module boundary" {',
        'test "runtime kretprobe sample keeps rejected re-selftest rollback explicit at the module boundary" {',
        'test "runtime kretprobe sample keeps duplicate registration and failed exit rollback explicit at the module boundary" {',
    ),
    BUILD_PATH: (
        '.name = "phase9-runtime-kretprobe-sample-tests"',
        '.name = "phase9-runtime-kretprobe-loader-tests"',
        '.name = "phase9-runtime-kretprobe-initialized-snapshot-guard-tests"',
        '.name = "phase9-runtime-kretprobe-registration-reentry-gate-tests"',
        '.name = "phase9-runtime-kretprobe-reinit-reexit-guard-tests"',
        '.name = "phase9-runtime-kretprobe-survey-tests"',
        '.name = "phase9-runtime-kretprobe-module-tests"',
        '"phase9-runtime-kretprobe-tests",',
        '"Run the Phase 9 runtime kretprobe sample, loader, initialized-snapshot guard, registration-reentry gate, reinit-reexit guard, survey, and module lifecycle tests.",',
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        path = repo_root / relative_path
        if not path.is_file():
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        text = _read(path)
        for marker in FILE_MARKERS[relative_path]:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in FILE_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def _expect_issue(root: Path, expected: str) -> None:
    issues = validate_repo(root)
    if expected not in issues:
        raise AssertionError(f"expected issue not reported: {expected}\nactual: {issues}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_kretprobe_runtime_packet_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)
        issues = validate_repo(root)
        if issues:
            print("PHASE9_KRETPROBE_RUNTIME_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        (root / SAMPLE_PATH).unlink()
        _expect_issue(root, "missing repo file: samples/zigux/runtime_kretprobe.zig")

        _populate_repo(root)
        (root / INITIALIZED_SNAPSHOT_GUARD_PATH).unlink()
        _expect_issue(
            root,
            "missing repo file: samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig",
        )

        _populate_repo(root)
        _write(
            root / OWNERSHIP_MAP_PATH,
            _read(root / OWNERSHIP_MAP_PATH).replace(
                "bounded `phase9-runtime-kretprobe-reinit-reexit-guard-tests`",
                "",
                1,
            ),
        )
        _expect_issue(
            root,
            "missing Documentation/zigux/phase9-runtime-pilot-ownership-map.md marker: bounded `phase9-runtime-kretprobe-reinit-reexit-guard-tests`",
        )

        _populate_repo(root)
        _write(
            root / REGISTRATION_REENTRY_GATE_PATH,
            _read(root / REGISTRATION_REENTRY_GATE_PATH).replace(
                'test "runtime kretprobe registration reentry stays reusable after selftest" {',
                "",
                1,
            ),
        )
        _expect_issue(
            root,
            'missing samples/zigux/runtime_kretprobe_registration_reentry_gate.zig marker: test "runtime kretprobe registration reentry stays reusable after selftest" {',
        )

        _populate_repo(root)
        _write(
            root / REINIT_REEXIT_GUARD_PATH,
            _read(root / REINIT_REEXIT_GUARD_PATH).replace(
                'test "phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after selftest-ready replay" {',
                "",
                1,
            ),
        )
        _expect_issue(
            root,
            'missing samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig marker: test "phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after selftest-ready replay" {',
        )

        _populate_repo(root)
        _write(
            root / BUILD_PATH,
            _read(root / BUILD_PATH).replace(
                '.name = "phase9-runtime-kretprobe-module-tests"',
                "",
                1,
            ),
        )
        _expect_issue(
            root,
            'missing zigux/tests/phase9_build.zig marker: .name = "phase9-runtime-kretprobe-module-tests"',
        )

        _populate_repo(root)
        _write(
            root / SURVEY_PATH,
            _read(root / SURVEY_PATH).replace(
                'try expectContains(phase9_build, "\\"phase9-runtime-kretprobe-tests\\"");',
                "",
                1,
            ),
        )
        _expect_issue(
            root,
            'missing zigux/tests/runtime_kretprobe_survey.zig marker: try expectContains(phase9_build, "\\"phase9-runtime-kretprobe-tests\\"");',
        )

    print("PHASE9_KRETPROBE_RUNTIME_PACKET_SELF_TEST=pass")
    print("PHASE9_KRETPROBE_RUNTIME_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 9 runtime kretprobe packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 9 runtime kretprobe packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE9_KRETPROBE_RUNTIME_PACKET=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / SAMPLE_PATH}")
    print("PHASE9_KRETPROBE_RUNTIME_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
