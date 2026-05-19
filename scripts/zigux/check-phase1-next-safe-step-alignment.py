#!/usr/bin/env python3
"""Guard the Phase 1 helper-specific next-safe-step packet against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    LANE_NOTE_REL,
    MANIFEST_REL,
)

REQUIRED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
    ),
    LANE_NOTE_REL: (
        "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are live companions again, while the older validator-first and make-route names stay historical`",
        "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, underscore-alias and Linux-style alias coverage including the shipped find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`",
        "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors together with the committed cached_leftmost_return_serials shared replay field it already owns`",
        "- `PHASE1_STRING_DIRECT_OWNER=string helper-local sysfs review anchors plus the direct counted-search, basename, trim, memchr moving-dirty, and memparse anchors it still owns, together with the committed replaceChar and memchrInv replay keys already preserved in zigux/tests/fixtures/phase1_helper_manifest.json`",
    ),
}

EXPECTED_NEXT_SAFE_STEP_NOTES = {
    "tools/lib/bitmap.zig": (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors here, while zero-bit and Linux-style alias follow-through no longer live in the helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is still outstanding, treat that as the only other bitmap follow-through."
    ),
    "tools/lib/find_bit.zig": (
        "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias, or tail-word skip anchors, or committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families."
    ),
    "tools/lib/rbtree.zig": (
        "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; until another committed cached-root field lands, insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors."
    ),
    "tools/lib/string.zig": (
        "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default."
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = load_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                failures.append(
                    f"{relative_path.as_posix()}:marker_count:{count}:{marker}"
                )

    manifest = json.loads(load_text(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected_json_object"]
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors_missing"]

    for helper, expected_note in EXPECTED_NEXT_SAFE_STEP_NOTES.items():
        helper_entry = review_anchors.get(helper)
        if not isinstance(helper_entry, dict):
            failures.append(f"{MANIFEST_REL.as_posix()}:missing_helper:{helper}")
            continue
        actual_note = helper_entry.get("next_safe_step_note")
        if actual_note != expected_note:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:next_safe_step_note:{helper}:expected={expected_note!r}:actual={actual_note!r}"
            )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")



def make_fixture_tree(root: Path) -> None:
    write_file(
        root,
        PHASE1_CLOSURE_REL,
        "# Phase 1 Closure\n\n"
        + "\n".join(REQUIRED_MARKERS[PHASE1_CLOSURE_REL])
        + "\n",
    )
    write_file(
        root,
        LANE_NOTE_REL,
        "# Lane Note\n\n" + "\n".join(REQUIRED_MARKERS[LANE_NOTE_REL]) + "\n",
    )
    write_file(
        root,
        MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    helper: {"next_safe_step_note": note}
                    for helper, note in EXPECTED_NEXT_SAFE_STEP_NOTES.items()
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-next-safe-step-alignment-") as tmpdir:
        root = Path(tmpdir)
        make_fixture_tree(root)
        baseline = collect_failures(root)
        if baseline:
            print(f"phase1-next-safe-step-self-test:baseline:unexpected={baseline}")
            return 1

        lane_text = load_text(root, LANE_NOTE_REL)
        write_file(
            root,
            LANE_NOTE_REL,
            lane_text.replace("clump8, getValue8(), and findLastBit()", "clump8 and getValue8()", 1),
        )
        if not collect_failures(root):
            print("phase1-next-safe-step-self-test:lane_note_refresh:expected_failure")
            return 1

        make_fixture_tree(root)
        manifest = json.loads(load_text(root, MANIFEST_REL))
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["next_safe_step_note"] = "drift"
        write_file(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if not collect_failures(root):
            print("phase1-next-safe-step-self-test:manifest_drift:expected_failure")
            return 1

        make_fixture_tree(root)
        (root / PHASE1_CLOSURE_REL).unlink()
        if not collect_failures(root):
            print("phase1-next-safe-step-self-test:missing_closure:expected_failure")
            return 1

        make_fixture_tree(root)
        manifest = json.loads(load_text(root, MANIFEST_REL))
        del manifest["review_anchors"]["tools/lib/string.zig"]
        write_file(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if not collect_failures(root):
            print("phase1-next-safe-step-self-test:missing_string_helper:expected_failure")
            return 1

        make_fixture_tree(root)
        closure_text = load_text(root, PHASE1_CLOSURE_REL)
        write_file(
            root,
            PHASE1_CLOSURE_REL,
            closure_text.replace("one helper-family tie-breaker", "one helper-family follow-up", 1),
        )
        if not collect_failures(root):
            print("phase1-next-safe-step-self-test:closure_phrase_drift:expected_failure")
            return 1

    print("PHASE1_NEXT_SAFE_STEP_ALIGNMENT_SELF_TEST=pass")
    print("PHASE1_NEXT_SAFE_STEP_ALIGNMENT_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_NEXT_SAFE_STEP_ALIGNMENT=pass")
    print(f"PHASE1_NEXT_SAFE_STEP_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_NEXT_SAFE_STEP_ALIGNMENT_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values()) + len(EXPECTED_NEXT_SAFE_STEP_NOTES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
