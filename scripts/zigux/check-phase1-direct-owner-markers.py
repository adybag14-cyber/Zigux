#!/usr/bin/env python3
"""Guard the Phase 1 direct-owner marker packet against lane-note drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parent
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

REQUIRED_EXACT_LINES = {
    "bitmap_direct_owner": "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys and the already-landed shared closure-validator bitmap review markers it already owns`",
    "find_bit_direct_owner": "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias, Linux-style alias, and tail-word skip anchors plus the committed tail-clamped find_bit replay fields already emitted by the shared C harness and consumed by the shared fixture`",
    "rbtree_direct_owner": "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree cached-root coverage stays helper-local while the committed shared replay owns duplicate-search parity and matchIterator() through the dedicated iterator fixture key, so the next widening is the cached-root leftmost-return fixture key only`",
    "string_direct_owner": "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    "find_bit_or_packet_note": '- current `master` also carries the newer direct `test "find or bit returns the next set bit from either bitmap"` proof inside `tools/lib/find_bit.zig`, so notes-only and closure-side rereads should treat the OR-path as part of the existing helper-local `find_bit` anchor family instead of inventing a new shared replay packet for it',
    "find_bit_or_next_step_note": '- the already-landed OR-path proof in `test "find or bit returns the next set bit from either bitmap"` belongs to that same `find_bit` direct-anchor packet, so if it drifts, refresh the existing helper-family notes or closure evidence instead of widening shared replay ownership',
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
        REQUIRED_EXACT_LINES["find_bit_or_packet_note"],
        REQUIRED_EXACT_LINES["bitmap_direct_owner"],
        REQUIRED_EXACT_LINES["find_bit_direct_owner"],
        REQUIRED_EXACT_LINES["rbtree_direct_owner"],
        REQUIRED_EXACT_LINES["string_direct_owner"],
        REQUIRED_EXACT_LINES["find_bit_or_next_step_note"],
    ]
    return (
        "# Phase 1 Host-Helper Lane Sequencing\n\n"
        "## Direct-Anchor Owner Map\n\n"
        + "\n".join(ordered_lines)
        + "\n\n## Next Bounded Step\n\n"
        "Keep the direct-owner packet parked unless one of those exact lines drifts.\n"
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
