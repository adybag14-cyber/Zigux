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
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "parked help-and-kallsyms packet reviewable",
    ),
    KALLSYMS_SLICE: (
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "shared validation overlap only",
        "oversized symbol names now truncate to `KSYM_NAME_LEN`",
        "weak-object `V` and `v` classes still follow the current C header contract",
    ),
    CHECKLIST: (
        "if the change touches the parked Phase 8 `help` packet",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "if the change touches the parked Phase 8 `kallsyms` parser packet",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-kallsyms-test`",
    ),
    VALIDATOR: (
        'HELP_KALLSYMS_PACKET_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-packet.py")',
        "HELP_KALLSYMS_PACKET_CHECKER,",
    ),
    MAKEFILE: (
        "phase8-help-kallsyms-test:",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test",
    ),
    TESTS_README: (
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
    ),
    HELP_KALLSYMS_BUILD: (
        "phase8_help.zig",
        "phase8_kallsyms.zig",
        "Run the focused Phase 8 help and kallsyms shared tests.",
    ),
    HELP_TEST: (
        'test "phase 8 help slice note keeps helper-first output-stable tooling posture and non-goals explicit"',
        'test "phase 8 help slice covers command-list ownership, filtering, exclusion, terminal sizing, and layout planning"',
        'test "phase 8 help output emission keeps column-major pretty-printing pure and testable"',
        'test "phase 8 help section rendering keeps the stable main and PATH headings reviewable"',
    ),
    KALLSYMS_TEST: (
        'test "phase 8 kallsyms slice note keeps the C-aligned truncation contract explicit"',
        'test "phase 8 kallsyms keeps weak object classes on the current header-backed path"',
        'test "phase 8 kallsyms wrappers preserve the parked callback contract"',
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


def _passing_fixture(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path in FILE_MARKERS:
            _write(root / relative_path, "\n".join(FILE_MARKERS[relative_path]) + "\n")
        else:
            _write(root / relative_path, f"{relative_path.as_posix()}\n")


def run_self_test() -> int:
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

        help_slice = root / HELP_SLICE
        original_help_slice = _read(help_slice)
        help_slice.write_text(original_help_slice.replace("parked help-and-kallsyms packet reviewable", "", 1), encoding="utf-8")
        missing_help_slice_marker = validate_root(root)
        expected_help_slice_marker = "Documentation/zigux/phase8-help-slice.md:parked help-and-kallsyms packet reviewable"
        if expected_help_slice_marker not in missing_help_slice_marker.missing_markers:
            raise AssertionError("expected missing help slice marker to be reported")
        help_slice.write_text(original_help_slice, encoding="utf-8")

        checklist = root / CHECKLIST
        original_checklist = _read(checklist)
        checklist.write_text(original_checklist.replace("`make -C zigux phase8-help-test`", "", 1), encoding="utf-8")
        missing_checklist_help_route = validate_root(root)
        expected_checklist_help_route = "Documentation/zigux/review-checklist.md:`make -C zigux phase8-help-test`"
        if expected_checklist_help_route not in missing_checklist_help_route.missing_markers:
            raise AssertionError("expected missing checklist help route marker to be reported")
        checklist.write_text(original_checklist, encoding="utf-8")

        checklist.write_text(original_checklist.replace("`zigux/tests/phase8_kallsyms_only_build.zig`", "", 1), encoding="utf-8")
        missing_checklist_kallsyms_build = validate_root(root)
        expected_checklist_kallsyms_build = "Documentation/zigux/review-checklist.md:`zigux/tests/phase8_kallsyms_only_build.zig`"
        if expected_checklist_kallsyms_build not in missing_checklist_kallsyms_build.missing_markers:
            raise AssertionError("expected missing checklist kallsyms build marker to be reported")
        checklist.write_text(original_checklist, encoding="utf-8")

        validator = root / VALIDATOR
        original_validator = _read(validator)
        validator.write_text(original_validator.replace('HELP_KALLSYMS_PACKET_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-packet.py")', "", 1), encoding="utf-8")
        missing_validator_constant = validate_root(root)
        expected_validator_constant = 'scripts/zigux/validate-phase8.py:HELP_KALLSYMS_PACKET_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-packet.py")'
        if expected_validator_constant not in missing_validator_constant.missing_markers:
            raise AssertionError("expected missing validator checker constant to be reported")
        validator.write_text(original_validator, encoding="utf-8")

        tests_readme = root / TESTS_README
        original_tests_readme = _read(tests_readme)
        tests_readme.write_text(original_tests_readme.replace("`zigux/tests/phase8_help_kallsyms_only_build.zig`", "", 1), encoding="utf-8")
        missing_tests_readme_marker = validate_root(root)
        expected_tests_readme_marker = "zigux/tests/README.md:`zigux/tests/phase8_help_kallsyms_only_build.zig`"
        if expected_tests_readme_marker not in missing_tests_readme_marker.missing_markers:
            raise AssertionError("expected missing tests README marker to be reported")
        tests_readme.write_text(original_tests_readme, encoding="utf-8")

        help_test = root / HELP_TEST
        original_help_test = _read(help_test)
        help_test.write_text(original_help_test.replace('test "phase 8 help slice covers command-list ownership, filtering, exclusion, terminal sizing, and layout planning"', "", 1), encoding="utf-8")
        missing_help_test_marker = validate_root(root)
        expected_help_test_marker = 'zigux/tests/phase8_help.zig:test "phase 8 help slice covers command-list ownership, filtering, exclusion, terminal sizing, and layout planning"'
        if expected_help_test_marker not in missing_help_test_marker.missing_markers:
            raise AssertionError("expected missing help test marker to be reported")
        help_test.write_text(original_help_test, encoding="utf-8")

        help_test.write_text(original_help_test.replace('test "phase 8 help output emission keeps column-major pretty-printing pure and testable"', "", 1), encoding="utf-8")
        missing_help_output_marker = validate_root(root)
        expected_help_output_marker = 'zigux/tests/phase8_help.zig:test "phase 8 help output emission keeps column-major pretty-printing pure and testable"'
        if expected_help_output_marker not in missing_help_output_marker.missing_markers:
            raise AssertionError("expected missing help output marker to be reported")
        help_test.write_text(original_help_test, encoding="utf-8")

        help_test.write_text(original_help_test.replace('test "phase 8 help section rendering keeps the stable main and PATH headings reviewable"', "", 1), encoding="utf-8")
        missing_help_section_marker = validate_root(root)
        expected_help_section_marker = 'zigux/tests/phase8_help.zig:test "phase 8 help section rendering keeps the stable main and PATH headings reviewable"'
        if expected_help_section_marker not in missing_help_section_marker.missing_markers:
            raise AssertionError("expected missing help section marker to be reported")
        help_test.write_text(original_help_test, encoding="utf-8")

        kallsyms_test = root / KALLSYMS_TEST
        original_kallsyms_test = _read(kallsyms_test)
        kallsyms_test.write_text(original_kallsyms_test.replace('test "phase 8 kallsyms wrappers preserve the parked callback contract"', "", 1), encoding="utf-8")
        missing_kallsyms_test_marker = validate_root(root)
        expected_kallsyms_test_marker = 'zigux/tests/phase8_kallsyms.zig:test "phase 8 kallsyms wrappers preserve the parked callback contract"'
        if expected_kallsyms_test_marker not in missing_kallsyms_test_marker.missing_markers:
            raise AssertionError("expected missing kallsyms test marker to be reported")
        kallsyms_test.write_text(original_kallsyms_test, encoding="utf-8")

        build_path = root / HELP_KALLSYMS_BUILD
        original_build = _read(build_path)
        build_path.write_text(original_build.replace("phase8_kallsyms.zig", "", 1), encoding="utf-8")
        missing_build_marker = validate_root(root)
        expected_build_marker = "zigux/tests/phase8_help_kallsyms_only_build.zig:phase8_kallsyms.zig"
        if expected_build_marker not in missing_build_marker.missing_markers:
            raise AssertionError("expected missing shared build marker to be reported")
        build_path.write_text(original_build, encoding="utf-8")

        build_path.write_text(original_build.replace("Run the focused Phase 8 help and kallsyms shared tests.", "", 1), encoding="utf-8")
        missing_build_description = validate_root(root)
        expected_build_description = "zigux/tests/phase8_help_kallsyms_only_build.zig:Run the focused Phase 8 help and kallsyms shared tests."
        if expected_build_description not in missing_build_description.missing_markers:
            raise AssertionError("expected missing shared build description to be reported")
        build_path.write_text(original_build, encoding="utf-8")

        makefile = root / MAKEFILE
        original_makefile = _read(makefile)
        makefile.write_text(original_makefile.replace("phase8-help-kallsyms-test:\n", "", 1), encoding="utf-8")
        missing_route = validate_root(root)
        expected_route_marker = "zigux/Makefile:phase8-help-kallsyms-test:"
        if expected_route_marker not in missing_route.missing_markers:
            raise AssertionError("expected missing make route marker to be reported")
        makefile.write_text(original_makefile, encoding="utf-8")

        kallsyms_slice = root / KALLSYMS_SLICE
        original_slice = _read(kallsyms_slice)
        kallsyms_slice.write_text(original_slice.replace("shared validation overlap only", "", 1), encoding="utf-8")
        missing_slice_marker = validate_root(root)
        expected_slice_marker = "Documentation/zigux/phase8-kallsyms-slice.md:shared validation overlap only"
        if expected_slice_marker not in missing_slice_marker.missing_markers:
            raise AssertionError("expected missing kallsyms slice marker to be reported")
        kallsyms_slice.write_text(original_slice, encoding="utf-8")

        kallsyms_slice.write_text(original_slice.replace("oversized symbol names now truncate to `KSYM_NAME_LEN`", "", 1), encoding="utf-8")
        missing_truncation_marker = validate_root(root)
        expected_truncation_marker = "Documentation/zigux/phase8-kallsyms-slice.md:oversized symbol names now truncate to `KSYM_NAME_LEN`"
        if expected_truncation_marker not in missing_truncation_marker.missing_markers:
            raise AssertionError("expected missing kallsyms truncation marker to be reported")
        kallsyms_slice.write_text(original_slice, encoding="utf-8")

        missing_source = root / KALLSYMS_SOURCE
        missing_source.unlink()
        missing_file = validate_root(root)
        if "tools/lib/symbol/kallsyms.zig" not in missing_file.missing_files:
            raise AssertionError("expected missing kallsyms helper file to be reported")
        _write(missing_source, "tools/lib/symbol/kallsyms.zig\n")

    print("PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST=pass")
    print("PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST_CASE_COUNT=12")
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
