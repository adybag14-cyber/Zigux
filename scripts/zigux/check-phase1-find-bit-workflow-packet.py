#!/usr/bin/env python3
"""Guard the current Phase 1 find_bit workflow packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIND_BIT_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")
FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")

REQUIRED_FILES = (
    WORKFLOW_REL,
    CLOSURE_REL,
    LANE_NOTE_REL,
    MANIFEST_REL,
    FIND_BIT_CHECKER_REL,
    FIND_BIT_HELPER_REL,
)

REQUIRED_WORKFLOW_LINES = (
    "      - name: Self-test current Phase 1 string review checker",
    "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "      - name: Check current Phase 1 string review packet",
    "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "      - name: Self-test current Phase 1 find-bit review checker",
    "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    "      - name: Check current Phase 1 find-bit review packet",
    "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    "      - name: Self-test current Phase 1 bitmap direct-anchor checker",
    "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    "      - name: Check current Phase 1 bitmap direct-anchor packet",
    "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
)

REQUIRED_CLOSURE_MARKERS = (
    "- `PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts.",
)

REQUIRED_LANE_NOTE_MARKERS = (
    "- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's `helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate shared replay family",
    "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, plus the public, Linux-style, and underscore andnot coverage including the shipped findFirstAndNotBit(), findNextAndNotBit(), find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`",
    "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
)

REQUIRED_MANIFEST_MARKERS = (
    '"tools/lib/find_bit.zig": {',
    '"same_word_start_masks": "test \\"single-word next scans honor start masks\\""',
    '"tail_word_inclusive_boundary_anchor": "test \\"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\\""',
    '"single_word_tail_inclusive_boundary_anchor": "test \\"single-word tail windows keep the last in-range next matches reachable from an inclusive start\\""',
    '"andnot_scan_entrypoint_contract": "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording."',
    '"tail_word_set_skip_anchor": "test \\"tail-word next set scans skip earlier in-range matches before clamping\\""',
    '"tail_word_skip_anchor": "test \\"tail-word next zero and shared scans skip earlier in-range matches before clamping\\""',
    '"review_packet_summary": "the committed Phase 1 fixture still owns the live cross-word find_bit replay through `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, and `last`, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master"',
    '"next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed shared replay drift in the live `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, or `last` fixture keys; do not reopen older saved validator cues or neighboring helper families."',
)

REQUIRED_FIND_BIT_CHECKER_MARKERS = (
    '"""Guard the Phase 1 find_bit review packet against helper, fixture, smoke, and lane drift."""',
    'print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass")',
    'print("PHASE1_FIND_BIT_REVIEW_PACKET=pass")',
)

REQUIRED_FIND_BIT_HELPER_MARKERS = (
    'test "find first and next set bits across words, with andnot gaps explicit"',
    'test "clump8 past-end scans return without reading bitmap words"',
    'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
    'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    'test "Linux-style aliases mirror the primary find helpers, including andnot"',
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

    manifest_text = load_text(root, MANIFEST_REL)
    for idx, marker in enumerate(REQUIRED_MANIFEST_MARKERS):
        failures.extend(require_exact_count(manifest_text, f"manifest_marker_{idx}", marker))

    checker_text = load_text(root, FIND_BIT_CHECKER_REL)
    for idx, marker in enumerate(REQUIRED_FIND_BIT_CHECKER_MARKERS):
        failures.extend(require_exact_count(checker_text, f"find_bit_checker_marker_{idx}", marker))

    helper_text = load_text(root, FIND_BIT_HELPER_REL)
    for idx, marker in enumerate(REQUIRED_FIND_BIT_HELPER_MARKERS):
        failures.extend(require_exact_count(helper_text, f"find_bit_helper_marker_{idx}", marker))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, WORKFLOW_REL, "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(root, CLOSURE_REL, "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(root, LANE_NOTE_REL, "\n".join(REQUIRED_LANE_NOTE_MARKERS) + "\n")
    write_text(root, MANIFEST_REL, "\n".join(REQUIRED_MANIFEST_MARKERS) + "\n")
    write_text(root, FIND_BIT_CHECKER_REL, "\n".join(REQUIRED_FIND_BIT_CHECKER_MARKERS) + "\n")
    write_text(root, FIND_BIT_HELPER_REL, "\n".join(REQUIRED_FIND_BIT_HELPER_MARKERS) + "\n")


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
    for marker in REQUIRED_MANIFEST_MARKERS:
        cases.append((f"missing_manifest:{marker}", lambda root, marker=marker: remove_marker(root, MANIFEST_REL, marker)))
    for marker in REQUIRED_FIND_BIT_CHECKER_MARKERS:
        cases.append((f"missing_find_bit_checker:{marker}", lambda root, marker=marker: remove_marker(root, FIND_BIT_CHECKER_REL, marker)))
    for marker in REQUIRED_FIND_BIT_HELPER_MARKERS:
        cases.append((f"missing_find_bit_helper:{marker}", lambda root, marker=marker: remove_marker(root, FIND_BIT_HELPER_REL, marker)))

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-find-bit-workflow-packet-") as tmpdir:
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

    print("PHASE1_FIND_BIT_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
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
        print("PHASE1_FIND_BIT_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_WORKFLOW_PACKET=pass")
    print(f"PHASE1_FIND_BIT_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_FIND_BIT_WORKFLOW_PACKET_REQUIRED_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
