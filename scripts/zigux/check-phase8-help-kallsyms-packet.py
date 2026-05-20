#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
KALLSYMS_SLICE = Path("Documentation/zigux/phase8-kallsyms-slice.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
VALIDATOR = Path("scripts/zigux/validate-phase8.py")
MAKEFILE = Path("zigux/Makefile")
TESTS_README = Path("zigux/tests/README.md")
HELP_KALLSYMS_BUILD = Path("zigux/tests/phase8_help_kallsyms_only_build.zig")
HELP_BUILD = Path("zigux/tests/phase8_help_only_build.zig")
KALLSYMS_BUILD = Path("zigux/tests/phase8_kallsyms_only_build.zig")
HELP_SOURCE = Path("tools/lib/subcmd/help.zig")
KALLSYMS_SOURCE = Path("tools/lib/symbol/kallsyms.zig")

REQUIRED_FILES = (
    KALLSYMS_SLICE,
    CHECKLIST,
    VALIDATOR,
    MAKEFILE,
    TESTS_README,
    HELP_KALLSYMS_BUILD,
    HELP_BUILD,
    KALLSYMS_BUILD,
    HELP_SOURCE,
    KALLSYMS_SOURCE,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    KALLSYMS_SLICE: (
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "shared validation overlap only",
    ),
    MAKEFILE: (
        "phase8-help-kallsyms-test:",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test",
    ),
    HELP_KALLSYMS_BUILD: (
        "phase8_help.zig",
        "phase8_kallsyms.zig",
        "Run the phase 8 help and kallsyms tests.",
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
    missing_files = [
        path.as_posix()
        for path in REQUIRED_FILES
        if not (root / path).exists()
    ]
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
    print(
        "PHASE8_HELP_KALLSYMS_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_MARKERS.values())}"
    )
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

        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers:
            raise AssertionError("expected passing fixture to validate")

        build_path = root / HELP_KALLSYMS_BUILD
        original_build = _read(build_path)
        build_path.write_text(
            original_build.replace("phase8_kallsyms.zig", "", 1),
            encoding="utf-8",
        )
        missing_build_marker = validate_root(root)
        expected_build_marker = (
            "zigux/tests/phase8_help_kallsyms_only_build.zig:phase8_kallsyms.zig"
        )
        if expected_build_marker not in missing_build_marker.missing_markers:
            raise AssertionError("expected missing shared build marker to be reported")
        build_path.write_text(original_build, encoding="utf-8")

        makefile = root / MAKEFILE
        original_makefile = _read(makefile)
        makefile.write_text(
            original_makefile.replace("phase8-help-kallsyms-test:\n", "", 1),
            encoding="utf-8",
        )
        missing_route = validate_root(root)
        expected_route_marker = "zigux/Makefile:phase8-help-kallsyms-test:"
        if expected_route_marker not in missing_route.missing_markers:
            raise AssertionError("expected missing make route marker to be reported")
        makefile.write_text(original_makefile, encoding="utf-8")

        kallsyms_slice = root / KALLSYMS_SLICE
        original_slice = _read(kallsyms_slice)
        kallsyms_slice.write_text(
            original_slice.replace("shared validation overlap only", "", 1),
            encoding="utf-8",
        )
        missing_slice_marker = validate_root(root)
        expected_slice_marker = (
            "Documentation/zigux/phase8-kallsyms-slice.md:shared validation overlap only"
        )
        if expected_slice_marker not in missing_slice_marker.missing_markers:
            raise AssertionError("expected missing kallsyms slice marker to be reported")
        kallsyms_slice.write_text(original_slice, encoding="utf-8")

        missing_source = root / KALLSYMS_SOURCE
        missing_source.unlink()
        missing_file = validate_root(root)
        if "tools/lib/symbol/kallsyms.zig" not in missing_file.missing_files:
            raise AssertionError("expected missing kallsyms helper file to be reported")
        _write(missing_source, "tools/lib/symbol/kallsyms.zig\n")

    print("PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST=pass")
    print("PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST_CASE_COUNT=4")
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