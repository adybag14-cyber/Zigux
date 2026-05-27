#!/usr/bin/env python3
"""Guard the shared Phase 9 initcall-versus-registration lifecycle boundary."""

from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path

SEQUENCING = Path("Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md")
OWNERSHIP = Path("Documentation/zigux/phase9-runtime-pilot-ownership-map.md")
SAMPLES_README = Path("samples/zigux/README.md")
LOADER_CONTRACT = Path("zigux/kernel/runtime_loader_contract.zig")
PHASE9_BUILD = Path("zigux/tests/phase9_build.zig")
TRACE_EVENTS_MODULE = Path("zigux/tests/runtime_trace_events_module.zig")
TRACE_EVENTS_REENTRY = Path("samples/zigux/runtime_trace_events_registration_reentry_gate.zig")
KRETPROBE_REENTRY = Path("samples/zigux/runtime_kretprobe_registration_reentry_gate.zig")

REQUIRED_FILES = (
    SEQUENCING,
    OWNERSHIP,
    SAMPLES_README,
    LOADER_CONTRACT,
    PHASE9_BUILD,
    TRACE_EVENTS_MODULE,
    TRACE_EVENTS_REENTRY,
    KRETPROBE_REENTRY,
)

REQUIRED_MARKERS: dict[Path, tuple[str, ...]] = {
    SEQUENCING: (
        "runtime module lifecycle parity",
        "`zigux/kernel/runtime_loader_contract.zig` keeps the initcall and registration boundary literal inside the surviving shared packet",
        "the shared-loader reminder packet keeps metadata-only registration posture explicit instead of executable runtime registration",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`",
    ),
    OWNERSHIP: (
        "Keep this packet shared-owner and metadata-only. It does not prove live runtime registration",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "`samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`",
    ),
    SAMPLES_README: (
        "Keep `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the reusable registration-reentry companion",
        "Keep `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig` explicit as the sample-side registration-reentry companion",
    ),
    LOADER_CONTRACT: (
        "entry_symbol: []const u8,",
        "exit_symbol: []const u8,",
        "pub const InitFlow = struct {",
        "pub fn readyForRuntimeLoad",
    ),
    PHASE9_BUILD: (
        ".name = \"phase9-runtime-loader-shared-tests\"",
        ".name = \"phase9-runtime-trace-events-registration-reentry-gate-tests\"",
        ".name = \"phase9-runtime-kretprobe-registration-reentry-gate-tests\"",
    ),
    TRACE_EVENTS_MODULE: (
        'test "runtime trace-events sample keeps lifecycle summary replay explicit at the module boundary" {',
        'test "runtime trace-events sample keeps initialized-stage exit replay explicit at the module boundary" {',
    ),
    TRACE_EVENTS_REENTRY: (
        'test "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages" {',
        'test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest" {',
    ),
    KRETPROBE_REENTRY: (
        'test "runtime kretprobe registration reentry stays reusable before selftest" {',
        'test "runtime kretprobe registration reentry stays reusable after selftest" {',
        'test "runtime kretprobe registration reentry stays fail-closed after exit" {',
    ),
}

FORBIDDEN_MARKERS: dict[Path, tuple[str, ...]] = {
    LOADER_CONTRACT: (
        "registerFunctionThread",
        "unregisterFunctionThread",
        "registerProbe(",
        "unregisterProbe(",
    ),
}


@dataclass
class ValidationResult:
    missing_files: list[str]
    missing_markers: list[str]
    forbidden_markers: list[str]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(repo_root: Path) -> ValidationResult:
    missing_files = [path.as_posix() for path in REQUIRED_FILES if not (repo_root / path).is_file()]
    missing_markers: list[str] = []
    forbidden_markers: list[str] = []

    for relative_path, markers in REQUIRED_MARKERS.items():
        absolute_path = repo_root / relative_path
        if not absolute_path.is_file():
            continue
        content = _read(absolute_path)
        for marker in markers:
            if marker not in content:
                missing_markers.append(f"{relative_path}:{marker}")

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        absolute_path = repo_root / relative_path
        if not absolute_path.is_file():
            continue
        content = _read(absolute_path)
        for marker in markers:
            if marker in content:
                forbidden_markers.append(f"{relative_path}:{marker}")

    return ValidationResult(
        missing_files=missing_files,
        missing_markers=missing_markers,
        forbidden_markers=forbidden_markers,
    )


def emit(result: ValidationResult) -> int:
    if result.missing_files or result.missing_markers or result.forbidden_markers:
        print("PHASE9_INITCALL_REGISTRATION_LIFECYCLE_BOUNDARY=fail")
        if result.missing_files:
            print("PHASE9_INITCALL_REGISTRATION_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE9_INITCALL_REGISTRATION_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE9_INITCALL_REGISTRATION_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE9_INITCALL_REGISTRATION_MISSING_MARKERS_END")
        if result.forbidden_markers:
            print("PHASE9_INITCALL_REGISTRATION_FORBIDDEN_MARKERS_START")
            for item in result.forbidden_markers:
                print(item)
            print("PHASE9_INITCALL_REGISTRATION_FORBIDDEN_MARKERS_END")
        return 1

    print("PHASE9_INITCALL_REGISTRATION_LIFECYCLE_BOUNDARY=pass")
    print(f"PHASE9_INITCALL_REGISTRATION_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE9_INITCALL_REGISTRATION_REQUIRED_MARKER_COUNT={sum(len(v) for v in REQUIRED_MARKERS.values())}")
    print(f"PHASE9_INITCALL_REGISTRATION_FORBIDDEN_MARKER_COUNT={sum(len(v) for v in FORBIDDEN_MARKERS.values())}")
    return 0


def _passing_fixture(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        required = "\n".join(REQUIRED_MARKERS.get(relative_path, ()))
        _write(root / relative_path, required + ("\n" if required else "fixture\n"))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase9-initcall-registration-") as tmp_dir:
        root = Path(tmp_dir)
        _passing_fixture(root)

        result = validate(root)
        if result.missing_files or result.missing_markers or result.forbidden_markers:
            raise AssertionError("expected passing fixture to validate")
        case_count += 1

        seq_path = root / SEQUENCING
        original = _read(seq_path)
        removed_marker = REQUIRED_MARKERS[SEQUENCING][1]
        _write(seq_path, original.replace(removed_marker, ""))
        result = validate(root)
        expected_missing = f"{SEQUENCING}:{removed_marker}"
        if expected_missing not in result.missing_markers:
            raise AssertionError("expected missing sequencing marker to be reported")
        case_count += 1
        _write(seq_path, original)

        contract_path = root / LOADER_CONTRACT
        original = _read(contract_path)
        _write(contract_path, original + "\nregisterProbe(\n")
        result = validate(root)
        expected_forbidden = f"{LOADER_CONTRACT}:registerProbe("
        if expected_forbidden not in result.forbidden_markers:
            raise AssertionError("expected forbidden loader marker to be reported")
        case_count += 1
        _write(contract_path, original)

        (root / KRETPROBE_REENTRY).unlink()
        result = validate(root)
        if KRETPROBE_REENTRY.as_posix() not in result.missing_files:
            raise AssertionError("expected missing file to be reported")
        case_count += 1

    print("PHASE9_INITCALL_REGISTRATION_LIFECYCLE_BOUNDARY_SELF_TEST=pass")
    print(f"PHASE9_INITCALL_REGISTRATION_LIFECYCLE_BOUNDARY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Guard the shared Phase 9 initcall-versus-registration lifecycle boundary."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to validate (defaults to current working directory).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker self-tests instead of validating a repository.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return emit(validate(args.repo_root.resolve()))


if __name__ == "__main__":
    raise SystemExit(main())
