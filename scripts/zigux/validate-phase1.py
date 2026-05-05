#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

REQUIRED_FILES = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/string.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "zigux/tests/fixtures/phase1_helpers.json",
]

REQUIRED_LEDGER_MARKERS = [
    "feat(tools/lib): start phase-1 helper ports",
    "test(zigux): add phase-1 helper harness and workflow gate",
    "feat(tools/lib): expand phase-1 helper batch",
    "test(zigux): add phase-1 golden parity fixtures and artifact diff gate",
    "feat(tools/lib): complete bounded phase-1 helper coverage",
]

REQUIRED_WORKFLOW_MARKERS = [
    "tools/lib/*.zig",
    "python3 scripts/zigux/validate-phase1.py",
    "python3 scripts/zigux/check-phase1-parity.py",
    "zig build test --build-file zigux/tests/build.zig",
]

REQUIRED_TEST_MARKERS = [
    '@import("argv_split")',
    '@import("bitmap")',
    '@import("cmdline")',
    '@import("ctype")',
    '@import("find_bit")',
    '@import("hweight")',
    '@import("list_sort")',
    '@import("slab")',
    '@import("str_error_r")',
    '@import("string")',
    '@import("vsprintf")',
    '@import("zalloc")',
    '@import("rbtree")',
    '@embedFile("fixtures/phase1_helpers.json")',
]


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def collect_exact_count_markers(text: str, label: str, markers: list[str]) -> list[str]:
    mismatches: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            mismatches.append(f"{label}:{marker}:expected=1:actual={count}")
    return mismatches


def collect_missing_markers(root: Path) -> list[str]:
    ledger = (root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    test_root = (root / "zigux" / "tests" / "phase1_helpers.zig").read_text(encoding="utf-8")

    missing_markers: list[str] = []
    for marker in REQUIRED_LEDGER_MARKERS:
        if marker not in ledger:
            missing_markers.append(f"ledger:{marker}")

    missing_markers.extend(collect_exact_count_markers(workflow, "workflow", REQUIRED_WORKFLOW_MARKERS))
    missing_markers.extend(collect_exact_count_markers(test_root, "test", REQUIRED_TEST_MARKERS))
    return missing_markers


def make_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")

    workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text("\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n", encoding="utf-8")

    ledger_path = tmp_root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text("\n".join(REQUIRED_LEDGER_MARKERS) + "\n", encoding="utf-8")

    test_path = tmp_root / "zigux" / "tests" / "phase1_helpers.zig"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text("\n".join(REQUIRED_TEST_MARKERS) + "\n", encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_fixture_root(tmp_root)

        assert collect_missing_files(tmp_root) == []
        assert collect_missing_markers(tmp_root) == []

        missing_file = "tools/lib/bitmap.zig"
        (tmp_root / missing_file).unlink()
        assert collect_missing_files(tmp_root) == [missing_file]
        make_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_path.write_text("tools/lib/*.zig\npython3 scripts/zigux/validate-phase1.py\n", encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert "workflow:python3 scripts/zigux/check-phase1-parity.py:expected=1:actual=0" in missing_markers
        assert "workflow:zig build test --build-file zigux/tests/build.zig:expected=1:actual=0" in missing_markers
        make_fixture_root(tmp_root)

        workflow_path.write_text(
            "\n".join(REQUIRED_WORKFLOW_MARKERS + [REQUIRED_WORKFLOW_MARKERS[2]]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "workflow:python3 scripts/zigux/check-phase1-parity.py:expected=1:actual=2" in missing_markers
        make_fixture_root(tmp_root)

        test_path = tmp_root / "zigux" / "tests" / "phase1_helpers.zig"
        test_path.write_text(
            "\n".join(REQUIRED_TEST_MARKERS + [REQUIRED_TEST_MARKERS[4]]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert 'test:@import("find_bit"):expected=1:actual=2' in missing_markers

    print("PHASE1_VALIDATION_SELF_TEST=pass")
    print("PHASE1_VALIDATION_SELF_TEST_CASE_COUNT=5")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 helper packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = collect_missing_files(ROOT)
    if missing:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_FILES_END")
        return 1

    missing_markers = collect_missing_markers(ROOT)
    if missing_markers:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE1_MARKERS_END")
        return 1

    print("PHASE1_VALIDATION=pass")
    print(f"PHASE1_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_REQUIRED_MARKER_COUNT={len(REQUIRED_LEDGER_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_TEST_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
