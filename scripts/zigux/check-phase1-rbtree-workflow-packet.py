#!/usr/bin/env python3
"""Guard the current Phase 1 rbtree workflow packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
RBTREE_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")
RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")

REQUIRED_FILES = (
    WORKFLOW_REL,
    CLOSURE_REL,
    LANE_NOTE_REL,
    SCRIPTS_README_REL,
    RBTREE_CHECKER_REL,
    RBTREE_HELPER_REL,
)

REQUIRED_WORKFLOW_LINES = (
    "      - name: Self-test current Phase 1 bitmap direct-anchor checker",
    "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    "      - name: Check current Phase 1 bitmap direct-anchor packet",
    "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    "      - name: Self-test current Phase 1 rbtree review checker",
    "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    "      - name: Check current Phase 1 rbtree review packet",
    "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    "      - name: Self-test current Phase 1 route summary checker",
    "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "      - name: Check current Phase 1 route summary packet",
    "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
)

REQUIRED_CLOSURE_MARKERS = (
    "- `PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`",
    "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.",
)

REQUIRED_LANE_NOTE_MARKERS = (
    "- `tools/lib/rbtree.zig` now keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed coverage helper-local while the committed fixture still owns exact `find()`, `findFirst()`, `nextMatch()`, and `matchIterator()` duplicate-search fields and the shared host-tools smoke route already keeps duplicate-range iteration plus the parked `cached_leftmost_return_serials` witness explicit. The dedicated `low_level_alias_anchor` and `cached_root_alias_anchor` entries in `zigux/tests/fixtures/phase1_helper_manifest.json` keep both Linux-style alias proofs named explicitly inside that same helper-local packet instead of leaving either alias path implied only by the broader helper test list. Until another committed cached-root replay field lands, leave the remaining cached-root anchors helper-local and do not batch a second widening into the same reopen step.",
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)

REQUIRED_RBTREE_CHECKER_MARKERS = (
    "\"\"\"Guard the Phase 1 rbtree review packet against helper, fixture, smoke, and lane drift.\"\"\"",
    "print(\"phase1-rbtree-review-packet:ok\")",
    "print(f\"self-test:ok:{case_count}\")",
)

REQUIRED_RBTREE_HELPER_MARKERS = (
    'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers" {',
    'test "rbtree nextMatch walks the duplicate range in order" {',
    'test "rbtree cached root keeps the leftmost pointer in sync" {',
    'test "rbtree cached-root Linux-style aliases mirror the primary helpers" {',
    'test "rbtree eraseInitCached clears singleton cached roots before reseed" {',
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_count(text: str, label: str, needle: str, expected: int = 1) -> list[str]:
    actual = text.count(needle)
    return [] if actual == expected else [f"{label}:expected={expected}:actual={actual}"]


def require_exact_line(text: str, label: str, needle: str, expected: int = 1) -> list[str]:
    actual = sum(1 for line in text.splitlines() if line == needle)
    return [] if actual == expected else [f"{label}:expected={expected}:actual={actual}"]


def collect_workflow_failures(text: str) -> list[str]:
    failures: list[str] = []
    lines = text.splitlines()
    positions: list[int] = []
    for idx, line in enumerate(REQUIRED_WORKFLOW_LINES):
        failures.extend(require_exact_line(text, f"workflow_line_{idx}", line))
        positions.append(next((line_idx for line_idx, current in enumerate(lines) if current == line), -1))
    if failures:
        return failures
    if positions != sorted(positions):
        failures.append("workflow_order:expected=ascending:actual=drifted")
    return failures


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    failures.extend(collect_workflow_failures(workflow_text))

    closure_text = load_text(root, CLOSURE_REL)
    for idx, marker in enumerate(REQUIRED_CLOSURE_MARKERS):
        failures.extend(require_exact_count(closure_text, f"closure_marker_{idx}", marker))

    lane_note_text = load_text(root, LANE_NOTE_REL)
    for idx, marker in enumerate(REQUIRED_LANE_NOTE_MARKERS):
        failures.extend(require_exact_count(lane_note_text, f"lane_note_marker_{idx}", marker))

    scripts_readme_text = load_text(root, SCRIPTS_README_REL)
    for idx, marker in enumerate(REQUIRED_SCRIPTS_README_MARKERS):
        failures.extend(require_exact_count(scripts_readme_text, f"scripts_readme_marker_{idx}", marker))

    rbtree_checker_text = load_text(root, RBTREE_CHECKER_REL)
    for idx, marker in enumerate(REQUIRED_RBTREE_CHECKER_MARKERS):
        failures.extend(require_exact_count(rbtree_checker_text, f"rbtree_checker_marker_{idx}", marker))

    rbtree_helper_text = load_text(root, RBTREE_HELPER_REL)
    for idx, marker in enumerate(REQUIRED_RBTREE_HELPER_MARKERS):
        failures.extend(require_exact_count(rbtree_helper_text, f"rbtree_helper_marker_{idx}", marker))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, WORKFLOW_REL, "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(root, CLOSURE_REL, "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(root, LANE_NOTE_REL, "\n".join(REQUIRED_LANE_NOTE_MARKERS) + "\n")
    write_text(root, SCRIPTS_README_REL, "\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root, RBTREE_CHECKER_REL, "\n".join(REQUIRED_RBTREE_CHECKER_MARKERS) + "\n")
    write_text(root, RBTREE_HELPER_REL, "\n".join(REQUIRED_RBTREE_HELPER_MARKERS) + "\n")


def write_sample_root(root: Path) -> None:
    build_sample_repo(root)


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("baseline", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", lambda root, relative_path=relative_path: (root / relative_path).unlink()))
    for marker in REQUIRED_WORKFLOW_LINES:
        cases.append((f"missing_workflow:{marker}", lambda root, marker=marker: remove_marker(root, WORKFLOW_REL, marker)))
        cases.append((f"duplicate_workflow:{marker}", lambda root, marker=marker: duplicate_marker(root, WORKFLOW_REL, marker)))
    for marker in REQUIRED_CLOSURE_MARKERS:
        cases.append((f"missing_closure:{marker}", lambda root, marker=marker: remove_marker(root, CLOSURE_REL, marker)))
    for marker in REQUIRED_LANE_NOTE_MARKERS:
        cases.append((f"missing_lane_note:{marker}", lambda root, marker=marker: remove_marker(root, LANE_NOTE_REL, marker)))
    for marker in REQUIRED_SCRIPTS_README_MARKERS:
        cases.append((f"missing_scripts_readme:{marker}", lambda root, marker=marker: remove_marker(root, SCRIPTS_README_REL, marker)))
    for marker in REQUIRED_RBTREE_CHECKER_MARKERS:
        cases.append((f"missing_rbtree_checker:{marker}", lambda root, marker=marker: remove_marker(root, RBTREE_CHECKER_REL, marker)))
    for marker in REQUIRED_RBTREE_HELPER_MARKERS:
        cases.append((f"missing_rbtree_helper:{marker}", lambda root, marker=marker: remove_marker(root, RBTREE_HELPER_REL, marker)))

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-rbtree-workflow-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_RBTREE_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_RBTREE_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run synthetic self-tests")
    parser.add_argument("--write-sample-root", help="materialize a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_RBTREE_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_RBTREE_WORKFLOW_PACKET=pass")
    print(f"PHASE1_RBTREE_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_RBTREE_WORKFLOW_PACKET_REQUIRED_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
