#!/usr/bin/env python3
"""Guard the current master Lane 16 bench packet across docs, tests, workflow, and checker surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
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
        'return ("missing_expectations_file", path)',
        'return ("expectations_json_error", exc)',
        'kind, payload = validate_expectations(expectations)',
        'assert kind == "pass", (kind, payload)',
        'kind, payload = load_runtime_expectations(EXPECTATIONS)',
        'print(f"PHASE1_BENCH_ZIG={zig}")',
        'print("PHASE1_BENCH_CHECK=pass")',
        'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")',
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        'print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
    ),
}

EXPECTED_ASSERT_BLOCKS = {
    BENCH_CHECKER_REL: (
        (
            "EXPECTED_ITERATIONS = {",
            '"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,',
            '"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,',
            '"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,',
            '"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,',
            '"PHASE1_BENCH_STRING_ITERATIONS": 40000,',
            '"PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,',
            '"PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,',
            '"PHASE1_BENCH_RBTREE_ITERATIONS": 4000,',
            "}",
        ),
        (
            "RBTREE_REQUIRED_ITERATIONS = {",
            '"PHASE1_BENCH_RBTREE_ITERATIONS",',
            "}",
        ),
        (
            "EXPECTED_CHECKSUMS = [",
            '"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",',
            '"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",',
            '"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",',
            '"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",',
            '"PHASE1_BENCH_STRING_CHECKSUM",',
            '"PHASE1_BENCH_HWEIGHT_CHECKSUM",',
            '"PHASE1_BENCH_LIST_SORT_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
            "]",
        ),
        (
            "REQUIRED_EXACT_CHECKSUMS = {",
            '"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",',
            '"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",',
            '"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",',
            '"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",',
            '"PHASE1_BENCH_STRING_CHECKSUM",',
            '"PHASE1_BENCH_HWEIGHT_CHECKSUM",',
            '"PHASE1_BENCH_LIST_SORT_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
            "}",
        ),
        (
            "BITMAP_REQUIRED_EXACT_CHECKSUMS = {",
            '"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",',
            '"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",',
            "}",
        ),
        (
            "FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {",
            '"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",',
            '"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",',
            "}",
        ),
        (
            "STRING_REQUIRED_EXACT_CHECKSUMS = {",
            '"PHASE1_BENCH_STRING_CHECKSUM",',
            "}",
        ),
        (
            "HWEIGHT_REQUIRED_EXACT_CHECKSUMS = {",
            '"PHASE1_BENCH_HWEIGHT_CHECKSUM",',
            "}",
        ),
        (
            "LIST_SORT_REQUIRED_EXACT_CHECKSUMS = {",
            '"PHASE1_BENCH_LIST_SORT_CHECKSUM",',
            "}",
        ),
        (
            "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
            '"PHASE1_BENCH_RBTREE_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",',
            '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
            "}",
        ),
        (
            'kind, payload = validate_expectations(load_expectations_text(duplicate_top_level_text))',
            'assert kind == "expectations_duplicate_keys"',
            'assert payload == ["status"]',
        ),
        (
            'kind, payload = validate_expectations(load_expectations_text(duplicate_iteration_text))',
            'assert kind == "expectations_duplicate_iteration_keys"',
            'assert payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"]',
        ),
        (
            'kind, payload = validate_expectations(load_expectations_text(duplicate_exact_checksum_text))',
            'assert kind == "expectations_duplicate_exact_checksum_keys"',
            'assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]',
        ),
        (
            'kind, payload = validate_expectations(duplicate_checksum_list)',
            'assert kind == "expectations_duplicate_checksums"',
            'assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]',
        ),
        (
            'kind, _ = validate_output(expectations, ok_output)',
            'assert kind == "pass"',
            "case_count += 1",
        ),
        (
            "status_mismatch_output = ok_output.replace(",
            'kind, payload = validate_output(expectations, status_mismatch_output)',
            'assert kind == "status"',
            'assert payload == ("pass", "fail")',
        ),
        (
            'missing_status_output = ok_output.replace("PHASE1_BENCH=pass\\n", "", 1)',
            'kind, payload = validate_output(expectations, missing_status_output)',
            'assert kind == "status"',
            'assert payload == ("pass", None)',
        ),
        (
            'unexpected_output = ok_output + "\\nPHASE1_BENCH_SPURIOUS=13"',
            'kind, payload = validate_output(expectations, unexpected_output)',
            'assert kind == "unexpected"',
            'assert payload == ["PHASE1_BENCH_SPURIOUS"]',
        ),
        (
            'duplicate_iteration_output = ok_output + "\\nPHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000"',
            'kind, payload = validate_output(expectations, duplicate_iteration_output)',
            'assert kind == "duplicate"',
            'assert payload == ["PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS"]',
        ),
        (
            'kind, payload = validate_output(expectations, missing_rbtree_iteration_output)',
            'assert kind == "missing_rbtree_iterations"',
            'assert payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"]',
        ),
        (
            'kind, payload = validate_output(expectations, rbtree_iteration_mismatch_output)',
            'assert kind == "rbtree_iteration_mismatch"',
            'assert payload == ("PHASE1_BENCH_RBTREE_ITERATIONS", 4000, "4")',
        ),
        (
            '("PHASE1_BENCH_RBTREE_CHECKSUM", "8"),',
            '("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM", "9"),',
            '("PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM", "10"),',
            '("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM", "11"),',
            '("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", "12"),',
            "):",
            'missing_output = ok_output.replace(f"\\n{key}={value}", "")',
            'kind, payload = validate_output(expectations, missing_output)',
            'assert kind == "missing_rbtree_exact_checksums"',
            'assert payload == [key]',
            "case_count += 1",
        ),
        (
            '("PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM", "1"),',
            '("PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM", "2"),',
            "):",
            'missing_output = ok_output.replace(f"\\n{key}={value}", "")',
            'kind, payload = validate_output(expectations, missing_output)',
            'assert kind == "missing_bitmap_exact_checksums"',
            'assert payload == [key]',
            "case_count += 1",
        ),
        (
            '("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM", "3"),',
            '("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM", "4"),',
            "):",
            'missing_output = ok_output.replace(f"\\n{key}={value}", "")',
            'kind, payload = validate_output(expectations, missing_output)',
            'assert kind == "missing_find_bit_exact_checksums"',
            'assert payload == [key]',
            "case_count += 1",
        ),
        (
            'kind, payload = validate_output(expectations, mismatch_output)',
            'assert kind == "exact_checksum_mismatch"',
            'assert payload == ("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", 12, 120)',
        ),
        (
            'kind, payload = validate_output(expectations, duplicate_mismatch_output)',
            'assert kind == "exact_checksum_mismatch"',
            'assert payload == ("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM", 11, 110)',
        ),
        (
            'duplicate_output = ok_output + "\\nPHASE1_BENCH_RBTREE_CACHED_CHECKSUM=12"',
            'kind, payload = validate_output(expectations, duplicate_output)',
            'assert kind == "duplicate"',
            'assert payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]',
        ),
        (
            "for key, value, expected_kind in (",
            'missing_output = ok_output.replace(f"\\n{key}={value}", "")',
            'kind, payload = validate_output(expectations, missing_output)',
            "assert kind == expected_kind",
            "assert payload == [key]",
            "case_count += 1",
        ),
        (
            "kind, payload = validate_expectations(reordered_checksums)",
            'assert kind == "expectations_checksum_order"',
            'assert payload == reordered_checksums["checksums"]',
        ),
        (
            "kind, payload = validate_expectations(downgraded_bitmap_weight_exact)",
            'assert kind == "expectations_checksums_bitmap_exact_required"',
            'assert payload == "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM"',
        ),
        (
            "kind, payload = validate_expectations(downgraded_bitmap_window_exact)",
            'assert kind == "expectations_checksums_bitmap_exact_required"',
            'assert payload == "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM"',
        ),
        (
            "kind, payload = validate_expectations(downgraded_rbtree_exact)",
            'assert kind == "expectations_checksums_rbtree_exact_required"',
            'assert payload == "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"',
        ),
        (
            "kind, payload = validate_expectations(missing_duplicate_exact)",
            'assert kind == "expectations_checksums_rbtree_exact_required"',
            'assert payload == "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM"',
        ),
        (
            "kind, payload = validate_expectations(missing_string_exact)",
            'assert kind == "expectations_checksums_string_exact_required"',
            'assert payload == "PHASE1_BENCH_STRING_CHECKSUM"',
        ),
        (
            "kind, payload = validate_expectations(missing_hweight_exact)",
            'assert kind == "expectations_checksums_hweight_exact_required"',
            'assert payload == "PHASE1_BENCH_HWEIGHT_CHECKSUM"',
        ),
        (
            "kind, payload = validate_expectations(missing_list_sort_exact)",
            'assert kind == "expectations_checksums_list_sort_exact_required"',
            'assert payload == "PHASE1_BENCH_LIST_SORT_CHECKSUM"',
        ),
        (
            "kind, payload = validate_expectations(missing_find_next_exact)",
            'assert kind == "expectations_checksums_find_bit_exact_required"',
            'assert payload == "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM"',
        ),
        (
            "kind, payload = validate_expectations(missing_find_bit_edge_exact)",
            'assert kind == "expectations_checksums_find_bit_exact_required"',
            'assert payload == "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM"',
        ),
        (
            "kind, payload = validate_expectations(missing_rbtree_iterations)",
            'assert kind == "expectations_missing_rbtree_iterations"',
            'assert payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"]',
        ),
        (
            'if kind == "missing_expectations_file":',
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
            'print(f"EXPECTATIONS_PATH={payload}")',
            "return 1",
        ),
        (
            'if kind == "expectations_json_error":',
            "exc = payload",
            "assert isinstance(exc, json.JSONDecodeError)",
            'print("PHASE1_BENCH_CHECK=fail")',
            'print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
            'print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
            'print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
            "return 1",
            'if kind != "pass":',
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
            "print(payload)",
            "return 1",
        ),
        (
            "expectations = payload",
            "assert isinstance(expectations, dict)",
            "zig = find_zig(args.zig)",
        ),
        (
            "result = subprocess.run(",
            '[zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"],',
            "cwd=str(ROOT),",
            "capture_output=True,",
            "text=True,",
            ")",
        ),
        (
            "if result.returncode != 0:",
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"BENCH_COMMAND_EXIT={result.returncode}")',
            "if result.stdout:",
            'print(result.stdout.rstrip("\\n"))',
            "if result.stderr:",
            'print(result.stderr.rstrip("\\n"))',
            "return 1",
        ),
        (
            "kind, payload = validate_output(expectations, result.stdout)",
            'if kind != "pass":',
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
            "print(payload)",
            "return 1",
        ),
    ),
}

FORBIDDEN_FRAGMENTS = {
    WORKFLOW_REL: (
        "run: zig build bench --build-file zigux/tests/build.zig",
    ),
    BENCH_CHECKER_REL: (
        "def emit_bench_command_failure(",
        "PHASE1_BENCH_EXPECTATION_COUNT",
        "PHASE1_BENCH_CHECK_REASON=bench_command_exit",
        "PHASE1_BENCH_CHECK_REASON=bench_command_missing",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def extract_assert_block(text: str, first_line: str, line_count: int) -> list[str]:
    block: list[str] = []
    capturing = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not capturing:
            if line == first_line:
                capturing = True
                block.append(line)
            continue
        if not line:
            return block
        block.append(line)
        if len(block) == line_count:
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

        stripped_lines = [line.strip() for line in text.splitlines()]
        for expected_block in EXPECTED_ASSERT_BLOCKS.get(relative_path, ()):
            first_line = expected_block[0]
            first_line_count = sum(1 for line in stripped_lines if line == first_line)
            if first_line_count != 1:
                issues.append(f"{relative_path}:marker_count:{first_line}:expected=1:actual={first_line_count}")
                continue
            actual_block = extract_assert_block(text, first_line, len(expected_block))
            if actual_block != list(expected_block):
                issues.append(f"{relative_path}:assert_block:{first_line}:{actual_block!r}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_file(relative_path: str) -> str:
    lines = list(MARKERS[relative_path])
    for block in EXPECTED_ASSERT_BLOCKS.get(relative_path, ()): 
        lines.extend(block)
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


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


def mutate_assert_block_reorder(root: Path, relative_path: str, first_line: str) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    expected_block = next(
        block
        for block in EXPECTED_ASSERT_BLOCKS[relative_path]
        if block[0] == first_line
    )
    actual_block = extract_assert_block(text, first_line, len(expected_block))
    reordered = list(actual_block)
    reordered[1], reordered[2] = reordered[2], reordered[1]
    original = "\n".join(actual_block)
    updated = "\n".join(reordered)
    path.write_text(text.replace(original, updated, 1), encoding="utf-8")
    return reordered


def mutate_assert_block_remove_line(
    root: Path, relative_path: str, first_line: str, line_index: int
) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    expected_block = next(
        block
        for block in EXPECTED_ASSERT_BLOCKS[relative_path]
        if block[0] == first_line
    )
    actual_block = extract_assert_block(text, first_line, len(expected_block))
    trimmed = actual_block[:line_index] + actual_block[line_index + 1 :]
    original = "\n".join(actual_block)
    updated = "\n".join(trimmed)
    path.write_text(text.replace(original, updated, 1), encoding="utf-8")
    return trimmed


def expected_issue(
    relative_path: str, needle: str | None, operation: str, block: list[str] | None = None
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
    assert operation in {"assert_block_reorder", "assert_block_remove_line"}
    assert needle is not None
    assert block is not None
    return f"{relative_path}:assert_block:{needle}:{block!r}"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-master-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            for issue in issues:
                print(issue)
            return 1

    cases: list[tuple[str, str, str | None, str, int | None]] = []
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", relative_path, None, "unlink", None))
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append((f"remove:{relative_path}", relative_path, marker, "remove", None))
            cases.append((f"duplicate:{relative_path}", relative_path, marker, "duplicate", None))
    for relative_path, fragments in FORBIDDEN_FRAGMENTS.items():
        for fragment in fragments:
            cases.append((f"forbidden:{relative_path}", relative_path, fragment, "append", None))
    for relative_path, blocks in EXPECTED_ASSERT_BLOCKS.items():
        for block in blocks:
            cases.append(
                (
                    f"assert_block:{relative_path}:{block[0]}:reorder",
                    relative_path,
                    block[0],
                    "assert_block_reorder",
                    None,
                )
            )
            for line_index in range(1, len(block)):
                cases.append(
                    (
                        f"assert_block:{relative_path}:{block[0]}:remove_line:{line_index}",
                        relative_path,
                        block[0],
                        "assert_block_remove_line",
                        line_index,
                    )
                )

    for label, relative_path, needle, operation, line_index in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-current-master-packet-case-") as tmpdir:
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
                block = mutate_assert_block_reorder(root, relative_path, needle)
            else:
                assert needle is not None
                assert line_index is not None
                block = mutate_assert_block_remove_line(root, relative_path, needle, line_index)
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
