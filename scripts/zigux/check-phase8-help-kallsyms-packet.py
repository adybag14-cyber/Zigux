#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import tempfile
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path


def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = _default_root()
HELP_SLICE = Path("Documentation/zigux/phase8-help-slice.md")
KALLSYMS_SLICE = Path("Documentation/zigux/phase8-kallsyms-slice.md")
TOOLING_LANE_SEQUENCE = Path("Documentation/zigux/phase8-tooling-lane-sequencing.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
VALIDATOR = Path("scripts/zigux/validate-phase8.py")
BUILD_SHARD_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-build-shard.py")
MAKEFILE = Path("zigux/Makefile")
TESTS_README = Path("zigux/tests/README.md")
HELP_KALLSYMS_BUILD = Path("zigux/tests/phase8_help_kallsyms_only_build.zig")
HELP_BUILD = Path("zigux/tests/phase8_help_only_build.zig")
HELP_TEST = Path("zigux/tests/phase8_help.zig")
KALLSYMS_BUILD = Path("zigux/tests/phase8_kallsyms_only_build.zig")
KALLSYMS_TEST = Path("zigux/tests/phase8_kallsyms.zig")
HELP_SOURCE = Path("tools/lib/subcmd/help.zig")
KALLSYMS_SOURCE = Path("tools/lib/symbol/kallsyms.zig")

REQUIRED_FILES = (
    HELP_SLICE,
    KALLSYMS_SLICE,
    TOOLING_LANE_SEQUENCE,
    CHECKLIST,
    SCRIPTS_README,
    VALIDATOR,
    BUILD_SHARD_CHECKER,
    MAKEFILE,
    TESTS_README,
    HELP_KALLSYMS_BUILD,
    HELP_BUILD,
    HELP_TEST,
    KALLSYMS_BUILD,
    KALLSYMS_TEST,
    HELP_SOURCE,
    KALLSYMS_SOURCE,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    HELP_SLICE: (
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "parked help-and-kallsyms packet reviewable",
        "`zigux/tests/phase8_help_only_build.zig` and `zigux/tests/phase8_help.zig` through current public default-branch raw readback only",
        "current public raw reread shows `zigux/tests/phase8_help.zig` still names older helper surfaces such as `CmdNames`, `commandNameFromEntry`, `planPrettyPrint`, `loadCommandListsFromEnvPath`, and `writeCommandSectionsForTerminal`, while the shipped helper body on current `master` exposes `CommandNames`, `trimCommandPrefix`, `computePrettyLayout`, `renderPrettyStringList`, and `renderCommandSections`, so the dedicated help replay should be treated as a mixed-source review note rather than same-source proof until that packet is realigned",
        "the current public raw `zigux/tests/phase8_help.zig` replay no longer matches that shipped helper surface, so it is not honest same-source proof for the parked help packet until a help-local replay refresh lands",
        "refresh the dedicated help replay so it uses the shipped helper surface instead of the older pre-rename API names",
    ),
    KALLSYMS_SLICE: (
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "shared validation overlap only",
        "oversized symbol names now truncate to `KSYM_NAME_LEN`",
        "weak-object `V` and `v` classes still follow the current C header contract",
        "the public raw fallback returns usable `tools/lib/symbol/kallsyms.zig` helper content",
        "the helper-local source tests still keep the split CRLF contract reviewable: the chunked parser normalizes the CRLF-backed name to `startup_64`, while the reader, path, and callback wrappers preserve one trailing carriage return before newline",
        "the public raw fallback also returns usable `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` bodies; the dedicated replay still keeps the chunked-reader `startup_64\\r` expectation visible as a broader symbol-packet witness, while the focused `make -C zigux phase8-kallsyms-test` build route remains tied to the helper-local source tests in `tools/lib/symbol/kallsyms.zig`",
        "the split raw-backed CRLF contract: the dedicated replay keeps the chunked-reader `startup_64\\r` witness visible, while the helper-local wrapper tests still preserve the trailing carriage return on the reader, path, and callback wrapper path",
    ),
    TOOLING_LANE_SEQUENCE: (
        "current public default-branch raw readback now also serves `tools/lib/symbol/kallsyms.zig`, so the shared owner map should treat the helper path as readable current-tree evidence while the mixed help-plus-kallsyms build shard stays a shared validation route instead of turning help-local and symbol-local follow-through into one owner",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig` and `make -C zigux phase8-help-kallsyms-test` are still shared smoke coverage only",
        "current public default-branch raw readback now also serves `tools/lib/symbol/kallsyms.zig`, so the live symbol lane should treat the helper path as readable current-tree evidence while the mixed help-plus-kallsyms build shard stays shared smoke coverage instead of turning help-local and symbol-local follow-through into one owner",
        "`Documentation/zigux/phase8-kallsyms-slice.md` and the public raw helper path are both readable again, so shared reminder surfaces should keep help-local output or command-source drift in the dedicated help lane and reserve symbol follow-through for parser, truncation, or callback-wrapper truthfulness instead of replaying older unreadable-helper assumptions",
        "When the mixed `phase8-help-kallsyms` smoke route reopens, treat it as shared validation only: help-local output or command-source drift stays in the help lane, while parser, truncation, or callback-wrapper drift stays in the symbol lane even though `tools/lib/symbol/kallsyms.zig` is publicly readable again.",
        "The earlier symbol-lane visible cue is no longer reopened: current public default-branch raw readback already serves `tools/lib/symbol/kallsyms.zig`, so shared sequencing should keep the mixed help-and-kallsyms build shard classified as validation overlap only while reserving parser follow-through for the dedicated `kallsyms` lane without replaying unreadable-helper assumptions.",
    ),
    CHECKLIST: (
        "if the change touches the parked Phase 8 `help` packet",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "if the change touches the parked Phase 8 `kallsyms` parser packet",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-kallsyms-test`",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
    ),
    SCRIPTS_README: (
        "while treating the returned help, kallsyms, and broader libbpf-segment companions as public-tree-backed broader packet evidence instead of as missing routes or direct scripts-root anchors",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py` and `scripts/zigux/check-phase8-libbpf-shard-routes.py` rematerialize those broader help, kallsyms, and libbpf-segment companions on `master`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`tools/lib/symbol/kallsyms.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
    ),
    VALIDATOR: (
        'HELP_KALLSYMS_PACKET_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-packet.py")',
        'HELP_KALLSYMS_BUILD_SHARD_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-build-shard.py")',
        "HELP_KALLSYMS_PACKET_CHECKER,",
        "HELP_KALLSYMS_BUILD_SHARD_CHECKER,",
    ),
    BUILD_SHARD_CHECKER: (
        'SCRIPT_PATH = "scripts/zigux/check-phase8-help-kallsyms-build-shard.py"',
        'BUILD_PATH = "zigux/tests/phase8_help_kallsyms_only_build.zig"',
        '"../../tools/lib/subcmd/help.zig"',
        '"../../tools/lib/symbol/kallsyms.zig"',
        '"phase8-help-tests"',
        '"phase8-kallsyms-tests"',
        '"Run the focused Phase 8 help and kallsyms shared tests."',
        "test_step.dependOn(&run_help_tests.step);",
        "test_step.dependOn(&run_kallsyms_tests.step);",
    ),
    MAKEFILE: (
        "phase8-help-kallsyms-test:",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test",
    ),
    TESTS_README: (
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
    ),
    HELP_KALLSYMS_BUILD: (
        "../../tools/lib/subcmd/help.zig",
        "../../tools/lib/symbol/kallsyms.zig",
        "Run the focused Phase 8 help and kallsyms shared tests.",
    ),
    HELP_BUILD: (
        "../../tools/lib/subcmd/help.zig",
        "phase8-help-only-tests",
        "Run the focused Phase 8 help-only tests.",
    ),
    HELP_TEST: (
        'test "phase 8 help slice note keeps helper-first output-stable tooling posture and non-goals explicit"',
        'test "phase 8 help slice covers command-list ownership, filtering, exclusion, terminal sizing, and layout planning"',
        'test "phase 8 help output emission keeps column-major pretty-printing pure and testable"',
        'test "phase 8 help section rendering keeps the stable main and PATH headings reviewable"',
        "help.CmdNames.init(",
        "help.commandNameFromEntry(",
        "help.planPrettyPrint(",
        "help.loadCommandListsFromEnvPath(",
        "help.writeCommandSectionsForTerminal(",
        "help.writePrettyPrintStringListForTerminal(",
    ),
    HELP_SOURCE: (
        'pub const default_command_prefix = "perf-";',
        "pub fn trimCommandPrefix(",
        "pub fn computePrettyLayout(",
        "pub fn renderPrettyStringList(",
        "pub fn renderCommandSections(",
        'test "renderPrettyStringList keeps the same row-major pretty layout as help.c" {',
        'test "renderCommandSections keeps stable headers for main and fallback command groups" {',
    ),
    KALLSYMS_BUILD: (
        "../../tools/lib/symbol/kallsyms.zig",
        "phase8-kallsyms-only-tests",
        "Run the focused Phase 8 kallsyms-only tests.",
    ),
    KALLSYMS_TEST: (
        'test "phase 8 kallsyms slice note keeps the C-aligned truncation contract explicit"',
        'test "phase 8 kallsyms direct parser truncates oversized names"',
        'test "phase 8 kallsyms keeps weak object classes on the current header-backed path"',
        'test "phase 8 kallsyms chunked parser also truncates oversized names"',
        'expectEqualStrings("startup_64\\r", symbols.items[0].name)',
        'test "phase 8 kallsyms wrappers preserve the parked callback contract"',
    ),
    KALLSYMS_SOURCE: (
        "pub const KSYM_NAME_LEN: usize = 512;",
        "pub fn parseLine(",
        "pub fn kallsymsParseFile(",
        "pub fn forEachParsedPath(",
        'test "weak object symbol classes keep the current C helper classification" {',
        'test "parseLine truncates oversized names without keeping a parser-local error surface" {',
        'test "reader, path, and callback wrappers preserve raw carriage returns before newline" {',
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
        print("PHASE8_HELP_KALLSYMS_PACKET=fail")
        if result.missing_files:
            print("PHASE8_HELP_KALLSYMS_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_HELP_KALLSYMS_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_HELP_KALLSYMS_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_HELP_KALLSYMS_MISSING_MARKERS_END")
        return 1

    print("PHASE8_HELP_KALLSYMS_PACKET=pass")
    print(f"PHASE8_HELP_KALLSYMS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE8_HELP_KALLSYMS_REQUIRED_MARKER_COUNT=" f"{sum(len(markers) for markers in FILE_MARKERS.values())}")
    return 0


def emit_captured_result(root: Path) -> tuple[int, str]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = emit_result(validate_root(root))
    return exit_code, buffer.getvalue()


def _passing_fixture(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path in FILE_MARKERS:
            _write(root / relative_path, "\n".join(FILE_MARKERS[relative_path]) + "\n")
        else:
            _write(root / relative_path, f"{relative_path.as_posix()}\n")


def run_self_test() -> int:
    case_count = 1
    with tempfile.TemporaryDirectory(prefix="phase8-help-kallsyms-packet-selftest-") as tmp:
        root = Path(tmp)
        _passing_fixture(root)

        expected_default_root = Path(__file__).resolve()
        if len(expected_default_root.parents) >= 3:
            expected_default_root = expected_default_root.parents[2]
        else:
            expected_default_root = expected_default_root.parent
        if ROOT != expected_default_root:
            raise AssertionError("expected default root to resolve to the repository root")

        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers:
            raise AssertionError("expected passing fixture to validate")

        for relative_path, markers in FILE_MARKERS.items():
            path = root / relative_path
            original = _read(path)
            for marker in markers:
                if marker not in original:
                    raise AssertionError(f"expected marker in fixture: {relative_path}:{marker}")
                mutated = original.replace(marker, "")
                if mutated == original:
                    raise AssertionError(f"expected fixture mutation to remove marker: {relative_path}:{marker}")
                path.write_text(mutated, encoding="utf-8")
                result = validate_root(root)
                expected = f"{relative_path}:{marker}"
                if expected not in result.missing_markers:
                    raise AssertionError(f"expected missing marker to be reported: {expected}")
                path.write_text(original, encoding="utf-8")
                case_count += 1

        output_case_root = root / "output_case"
        _passing_fixture(output_case_root)
        crlf_marker = "the split raw-backed CRLF contract: the dedicated replay keeps the chunked-reader `startup_64\\r` witness visible, while the helper-local wrapper tests still preserve the trailing carriage return on the reader, path, and callback wrapper path"
        kallsyms_slice_path = output_case_root / KALLSYMS_SLICE
        kallsyms_slice_path.write_text(
            _read(kallsyms_slice_path).replace(crlf_marker, ""),
            encoding="utf-8",
        )
        exit_code, output = emit_captured_result(output_case_root)
        expected_marker = f"{KALLSYMS_SLICE}:{crlf_marker}"
        if exit_code != 1:
            raise AssertionError("expected emit_result to fail for a missing kallsyms slice marker")
        if "PHASE8_HELP_KALLSYMS_PACKET=fail" not in output:
            raise AssertionError("expected fail banner in captured output")
        if "PHASE8_HELP_KALLSYMS_MISSING_MARKERS_START" not in output:
            raise AssertionError("expected missing marker banner in captured output")
        if expected_marker not in output:
            raise AssertionError(f"expected missing marker in captured output: {expected_marker}")
        case_count += 1

        missing_file_case_root = root / "missing_file_output_case"
        _passing_fixture(missing_file_case_root)
        (missing_file_case_root / KALLSYMS_SOURCE).unlink()
        exit_code, output = emit_captured_result(missing_file_case_root)
        expected_file = KALLSYMS_SOURCE.as_posix()
        if exit_code != 1:
            raise AssertionError("expected emit_result to fail for a missing kallsyms helper file")
        if "PHASE8_HELP_KALLSYMS_MISSING_FILES_START" not in output:
            raise AssertionError("expected missing file banner in captured output")
        if expected_file not in output:
            raise AssertionError(f"expected missing file in captured output: {expected_file}")
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

    print("PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
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