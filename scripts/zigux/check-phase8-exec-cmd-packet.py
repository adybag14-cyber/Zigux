#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path


def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = _default_root()
DOCS_README = Path("Documentation/zigux/README.md")
EXEC_CMD_SLICE = Path("Documentation/zigux/phase8-exec-cmd-slice.md")
EXEC_CMD_SEQUENCING = Path("Documentation/zigux/phase8-tooling-lane-sequencing.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
VALIDATOR = Path("scripts/zigux/validate-phase8.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
EXEC_CMD_HELPER = Path("tools/lib/subcmd/exec-cmd.zig")
EXEC_CMD_TEST = Path("zigux/tests/phase8_exec_cmd.zig")
EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")
EXEC_CMD_SHARED_BUILD = Path("zigux/tests/phase8_build.zig")

REQUIRED_FILES = (
    DOCS_README,
    EXEC_CMD_SLICE,
    EXEC_CMD_SEQUENCING,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    VALIDATOR,
    MAKEFILE,
    WORKFLOW,
    EXEC_CMD_HELPER,
    EXEC_CMD_TEST,
    EXEC_CMD_BUILD,
    EXEC_CMD_SHARED_BUILD,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    DOCS_README: (
        "Phase 8 notes",
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        "scripts/zigux/validate-phase8.py",
        "tools/lib/subcmd/exec-cmd.zig",
        "zigux/tests/phase8_exec_cmd.zig",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        "make -C zigux phase8-exec-cmd-test",
        "make -C zigux phase8-validate",
    ),
    EXEC_CMD_SLICE: (
        "`PHASE8_SLICE=exec-cmd-deferred-exec-packet`",
        "buildDeferredExeclCall()",
        "buildDeferredExecvCall()",
        "`make -C zigux phase8-validate`",
        "deferred execution",
        "queue ownership",
        "kernel/workqueue.c remains a Phase 14 boundary-study target",
        "preserved explicit-empty exec-path sentinel",
        "inherited-empty-`PATH` trailing-`:` shape",
        "root-cwd `//relative` output shape",
        "samePathIdentity()",
        "choosePwdCwdFromIdentities()",
        "stat-backed same-location proof",
        "no retry scheduling, timer-backed backoff, timeout handling, or poll-loop ownership around deferred execution",
        "no queue ownership, wakeup routing, worker-pool control, or scheduler-visible execution substrate",
        "deferred-execution runtime, a broader task queue, or any workqueue-style execution substrate",
    ),
    EXEC_CMD_SEQUENCING: (
        "### 1. Exec-cmd lane",
        "shared validator-first entrypoint: `python3 scripts/zigux/validate-phase8.py`",
        "`Documentation/zigux/phase8-exec-cmd-slice.md`",
        "`tools/lib/subcmd/exec-cmd.zig`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "Keep follow-up in this lane limited to truthful survey or reminder-surface repair around the now-readable direct exec-cmd shard.",
    ),
    REVIEW_CHECKLIST: (
        "if the change touches the shared Phase 8 userspace-adjacent tooling packet",
        "`Documentation/zigux/phase8-exec-cmd-slice.md`",
        "`tools/lib/subcmd/exec-cmd.zig`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context",
        "runtime-substrate or bridge-readiness evidence",
    ),
    SCRIPTS_README: (
        "Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit",
        "`Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, and `make -C zigux phase8-exec-cmd-test` keep the direct command-boundary packet explicit from the scripts root without collapsing the separately owned help packet back into the same owner lane`",
    ),
    TESTS_README: (
        "current direct-readback Phase 8 anchors:",
        "`scripts/zigux/validate-phase8.py`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
    ),
    VALIDATOR: (
        'EXEC_CMD_HELPER = Path("tools/lib/subcmd/exec-cmd.zig")',
        'EXEC_CMD_TEST = Path("zigux/tests/phase8_exec_cmd.zig")',
        'EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")',
        'EXEC_CMD_PACKET_CHECKER = Path("scripts/zigux/check-phase8-exec-cmd-packet.py")',
        "EXEC_CMD_PACKET_CHECKER,",
    ),
    MAKEFILE: (
        "phase8-exec-cmd-test:",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        "phase8: phase8-validate phase8-exec-cmd-test",
    ),
    WORKFLOW: (
        "Validate Phase 8 tooling routes",
        "Run focused Phase 8 exec-cmd tests",
    ),
    EXEC_CMD_HELPER: (
        "pub fn samePathIdentity(",
        "pub fn collectExeclArgs(",
        "pub fn buildDeferredExeclCall(",
        "pub fn buildDeferredExecvCall(",
        "pub fn choosePwdCwdFromIdentities(",
        'test "EnvMap owns inserted keys so later caller mutations cannot corrupt lookups" {',
        'test "buildSearchPath rewrites relative entries against the working directory" {',
        'test "setupPathWithPwd falls back to cwd when logical PWD identity is unavailable" {',
        'test "setupPathWithPwd ignores an explicitly empty logical PWD even when identity matches" {',
        'test "collectExeclArgs rejects a null terminator that lands in MAX_ARGS" {',
        'test "buildDeferredExeclCall keeps the execl handoff pure and launch-free" {',
    ),
    EXEC_CMD_TEST: (
        'test "phase 8 exec-cmd note keeps deferred execution boundaries explicit" {',
        'test "phase 8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit" {',
        'test "phase 8 exec-cmd shared witness keeps argv0 sentinel path shapes explicit" {',
        '"tools/lib/subcmd/exec-cmd.zig"',
        '"Run focused Phase 8 exec-cmd tests"',
        'try expectContains(slice_note, "deferred execution");',
        'try expectContains(slice_note, "queue ownership");',
        'try expectContains(slice_note, "kernel/workqueue.c remains a Phase 14 boundary-study target");',
        'try expectContains(slice_note, "no retry scheduling, timer-backed backoff, timeout handling, or poll-loop ownership around deferred execution");',
        'try expectContains(slice_note, "no queue ownership, wakeup routing, worker-pool control, or scheduler-visible execution substrate");',
        'try expectContains(slice_note, "deferred-execution runtime, a broader task queue, or any workqueue-style execution substrate");',
        'const matched = try exec_cmd.setupPathWithPwd(',
        '"/logical/repo/tools/bin:/logical/repo/scripts:/usr/bin",',
        'try std.testing.expectError(',
        'error.MissingNullTerminator,',
        'error.TooManyArguments,',
        'exec_cmd.collectExeclArgs(',
        'exec_cmd.buildDeferredExeclCall(\n            std.testing.allocator,\n            config,\n            "record",\n            overflowing_tail[0..],\n        ),',
        'var deferred_execv = try exec_cmd.buildDeferredExecvCall(',
        'const rooted_search_path = try exec_cmd.buildSearchPath(',
        'try std.testing.expectEqualStrings("/repo/tools/bin:/tmp:/usr/bin", directory_only_search_path);',
        'const root_only_search_path = try exec_cmd.buildSearchPath(',
        'try expectNotContains(validate_phase8, "expectMissingPath(\\"tools/lib/subcmd/exec-cmd.zig\\")");',
        'const explicit_empty = try exec_cmd.getArgvExecPath(',
        'try std.testing.expectEqualStrings("", explicit_empty);',
        'var deferred_execl_command_only = try exec_cmd.buildDeferredExeclCall(',
        'try std.testing.expectEqual(@as(usize, 3), deferred_execl_command_only.argv.len);',
        'try std.testing.expectEqualStrings("record", deferred_execl_command_only.argv[1].?);',
        'const root_empty_path = try exec_cmd.setupPath(',
        'try std.testing.expectEqualStrings("//tools:", root_empty_path);',
    ),
    EXEC_CMD_BUILD: (
        "phase8_exec_cmd.zig",
        "phase8-exec-cmd-tests",
        "Run focused Phase 8 exec-cmd tests",
    ),
    EXEC_CMD_SHARED_BUILD: (
        '../../tools/lib/subcmd/exec-cmd.zig',
        'phase8_exec_cmd.zig',
        '"phase8-exec-cmd-shared-tests"',
        'test_step.dependOn(&run_exec_cmd_tests.step);',
    ),
}


@dataclass
class ValidationResult:
    missing_files: list[str]
    missing_markers: list[str]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_root(root: Path) -> ValidationResult:
    missing_files = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    missing_markers: list[str] = []
    for relative_path, markers in FILE_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{relative_path}:{marker}")
    return ValidationResult(missing_files=missing_files, missing_markers=missing_markers)


def emit_result(result: ValidationResult) -> int:
    if result.missing_files or result.missing_markers:
        print("PHASE8_EXEC_CMD_PACKET=fail")
        if result.missing_files:
            print("PHASE8_EXEC_CMD_PACKET_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_EXEC_CMD_PACKET_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_EXEC_CMD_PACKET_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_EXEC_CMD_PACKET_MISSING_MARKERS_END")
        return 1

    print("PHASE8_EXEC_CMD_PACKET=pass")
    print(f"PHASE8_EXEC_CMD_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_EXEC_CMD_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_MARKERS.values())}"
    )
    return 0


def _passing_fixture(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        markers = FILE_MARKERS.get(relative_path)
        if markers is None:
            _write(root / relative_path, f"{relative_path.as_posix()}\n")
        else:
            _write(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    case_count = 1
    with tempfile.TemporaryDirectory(prefix="phase8-exec-cmd-packet-selftest-") as tmp:
        root = Path(tmp)
        _passing_fixture(root)

        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers:
            raise AssertionError("expected passing fixture to validate")

        for relative_path, markers in FILE_MARKERS.items():
            path = root / relative_path
            original = _read(path)
            for marker in markers:
                path.write_text(original.replace(marker, "", 1), encoding="utf-8")
                result = validate_root(root)
                expected = f"{relative_path}:{marker}"
                if expected not in result.missing_markers:
                    raise AssertionError(f"expected missing marker to be reported: {expected}")
                path.write_text(original, encoding="utf-8")
                case_count += 1

        for relative_path in REQUIRED_FILES:
            path = root / relative_path
            original = _read(path)
            path.unlink()
            result = validate_root(root)
            expected = relative_path.as_posix()
            if expected not in result.missing_files:
                raise AssertionError(f"expected missing file to be reported: {expected}")
            _write(path, original)
            case_count += 1

    print("PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass")
    print(f"PHASE8_EXEC_CMD_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return emit_result(validate_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())