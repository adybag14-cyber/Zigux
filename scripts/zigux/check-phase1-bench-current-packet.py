#!/usr/bin/env python3
"""Guard the current Lane 16 bench packet across closure, scripts, tests, workflow, and checker surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"
BENCH_FAILURE_CHECKER_REL = "scripts/zigux/check-phase1-bench-failure-packet.py"
BENCH_SUCCESS_CHECKER_REL = "scripts/zigux/check-phase1-bench-success-packet.py"

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
    BENCH_FAILURE_CHECKER_REL,
    BENCH_SUCCESS_CHECKER_REL,
)

MARKERS = {
    PHASE1_CLOSURE_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `zigux/tests/phase1_bench.zig`",
        "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    ),
    SCRIPTS_README_REL: (
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
    ),
    TESTS_README_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "That shared smoke route should stay paired with the restored closure-side validator, the direct owner-map and string-review guards, the shipped bench checker, and the committed helper manifest so the tests-root note matches the same bounded Phase 1 packet already named by the docs root, lane-sequencing note, and scripts-root reminder.",
        "Current `master` still keeps `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` outside the direct-readback packet here, so leave those validator-first, parity, bench-route, harness, and make-wrapper names framed as historical packet members until a fresh reread restores them on current `master`.",
    ),
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        "def emit_bench_command_failure(",
        'print("PHASE1_BENCH_CHECK_REASON=bench_command_missing")',
        "print(f\"PHASE1_BENCH_EXPECTATION_COUNT={len(expectations['checksums'])}\")",
        "def run_self_test() -> None:",
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
    ),
    BENCH_FAILURE_CHECKER_REL: (
        '"""Guard the Lane 16 bench checker\'s fail-closed failure packets."""',
        "def extract_assert_block(text: str, first_line: str) -> list[str]:",
        "FORBIDDEN_EXPECTATION_FAILURE_FRAGMENTS = (",
        '"EXPECTATIONS_PATH=",',
        "FORBIDDEN_BENCH_FAILURE_BLOCK_FRAGMENTS = (",
        '"PHASE1_BENCH_CHECK=pass",',
        '"PHASE1_BENCH_EXPECTATION_COUNT=",',
        'assert command_failure_output == [',
        'assert command_missing_output == [',
        'print("PHASE1_BENCH_FAILURE_PACKET=pass")',
        'print("PHASE1_BENCH_FAILURE_PACKET_SELF_TEST=pass")',
    ),
    BENCH_SUCCESS_CHECKER_REL: (
        '"""Guard the Lane 16 bench checker\'s clean success packet."""',
        'def capture_success_packet_output(expectations: dict[str, object]) -> list[str]:',
        "FORBIDDEN_FRAGMENTS = (",
        "FORBIDDEN_SUCCESS_BLOCK_FRAGMENTS = (",
        "'PHASE1_BENCH_CHECK_REASON=',",
        "'PHASE1_BENCH_EXPECTATIONS=',",
        "'BENCH_COMMAND_EXIT=',",
        "'BENCH_COMMAND_MISSING=',",
        "'EXPECTATIONS_JSON_ERROR=',",
        "'EXPECTATIONS_JSON_LINE=',",
        "'EXPECTATIONS_JSON_COLUMN=',",
        'success_output = capture_success_packet_output(expectations)',
        'assert success_output == [',
        "print('PHASE1_BENCH_SUCCESS_PACKET=pass')",
        "print('PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST=pass')",
    ),
}

EXPECTED_ASSERT_BLOCKS = {
    BENCH_FAILURE_CHECKER_REL: (
        (
            "assert missing_output == [",
            '"PHASE1_BENCH_CHECK=fail",',
            '"PHASE1_BENCH_CHECK_REASON=expectations_missing",',
            'f"PHASE1_BENCH_EXPECTATIONS={missing_expectations_path}",',
            "]",
        ),
        (
            "assert malformed_output == [",
            '"PHASE1_BENCH_CHECK=fail",',
            '"PHASE1_BENCH_CHECK_REASON=expectations_json_error",',
            'f"PHASE1_BENCH_EXPECTATIONS={invalid_expectations_path}",',
            '"EXPECTATIONS_JSON_ERROR=Expecting property name enclosed in double quotes",',
            '"EXPECTATIONS_JSON_LINE=1",',
            '"EXPECTATIONS_JSON_COLUMN=2",',
            "]",
        ),
        (
            "assert invalid_status_output == [",
            '"PHASE1_BENCH_CHECK=fail",',
            '"PHASE1_BENCH_CHECK_REASON=expectations_status",',
            'f"PHASE1_BENCH_EXPECTATIONS={status_mismatch_path}",',
            '"fail",',
            "]",
        ),
        (
            "assert status_drift_output == [",
            '"PHASE1_BENCH_CHECK=fail",',
            '"PHASE1_BENCH_CHECK_REASON=status",',
            'f"PHASE1_BENCH_EXPECTATIONS={bench_status_drift_path}",',
            '"(\'pass\', \'fail\')",',
            "]",
        ),
        (
            "assert command_failure_output == [",
            '"PHASE1_BENCH_CHECK=fail",',
            '"PHASE1_BENCH_CHECK_REASON=bench_command_exit",',
            'f"PHASE1_BENCH_EXPECTATIONS={command_failure_path}",',
            '"BENCH_COMMAND_EXIT=7",',
            '"stdout-line-1",',
            '"stdout-line-2",',
            '"stderr-line-1",',
            '"stderr-line-2",',
            "]",
        ),
        (
            "assert command_missing_output == [",
            '"PHASE1_BENCH_CHECK=fail",',
            '"PHASE1_BENCH_CHECK_REASON=bench_command_missing",',
            'f"PHASE1_BENCH_EXPECTATIONS={command_missing_path}",',
            '"BENCH_COMMAND_MISSING=/missing/zig",',
            "]",
        ),
        (
            "assert checksum_drift_output == [",
            '"PHASE1_BENCH_CHECK=fail",',
            '"PHASE1_BENCH_CHECK_REASON=exact_checksum_mismatch",',
            'f"PHASE1_BENCH_EXPECTATIONS={checksum_drift_path}",',
            '"(\'PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\', 12, 120)",',
            "]",
        ),
    ),
    BENCH_SUCCESS_CHECKER_REL: (
        (
            "assert success_output == [",
            '"PHASE1_BENCH_CHECK=pass",',
            'f"PHASE1_BENCH_EXPECTATION_COUNT={len(expectations[\'checksums\'])}",',
            "]",
        ),
    ),
}

FORBIDDEN_FRAGMENTS = {
    SCRIPTS_README_REL: (
        "treating the bench checker itself as a missing tests-root route",
    ),
    TESTS_README_REL: (
        "promoting missing validator-first and make-route surfaces back into current tests-root evidence",
    ),
    WORKFLOW_REL: (
        "run: zig build bench --build-file zigux/tests/build.zig",
    ),
    BENCH_CHECKER_REL: (
        'print(f"PHASE1_BENCH_ZIG={zig}")',
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


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
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        if relative_path == WORKFLOW_REL:
            lines = text.splitlines()
            for marker in markers:
                count = sum(1 for line in lines if line.strip() == marker)
                if count != 1:
                    issues.append(f"{relative_path}:marker_count:{marker}:expected=1:actual={count}")
        else:
            for marker in markers:
                count = text.count(marker)
                if count != 1:
                    issues.append(f"{relative_path}:marker_count:{marker}:expected=1:actual={count}")

        for fragment in FORBIDDEN_FRAGMENTS.get(relative_path, ()):
            count = text.count(fragment)
            if count != 0:
                issues.append(f"{relative_path}:forbidden:{fragment}:actual={count}")

        for expected_block in EXPECTED_ASSERT_BLOCKS.get(relative_path, ()):
            first_line = expected_block[0]
            if text.count(first_line) != 1:
                continue
            actual_block = extract_assert_block(text, first_line)
            if actual_block != list(expected_block):
                issues.append(f"{relative_path}:assert_block:{first_line}:{actual_block!r}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_file(relative_path: str) -> str:
    if relative_path in (BENCH_FAILURE_CHECKER_REL, BENCH_SUCCESS_CHECKER_REL):
        block_lines = {line for block in EXPECTED_ASSERT_BLOCKS[relative_path] for line in block}
        lines = [line for line in MARKERS[relative_path] if line not in block_lines]
        for block in EXPECTED_ASSERT_BLOCKS[relative_path]:
            lines.extend(block)
        return "\n".join(lines) + "\n"
    return "\n".join(MARKERS[relative_path]) + "\n"


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, build_sample_file(relative_path))


def mutate_remove(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_assert_block_order(root: Path, relative_path: str, first_line: str) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_block = extract_assert_block(text, first_line)
    reordered = list(actual_block)
    reordered[1], reordered[2] = reordered[2], reordered[1]
    original = "\n".join(actual_block)
    updated = "\n".join(reordered)
    path.write_text(text.replace(original, updated, 1), encoding="utf-8")
    return reordered


def mutate_assert_block_remove_line(
    root: Path,
    relative_path: str,
    first_line: str,
    removed_line: str,
) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_block = extract_assert_block(text, first_line)
    updated_block = [line for line in actual_block if line != removed_line]
    original = "\n".join(actual_block)
    updated = "\n".join(updated_block)
    path.write_text(text.replace(original, updated, 1), encoding="utf-8")
    return updated_block


def mutate_assert_block_duplicate_line(
    root: Path,
    relative_path: str,
    first_line: str,
    duplicated_line: str,
) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_block = extract_assert_block(text, first_line)
    updated_block: list[str] = []
    duplicated = False
    for line in actual_block:
        updated_block.append(line)
        if not duplicated and line == duplicated_line:
            updated_block.append(line)
            duplicated = True
    original = "\n".join(actual_block)
    updated = "\n".join(updated_block)
    path.write_text(text.replace(original, updated, 1), encoding="utf-8")
    return updated_block


def expected_issue(
    relative_path: str,
    needle: str | None,
    operation: str,
    block: list[str] | None = None,
) -> str:
    if operation == "unlink":
        return f"missing_file:{relative_path}"
    if operation == "remove":
        assert needle is not None
        return f"{relative_path}:marker_count:{needle}:expected=1:actual=0"
    if operation == "duplicate":
        assert needle is not None
        return f"{relative_path}:marker_count:{needle}:expected=1:actual=2"
    if operation == "append":
        assert needle is not None
        return f"{relative_path}:forbidden:{needle}:actual=1"
    assert operation in (
        "assert_block_reorder",
        "assert_block_remove_line",
        "assert_block_duplicate_line",
    )
    assert needle is not None
    assert block is not None
    return f"{relative_path}:assert_block:{needle}:{block!r}"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            for issue in issues:
                print(issue)
            return 1

    cases: list[tuple[str, str, str | None, str]] = []
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", relative_path, None, "unlink"))
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append((f"remove:{relative_path}", relative_path, marker, "remove"))
            cases.append((f"duplicate:{relative_path}", relative_path, marker, "duplicate"))
    for relative_path, fragments in FORBIDDEN_FRAGMENTS.items():
        for fragment in fragments:
            cases.append((f"forbidden:{relative_path}", relative_path, fragment, "append"))
    for relative_path, blocks in EXPECTED_ASSERT_BLOCKS.items():
        for block in blocks:
            cases.append((f"assert_block:{relative_path}:{block[0]}", relative_path, block[0], "assert_block_reorder"))
            for removed_line in block[1:-1]:
                cases.append(
                    (
                        f"assert_block_line_drop:{relative_path}:{block[0]}:{removed_line}",
                        relative_path,
                        f"{block[0]}\n{removed_line}",
                        "assert_block_remove_line",
                    )
                )
            for duplicated_line in block[1:-1]:
                cases.append(
                    (
                        f"assert_block_line_duplicate:{relative_path}:{block[0]}:{duplicated_line}",
                        relative_path,
                        f"{block[0]}\n{duplicated_line}",
                        "assert_block_duplicate_line",
                    )
                )

    for label, relative_path, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            target = root / relative_path
            block: list[str] | None = None
            if operation == "unlink":
                target.unlink()
            elif operation == "remove":
                assert needle is not None
                mutate_remove(root, relative_path, needle)
            elif operation == "duplicate":
                assert needle is not None
                mutate_duplicate(root, relative_path, needle)
            elif operation == "append":
                assert needle is not None
                target.write_text(target.read_text(encoding="utf-8") + needle + "\n", encoding="utf-8")
            elif operation == "assert_block_reorder":
                assert needle is not None
                block = mutate_assert_block_order(root, relative_path, needle)
            elif operation == "assert_block_duplicate_line":
                assert needle is not None
                first_line, duplicated_line = needle.split("\n", 1)
                block = mutate_assert_block_duplicate_line(root, relative_path, first_line, duplicated_line)
                needle = first_line
            else:
                assert needle is not None
                first_line, removed_line = needle.split("\n", 1)
                block = mutate_assert_block_remove_line(root, relative_path, first_line, removed_line)
                needle = first_line
            issues = collect_issues(root)
            if issues != [expected_issue(relative_path, needle, operation, block)]:
                print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
                print(f"case={label}")
                print(f"expected={expected_issue(relative_path, needle, operation, block)}")
                print(f"actual={issues!r}")
                return 1

    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
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
        print("PHASE1_BENCH_CURRENT_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_CURRENT_PACKET=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_CURRENT_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
