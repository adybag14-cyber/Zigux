#!/usr/bin/env python3
"""Guard the current master Lane 16 bench success packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"

REQUIRED_FILES = (
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
)

MARKERS = {
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (),
}

EXPECTED_BLOCKS = {
    BENCH_CHECKER_REL: (
        (
            "kind, payload = validate_output(expectations, result.stdout)",
            'if kind != "pass":',
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
            "print(payload)",
            "return 1",
            'print("PHASE1_BENCH_CHECK=pass")',
            'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")',
            'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")',
            'print(f"PHASE1_BENCH_ZIG={zig}")',
            "return 0",
        ),
    ),
}

FORBIDDEN_FRAGMENTS = {
    BENCH_CHECKER_REL: (
        "PHASE1_BENCH_EXPECTATION_COUNT",
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
            if relative_path == WORKFLOW_REL:
                count = sum(1 for line in lines if line.strip() == marker)
            else:
                count = text.count(marker)
            if count != 1:
                issues.append(f"{relative_path}:marker_count:{marker}:expected=1:actual={count}")

        for fragment in FORBIDDEN_FRAGMENTS.get(relative_path, ()):
            count = text.count(fragment)
            if count != 0:
                issues.append(f"{relative_path}:forbidden:{fragment}:actual={count}")

        stripped_lines = [line.strip() for line in lines]
        for expected_block in EXPECTED_BLOCKS.get(relative_path, ()):
            first_line = expected_block[0]
            first_line_count = sum(1 for line in stripped_lines if line == first_line)
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


def build_sample_file(relative_path: str) -> str:
    lines: list[str] = []
    seen: set[str] = set()

    def append_line(line: str) -> None:
        if line in seen:
            return
        seen.add(line)
        lines.append(line)

    for block in EXPECTED_BLOCKS.get(relative_path, ()):
        for line in block:
            append_line(line)
        lines.append("")
    for marker in MARKERS[relative_path]:
        append_line(marker)
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


def mutate_append_forbidden(root: Path, relative_path: str, fragment: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + fragment + "\n", encoding="utf-8")


def mutate_block_remove_line(root: Path, relative_path: str, first_line: str, line_index: int) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_section = extract_section(text, first_line)
    trimmed = actual_section[:line_index] + actual_section[line_index + 1 :]
    path.write_text(text.replace("\n".join(actual_section), "\n".join(trimmed), 1), encoding="utf-8")
    return trimmed


def mutate_block_reorder(root: Path, relative_path: str, first_line: str, left_index: int, right_index: int) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_section = extract_section(text, first_line)
    updated = list(actual_section)
    updated[left_index], updated[right_index] = updated[right_index], updated[left_index]
    path.write_text(text.replace("\n".join(actual_section), "\n".join(updated), 1), encoding="utf-8")
    return updated


def expected_issue(relative_path: str, needle: str, operation: str, block: list[str] | None = None) -> str:
    if operation == "remove":
        return f"{relative_path}:marker_count:{needle}:expected=1:actual=0"
    if operation == "duplicate":
        return f"{relative_path}:marker_count:{needle}:expected=1:actual=2"
    if operation == "append":
        return f"{relative_path}:forbidden:{needle}:actual=1"
    assert block is not None
    return f"{relative_path}:assert_block:{needle}:{block!r}"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-success-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST=fail")
            print(f"actual={issues!r}")
            return 1

    cases: list[tuple[str, str, str, str, tuple[int, int] | int | None]] = []
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append((f"remove:{relative_path}:{marker}", relative_path, marker, "remove", None))
            cases.append((f"duplicate:{relative_path}:{marker}", relative_path, marker, "duplicate", None))
    for relative_path, fragments in FORBIDDEN_FRAGMENTS.items():
        for fragment in fragments:
            cases.append((f"append:{relative_path}:{fragment}", relative_path, fragment, "append", None))
    for relative_path, blocks in EXPECTED_BLOCKS.items():
        for block in blocks:
            first_line = block[0]
            for line_index in range(1, len(block)):
                cases.append(
                    (
                        f"remove_line:{relative_path}:{first_line}:{line_index}",
                        relative_path,
                        first_line,
                        "block_remove_line",
                        line_index,
                    )
                )
            cases.append(
                (
                    f"reorder_footer:{relative_path}:{first_line}",
                    relative_path,
                    first_line,
                    "block_reorder",
                    (7, 8),
                )
            )

    for label, relative_path, needle, operation, payload in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-success-packet-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            block: list[str] | None = None
            if operation == "remove":
                mutate_remove(root, relative_path, needle)
            elif operation == "duplicate":
                mutate_duplicate(root, relative_path, needle)
            elif operation == "append":
                mutate_append_forbidden(root, relative_path, needle)
            elif operation == "block_remove_line":
                assert isinstance(payload, int)
                block = mutate_block_remove_line(root, relative_path, needle, payload)
            else:
                assert isinstance(payload, tuple)
                block = mutate_block_reorder(root, relative_path, needle, payload[0], payload[1])
            issues = collect_issues(root)
            expected = expected_issue(relative_path, needle, "append" if operation == "append" else ("remove" if operation == "remove" else ("duplicate" if operation == "duplicate" else "assert_block")), block)
            if issues != [expected]:
                print("PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST=fail")
                print(f"case={label}")
                print(f"expected={expected}")
                print(f"actual={issues!r}")
                return 1

    print("PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
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
        print("PHASE1_BENCH_SUCCESS_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_SUCCESS_PACKET=pass")
    print(f"PHASE1_BENCH_SUCCESS_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_SUCCESS_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
