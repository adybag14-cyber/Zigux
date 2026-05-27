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
HELP_SLICE = Path("Documentation/zigux/phase8-help-slice.md")
KALLSYMS_SLICE = Path("Documentation/zigux/phase8-kallsyms-slice.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
VALIDATOR = Path("scripts/zigux/validate-phase8.py")
SCRIPTS_README = Path("scripts/zigux/README.md")
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
    CHECKLIST,
    VALIDATOR,
    SCRIPTS_README,
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
        "`PHASE8_SLICE=help-output-stable-packet`",
        "`tools/lib/subcmd/*.zig`",
        "`make -C zigux phase8-help-test`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig` through the public raw fallback as shared validation overlap only",
        "the mixed `zigux/tests/phase8_help_kallsyms_only_build.zig` shard remains shared validation overlap only and does not transfer help-lane ownership into the dedicated symbol lane",
        "`CommandNames`, `trimCommandPrefix`, `computePrettyLayout`, `renderPrettyStringList`, and `renderCommandSections`",
        "shared-overlap build shard in `zigux/tests/phase8_help_kallsyms_only_build.zig` through the public raw fallback",
        "without reopening exec-cmd command ownership, symbol-lane parser behavior, or bridge-heavy libbpf work",
    ),
    KALLSYMS_SLICE: (
        "`PHASE8_SLICE=kallsyms-parse-wrapper-parked`",
        "oversized symbol names now truncate to `KSYM_NAME_LEN`",
        "weak-object `V` and `v` classes still follow the current C header contract",
        "`make -C zigux phase8-kallsyms-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "the dedicated replay now keeps the chunked-reader `startup_64` witness aligned with that helper-local CRLF normalization path",
    ),
    CHECKLIST: (
        "if the change touches the parked Phase 8 `help` packet",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "if the change touches the parked Phase 8 `kallsyms` parser packet",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-kallsyms-test`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
    ),
    VALIDATOR: (
        'HELP_KALLSYMS_PACKET_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-packet.py")',
        'HELP_KALLSYMS_BUILD_SHARD_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-build-shard.py")',
    ),
    SCRIPTS_README: (
        "## Phase 8",
        "scripts/zigux/check-phase8-help-kallsyms-packet.py",
        "returned help, kallsyms, and broader libbpf-segment companions as public-tree-backed broader packet evidence instead of as missing routes or direct scripts-root anchors",
        "current public-tree rereads plus the shared packet guards `scripts/zigux/check-phase8-help-kallsyms-packet.py` and `scripts/zigux/check-phase8-libbpf-shard-routes.py` rematerialize those broader help, kallsyms, and libbpf-segment companions on `master`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`, `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`",
    ),
    MAKEFILE: (
        "phase8-help-test:",
        "phase8-help-kallsyms-test:",
        "phase8-kallsyms-test:",
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test",
    ),
    TESTS_README: (
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
    ),
    HELP_KALLSYMS_BUILD: (
        "../../tools/lib/subcmd/help.zig",
        "../../tools/lib/symbol/kallsyms.zig",
        "Run the focused Phase 8 help and kallsyms shared tests.",
        "test_step.dependOn(&run_help_tests.step);",
        "test_step.dependOn(&run_kallsyms_tests.step);",
    ),
    HELP_BUILD: (
        "../../tools/lib/subcmd/help.zig",
        "phase8-help-only-tests",
        "Run the focused Phase 8 help-only tests.",
    ),
    HELP_TEST: (
        'test "phase 8 help slice keeps helper-first stable-output evidence explicit"',
        'test "phase 8 help command-set helpers keep stable filtering and layout planning"',
        'test "phase 8 help pretty printer keeps the current row-major stable output"',
        'test "phase 8 help section rendering keeps stable main and fallback headings"',
        'test "phase 8 help empty exec path keeps the stable heading unquoted"',
        'test "phase 8 help fallback-only packet suppresses the empty main heading"',
        'try main_cmds.add("");',
        'try std.testing.expect(main_cmds.contains(""));',
        "const narrow_layout = help.computePrettyLayout(3, 8, 9);",
        "const empty_layout = help.computePrettyLayout(0, 8, 41);",
        "const phase8_help_slice = phase8_help_options.phase8_help_slice;",
    ),
    HELP_SOURCE: (
        'pub const default_command_prefix = "perf-";',
        "pub fn trimCommandPrefix(",
        "pub fn computePrettyLayout(",
        "pub fn renderPrettyStringList(",
        "pub fn renderCommandSections(",
        "pub fn uniqSorted(",
        "pub fn excludeSorted(",
        "pub fn longest(",
        "pub fn contains(",
        'test "computePrettyLayout falls back to the default width and one-column floor" {',
        'test "renderPrettyStringList falls back to the default width when terminal columns are unavailable" {',
        'test "renderCommandSections treats an empty exec path like a missing one" {',
        'test "renderCommandSections returns an empty packet when both command groups are empty" {',
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
        'expectEqualStrings("startup_64", symbols.items[0].name)',
        'test "phase 8 kallsyms wrappers preserve the parked callback contract"',
    ),
    KALLSYMS_SOURCE: (
        "pub const KSYM_NAME_LEN: usize = 512;",
        "pub fn parseLine(",
        "pub fn kallsymsParseFile(",
        "pub fn forEachParsedPath(",
        'test "weak object symbol classes keep the current C helper classification" {',
        'test "parseLine truncates oversized names without keeping a parser-local error surface" {',
        'test "reader, path, and callback wrappers normalize carriage returns before newline" {',
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
    print(f"PHASE8_HELP_KALLSYMS_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in FILE_MARKERS.values())}")
    return 0


def _passing_fixture(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        _write(root / relative_path, "\n".join(FILE_MARKERS.get(relative_path, (relative_path.as_posix(),))) + "\n")


def run_self_test() -> int:
    case_count = 1
    with tempfile.TemporaryDirectory(prefix="phase8-help-kallsyms-packet-selftest-") as tmp:
        root = Path(tmp)
        _passing_fixture(root)

        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers:
            raise AssertionError("expected passing fixture to validate")

        for relative_path, markers in FILE_MARKERS.items():
            path = root / relative_path
            original = _read(path)
            for marker in markers:
                mutated = original.replace(marker, "", 1)
                if mutated == original:
                    raise AssertionError(f"expected marker in fixture: {relative_path}:{marker}")
                path.write_text(mutated, encoding="utf-8")
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
