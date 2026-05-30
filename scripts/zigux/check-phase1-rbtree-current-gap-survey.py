#!/usr/bin/env python3
"""Validate the Phase 1 rbtree current-gap survey against live helper text."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/rbtree.zig")
SURVEY_REL = Path("Documentation/zigux/phase1-rbtree-current-gap-survey.md")

MISSING_ALIAS_MARKERS = [
    "pub fn rb_link_node(",
    "pub fn rb_insert_color(node: *Node, root: *Root) void {",
    "pub fn rb_erase(node: *Node, root: *Root) void {",
    "pub fn rb_erase_init(node: *Node, root: *Root) void {",
]

REQUIRED_HELPER_MARKERS = [
    "pub fn rb_add(node: *Node, root: *Root, less: LessFn) void {",
    "pub fn rb_find_add(node: *Node, root: *Root, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_replace_node(victim: *Node, new: *Node, root: *Root) void {",
    "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
    "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
    'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
    'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
]

REQUIRED_SURVEY_MARKERS = [
    "PHASE1_RBTREE_CURRENT_SURVEY_STATUS=helper_gap_open",
    "PHASE1_RBTREE_CURRENT_HELPER_BLOB=b8cc3d811028922be412f40cfddfd8da82ea6d8c",
    "PHASE1_RBTREE_MISSING_LOW_LEVEL_ALIASES=rb_link_node,rb_insert_color,rb_erase,rb_erase_init",
    'PHASE1_RBTREE_MISSING_TEST_ANCHOR=test "rbtree low-level Linux-style aliases mirror node-state helpers"',
    "PHASE1_RBTREE_EXISTING_HELPER_ANCHORS=ordered_linux_style_aliases,cached_root_aliases,cached_root_insert_miss,leftmost_sync,singleton_erase,replacement,detach,reseed",
    "PHASE1_RBTREE_NEXT_BOUNDED_STEP=apply the already-scoped non-cached low-level alias helper patch for rb_link_node, rb_insert_color, rb_erase, and rb_erase_init plus the direct low-level alias test once a trustworthy patch-capable current-head write path is available; otherwise keep this survey and its checker aligned with current helper reality",
]


def repo_root(raw_root: str | None) -> Path:
    return Path(raw_root).resolve() if raw_root else DEFAULT_ROOT


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    helper_path = root / HELPER_REL
    survey_path = root / SURVEY_REL

    if not helper_path.exists():
        failures.append(f"missing:{HELPER_REL}")
        helper_text = ""
    else:
        helper_text = helper_path.read_text(encoding="utf-8")

    if not survey_path.exists():
        failures.append(f"missing:{SURVEY_REL}")
        survey_text = ""
    else:
        survey_text = survey_path.read_text(encoding="utf-8")

    for marker in REQUIRED_HELPER_MARKERS:
        if helper_text.count(marker) != 1:
            failures.append(f"helper-marker-count:{marker}:{helper_text.count(marker)}")

    for marker in MISSING_ALIAS_MARKERS:
        if marker in helper_text:
            failures.append(f"missing-alias-now-present:{marker}")

    for marker in REQUIRED_SURVEY_MARKERS:
        if survey_text.count(marker) != 1:
            failures.append(f"survey-marker-count:{marker}:{survey_text.count(marker)}")

    return failures


def write_sample_repo(root: Path) -> None:
    helper = root / HELPER_REL
    survey = root / SURVEY_REL
    helper.parent.mkdir(parents=True, exist_ok=True)
    survey.parent.mkdir(parents=True, exist_ok=True)
    helper.write_text("\n".join(REQUIRED_HELPER_MARKERS) + "\n", encoding="utf-8")
    survey.write_text("\n".join(REQUIRED_SURVEY_MARKERS) + "\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    mutation_specs: list[tuple[str, Path, str]] = []
    mutation_specs.extend((f"helper-required-{idx}", HELPER_REL, marker) for idx, marker in enumerate(REQUIRED_HELPER_MARKERS))
    mutation_specs.extend((f"survey-required-{idx}", SURVEY_REL, marker) for idx, marker in enumerate(REQUIRED_SURVEY_MARKERS))

    for name, rel_path, marker in mutation_specs:
        with tempfile.TemporaryDirectory(prefix=f"phase1-rbtree-gap-{name}-") as tmpdir:
            root = Path(tmpdir)
            write_sample_repo(root)
            path = root / rel_path
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")
            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure_but_passed")
                return 1
            case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-rbtree-gap-alias-present-") as tmpdir:
        root = Path(tmpdir)
        write_sample_repo(root)
        helper = root / HELPER_REL
        helper.write_text(helper.read_text(encoding="utf-8") + MISSING_ALIAS_MARKERS[0] + "\n", encoding="utf-8")
        failures = collect_failures(root)
        if not failures:
            print("self-test:alias-present:expected_failure_but_passed")
            return 1
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-rbtree-gap-missing-file-") as tmpdir:
        root = Path(tmpdir)
        write_sample_repo(root)
        shutil.rmtree(root / "tools")
        failures = collect_failures(root)
        if not failures:
            print("self-test:missing-helper:expected_failure_but_passed")
            return 1
        case_count += 1

    print(f"self-test:ok:{case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in negative coverage tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("phase1-rbtree-current-gap-survey:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
