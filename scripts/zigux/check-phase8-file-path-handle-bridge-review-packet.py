#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path

VALIDATOR = Path("scripts/zigux/validate-phase8.py")
MAKEFILE = Path("zigux/Makefile")
TESTS_README = Path("zigux/tests/README.md")
BRIDGE_TEST = Path("zigux/tests/phase8_file_path_handle_bridge.zig")

REQUIRED_FILES = (
    VALIDATOR,
    MAKEFILE,
    TESTS_README,
    BRIDGE_TEST,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    VALIDATOR: (
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    ),
    MAKEFILE: (
        "phase8-file-path-handle-bridge-test:",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
    ),
    TESTS_README: (
        "current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`zigux/tests/phase8_build.zig`",
    ),
    BRIDGE_TEST: (
        "phase 8 file-path handle bridge helper stays wired into its focused Phase 8 build shard",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge_only_build.zig",
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
        print("PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET=fail")
        if result.missing_files:
            print("PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_MISSING_MARKERS_END")
        return 1

    print("PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET=pass")
    print(f"PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_MARKERS.values())}"
    )
    return 0


def _passing_fixture(root: Path) -> None:
    for relative_path, markers in FILE_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase8-file-path-handle-bridge-review-packet-") as tmp:
        root = Path(tmp)
        _passing_fixture(root)

        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers:
            raise AssertionError("expected passing fixture to validate")

        tests_readme = root / TESTS_README
        original_tests_readme = _read(tests_readme)
        tests_readme.write_text(
            original_tests_readme.replace(
                "`make -C zigux phase8-file-path-handle-bridge-test`", "", 1
            ),
            encoding="utf-8",
        )
        missing_tests_readme_marker = validate_root(root)
        expected_tests_readme_marker = (
            "zigux/tests/README.md:`make -C zigux phase8-file-path-handle-bridge-test`"
        )
        if expected_tests_readme_marker not in missing_tests_readme_marker.missing_markers:
            raise AssertionError("expected missing tests README route marker to be reported")
        tests_readme.write_text(original_tests_readme, encoding="utf-8")

        makefile = root / MAKEFILE
        original_makefile = _read(makefile)
        makefile.write_text(
            original_makefile.replace("phase8-file-path-handle-bridge-test:\n", "", 1),
            encoding="utf-8",
        )
        missing_makefile_marker = validate_root(root)
        expected_makefile_marker = "zigux/Makefile:phase8-file-path-handle-bridge-test:"
        if expected_makefile_marker not in missing_makefile_marker.missing_markers:
            raise AssertionError("expected missing make route marker to be reported")
        makefile.write_text(original_makefile, encoding="utf-8")

        validator = root / VALIDATOR
        original_validator = _read(validator)
        validator.write_text(
            original_validator.replace(
                "zigux/tests/phase8_file_path_handle_bridge_only_build.zig", "", 1
            ),
            encoding="utf-8",
        )
        missing_validator_marker = validate_root(root)
        expected_validator_marker = (
            "scripts/zigux/validate-phase8.py:"
            "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
        )
        if expected_validator_marker not in missing_validator_marker.missing_markers:
            raise AssertionError("expected missing validator bridge build marker to be reported")
        validator.write_text(original_validator, encoding="utf-8")

        bridge_test = root / BRIDGE_TEST
        original_bridge_test = _read(bridge_test)
        bridge_test.write_text(
            original_bridge_test.replace("phase8_file_path_handle_bridge_only_build.zig", "", 1),
            encoding="utf-8",
        )
        missing_bridge_test_marker = validate_root(root)
        expected_bridge_test_marker = (
            "zigux/tests/phase8_file_path_handle_bridge.zig:"
            "phase8_file_path_handle_bridge_only_build.zig"
        )
        if expected_bridge_test_marker not in missing_bridge_test_marker.missing_markers:
            raise AssertionError("expected missing bridge test build marker to be reported")
        bridge_test.write_text(original_bridge_test, encoding="utf-8")

        validator.unlink()
        missing_validator_file = validate_root(root)
        if VALIDATOR.as_posix() not in missing_validator_file.missing_files:
            raise AssertionError("expected missing validator file to be reported")
        _write(validator, "\n".join(FILE_MARKERS[VALIDATOR]) + "\n")

    print("PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET_SELF_TEST=pass")
    print("PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET_SELF_TEST_CASE_COUNT=5")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return emit_result(validate_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
