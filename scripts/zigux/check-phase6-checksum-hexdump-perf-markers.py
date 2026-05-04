#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
SELF_TEST_CASE_COUNT = 13

CHECKSUM_PERF_PATH = "zigux/tests/phase6_checksum_perf.zig"
HEXDUMP_PERF_PATH = "zigux/tests/phase6_hexdump_perf.zig"
PERF_SURVEY_PATH = "Documentation/zigux/phase6-perf-gate-survey.md"
CATALOG_PATH = "Documentation/zigux/phase6-helper-parity-catalog.md"
MAKEFILE_PATH = "zigux/Makefile"
MANIFEST_PATH = "zigux/tests/phase6_helper_parity_manifest.json"

CHECKSUM_PERF_MARKERS = [
    '"phase6-checksum-perf {s} len={} reps={} helper_ns_per_call={} helper_ns_per_byte={d:.2} reference_ns_per_call={} reference_ns_per_byte={d:.2} slowdown_pct={} folded=0x{x:0>4} sink=0x{x:0>8}\\n"',
    "const expected_partial = referencePartial(payload, case.seed);",
    "try std.testing.expectEqual(expected_partial, checksum.partial(payload, case.seed));",
    "const slowdown_pct = median3(",
]

HEXDUMP_PERF_MARKERS = [
    '"phase6-hexdump-perf {s} len={} rowsize={} groupsize={} ascii={} reps={} helper_ns_per_call={} helper_ns_per_byte={d:.2} reference_ns_per_call={} reference_ns_per_byte={d:.2} slowdown_pct={} required={} sink=0x{x:0>8}\\n"',
    "const expected = fixtures.prepareExpectedLine(expected_buf[0..], case.len, case.rowsize, case.groupsize, case.ascii);",
    "try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(actual[0..], 0));",
    "const slowdown_pct = median3(",
]

PERF_SURVEY_MARKERS = [
    "`python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py --self-test` and `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py` now keep the shipped checksum and hexdump perf-marker packet fail-closed around the per-call, per-byte, slowdown, folded-checksum, required-length, and reference-path reporting markers before broader Phase 6 replay claims stay green",
]

CATALOG_MARKERS = [
    "`python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py --self-test` and `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py` keep the shipped checksum and hexdump perf-marker packet fail-closed around the per-call, per-byte, slowdown, folded-checksum, required-length, and reference-path reporting markers before broader Phase 6 replay claims stay green.",
]

MAKEFILE_MARKERS = [
    "$(PYTHON) scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py --self-test",
    "$(PYTHON) scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
]

MANIFEST_MARKERS = [
    "python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py --self-test",
    "python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
]


def text(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def missing_markers(content: str, markers: list[str]) -> list[str]:
    return [marker for marker in markers if marker not in content]


def normalized_lines(content: str) -> list[str]:
    return [line.strip() for line in content.splitlines()]


def missing_exact_lines(content: str, markers: list[str]) -> list[str]:
    lines = normalized_lines(content)
    missing: list[str] = []
    for marker in markers:
        if sum(1 for line in lines if line == marker) != 1:
            missing.append(marker)
    return missing


def drop_exact_line(content: str, marker: str) -> str:
    kept: list[str] = []
    removed = False
    for line in content.splitlines():
        if not removed and line.strip() == marker:
            removed = True
            continue
        kept.append(line)
    return "\n".join(kept) + ("\n" if kept else "")


def validate(root: Path) -> dict[str, object]:
    missing_files: list[str] = []
    missing: list[str] = []

    checksum_path = root / CHECKSUM_PERF_PATH
    hexdump_path = root / HEXDUMP_PERF_PATH
    perf_survey_path = root / PERF_SURVEY_PATH
    catalog_path = root / CATALOG_PATH
    makefile_path = root / MAKEFILE_PATH
    manifest_path = root / MANIFEST_PATH

    if not checksum_path.exists():
        missing_files.append(CHECKSUM_PERF_PATH)
    else:
        for marker in missing_markers(text(root, CHECKSUM_PERF_PATH), CHECKSUM_PERF_MARKERS):
            missing.append(f"checksum_perf:missing:{marker}")

    if not hexdump_path.exists():
        missing_files.append(HEXDUMP_PERF_PATH)
    else:
        for marker in missing_markers(text(root, HEXDUMP_PERF_PATH), HEXDUMP_PERF_MARKERS):
            missing.append(f"hexdump_perf:missing:{marker}")

    if not perf_survey_path.exists():
        missing_files.append(PERF_SURVEY_PATH)
    else:
        for marker in missing_markers(text(root, PERF_SURVEY_PATH), PERF_SURVEY_MARKERS):
            missing.append(f"perf_survey:missing:{marker}")

    if not catalog_path.exists():
        missing_files.append(CATALOG_PATH)
    else:
        for marker in missing_markers(text(root, CATALOG_PATH), CATALOG_MARKERS):
            missing.append(f"catalog:missing:{marker}")

    if not makefile_path.exists():
        missing_files.append(MAKEFILE_PATH)
    else:
        for marker in missing_exact_lines(text(root, MAKEFILE_PATH), MAKEFILE_MARKERS):
            missing.append(f"makefile:missing:{marker}")

    if not manifest_path.exists():
        missing_files.append(MANIFEST_PATH)
    else:
        for marker in missing_exact_lines(text(root, MANIFEST_PATH), MANIFEST_MARKERS):
            missing.append(f"manifest:missing:{marker}")

    return {
        "ok": not missing_files and not missing,
        "missing_files": missing_files,
        "missing": missing,
    }


def report(result: dict[str, object]) -> int:
    if result["missing_files"]:
        print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=fail")
        print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_MISSING_FILES_START")
        for path in result["missing_files"]:
            print(path)
        print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_MISSING_FILES_END")
        return 1
    if result["missing"]:
        print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=fail")
        print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_MISSING_START")
        for item in result["missing"]:
            print(item)
        print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_MISSING_END")
        return 1

    print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=pass")
    return 0


def write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_self_test_tree(root: Path) -> None:
    write(root, CHECKSUM_PERF_PATH, "\n".join(CHECKSUM_PERF_MARKERS) + "\n")
    write(root, HEXDUMP_PERF_PATH, "\n".join(HEXDUMP_PERF_MARKERS) + "\n")
    write(root, PERF_SURVEY_PATH, "\n".join(PERF_SURVEY_MARKERS) + "\n")
    write(root, CATALOG_PATH, "\n".join(CATALOG_MARKERS) + "\n")
    write(root, MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")
    write(root, MANIFEST_PATH, "\n".join(MANIFEST_MARKERS) + "\n")


def expect_missing_file(result: dict[str, object], path: str) -> None:
    if path not in result["missing_files"]:
        raise AssertionError(f"missing file expectation {path}")


def expect_contains(result: dict[str, object], item: str) -> None:
    if item not in result["missing"]:
        raise AssertionError(f"missing expectation {item}")


def run_self_test() -> int:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            count = 0

            build_self_test_tree(root)
            if not validate(root)["ok"]:
                raise AssertionError("baseline tree should pass")
            count += 1

            build_self_test_tree(root)
            (root / CHECKSUM_PERF_PATH).unlink()
            expect_missing_file(validate(root), CHECKSUM_PERF_PATH)
            count += 1

            build_self_test_tree(root)
            (root / HEXDUMP_PERF_PATH).unlink()
            expect_missing_file(validate(root), HEXDUMP_PERF_PATH)
            count += 1

            build_self_test_tree(root)
            (root / PERF_SURVEY_PATH).unlink()
            expect_missing_file(validate(root), PERF_SURVEY_PATH)
            count += 1

            build_self_test_tree(root)
            (root / CATALOG_PATH).unlink()
            expect_missing_file(validate(root), CATALOG_PATH)
            count += 1

            build_self_test_tree(root)
            checksum_path = root / CHECKSUM_PERF_PATH
            checksum_path.write_text(
                checksum_path.read_text(encoding="utf-8").replace(CHECKSUM_PERF_MARKERS[1], "", 1),
                encoding="utf-8",
            )
            expect_contains(validate(root), f"checksum_perf:missing:{CHECKSUM_PERF_MARKERS[1]}")
            count += 1

            build_self_test_tree(root)
            hexdump_path = root / HEXDUMP_PERF_PATH
            hexdump_path.write_text(
                hexdump_path.read_text(encoding="utf-8").replace(HEXDUMP_PERF_MARKERS[1], "", 1),
                encoding="utf-8",
            )
            expect_contains(validate(root), f"hexdump_perf:missing:{HEXDUMP_PERF_MARKERS[1]}")
            count += 1

            build_self_test_tree(root)
            survey_path = root / PERF_SURVEY_PATH
            survey_path.write_text(
                survey_path.read_text(encoding="utf-8").replace(PERF_SURVEY_MARKERS[0], "", 1),
                encoding="utf-8",
            )
            expect_contains(validate(root), f"perf_survey:missing:{PERF_SURVEY_MARKERS[0]}")
            count += 1

            build_self_test_tree(root)
            catalog_path = root / CATALOG_PATH
            catalog_path.write_text(
                catalog_path.read_text(encoding="utf-8").replace(CATALOG_MARKERS[0], "", 1),
                encoding="utf-8",
            )
            expect_contains(validate(root), f"catalog:missing:{CATALOG_MARKERS[0]}")
            count += 1

            build_self_test_tree(root)
            makefile_path = root / MAKEFILE_PATH
            makefile_path.write_text(
                drop_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[0]),
                encoding="utf-8",
            )
            expect_contains(validate(root), f"makefile:missing:{MAKEFILE_MARKERS[0]}")
            count += 1

            build_self_test_tree(root)
            makefile_path = root / MAKEFILE_PATH
            makefile_path.write_text(
                drop_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[1]),
                encoding="utf-8",
            )
            expect_contains(validate(root), f"makefile:missing:{MAKEFILE_MARKERS[1]}")
            count += 1

            build_self_test_tree(root)
            manifest_path = root / MANIFEST_PATH
            manifest_path.write_text(
                drop_exact_line(manifest_path.read_text(encoding="utf-8"), MANIFEST_MARKERS[0]),
                encoding="utf-8",
            )
            expect_contains(validate(root), f"manifest:missing:{MANIFEST_MARKERS[0]}")
            count += 1

            build_self_test_tree(root)
            manifest_path = root / MANIFEST_PATH
            manifest_path.write_text(
                drop_exact_line(manifest_path.read_text(encoding="utf-8"), MANIFEST_MARKERS[1]),
                encoding="utf-8",
            )
            expect_contains(validate(root), f"manifest:missing:{MANIFEST_MARKERS[1]}")
            count += 1

            if count != SELF_TEST_CASE_COUNT:
                raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} self-test cases, got {count}")
    except AssertionError as exc:
        print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST=fail")
        print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST_REASON={exc}")
        return 1

    print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST=pass")
    print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that the live Phase 6 checksum and hexdump perf harnesses stay aligned with their published review routes.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()
    return report(validate(ROOT))


if __name__ == "__main__":
    sys.exit(main())