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
DEFERRED_EXEC_GAP_SURVEY = Path("Documentation/zigux/phase8-deferred-exec-gap-survey.md")
EXEC_CMD_SLICE = Path("Documentation/zigux/phase8-exec-cmd-slice.md")
EXEC_CMD_HELPER = Path("tools/lib/subcmd/exec-cmd.zig")
EXEC_CMD_TEST = Path("zigux/tests/phase8_exec_cmd.zig")
EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")
EXEC_CMD_PACKET_CHECKER = Path("scripts/zigux/check-phase8-exec-cmd-packet.py")
VALIDATOR = Path("scripts/zigux/validate-phase8.py")

REQUIRED_FILES = (
    DEFERRED_EXEC_GAP_SURVEY,
    EXEC_CMD_SLICE,
    EXEC_CMD_HELPER,
    EXEC_CMD_TEST,
    EXEC_CMD_BUILD,
    EXEC_CMD_PACKET_CHECKER,
    VALIDATOR,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    DEFERRED_EXEC_GAP_SURVEY: (
        "`PHASE8_SURVEY=deferred-exec-gap-readback`",
        "`tools/lib/subcmd/exec-cmd.c`",
        "`buildDeferredExeclCall()`",
        "`buildDeferredExecvCall()`",
        "`kernel/workqueue.c`",
        "helper-first",
        "focused exec-cmd build shard",
        "existing packet checker",
        "no direct `execvp()` side effects",
        "no waiting or retry scheduling",
        "no queue ownership",
        "no scheduler-facing transport",
    ),
    EXEC_CMD_SLICE: (
        "`PHASE8_SLICE=exec-cmd-deferred-exec-packet`",
        "deferred execution",
        "queue ownership",
        "`kernel/workqueue.c`",
        "Phase 14",
    ),
    EXEC_CMD_HELPER: (
        "pub fn buildDeferredExeclCall(",
        "pub fn buildDeferredExecvCall(",
        "pub fn collectExeclArgs(",
    ),
    EXEC_CMD_TEST: (
        'test "phase 8 exec-cmd note keeps deferred execution boundaries explicit" {',
        'try expectContains(slice_note, "deferred execution");',
        'try expectContains(slice_note, "queue ownership");',
        'try expectContains(slice_note, "kernel/workqueue.c remains a Phase 14 boundary-study target");',
    ),
    EXEC_CMD_BUILD: (
        'b.path("../../tools/lib/subcmd/exec-cmd.zig")',
        'b.path("phase8_exec_cmd.zig")',
        '"Run focused Phase 8 exec-cmd tests"',
    ),
    EXEC_CMD_PACKET_CHECKER: (
        'EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")',
        'EXEC_CMD_PACKET_CHECKER = Path("scripts/zigux/check-phase8-exec-cmd-packet.py")',
        '"Run focused Phase 8 exec-cmd tests"',
    ),
    VALIDATOR: (
        'EXEC_CMD_PACKET_CHECKER = Path("scripts/zigux/check-phase8-exec-cmd-packet.py")',
        'EXEC_CMD_HELPER = Path("tools/lib/subcmd/exec-cmd.zig")',
        'EXEC_CMD_TEST = Path("zigux/tests/phase8_exec_cmd.zig")',
        'EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")',
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
        print("PHASE8_DEFERRED_EXEC_GAP_SURVEY=fail")
        if result.missing_files:
            print("PHASE8_DEFERRED_EXEC_GAP_SURVEY_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_DEFERRED_EXEC_GAP_SURVEY_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_DEFERRED_EXEC_GAP_SURVEY_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_DEFERRED_EXEC_GAP_SURVEY_MISSING_MARKERS_END")
        return 1

    print("PHASE8_DEFERRED_EXEC_GAP_SURVEY=pass")
    print(f"PHASE8_DEFERRED_EXEC_GAP_SURVEY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_DEFERRED_EXEC_GAP_SURVEY_REQUIRED_MARKER_COUNT="
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
    with tempfile.TemporaryDirectory(prefix="phase8-deferred-exec-gap-selftest-") as tmp:
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

    print("PHASE8_DEFERRED_EXEC_GAP_SURVEY_SELF_TEST=pass")
    print(f"PHASE8_DEFERRED_EXEC_GAP_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
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