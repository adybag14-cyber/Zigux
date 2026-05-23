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
SCRIPTS_README = Path("scripts/zigux/README.md")
PHASE8_VALIDATOR = Path("scripts/zigux/validate-phase8.py")
HELP_KALLSYMS_PACKET_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-packet.py")
LIBBPF_SHARD_ROUTES_CHECKER = Path("scripts/zigux/check-phase8-libbpf-shard-routes.py")
TESTS_README = Path("zigux/tests/README.md")

REQUIRED_FILES = (
    SCRIPTS_README,
    PHASE8_VALIDATOR,
    HELP_KALLSYMS_PACKET_CHECKER,
    LIBBPF_SHARD_ROUTES_CHECKER,
    TESTS_README,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    SCRIPTS_README: (
        "## Phase 8",
        "`tools/lib/subcmd/help.zig`",
        "`tools/lib/symbol/kallsyms.zig`",
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "current public-tree rereads plus the shared packet guards `scripts/zigux/check-phase8-help-kallsyms-packet.py` and `scripts/zigux/check-phase8-libbpf-shard-routes.py` rematerialize those broader help, kallsyms, and libbpf-segment companions on `master`",
    ),
    PHASE8_VALIDATOR: (
        'HELP_KALLSYMS_PACKET_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-packet.py")',
        'LIBBPF_SHARD_ROUTES_CHECKER = Path("scripts/zigux/check-phase8-libbpf-shard-routes.py")',
        "HELP_KALLSYMS_PACKET_CHECKER,",
        "LIBBPF_SHARD_ROUTES_CHECKER,",
        'Path("scripts/zigux/README.md"): (',
    ),
    HELP_KALLSYMS_PACKET_CHECKER: (
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py` and `scripts/zigux/check-phase8-libbpf-shard-routes.py` rematerialize those broader help, kallsyms, and libbpf-segment companions on `master`",
        "`tools/lib/subcmd/help.zig`",
        "`tools/lib/symbol/kallsyms.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
    ),
    LIBBPF_SHARD_ROUTES_CHECKER: (
        'VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"',
        'LIBBPF_SEGMENTS_TEST_PATH = "zigux/tests/phase8_libbpf_segments.zig"',
        'LIBBPF_SEGMENTS_BUILD_PATH = "zigux/tests/phase8_libbpf_segments_only_build.zig"',
        'VERIFY_PATH = "tools/lib/bpf/zigux_segments/verify.zig"',
    ),
    TESTS_README: (
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
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
        print("PHASE8_SCRIPTS_README_BROADER_PACKET=fail")
        if result.missing_files:
            print("PHASE8_SCRIPTS_README_BROADER_PACKET_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_SCRIPTS_README_BROADER_PACKET_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_SCRIPTS_README_BROADER_PACKET_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_SCRIPTS_README_BROADER_PACKET_MISSING_MARKERS_END")
        return 1

    print("PHASE8_SCRIPTS_README_BROADER_PACKET=pass")
    print(f"PHASE8_SCRIPTS_README_BROADER_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_SCRIPTS_README_BROADER_PACKET_REQUIRED_MARKER_COUNT="
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
    case_count = 1
    with tempfile.TemporaryDirectory(prefix="phase8-scripts-readme-broader-packet-") as tmp:
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

    print("PHASE8_SCRIPTS_README_BROADER_PACKET_SELF_TEST=pass")
    print(f"PHASE8_SCRIPTS_README_BROADER_PACKET_SELF_TEST_CASE_COUNT={case_count}")
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
