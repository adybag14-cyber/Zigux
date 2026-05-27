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
MAKEFILE = Path("zigux/Makefile")
HELP_TEST = Path("zigux/tests/phase8_help.zig")
KALLSYMS_TEST = Path("zigux/tests/phase8_kallsyms.zig")
HELP_SOURCE = Path("tools/lib/subcmd/help.zig")
KALLSYMS_SOURCE = Path("tools/lib/symbol/kallsyms.zig")

REQUIRED_FILES = (
    HELP_SLICE,
    KALLSYMS_SLICE,
    MAKEFILE,
    HELP_TEST,
    KALLSYMS_TEST,
    HELP_SOURCE,
    KALLSYMS_SOURCE,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    HELP_SLICE: (
        "`PHASE8_SLICE=help-output-stable-packet`",
        "stable output-local packet explicit through `trimCommandPrefix()`, `computePrettyLayout()`, `renderPrettyStringList()`, and `renderCommandSections()`",
        "stable pretty-printer and heading contract reviewable",
        "the mixed `help+kallsyms` build shard is still shared validation overlap only",
    ),
    KALLSYMS_SLICE: (
        "`PHASE8_SLICE=kallsyms-parse-wrapper-parked`",
        "oversized symbol names now truncate to `KSYM_NAME_LEN`",
        "weak-object `V` and `v` classes still follow the current C header contract",
        "the dedicated replay keeps the chunked-reader `startup_64\\r` witness visible",
    ),
    MAKEFILE: (
        "scripts/zigux/check-phase8-help-symbol-output-stability.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-help-symbol-output-stability.py",
    ),
    HELP_TEST: (
        'test "phase 8 help pretty printer keeps the current row-major stable output"',
        'test "phase 8 help fallback-only packet suppresses the empty main heading"',
        'test "phase 8 help fully empty section rendering stays empty"',
        '" annotate      diff\\n"',
    ),
    KALLSYMS_TEST: (
        'test "phase 8 kallsyms direct parser truncates oversized names"',
        'test "phase 8 kallsyms chunked parser also truncates oversized names"',
        'expectEqualStrings("startup_64\\\\r", symbols.items[0].name)',
        'test "phase 8 kallsyms segmented reader bubbles callback failures unchanged"',
    ),
    HELP_SOURCE: (
        "pub fn computePrettyLayout(",
        "pub fn renderPrettyStringList(",
        "pub fn renderCommandSections(",
        'test "renderCommandSections returns an empty packet when both command groups are empty" {',
    ),
    KALLSYMS_SOURCE: (
        "pub const KSYM_NAME_LEN: usize = 512;",
        "pub fn parseLine(",
        "pub fn forEachParsedChunked(",
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
        print("PHASE8_HELP_SYMBOL_OUTPUT_STABILITY=fail")
        if result.missing_files:
            print("PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_MISSING_MARKERS_END")
        return 1

    print("PHASE8_HELP_SYMBOL_OUTPUT_STABILITY=pass")
    print(f"PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_MARKERS.values())}"
    )
    return 0


def _passing_fixture(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        _write(root / relative_path, "\n".join(FILE_MARKERS[relative_path]) + "\n")


def run_self_test() -> int:
    case_count = 1
    with tempfile.TemporaryDirectory(prefix="phase8-help-symbol-output-stability-") as tmp:
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

    print("PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_SELF_TEST=pass")
    print(f"PHASE8_HELP_SYMBOL_OUTPUT_STABILITY_SELF_TEST_CASE_COUNT={case_count}")
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
