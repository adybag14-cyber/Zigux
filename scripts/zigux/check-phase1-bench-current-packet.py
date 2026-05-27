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
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    ),
    SCRIPTS_README_REL: (
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
    ),
    TESTS_README_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (
        "class DuplicateTrackingDict(dict[str, object]):",
        "def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:",
        "return json.loads(text, object_pairs_hook=DuplicateTrackingDict)",
        "def load_runtime_expectations(path: Path) -> tuple[str, object]:",
        'return ("missing_expectations_file", path)',
        'return ("expectations_json_error", exc)',
        "kind, payload = validate_expectations(expectations)",
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        'print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
    ),
}

EXPECTED_BLOCKS = {
    BENCH_CHECKER_REL: (
        (
            "DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent",
            'EXPECTATIONS_REL = Path("zigux/tests/fixtures/phase1_bench_expectations.json")',
            'PHASE1_BENCH_REL = Path("zigux/tests/phase1_bench.zig")',
        ),
        (
            "def repo_root(root: str | None) -> Path:",
            "return Path(root).resolve() if root else DEFAULT_ROOT.resolve()",
        ),
        (
            "def expectations_path(root: Path) -> Path:",
            "return root / EXPECTATIONS_REL",
        ),
        (
            "def bench_source_path(root: Path) -> Path:",
            "return root / PHASE1_BENCH_REL",
        ),
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
            "REQUIRED_EXACT_CHECKSUMS = set(EXPECTED_CHECKSUMS)",
            'RBTREE_REQUIRED_ITERATIONS = {"PHASE1_BENCH_RBTREE_ITERATIONS"}',
        ),
        (
            "SOURCE_MARKER_SETS = (",
            "FIND_BIT_REQUIRED_SOURCE_MARKERS,",
            "RBTREE_REQUIRED_SOURCE_MARKERS,",
            ")",
        ),
        (
            "def duplicate_marker_labels(text: str, marker_set: dict[str, str]) -> list[str]:",
            "duplicates: list[str] = []",
            "for label, marker in marker_set.items():",
            "if text.count(marker) > 1:",
            "duplicates.append(label)",
            "return duplicates",
        ),
        (
            "def validate_bench_source(text: str) -> tuple[str, object]:",
            "missing: list[str] = []",
            "for marker_set in SOURCE_MARKER_SETS:",
            "for label, marker in marker_set.items():",
            "if marker not in text:",
            "missing.append(label)",
            "if missing:",
            'return ("bench_source_missing_markers", missing)',
            "duplicate_rbtree_markers = duplicate_marker_labels(text, RBTREE_REQUIRED_SOURCE_MARKERS)",
            "if duplicate_rbtree_markers:",
            'return ("bench_source_duplicate_rbtree_markers", duplicate_rbtree_markers)',
            'return ("pass", text)',
        ),
        (
            "def load_runtime_bench_source(path: Path) -> tuple[str, object]:",
            "try:",
            'text = path.read_text(encoding="utf-8")',
            "except FileNotFoundError:",
            'return ("missing_bench_source_file", path)',
            "return validate_bench_source(text)",
        ),
        (
            "exact_requirements = (",
            '("expectations_checksums_bitmap_exact_required", BITMAP_REQUIRED_EXACT_CHECKSUMS),',
            '("expectations_checksums_find_bit_exact_required", FIND_BIT_REQUIRED_EXACT_CHECKSUMS),',
            '("expectations_checksums_string_exact_required", STRING_REQUIRED_EXACT_CHECKSUMS),',
            '("expectations_checksums_hweight_exact_required", HWEIGHT_REQUIRED_EXACT_CHECKSUMS),',
            '("expectations_checksums_list_sort_exact_required", LIST_SORT_REQUIRED_EXACT_CHECKSUMS),',
            '("expectations_checksums_rbtree_exact_required", RBTREE_REQUIRED_EXACT_CHECKSUMS),',
            ")",
        ),
        (
            "for reason, required_keys in exact_requirements:",
            "for key in sorted(required_keys):",
            "if key in checksum_keys and key not in exact_checksums:",
            "return (reason, key)",
        ),
        (
            'with tempfile.TemporaryDirectory(prefix="phase1-bench-source-") as tmp:',
            'source_path = Path(tmp) / "phase1_bench.zig"',
            "kind, payload = load_runtime_bench_source(source_path)",
            'assert_case(kind == "missing_bench_source_file", "missing bench source", (kind, payload))',
        ),
        (
            'with tempfile.TemporaryDirectory(prefix="phase1-bench-root-") as tmp:',
            "root = Path(tmp)",
            "source_path = bench_source_path(root)",
            "expectations_file = expectations_path(root)",
            'assert_case(repo_root(str(root)) == root.resolve(), "repo root override")',
        ),
        (
            'parser.add_argument("--repo-root", "--root", dest="repo_root", help="Override the repository root used for validation.")',
            'parser.add_argument("--zig", help="Path to Zig executable")',
            'parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without invoking Zig.")',
        ),
        (
            'if kind == "expectations_json_error":',
            "exc = payload",
            "assert isinstance(exc, json.JSONDecodeError)",
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")',
            'print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")',
            'print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")',
            "return 1",
        ),
        (
            "phase1_bench = bench_source_path(root)",
            "kind, payload = load_runtime_bench_source(phase1_bench)",
            'if kind != "pass":',
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
            "print(payload)",
            "return 1",
        ),
        (
            "result = subprocess.run(",
            '[zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"],',
            "cwd=str(root),",
            "capture_output=True,",
            "text=True,",
            ")",
        ),
        (
            'print("PHASE1_BENCH_CHECK=pass")',
            'print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")',
            'print(f"PHASE1_BENCH_SOURCE={phase1_bench}")',
            'print(f"PHASE1_BENCH_ZIG={zig}")',
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
        "def validate_find_bit_bench_source(text: str) -> tuple[str, object]:",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def extract_section(text: str, first_line: str) -> list[str]:
    section: list[str] = []
    capturing = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not capturing:
            if line == first_line:
                capturing = True
                section.append(line)
            continue
        if not line:
            return section
        section.append(line)
    return section


def section_contains_expected_lines(section: list[str], expected_lines: tuple[str, ...]) -> bool:
    expected_index = 0
    for line in section:
        if expected_index == len(expected_lines):
            return True
        if line == expected_lines[expected_index]:
            expected_index += 1
    return expected_index == len(expected_lines)


def collect_expected_line_count_issues(
    relative_path: str,
    first_line: str,
    section: list[str],
    expected_lines: tuple[str, ...],
) -> list[str]:
    issues: list[str] = []
    for expected_line in expected_lines[1:]:
        count = section.count(expected_line)
        if count != 1:
            issues.append(
                f"{relative_path}:section_line_count:{first_line}:{expected_line}:expected=1:actual={count}"
            )
    return issues


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
        for expected_block in EXPECTED_BLOCKS.get(relative_path, ()):
            first_line = expected_block[0]
            first_line_count = sum(1 for line in stripped_lines if line == first_line)
            if first_line_count != 1:
                issues.append(f"{relative_path}:marker_count:{first_line}:expected=1:actual={first_line_count}")
                continue
            actual_section = extract_section(text, first_line)
            if not section_contains_expected_lines(actual_section, expected_block):
                issues.append(f"{relative_path}:assert_block:{first_line}:{actual_section!r}")
                continue
            issues.extend(
                collect_expected_line_count_issues(relative_path, first_line, actual_section, expected_block)
            )

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_file(relative_path: str) -> str:
    lines = list(MARKERS[relative_path])
    for block in EXPECTED_BLOCKS.get(relative_path, ()):
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


def mutate_missing_file(root: Path, relative_path: str) -> None:
    (root / relative_path).unlink()


def mutate_append_forbidden_fragment(root: Path, relative_path: str, fragment: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    suffix = "" if text.endswith("\n") else "\n"
    path.write_text(text + suffix + fragment + "\n", encoding="utf-8")


def mutate_assert_block_reorder(root: Path, relative_path: str, first_line: str) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_section = extract_section(text, first_line)
    reordered = list(actual_section)
    reordered[1], reordered[2] = reordered[2], reordered[1]
    path.write_text(
        text.replace("\n".join(actual_section), "\n".join(reordered), 1),
        encoding="utf-8",
    )
    return reordered


def mutate_assert_section_insert_after(
    root: Path,
    relative_path: str,
    first_line: str,
    anchor_line: str,
    inserted_lines: tuple[str, ...],
) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_section = extract_section(text, first_line)
    anchor_index = actual_section.index(anchor_line)
    updated_section = (
        actual_section[: anchor_index + 1]
        + list(inserted_lines)
        + actual_section[anchor_index + 1 :]
    )
    path.write_text(
        text.replace("\n".join(actual_section), "\n".join(updated_section), 1),
        encoding="utf-8",
    )
    return updated_section


def mutate_assert_section_duplicate_line(
    root: Path,
    relative_path: str,
    first_line: str,
    duplicated_line: str,
) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_section = extract_section(text, first_line)
    duplicate_index = actual_section.index(duplicated_line)
    updated_section = (
        actual_section[: duplicate_index + 1]
        + [duplicated_line]
        + actual_section[duplicate_index + 1 :]
    )
    path.write_text(
        text.replace("\n".join(actual_section), "\n".join(updated_section), 1),
        encoding="utf-8",
    )


def expected_issue(relative_path: str, needle: str, operation: str, block: list[str] | None = None) -> str:
    if operation == "remove":
        return f"{relative_path}:marker_count:{needle}:expected=1:actual=0"
    if operation == "duplicate":
        return f"{relative_path}:marker_count:{needle}:expected=1:actual=2"
    if operation == "missing_file":
        return f"missing_file:{relative_path}"
    if operation == "forbidden":
        return f"{relative_path}:forbidden:{needle}:actual=1"
    if operation == "duplicate_section_line":
        first_line = block[0] if block is not None else ""
        return f"{relative_path}:section_line_count:{first_line}:{needle}:expected=1:actual=2"
    assert block is not None
    return f"{relative_path}:assert_block:{needle}:{block!r}"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-interleaved-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        mutate_assert_section_insert_after(
            root,
            BENCH_CHECKER_REL,
            "for reason, required_keys in exact_requirements:",
            "for reason, required_keys in exact_requirements:",
            (
                "if not required_keys:",
                "continue",
            ),
        )
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=interleaved_exact_requirements_loop")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-multiline-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        mutate_assert_section_insert_after(
            root,
            BENCH_CHECKER_REL,
            "result = subprocess.run(",
            "result = subprocess.run(",
            (
                "check=False,",
            ),
        )
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=multiline_subprocess_section")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-duplicate-section-line-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        first_line = "for reason, required_keys in exact_requirements:"
        duplicated_line = "for key in sorted(required_keys):"
        mutate_assert_section_duplicate_line(root, BENCH_CHECKER_REL, first_line, duplicated_line)
        issues = collect_issues(root)
        expected = expected_issue(
            BENCH_CHECKER_REL,
            duplicated_line,
            "duplicate_section_line",
            [first_line],
        )
        if issues != [expected]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=duplicate_section_line")
            print(f"expected={expected}")
            print(f"actual={issues!r}")
            return 1

    cases: list[tuple[str, str, str, str]] = []
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append((f"remove:{relative_path}", relative_path, marker, "remove"))
            cases.append((f"duplicate:{relative_path}", relative_path, marker, "duplicate"))
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", relative_path, "", "missing_file"))
    for relative_path, fragments in FORBIDDEN_FRAGMENTS.items():
        for fragment in fragments:
            cases.append((f"forbidden:{relative_path}:{fragment}", relative_path, fragment, "forbidden"))
    for block in EXPECTED_BLOCKS[BENCH_CHECKER_REL]:
        if len(block) > 2:
            cases.append((f"assert_block:{block[0]}", BENCH_CHECKER_REL, block[0], "assert_block_reorder"))

    for label, relative_path, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            block: list[str] | None = None
            if operation == "remove":
                mutate_remove(root, relative_path, needle)
            elif operation == "duplicate":
                mutate_duplicate(root, relative_path, needle)
            elif operation == "missing_file":
                mutate_missing_file(root, relative_path)
            elif operation == "forbidden":
                mutate_append_forbidden_fragment(root, relative_path, needle)
            else:
                block = mutate_assert_block_reorder(root, relative_path, needle)
            issues = collect_issues(root)
            expected = expected_issue(relative_path, needle, operation, block)
            if issues != [expected]:
                print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
                print(f"case={label}")
                print(f"expected={expected}")
                print(f"actual={issues!r}")
                return 1

    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 4}")
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
