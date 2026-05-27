#!/usr/bin/env python3
"""Guard the current Phase 4 perf wrapper self-test gap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

MAKEFILE = Path("zigux/Makefile")
VALIDATOR = Path("scripts/zigux/validate-phase4.py")
MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")

PERF_THRESHOLD_SELFTEST = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-threshold-matrix.py --self-test"
)
PERF_THRESHOLD_LIVE = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-threshold-matrix.py"
)
PERF_BASELINE_SELFTEST = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-baseline-packet.py --self-test"
)
PERF_BASELINE_LIVE = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-baseline-packet.py"
)

VALIDATOR_MARKERS = (
    'CheckSpec("phase4-perf-baseline-packet-self-test", ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py", "--self-test"))',
    'CheckSpec("phase4-perf-baseline-packet", ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py"))',
    'CheckSpec("phase4-perf-threshold-matrix-self-test", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py", "--self-test"))',
    'CheckSpec("phase4-perf-threshold-matrix", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py"))',
)

MATRIX_MARKERS = (
    "local-only benchmark commands and acceptable limits are approved today",
    "shared CI perf promotion pending",
    "current replay path: `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`",
)

EXPECTED_SELF_TEST_CASE_COUNT = 7


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def target_body(makefile_text: str, target: str) -> list[str]:
    lines = makefile_text.splitlines()
    body: list[str] = []
    inside_target = False
    target_prefix = f"{target}:"
    for line in lines:
        if inside_target:
            if line.startswith("\t"):
                body.append(line)
                continue
            break
        if line.startswith(target_prefix):
            inside_target = True
    if not inside_target:
        raise SystemExit(f"missing target:{target}")
    return body


def require_marker(text: str, marker: str, issues: list[str], label: str) -> None:
    if marker not in text:
        issues.append(f"{label}:{marker}")


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    makefile_path = root / MAKEFILE
    validator_path = root / VALIDATOR
    matrix_path = root / MATRIX
    for path in (makefile_path, validator_path, matrix_path):
        if not path.is_file():
            issues.append(f"file:{path.relative_to(root).as_posix()}")
    if issues:
        return issues

    phase4_validate_body = target_body(read_text(makefile_path), "phase4-validate")
    if PERF_THRESHOLD_LIVE not in phase4_validate_body:
        issues.append(f"makefile_missing_live:{PERF_THRESHOLD_LIVE}")
    if PERF_BASELINE_LIVE not in phase4_validate_body:
        issues.append(f"makefile_missing_live:{PERF_BASELINE_LIVE}")
    if PERF_THRESHOLD_SELFTEST in phase4_validate_body:
        issues.append(f"makefile_gap_closed_unexpectedly:{PERF_THRESHOLD_SELFTEST}")
    if PERF_BASELINE_SELFTEST in phase4_validate_body:
        issues.append(f"makefile_gap_closed_unexpectedly:{PERF_BASELINE_SELFTEST}")

    validator_text = read_text(validator_path)
    for marker in VALIDATOR_MARKERS:
        require_marker(validator_text, marker, issues, "validator_marker_missing")

    matrix_text = read_text(matrix_path)
    for marker in MATRIX_MARKERS:
        require_marker(matrix_text, marker, issues, "matrix_marker_missing")

    return issues


def build_fixture_tree(root: Path) -> None:
    write_text(
        root / MAKEFILE,
        "\n".join(
            [
                "phase4-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-threshold-matrix.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-baseline-packet.py",
                "",
            ]
        ),
    )
    write_text(
        root / VALIDATOR,
        "\n".join(VALIDATOR_MARKERS) + "\n",
    )
    write_text(
        root / MATRIX,
        "\n".join(MATRIX_MARKERS) + "\n",
    )


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(issue.startswith(expected_prefix) for issue in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-perf-wrapper-gap-") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        cases = 1

        build_fixture_tree(root)
        write_text(root / MAKEFILE, replace_once(read_text(root / MAKEFILE), PERF_THRESHOLD_LIVE + "\n", ""))
        if not expect_failure(root, "makefile_missing_live:"):
            print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=fail")
            print("missing threshold live route did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(root / MAKEFILE, replace_once(read_text(root / MAKEFILE), PERF_BASELINE_LIVE + "\n", ""))
        if not expect_failure(root, "makefile_missing_live:"):
            print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=fail")
            print("missing baseline live route did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(root / MAKEFILE, read_text(root / MAKEFILE).replace(PERF_THRESHOLD_LIVE, PERF_THRESHOLD_SELFTEST + "\n" + PERF_THRESHOLD_LIVE, 1))
        if not expect_failure(root, "makefile_gap_closed_unexpectedly:"):
            print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=fail")
            print("unexpected threshold self-test closure did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(root / MAKEFILE, read_text(root / MAKEFILE).replace(PERF_BASELINE_LIVE, PERF_BASELINE_SELFTEST + "\n" + PERF_BASELINE_LIVE, 1))
        if not expect_failure(root, "makefile_gap_closed_unexpectedly:"):
            print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=fail")
            print("unexpected baseline self-test closure did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(root / VALIDATOR, replace_once(read_text(root / VALIDATOR), VALIDATOR_MARKERS[0] + "\n", ""))
        if not expect_failure(root, "validator_marker_missing:"):
            print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=fail")
            print("validator marker drift did not fail closed")
            return 1
        cases += 1

        build_fixture_tree(root)
        write_text(root / MATRIX, replace_once(read_text(root / MATRIX), MATRIX_MARKERS[0] + "\n", ""))
        if not expect_failure(root, "matrix_marker_missing:"):
            print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=fail")
            print("matrix marker drift did not fail closed")
            return 1
        cases += 1

        if cases != EXPECTED_SELF_TEST_CASE_COUNT:
            print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASE_COUNT} self-test cases, saw {cases}")
            return 1

    print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST=pass")
    print(f"PHASE4_PERF_WRAPPER_SELFTEST_GAP_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_root(Path(args.root).resolve())
    if issues:
        print("PHASE4_PERF_WRAPPER_SELFTEST_GAP=fail")
        for issue in issues:
            print(issue)
        return 1
    print("PHASE4_PERF_WRAPPER_SELFTEST_GAP=pass")
    print("PHASE4_PERF_WRAPPER_SELFTEST_GAP_STATUS=current_gap_explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())