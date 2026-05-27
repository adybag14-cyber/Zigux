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
GAP_NOTE = Path("Documentation/zigux/phase8-command-syscall-boundary-gap.md")
EXEC_CMD_SLICE = Path("Documentation/zigux/phase8-exec-cmd-slice.md")
BRIDGE_SURVEY = Path("Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
EXEC_CMD_PACKET_CHECKER = Path("scripts/zigux/check-phase8-exec-cmd-packet.py")
VALIDATOR = Path("scripts/zigux/validate-phase8.py")
EXEC_CMD_HELPER = Path("tools/lib/subcmd/exec-cmd.zig")
EXEC_CMD_TEST = Path("zigux/tests/phase8_exec_cmd.zig")
EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")
SHARED_BUILD = Path("zigux/tests/phase8_build.zig")
MAKEFILE = Path("zigux/Makefile")

REQUIRED_FILES = (
    GAP_NOTE,
    EXEC_CMD_SLICE,
    BRIDGE_SURVEY,
    SCRIPTS_README,
    TESTS_README,
    EXEC_CMD_PACKET_CHECKER,
    VALIDATOR,
    EXEC_CMD_HELPER,
    EXEC_CMD_TEST,
    EXEC_CMD_BUILD,
    SHARED_BUILD,
    MAKEFILE,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    GAP_NOTE: (
        "`PHASE8_COMMAND_SYSCALL_GAP=userspace-adjacent-tooling`",
        "`tools/lib/subcmd/exec-cmd.c`",
        "`tools/lib/subcmd/help.c`",
        "`tools/lib/symbol/kallsyms.c`",
        "`tools/lib/bpf/libbpf.c`",
        "`tools/lib/subcmd/exec-cmd.zig`",
        "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
        "`scripts/zigux/validate-phase8.py`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
        "no direct `execvp()` parity",
        "no child launch",
        "no process waiting",
        "no syscall-backed runtime command boundary beyond helper-local deferred carriers",
        "helper-first command foothold",
    ),
    EXEC_CMD_SLICE: (
        "`PHASE8_SLICE=exec-cmd-deferred-exec-packet`",
        "deferred execution",
        "buildDeferredExeclCall()",
        "buildDeferredExecvCall()",
        "no direct `execvp()` parity or process-launch behavior",
    ),
    BRIDGE_SURVEY: (
        "The separate Phase 8 command-side anchors under `tools/lib/subcmd/` and `tools/lib/symbol/` keep their own parked packets.",
        "This survey stays limited to the libbpf-side syscall, descriptor, and routing boundary from `tools/lib/bpf/libbpf.c`.",
    ),
    SCRIPTS_README: (
        "Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit",
        "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
        "`scripts/zigux/validate-phase8.py`",
    ),
    TESTS_README: (
        "current direct-readback Phase 8 anchors:",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
    ),
    EXEC_CMD_PACKET_CHECKER: (
        "EXEC_CMD_SLICE = Path(\"Documentation/zigux/phase8-exec-cmd-slice.md\")",
        "EXEC_CMD_HELPER = Path(\"tools/lib/subcmd/exec-cmd.zig\")",
        "EXEC_CMD_TEST = Path(\"zigux/tests/phase8_exec_cmd.zig\")",
    ),
    VALIDATOR: (
        'EXEC_CMD_HELPER = Path("tools/lib/subcmd/exec-cmd.zig")',
        'EXEC_CMD_TEST = Path("zigux/tests/phase8_exec_cmd.zig")',
        'EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")',
    ),
    EXEC_CMD_HELPER: (
        "pub fn buildDeferredExeclCall(",
        "pub fn buildDeferredExecvCall(",
        "pub fn setupPathWithPwd(",
    ),
    EXEC_CMD_TEST: (
        'test "phase 8 exec-cmd note keeps deferred execution boundaries explicit" {',
        'test "phase 8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit" {',
    ),
    EXEC_CMD_BUILD: (
        "phase8_exec_cmd.zig",
        "phase8-exec-cmd-tests",
    ),
    SHARED_BUILD: (
        '"phase8-exec-cmd-shared-tests"',
        "../../tools/lib/subcmd/exec-cmd.zig",
    ),
    MAKEFILE: (
        "phase8-exec-cmd-test:",
        "phase8: phase8-validate phase8-exec-cmd-test",
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
        print("PHASE8_COMMAND_SYSCALL_GAP=fail")
        if result.missing_files:
            print("PHASE8_COMMAND_SYSCALL_GAP_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_COMMAND_SYSCALL_GAP_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_COMMAND_SYSCALL_GAP_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_COMMAND_SYSCALL_GAP_MISSING_MARKERS_END")
        return 1

    print("PHASE8_COMMAND_SYSCALL_GAP=pass")
    print(f"PHASE8_COMMAND_SYSCALL_GAP_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_COMMAND_SYSCALL_GAP_REQUIRED_MARKER_COUNT="
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
    with tempfile.TemporaryDirectory(prefix="phase8-command-syscall-gap-selftest-") as tmp:
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

        missing_path = root / GAP_NOTE
        original = _read(missing_path)
        missing_path.unlink()
        result = validate_root(root)
        if GAP_NOTE.as_posix() not in result.missing_files:
            raise AssertionError("expected missing gap note to be reported")
        _write(missing_path, original)
        case_count += 1

    print("PHASE8_COMMAND_SYSCALL_GAP_SELF_TEST=pass")
    print(f"PHASE8_COMMAND_SYSCALL_GAP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 8 command/syscall boundary gap survey against live reminder surfaces."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate (defaults to the current repository root).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run fixture-based self-tests instead of validating a repository.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return emit_result(validate_root(args.root.resolve()))


if __name__ == "__main__":
    raise SystemExit(main())
