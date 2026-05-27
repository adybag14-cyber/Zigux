#!/usr/bin/env python3
"""Guard the current Phase 1 delegated review-family workflow packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
BITMAP_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")
RBTREE_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    WORKFLOW_REL,
    VALIDATOR_REL,
    CLOSURE_REL,
    LANE_NOTE_REL,
    BITMAP_CHECKER_REL,
    RBTREE_CHECKER_REL,
    MANIFEST_REL,
)

WORKFLOW_REQUIRED_MARKERS = (
    "      - name: Self-test current Phase 1 shared reminder checker\n",
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
    "      - name: Check current Phase 1 shared reminder packet\n",
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
    "      - name: Self-test current Phase 1 closure validator\n",
    "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
    "      - name: Check current Phase 1 closure packet\n",
    "        run: python3 scripts/zigux/validate-phase1-closure.py\n",
)

WORKFLOW_REQUIRED_BLOCK = (
    "      - name: Self-test current Phase 1 shared reminder checker\n"
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n"
    "\n"
    "      - name: Check current Phase 1 shared reminder packet\n"
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n"
    "\n"
    "      - name: Self-test current Phase 1 closure validator\n"
    "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n"
    "\n"
    "      - name: Check current Phase 1 closure packet\n"
    "        run: python3 scripts/zigux/validate-phase1-closure.py\n"
)

WORKFLOW_FORBIDDEN_MARKERS = (
    "check-phase1-bitmap-direct-anchors.py --self-test",
    "check-phase1-bitmap-direct-anchors.py\n",
    "check-phase1-rbtree-review-packet.py --self-test",
    "check-phase1-rbtree-review-packet.py\n",
    "Self-test current Phase 1 bitmap direct-anchor checker",
    "Check current Phase 1 bitmap direct-anchor packet",
    "Self-test current Phase 1 rbtree review checker",
    "Check current Phase 1 rbtree review packet",
)

VALIDATOR_REQUIRED_MARKERS = (
    'BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")',
    'RBTREE_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")',
    "    BITMAP_DIRECT_ANCHOR_CHECKER_REL,\n",
    "    RBTREE_REVIEW_CHECKER_REL,\n",
    '    "bitmap_direct_review": "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet',
    '    "rbtree_review_guard": "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors',
)

VALIDATOR_REQUIRED_SUBSTRINGS = (
    "phase1-bitmap-direct-anchors",
    "phase1-rbtree-review-packet",
)

CLOSURE_REQUIRED_MARKERS = (
    "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet",
    "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`",
    "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
)

LANE_REQUIRED_MARKERS = (
    "current authenticated reads also recover `scripts/zigux/check-phase1-bitmap-direct-anchors.py`, `scripts/zigux/check-phase1-find-bit-review-packet.py`, `scripts/zigux/check-phase1-find-bit-bench-anchors.py`, and `scripts/zigux/check-phase1-rbtree-review-packet.py`, so bitmap, find_bit, and rbtree follow-through should stay inside those helper-local guards instead of being retold as shared reminder drift or string-packet work",
    "`PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
    "`PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
)

EXPECTED_MANIFEST_BITMAP_KEYS = (
    "review_packet_summary",
    "next_safe_step_note",
    "copy_raw_alias_anchor",
    "linux_alias_anchor",
)

EXPECTED_MANIFEST_RBTREE_KEYS = (
    "review_packet_summary",
    "next_safe_step_note",
    "cached_root_alias_anchor",
    "cached_leftmost_fixture_keys",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected_once:actual={count}"]


def require_absent(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 0 else [f"{label}:expected_absent:actual={count}"]


def require_present(text: str, label: str, marker: str) -> list[str]:
    return [] if marker in text else [f"{label}:missing"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    validator_text = load_text(root, VALIDATOR_REL)
    closure_text = load_text(root, CLOSURE_REL)
    lane_text = load_text(root, LANE_NOTE_REL)
    manifest = json.loads(load_text(root, MANIFEST_REL))

    for marker in WORKFLOW_REQUIRED_MARKERS:
        failures.extend(require_once(workflow_text, f"workflow:{marker.strip()}", marker))
    failures.extend(require_once(workflow_text, "workflow:delegated_block", WORKFLOW_REQUIRED_BLOCK))
    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        failures.extend(require_absent(workflow_text, f"workflow:{marker}", marker))

    for marker in VALIDATOR_REQUIRED_MARKERS:
        failures.extend(require_once(validator_text, f"validator:{marker}", marker))
    for marker in VALIDATOR_REQUIRED_SUBSTRINGS:
        failures.extend(require_present(validator_text, f"validator:{marker}", marker))

    for marker in CLOSURE_REQUIRED_MARKERS:
        failures.extend(require_once(closure_text, f"closure:{marker[:64]}", marker))

    for marker in LANE_REQUIRED_MARKERS:
        failures.extend(require_once(lane_text, f"lane:{marker[:64]}", marker))

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["manifest:review_anchors:expected_dict"]

    bitmap_packet = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_packet, dict):
        failures.append("manifest:tools/lib/bitmap.zig:expected_dict")
    else:
        for key in EXPECTED_MANIFEST_BITMAP_KEYS:
            if key not in bitmap_packet:
                failures.append(f"manifest:tools/lib/bitmap.zig:{key}:missing")

    rbtree_packet = review_anchors.get("tools/lib/rbtree.zig")
    if not isinstance(rbtree_packet, dict):
        failures.append("manifest:tools/lib/rbtree.zig:expected_dict")
    else:
        for key in EXPECTED_MANIFEST_RBTREE_KEYS:
            if key not in rbtree_packet:
                failures.append(f"manifest:tools/lib/rbtree.zig:{key}:missing")

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/bitmap.zig": {
                        "review_packet_summary": "bitmap summary",
                        "next_safe_step_note": "bitmap next step",
                        "copy_raw_alias_anchor": "bitmap raw alias",
                        "linux_alias_anchor": "bitmap alias",
                    },
                    "tools/lib/rbtree.zig": {
                        "review_packet_summary": "rbtree summary",
                        "next_safe_step_note": "rbtree next step",
                        "cached_root_alias_anchor": "rbtree alias",
                        "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
                    },
                }
            },
            indent=2,
        )
        + "\n"
    )


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW_REL,
        "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n"
        + WORKFLOW_REQUIRED_BLOCK,
    )
    write_text(root, VALIDATOR_REL, "\n".join(VALIDATOR_REQUIRED_MARKERS) + "\n")
    write_text(root, CLOSURE_REL, "\n".join(CLOSURE_REQUIRED_MARKERS) + "\n")
    write_text(root, LANE_NOTE_REL, "\n".join(LANE_REQUIRED_MARKERS) + "\n")
    write_text(root, BITMAP_CHECKER_REL, "# bitmap checker\n")
    write_text(root, RBTREE_CHECKER_REL, "# rbtree checker\n")
    write_text(root, MANIFEST_REL, sample_manifest())


def mutate_remove(root: Path, relative_path: Path, needle: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(needle, "", 1), encoding="utf-8")


def mutate_append(root: Path, relative_path: Path, line: str) -> None:
    path = root / relative_path
    path.write_text(path.read_text(encoding="utf-8") + line, encoding="utf-8")


def mutate_manifest_delete(root: Path, helper: str, key: str) -> None:
    path = root / MANIFEST_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["review_anchors"][helper][key]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_closure_step", lambda root: mutate_remove(root, WORKFLOW_REL, "      - name: Check current Phase 1 closure packet\n")),
        ("missing_closure_run", lambda root: mutate_remove(root, WORKFLOW_REL, "        run: python3 scripts/zigux/validate-phase1-closure.py\n")),
        ("forbidden_bitmap_step", lambda root: mutate_append(root, WORKFLOW_REL, "      - name: Self-test current Phase 1 bitmap direct-anchor checker\n")),
        ("forbidden_rbtree_run", lambda root: mutate_append(root, WORKFLOW_REL, "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py\n")),
        ("missing_validator_bitmap_constant", lambda root: mutate_remove(root, VALIDATOR_REL, 'BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")')),
        ("missing_validator_rbtree_constant", lambda root: mutate_remove(root, VALIDATOR_REL, 'RBTREE_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-rbtree-review-packet.py")')),
        ("missing_closure_bitmap_marker", lambda root: mutate_remove(root, CLOSURE_REL, CLOSURE_REQUIRED_MARKERS[0])),
        ("missing_lane_rbtree_marker", lambda root: mutate_remove(root, LANE_NOTE_REL, LANE_REQUIRED_MARKERS[1])),
        ("missing_manifest_bitmap_key", lambda root: mutate_manifest_delete(root, "tools/lib/bitmap.zig", "copy_raw_alias_anchor")),
        ("missing_manifest_rbtree_key", lambda root: mutate_manifest_delete(root, "tools/lib/rbtree.zig", "cached_root_alias_anchor")),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-review-family-workflow-") as tmp:
            root = Path(tmp)
            build_sample_root(root)
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

    print("PHASE1_REVIEW_FAMILY_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_REVIEW_FAMILY_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", help="write a passing sample root")
    args = parser.parse_args()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_REVIEW_FAMILY_WORKFLOW_PACKET=pass")
    print("PHASE1_REVIEW_FAMILY_WORKFLOW_PACKET_MODE=delegated-current-master")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
