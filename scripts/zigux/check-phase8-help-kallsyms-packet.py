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
TOOLING_LANE_SEQUENCE = Path("Documentation/zigux/phase8-tooling-lane-sequencing.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
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
    TOOLING_LANE_SEQUENCE,
    CHECKLIST,
    SCRIPTS_README,
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
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
        "shared validation overlap only",
        "oversized symbol names now truncate to `KSYM_NAME_LEN`",
        "weak-object `V` and `v` classes still follow the current C header contract",
        "the public raw fallback returns usable `tools/lib/symbol/kallsyms.zig` helper content",
        "the current raw-backed CRLF contract, where chunked reader and wrapper paths still preserve the trailing carriage return in symbol names",
    ),
    TOOLING_LANE_SEQUENCE: (
        "`zigux/tests/phase8_help_kallsyms_only_build.zig` and `make -C zigux phase8-help-kallsyms-test` are still shared smoke coverage only",
        "help-local output or command-source drift stays in the help lane, while parser, truncation, or callback-wrapper drift stays in the symbol lane until `tools/lib/symbol/kallsyms.zig` is readable again.",
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
        "`make -C zigux phase8-help-kallsyms-test`",
    ),
    HELP_KALLSYMS_BUILD: (
        "phase8_help.zig",
        "phase8_kallsyms.zig",
        "Run focused Phase 8 help and kallsyms tests",
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
    ),
    KALLSYMS_BUILD: (
        "../../tools/lib/symbol/kallsyms.zig",
        "phase8-kallsyms-only-tests",
        "Run the focused Phase 8 kallsyms-only tests.",
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
