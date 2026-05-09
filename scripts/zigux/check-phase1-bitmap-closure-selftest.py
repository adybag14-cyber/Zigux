#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re
import tempfile


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
TARGET_REL = "scripts/zigux/validate-phase1-closure.py"

REQUIRED_BITMAP_CLOSURE_MARKERS = {
    "bitmap_final_partial_word": (
        "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW="
        "helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor "
        "so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it"
    ),
    "bitmap_linux_alias": (
        "PHASE1_BITMAP_LINUX_ALIAS_REVIEW="
        "helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest "
        "so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface"
    ),
}


def repo_root_from_arg(arg_root: str | None) -> Path:
    return Path(arg_root).resolve() if arg_root else DEFAULT_ROOT


def load_target_text(root: Path) -> str:
    return (root / TARGET_REL).read_text(encoding="utf-8")


def collect_issues(text: str) -> list[str]:
    issues: list[str] = []
    closure_markers_match = re.search(r"CLOSURE_MARKERS\s*=\s*\[(?P<body>.*?)\n\]", text, re.DOTALL)
    closure_markers_body = closure_markers_match.group("body") if closure_markers_match else ""
    for slug, marker in REQUIRED_BITMAP_CLOSURE_MARKERS.items():
        if marker not in closure_markers_body:
            issues.append(f"missing_marker:{slug}")
        expected_selftest_call = f'assert_missing_closure_marker(root, "{marker}")'
        if expected_selftest_call not in text:
            issues.append(f"missing_selftest:{slug}")
    return issues


def make_fixture_text() -> str:
    lines = [
        "CLOSURE_MARKERS = [",
    ]
    for marker in REQUIRED_BITMAP_CLOSURE_MARKERS.values():
        lines.append(f'    "{marker}",')
    lines.extend(
        [
            "]",
            "",
            "def assert_missing_closure_marker(root, marker):",
            "    return (root, marker)",
            "",
            "def run_self_test():",
        ]
    )
    for marker in REQUIRED_BITMAP_CLOSURE_MARKERS.values():
        lines.append(f'    assert_missing_closure_marker(root, "{marker}")')
    lines.append("")
    return "\n".join(lines)


def write_fixture(root: Path, text: str) -> None:
    path = root / TARGET_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bitmap_closure_selftest_") as tmpdir:
        root = Path(tmpdir)
        baseline = make_fixture_text()
        write_fixture(root, baseline)
        assert collect_issues(load_target_text(root)) == []
        cases += 1

        broken = baseline.replace(
            REQUIRED_BITMAP_CLOSURE_MARKERS["bitmap_final_partial_word"],
            "",
            1,
        )
        write_fixture(root, broken)
        assert collect_issues(load_target_text(root)) == [
            "missing_marker:bitmap_final_partial_word",
        ]
        cases += 1

        write_fixture(root, baseline)
        broken = baseline.replace(
            f'assert_missing_closure_marker(root, "{REQUIRED_BITMAP_CLOSURE_MARKERS["bitmap_final_partial_word"]}")',
            "",
            1,
        )
        write_fixture(root, broken)
        assert collect_issues(load_target_text(root)) == [
            "missing_selftest:bitmap_final_partial_word",
        ]
        cases += 1

        write_fixture(root, baseline)
        broken = baseline.replace(
            f'assert_missing_closure_marker(root, "{REQUIRED_BITMAP_CLOSURE_MARKERS["bitmap_linux_alias"]}")',
            "",
            1,
        )
        write_fixture(root, broken)
        assert collect_issues(load_target_text(root)) == [
            "missing_selftest:bitmap_linux_alias",
        ]
        cases += 1

    print("PHASE1_BITMAP_CLOSURE_SELFTEST_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_CLOSURE_SELFTEST_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Phase 1 bitmap closure markers stay covered by the closure validator self-test."
    )
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    target_path = root / TARGET_REL
    if not target_path.exists():
        print("PHASE1_BITMAP_CLOSURE_SELFTEST=fail")
        print(f"MISSING_TARGET={TARGET_REL}")
        return 1

    issues = collect_issues(load_target_text(root))
    if issues:
        print("PHASE1_BITMAP_CLOSURE_SELFTEST=fail")
        print("PHASE1_BITMAP_CLOSURE_SELFTEST_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_BITMAP_CLOSURE_SELFTEST_ISSUES_END")
        return 1

    print("PHASE1_BITMAP_CLOSURE_SELFTEST=pass")
    print(f"PHASE1_BITMAP_CLOSURE_SELFTEST_MARKER_COUNT={len(REQUIRED_BITMAP_CLOSURE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
