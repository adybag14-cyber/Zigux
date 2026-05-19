#!/usr/bin/env python3
"""Guard the Lane 16 bench checker's fail-closed failure packets."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"

REQUIRED_MARKERS = (
    "def emit_expectations_failure(",
    "def emit_validation_failure(kind: str, payload: object, expectations_path: Path) -> int:",
    "def emit_bench_command_failure(",
    "def emit_bench_command_missing(error: FileNotFoundError, expectations_path: Path) -> int:",
    "def capture_expectations_failure_output(",
    "def capture_validation_failure_output(",
    "def capture_bench_command_failure_output(",
    "def capture_bench_command_missing_output(",
    'print("PHASE1_BENCH_CHECK_REASON=bench_command_exit")',
    'print("PHASE1_BENCH_CHECK_REASON=bench_command_missing")',
    'assert missing_output == [',
    '"PHASE1_BENCH_CHECK_REASON=expectations_missing",',
    'assert malformed_output == [',
    '"PHASE1_BENCH_CHECK_REASON=expectations_json_error",',
    'assert invalid_status_output == [',
    '"PHASE1_BENCH_CHECK_REASON=expectations_status",',
    'assert status_drift_output == [',
    '"PHASE1_BENCH_CHECK_REASON=status",',
    'assert command_failure_output == [',
    '"PHASE1_BENCH_CHECK_REASON=bench_command_exit",',
    'assert command_missing_output == [',
    '"PHASE1_BENCH_CHECK_REASON=bench_command_missing",',
    'assert checksum_drift_output == [',
    '"PHASE1_BENCH_CHECK_REASON=exact_checksum_mismatch",',
    'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
)

FORBIDDEN_FRAGMENTS = (
    "missing_expectations_file",
    'print(f"EXPECTATIONS_PATH={payload}")',
)

FORBIDDEN_EXPECTATION_FAILURE_FRAGMENTS = (
    "EXPECTATIONS_PATH=",
)

FORBIDDEN_BENCH_FAILURE_BLOCK_FRAGMENTS = (
    "PHASE1_BENCH_CHECK=pass",
    "PHASE1_BENCH_EXPECTATION_COUNT=",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def checker_path(root: Path) -> Path:
    return root / BENCH_CHECKER_REL


def extract_assert_block(text: str, first_line: str) -> list[str]:
    block: list[str] = []
    capturing = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not capturing:
            if line == first_line:
                capturing = True
                block.append(line)
            continue
        block.append(line)
        if line == "]":
            return block
    return block


def collect_issues(root: Path) -> list[str]:
    path = checker_path(root)
    if not path.exists():
        return [f"missing_file:{BENCH_CHECKER_REL}"]

    text = path.read_text(encoding="utf-8")
    issues: list[str] = []

    for marker in REQUIRED_MARKERS:
        count = text.count(marker)
        if count != 1:
            issues.append(f"marker_count:{marker}:expected=1:actual={count}")

    for fragment in FORBIDDEN_FRAGMENTS:
        count = text.count(fragment)
        if count != 0:
            issues.append(f"forbidden:{fragment}:actual={count}")

    expectation_block = extract_assert_block(text, "assert missing_output == [")
    if expectation_block:
        joined = "\n".join(expectation_block)
        for fragment in FORBIDDEN_EXPECTATION_FAILURE_FRAGMENTS:
            count = joined.count(fragment)
            if count != 0:
                issues.append(f"expectation_block_forbidden:{fragment}:actual={count}")

    command_failure_block = extract_assert_block(text, "assert command_failure_output == [")
    if command_failure_block:
        joined = "\n".join(command_failure_block)
        for fragment in FORBIDDEN_BENCH_FAILURE_BLOCK_FRAGMENTS:
            count = joined.count(fragment)
            if count != 0:
                issues.append(f"bench_failure_block_forbidden:{fragment}:actual={count}")

    return issues


def write_checker(root: Path, content: str) -> None:
    path = checker_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_checker() -> str:
    lines = [
        "def emit_expectations_failure(",
        "def emit_validation_failure(kind: str, payload: object, expectations_path: Path) -> int:",
        "def emit_bench_command_failure(",
        "def emit_bench_command_missing(error: FileNotFoundError, expectations_path: Path) -> int:",
        "def capture_expectations_failure_output(",
        "def capture_validation_failure_output(",
        "def capture_bench_command_failure_output(",
        "def capture_bench_command_missing_output(",
        'print("PHASE1_BENCH_CHECK_REASON=bench_command_exit")',
        'print("PHASE1_BENCH_CHECK_REASON=bench_command_missing")',
        "assert missing_output == [",
        '"PHASE1_BENCH_CHECK=fail",',
        '"PHASE1_BENCH_CHECK_REASON=expectations_missing",',
        'f"PHASE1_BENCH_EXPECTATIONS={missing_expectations_path}",',
        "]",
        "assert malformed_output == [",
        '"PHASE1_BENCH_CHECK=fail",',
        '"PHASE1_BENCH_CHECK_REASON=expectations_json_error",',
        'f"PHASE1_BENCH_EXPECTATIONS={invalid_expectations_path}",',
        '"EXPECTATIONS_JSON_ERROR=Expecting property name enclosed in double quotes",',
        "]",
        "assert invalid_status_output == [",
        '"PHASE1_BENCH_CHECK=fail",',
        '"PHASE1_BENCH_CHECK_REASON=expectations_status",',
        'f"PHASE1_BENCH_EXPECTATIONS={status_mismatch_path}",',
        "]",
        "assert status_drift_output == [",
        '"PHASE1_BENCH_CHECK=fail",',
        '"PHASE1_BENCH_CHECK_REASON=status",',
        'f"PHASE1_BENCH_EXPECTATIONS={bench_status_drift_path}",',
        "]",
        "assert command_failure_output == [",
        '"PHASE1_BENCH_CHECK=fail",',
        '"PHASE1_BENCH_CHECK_REASON=bench_command_exit",',
        'f"PHASE1_BENCH_EXPECTATIONS={command_failure_path}",',
        '"BENCH_COMMAND_EXIT=7",',
        "]",
        "assert command_missing_output == [",
        '"PHASE1_BENCH_CHECK=fail",',
        '"PHASE1_BENCH_CHECK_REASON=bench_command_missing",',
        'f"PHASE1_BENCH_EXPECTATIONS={command_missing_path}",',
        '"BENCH_COMMAND_MISSING=/missing/zig",',
        "]",
        "assert checksum_drift_output == [",
        '"PHASE1_BENCH_CHECK=fail",',
        '"PHASE1_BENCH_CHECK_REASON=exact_checksum_mismatch",',
        'f"PHASE1_BENCH_EXPECTATIONS={checksum_drift_path}",',
        "]",
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        "",
    ]
    return "\n".join(lines) + "\n"


def expected_issue(needle: str | None, operation: str) -> str:
    if operation == "unlink":
        return f"missing_file:{BENCH_CHECKER_REL}"
    assert needle is not None
    if operation == "remove":
        return f"marker_count:{needle}:expected=1:actual=0"
    if operation == "duplicate":
        return f"marker_count:{needle}:expected=1:actual=2"
    if operation == "append_forbidden":
        return f"forbidden:{needle}:actual=1"
    if operation == "append_expectation_block":
        return f"expectation_block_forbidden:{needle}:actual=1"
    return f"bench_failure_block_forbidden:{needle}:actual=1"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-failure-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        write_checker(root, build_sample_checker())
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_FAILURE_PACKET_SELF_TEST=fail")
            for issue in issues:
                print(issue)
            return 1

    cases: list[tuple[str, str | None, str]] = [(None, None, "unlink")]
    for marker in REQUIRED_MARKERS:
        cases.append((f"remove:{marker}", marker, "remove"))
        cases.append((f"duplicate:{marker}", marker, "duplicate"))
    for fragment in FORBIDDEN_FRAGMENTS:
        cases.append((f"forbidden:{fragment}", fragment, "append_forbidden"))
    for fragment in FORBIDDEN_EXPECTATION_FAILURE_FRAGMENTS:
        cases.append((f"expectation-block-forbidden:{fragment}", fragment, "append_expectation_block"))
    for fragment in FORBIDDEN_BENCH_FAILURE_BLOCK_FRAGMENTS:
        cases.append((f"bench-failure-block-forbidden:{fragment}", fragment, "append_bench_failure_block"))

    for label, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-failure-packet-case-") as tmpdir:
            root = Path(tmpdir)
            write_checker(root, build_sample_checker())
            path = checker_path(root)

            if operation == "unlink":
                path.unlink()
            elif operation == "remove":
                assert needle is not None
                path.write_text(
                    path.read_text(encoding="utf-8").replace(needle + "\n", "", 1),
                    encoding="utf-8",
                )
            elif operation == "duplicate":
                assert needle is not None
                path.write_text(
                    path.read_text(encoding="utf-8").replace(needle, needle + "\n" + needle, 1),
                    encoding="utf-8",
                )
            elif operation == "append_forbidden":
                assert needle is not None
                path.write_text(path.read_text(encoding="utf-8") + needle + "\n", encoding="utf-8")
            elif operation == "append_expectation_block":
                assert needle is not None
                text = path.read_text(encoding="utf-8")
                text = text.replace(
                    'f"PHASE1_BENCH_EXPECTATIONS={missing_expectations_path}",\n]',
                    f'f"PHASE1_BENCH_EXPECTATIONS={{missing_expectations_path}}",\n"{needle}",\n]',
                    1,
                )
                path.write_text(text, encoding="utf-8")
            else:
                assert needle is not None
                text = path.read_text(encoding="utf-8")
                text = text.replace(
                    '"BENCH_COMMAND_EXIT=7",\n]',
                    f'"BENCH_COMMAND_EXIT=7",\n"{needle}",\n]',
                    1,
                )
                path.write_text(text, encoding="utf-8")

            issues = collect_issues(root)
            if issues != [expected_issue(needle, operation)]:
                print("PHASE1_BENCH_FAILURE_PACKET_SELF_TEST=fail")
                print(f"case={label}")
                print(f"expected={expected_issue(needle, operation)}")
                print(f"actual={issues!r}")
                return 1

    print("PHASE1_BENCH_FAILURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_FAILURE_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_BENCH_FAILURE_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_FAILURE_PACKET=pass")
    print(f"PHASE1_BENCH_FAILURE_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
