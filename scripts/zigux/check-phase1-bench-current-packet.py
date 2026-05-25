#!/usr/bin/env python3
"""Guard the current Lane 16 Phase 1 bench packet on current master."""

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
        "- `PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig`",
        "- `PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py`",
        "- explicit opt-in to Node 24 action execution on GitHub-hosted runners",
        "- `python3 scripts/zigux/install-zig.py --self-test` stays reviewable as the bounded installer-viability replay for that in-repo download step",
        "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
        "- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
        "- `PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    ),
    SCRIPTS_README_REL: (
        "- `validate-phase1-closure.py` confirms the closed Phase 1 packet still matches `Documentation/zigux/phase1-closure.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, the shared helper build wiring, and the bootstrap workflow.",
        "- `check-phase1-parity.py` compares the bounded helper outputs against the committed Phase 1 fixture corpus so `bitmap`, `find_bit`, `string`, `rbtree`, and the rest of the closed helper set stay pinned to the current C behavior. - `check-phase1-bench.py` verifies the benchmark smoke outputs recorded in `zigux/tests/fixtures/phase1_bench_expectations.json` so the helper hot loops keep their checksum-backed replay contract.",
        "- `zig build test --build-file zigux/tests/build.zig` and `zig build bench --build-file zigux/tests/build.zig` remain the executable Phase 1 unit and benchmark gates behind the validator and closure records.",
    ),
    TESTS_README_REL: (
        "* keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
        "* keep `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, and `python3 scripts/zigux/check-phase1-installer-companion-checks.py` visible as focused companion checks for the closed Phase 1 installer-review surface without widening the counted tests-root packet line that `scripts/zigux/validate-phase1.py` currently enforces",
    ),
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe",
    ),
    BENCH_CHECKER_REL: (
        "class DuplicateTrackingDict(dict[str, object]):",
        "def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:",
        "print('PHASE1_BENCH_CHECK_SELF_TEST=pass')",
        "print(f'PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}')",
    ),
}

EXPECTED_BLOCKS = {
    BENCH_CHECKER_REL: (
        (
            "HERE = Path(__file__).resolve()",
            "DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent",
            'EXPECTATIONS_REL = Path("zigux/tests/fixtures/phase1_bench_expectations.json")',
            'PHASE1_BENCH_REL = Path("zigux/tests/phase1_bench.zig")',
        ),
        (
            "except json.JSONDecodeError as exc:",
            'return ("expectations_json_error", exc)',
        ),
        (
            "exact_categories = (",
            '("missing_rbtree_exact_checksums", RBTREE_REQUIRED_EXACT_CHECKSUMS),',
            '("missing_bitmap_exact_checksums", BITMAP_REQUIRED_EXACT_CHECKSUMS),',
            '("missing_find_bit_exact_checksums", FIND_BIT_REQUIRED_EXACT_CHECKSUMS),',
            '("missing_string_exact_checksums", STRING_REQUIRED_EXACT_CHECKSUMS),',
            '("missing_hweight_exact_checksums", HWEIGHT_REQUIRED_EXACT_CHECKSUMS),',
            '("missing_list_sort_exact_checksums", LIST_SORT_REQUIRED_EXACT_CHECKSUMS),',
            ")",
            "for reason, keys in exact_categories:",
            "missing_exact = sorted(key for key in keys if parsed.get(key) is None)",
            "if missing_exact:",
            'return (reason, missing_exact)',
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
            "kind, payload = validate_output(expectations, result.stdout)",
            "if kind != 'pass':",
            "print('PHASE1_BENCH_CHECK=fail')",
            "print(f'PHASE1_BENCH_CHECK_REASON={kind}')",
            "print(payload)",
            "return 1",
        ),
        (
            "print('PHASE1_BENCH_CHECK=pass')",
            "print(f'PHASE1_BENCH_EXPECTATIONS={expectations_file}')",
            "print(f'PHASE1_BENCH_SOURCE={phase1_bench}')",
            "print(f'PHASE1_BENCH_ZIG={zig}')",
            "return 0",
        ),
    ),
}

FORBIDDEN_FRAGMENTS = {
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py\n",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line_occurrences(lines: list[str], marker: str) -> int:
    return sum(1 for line in lines if line.strip() == marker)


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
    index = 0
    for line in section:
        if index == len(expected_lines):
            return True
        if line == expected_lines[index]:
            index += 1
    return index == len(expected_lines)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        lines = text.splitlines()
        for marker in markers:
            count = count_exact_line_occurrences(lines, marker)
            if count != 1:
                issues.append(f"{relative_path}:marker_count:{marker}:expected=1:actual={count}")

        for fragment in FORBIDDEN_FRAGMENTS.get(relative_path, ()):
            count = text.count(fragment)
            if count != 0:
                issues.append(f"{relative_path}:forbidden:{fragment}:actual={count}")

        stripped = [line.strip() for line in lines]
        for expected_block in EXPECTED_BLOCKS.get(relative_path, ()):
            first_line = expected_block[0]
            first_line_count = sum(1 for line in stripped if line == first_line)
            if first_line_count != 1:
                issues.append(f"{relative_path}:marker_count:{first_line}:expected=1:actual={first_line_count}")
                continue
            actual_section = extract_section(text, first_line)
            if not section_contains_expected_lines(actual_section, expected_block):
                issues.append(f"{relative_path}:assert_block:{first_line}:{actual_section!r}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path, markers in MARKERS.items():
        lines = list(markers)
        for block in EXPECTED_BLOCKS.get(relative_path, ()):
            lines.extend(block)
            lines.append("")
        write_text(root, relative_path, "\n".join(lines).rstrip("\n") + "\n")


def insert_after(root: Path, relative_path: str, first_line: str, anchor: str, inserted_lines: tuple[str, ...]) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    section = extract_section(text, first_line)
    anchor_index = section.index(anchor)
    updated_section = section[: anchor_index + 1] + list(inserted_lines) + section[anchor_index + 1 :]
    path.write_text(text.replace("\n".join(section), "\n".join(updated_section), 1), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-pass-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=base_sample")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-tuple-ordered-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        insert_after(
            root,
            BENCH_CHECKER_REL,
            "exact_categories = (",
            '("missing_bitmap_exact_checksums", BITMAP_REQUIRED_EXACT_CHECKSUMS),',
            ('("missing_placeholder_exact_checksums", PLACEHOLDER_REQUIRED_EXACT_CHECKSUMS),',),
        )
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=interleaved_tuple_entries")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-run-call-ordered-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        insert_after(
            root,
            BENCH_CHECKER_REL,
            "result = subprocess.run(",
            "cwd=str(root),",
            ("timeout=30,",),
        )
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=multiline_run_call_with_interleaved_kwarg")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-reordered-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        path = root / BENCH_CHECKER_REL
        text = path.read_text(encoding="utf-8")
        old = "\n".join(
            (
                "if kind != 'pass':",
                "print('PHASE1_BENCH_CHECK=fail')",
                "print(f'PHASE1_BENCH_CHECK_REASON={kind}')",
            )
        )
        new = "\n".join(
            (
                "print('PHASE1_BENCH_CHECK=fail')",
                "if kind != 'pass':",
                "print(f'PHASE1_BENCH_CHECK_REASON={kind}')",
            )
        )
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        issues = collect_issues(root)
        expected_prefix = f"{BENCH_CHECKER_REL}:assert_block:kind, payload = validate_output(expectations, result.stdout)"
        if len(issues) != 1 or not issues[0].startswith(expected_prefix):
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=reordered_validation_result_block_fail_closed")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-duplicate-anchor-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        path = root / BENCH_CHECKER_REL
        text = path.read_text(encoding="utf-8")
        duplicated_anchor = "\n".join(
            (
                "kind, payload = validate_output(expectations, result.stdout)",
                "kind, payload = validate_output(expectations, result.stdout)",
            )
        )
        path.write_text(
            text.replace("kind, payload = validate_output(expectations, result.stdout)", duplicated_anchor, 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        expected_issue = (
            f"{BENCH_CHECKER_REL}:marker_count:"
            "kind, payload = validate_output(expectations, result.stdout):expected=1:actual=2"
        )
        if issues != [expected_issue]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=duplicate_validation_result_anchor_fail_closed")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-closure-marker-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        path = root / PHASE1_CLOSURE_REL
        marker = "- `PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py`"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(marker, f"{marker}\n{marker}", 1), encoding="utf-8")
        issues = collect_issues(root)
        expected_issue = (
            f"{PHASE1_CLOSURE_REL}:marker_count:{marker}:expected=1:actual=2"
        )
        if issues != [expected_issue]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=duplicate_closure_marker_fail_closed")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-find-bit-guard-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        path = root / PHASE1_CLOSURE_REL
        marker = "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(marker, f"{marker}\n{marker}", 1), encoding="utf-8")
        issues = collect_issues(root)
        expected_issue = (
            f"{PHASE1_CLOSURE_REL}:marker_count:{marker}:expected=1:actual=2"
        )
        if issues != [expected_issue]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=duplicate_find_bit_bench_guard_marker_fail_closed")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-rbtree-guard-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        path = root / PHASE1_CLOSURE_REL
        marker = "- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(marker, f"{marker}\n{marker}", 1), encoding="utf-8")
        issues = collect_issues(root)
        expected_issue = (
            f"{PHASE1_CLOSURE_REL}:marker_count:{marker}:expected=1:actual=2"
        )
        if issues != [expected_issue]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=duplicate_rbtree_bench_guard_marker_fail_closed")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-find-bit-anchor-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        path = root / PHASE1_CLOSURE_REL
        marker = "- `PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(marker, f"{marker}\n{marker}", 1), encoding="utf-8")
        issues = collect_issues(root)
        expected_issue = (
            f"{PHASE1_CLOSURE_REL}:marker_count:{marker}:expected=1:actual=2"
        )
        if issues != [expected_issue]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=duplicate_find_bit_bench_anchor_marker_fail_closed")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-embedded-marker-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        path = root / PHASE1_CLOSURE_REL
        marker = "- `PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py`"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(marker, f"prefix {marker} suffix", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        expected_issue = (
            f"{PHASE1_CLOSURE_REL}:marker_count:{marker}:expected=1:actual=0"
        )
        if issues != [expected_issue]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=embedded_closure_marker_fail_closed")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-workflow-direct-run-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        path = root / WORKFLOW_REL
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text + "run: python3 scripts/zigux/check-phase1-bench.py\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        expected_issue = (
            f"{WORKFLOW_REL}:forbidden:"
            "run: python3 scripts/zigux/check-phase1-bench.py\n:actual=1"
        )
        if issues != [expected_issue]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=workflow_direct_run_fail_closed")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-workflow-bench-duplicate-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        path = root / WORKFLOW_REL
        marker = "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(marker, f"{marker}\n{marker}", 1), encoding="utf-8")
        issues = collect_issues(root)
        expected_issue = (
            f"{WORKFLOW_REL}:marker_count:{marker}:expected=1:actual=2"
        )
        if issues != [expected_issue]:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=duplicate_workflow_bench_run_marker_fail_closed")
            print(f"actual={issues!r}")
            return 1

    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=pass")
    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST_CASE_COUNT=12")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Override repository root")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in self-test")
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