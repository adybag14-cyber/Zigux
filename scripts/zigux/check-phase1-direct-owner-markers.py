#!/usr/bin/env python3
"""Guard the Phase 1 direct-owner marker packet against lane-note drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

REQUIRED_EXACT_LINES = {
    "missing_phase1_packet_note": "- current authenticated reads do not recover `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, or `zigux/Makefile` on `master`, so this lane should treat those older closure-side and make-route names as historical packet members that need fresh re-materialization before they are reused as live owner-map evidence",
    "bitmap_direct_owner": "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; older closure-side bitmap note names stay historical until current master exposes them again`",
    "find_bit_direct_owner": "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias, Linux-style alias, and tail-word skip anchors plus the committed tail-clamped find_bit replay fields already emitted by the shared C harness and consumed by the shared fixture`",
    "rbtree_direct_owner": "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed shared replay already owns duplicate-search parity through find(), findFirst(), nextMatch(), and matchIterator() plus the parked cached_leftmost_return_serials witness`",
    "string_direct_owner": "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    "find_bit_or_packet_note": '- current `master` also carries the newer direct `test "find or bit returns the next set bit from either bitmap"` proof inside `tools/lib/find_bit.zig`, so notes-only rereads should treat the OR-path as part of the existing helper-local `find_bit` anchor family instead of inventing a new shared replay packet for it',
    "find_bit_clump_packet_note": "- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's `helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate shared replay family",
    "string_review_rule_note": "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts/zigux/check-phase1-string-review-packet.py`; treat the older `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` names as historical packet members until current `master` exposes them again",
    "shared_reminder_gap_note": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=Documentation/zigux/README.md still treats scripts/zigux/check-phase1-installer-companion-checks.py as a live reminder surface even though the current checklist, tests-root, and scripts-root packet already treats that path as historical until direct reads recover it`",
    "shared_reminder_active_packet": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py`",
    "shared_reminder_route_split": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md already keep the repo-reality warning explicit for the missing installer companion, while scripts/zigux/check-phase1-string-review-packet.py and scripts/zigux/check-phase1-direct-owner-markers.py carry the live self-test-versus-guard split for the shipped Phase 1 reminder packet; Documentation/zigux/README.md is the remaining docs-root sync step`",
    "shared_reminder_next_step": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=sync Documentation/zigux/README.md to the already-landed historical-warning wording carried by Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md so the docs-root Phase 1 reminder packet stops treating scripts/zigux/check-phase1-installer-companion-checks.py as a live current-master checker; after that, leave the shared reminder packet parked and reopen helper-local follow-through only from the helper-specific next-safe-step markers below`",
    "bitmap_next_safe_step": "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
    "find_bit_next_safe_step": "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias, Linux-style alias, or tail-word skip anchors, or for committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families`",
    "find_bit_or_next_step_note": '- the already-landed OR-path proof in `test "find or bit returns the next set bit from either bitmap"` belongs to that same `find_bit` direct-anchor packet, so if it drifts, refresh the existing helper-family notes instead of widening shared replay ownership',
    "find_bit_clump_next_step_note": "- the existing byte-clump and `findLastBit()` proofs belong to that same `find_bit` direct-anchor packet too, so if one of those helper-local anchors drifts, refresh the current helper-family note before widening shared replay ownership",
    "rbtree_next_safe_step": "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
    "string_next_safe_step": "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == line)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def collect_direct_owner_failures(root: Path) -> list[str]:
    lane_note_path = root / LANE_NOTE_REL
    if not lane_note_path.exists():
        return [f"missing_file:{LANE_NOTE_REL.as_posix()}"]

    lane_note_text = load_text(root, LANE_NOTE_REL)
    missing: list[str] = []
    for label, line in REQUIRED_EXACT_LINES.items():
        missing.extend(require_exact_line(lane_note_text, f"lane_note:{label}", line))
    return missing


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_lane_note_text() -> str:
    ordered_lines = [
        REQUIRED_EXACT_LINES["missing_phase1_packet_note"],
        REQUIRED_EXACT_LINES["find_bit_or_packet_note"],
        REQUIRED_EXACT_LINES["find_bit_clump_packet_note"],
        REQUIRED_EXACT_LINES["shared_reminder_gap_note"],
        REQUIRED_EXACT_LINES["shared_reminder_active_packet"],
        REQUIRED_EXACT_LINES["shared_reminder_route_split"],
        REQUIRED_EXACT_LINES["bitmap_direct_owner"],
        REQUIRED_EXACT_LINES["find_bit_direct_owner"],
        REQUIRED_EXACT_LINES["rbtree_direct_owner"],
        REQUIRED_EXACT_LINES["string_direct_owner"],
        REQUIRED_EXACT_LINES["string_review_rule_note"],
        REQUIRED_EXACT_LINES["shared_reminder_next_step"],
        REQUIRED_EXACT_LINES["bitmap_next_safe_step"],
        REQUIRED_EXACT_LINES["find_bit_next_safe_step"],
        REQUIRED_EXACT_LINES["find_bit_or_next_step_note"],
        REQUIRED_EXACT_LINES["find_bit_clump_next_step_note"],
        REQUIRED_EXACT_LINES["rbtree_next_safe_step"],
        REQUIRED_EXACT_LINES["string_next_safe_step"],
    ]
    return (
        "# Phase 1 Host-Helper Lane Sequencing\n\n"
        "## Current Repo Reality\n\n"
        + "\n".join(ordered_lines[:6])
        + "\n\n## Direct-Anchor Owner Map\n\n"
        + "\n".join(ordered_lines[6:11])
        + "\n\n## Next Bounded Step\n\n"
        + "\n".join(ordered_lines[11:])
        + "\n"
    )


def build_sample_repo(root: Path) -> None:
    write_file(root, LANE_NOTE_REL, sample_lane_note_text())


def run_self_test() -> int:
    cases: list[tuple[str, str | None, str]] = [("success", None, "none")]
    for label, line in REQUIRED_EXACT_LINES.items():
        cases.append((f"missing_{label}", line, "remove"))
        cases.append((f"duplicate_{label}", line, "duplicate"))

    for name, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-direct-owner-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if needle:
                target = root / LANE_NOTE_REL
                text = target.read_text(encoding="utf-8")
                if operation == "remove":
                    target.write_text(text.replace(needle + "\n", "", 1), encoding="utf-8")
                elif operation == "duplicate":
                    target.write_text(text.replace(needle, needle + "\n" + needle, 1), encoding="utf-8")

            missing = collect_direct_owner_failures(root)
            if name == "success":
                if missing:
                    print(f"self-test:{name}:unexpected_failures")
                    for item in missing:
                        print(item)
                    return 1
                continue

            if not missing:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_direct_owner_failures(repo_root(args.root))
    if missing:
        for item in missing:
            print(item)
        return 1

    print("phase1-direct-owner-markers:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
