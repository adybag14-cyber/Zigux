#!/usr/bin/env python3
"""Guard the Lane 03 bootstrap preflight sequence in the workflow."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"

STEP_HEADING_SETUP = "- name: Setup pinned Zig toolchain"
STEP_HEADING_COMPILE = "- name: Compile current scripts"
SETUP_SENTINEL_LINE = 'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"'
COMPILE_SENTINEL_LINE = 'python3 -m py_compile "${scripts[@]}"'

ORDERED_MARKERS = (
    STEP_HEADING_SETUP,
    SETUP_SENTINEL_LINE,
    STEP_HEADING_COMPILE,
    COMPILE_SENTINEL_LINE,
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
)

EXPECTED_SELF_TEST_CASE_COUNT = 10


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = next(index for index, line in enumerate(lines) if line.strip() == first)
    second_index = next(index for index, line in enumerate(lines) if line.strip() == second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def find_exact_line_indices(text: str, markers: tuple[str, ...]) -> list[int]:
    indices: list[int] = []
    lines = text.splitlines()
    for marker in markers:
        matches = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(matches) != 1:
            return []
        indices.append(matches[0])
    return indices


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)

    for marker in ORDERED_MARKERS:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_PREFLIGHT_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_PREFLIGHT_MARKER", f"{marker}:count={count}"))

    if not issues:
        indices = find_exact_line_indices(workflow_text, ORDERED_MARKERS)
        if indices != sorted(indices):
            issues.append(("OUT_OF_ORDER_PREFLIGHT_MARKER", " -> ".join(ORDERED_MARKERS)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                f"      {STEP_HEADING_SETUP}",
                "        run: |",
                "          set -euxo pipefail",
                f"          {SETUP_SENTINEL_LINE}",
                "          if try_local_archive; then",
                "            download_success=1",
                "          fi",
                f"      {STEP_HEADING_COMPILE}",
                "        run: |",
                "          set -euxo pipefail",
                f"          {COMPILE_SENTINEL_LINE}",
                "      - name: Self-test current Zig toolchain checker",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "      - name: Check current Zig toolchain policy packet",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
                "      - name: Check current pinned Zig archive packet",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
                "      - name: Run current Phase 2 toolchain make route",
                "        run: make -C zigux phase2-toolchain",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_preflight_sequence_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), STEP_HEADING_SETUP))
        assert ("MISSING_PREFLIGHT_MARKER", STEP_HEADING_SETUP) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), STEP_HEADING_COMPILE))
        assert ("DUPLICATE_PREFLIGHT_MARKER", f"{STEP_HEADING_COMPILE}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), SETUP_SENTINEL_LINE))
        assert ("MISSING_PREFLIGHT_MARKER", SETUP_SENTINEL_LINE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), COMPILE_SENTINEL_LINE))
        assert ("DUPLICATE_PREFLIGHT_MARKER", f"{COMPILE_SENTINEL_LINE}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            swap_exact_lines(read_text(root, WORKFLOW), STEP_HEADING_SETUP, STEP_HEADING_COMPILE),
        )
        assert any(code == "OUT_OF_ORDER_PREFLIGHT_MARKER" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            swap_exact_lines(
                read_text(root, WORKFLOW),
                "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
                "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
            ),
        )
        assert any(code == "OUT_OF_ORDER_PREFLIGHT_MARKER" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                "run: make -C zigux phase2-toolchain",
                "run: make -C zigux phase2-tools",
            ),
        )
        assert ("MISSING_PREFLIGHT_MARKER", "run: make -C zigux phase2-toolchain") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
            ),
        )
        assert (
            "DUPLICATE_PREFLIGHT_MARKER",
            "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only:count=2",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), COMPILE_SENTINEL_LINE, "python3 -m py_compile"))
        assert ("MISSING_PREFLIGHT_MARKER", COMPILE_SENTINEL_LINE) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT, checks
    print("PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 03 bootstrap workflow keeps the preflight setup, compile, and toolchain sequence aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        print("PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE_SAMPLE_ROOT=pass")
        print(f"PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE=pass")
    print(f"PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE_MARKER_COUNT={len(ORDERED_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE_WORKFLOW_PATH={args.root.resolve() / WORKFLOW}")
    print(f"PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE_SETUP_HEADING={STEP_HEADING_SETUP}")
    print(f"PHASE2_BOOTSTRAP_PREFLIGHT_SEQUENCE_COMPILE_HEADING={STEP_HEADING_COMPILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
