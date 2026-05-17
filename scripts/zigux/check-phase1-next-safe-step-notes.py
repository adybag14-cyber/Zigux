#!/usr/bin/env python3
"""Guard Phase 1 next-safe-step tie-breakers against lane-note and manifest drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parent
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_NEXT_SAFE_STEP_LINES = {
    "bitmap": "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
    "find_bit": "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias, Linux-style alias, or tail-word skip anchors, or for committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families`",
    "rbtree": "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`",
    "string": "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
}

EXPECTED_NEXT_SAFE_STEP_NOTES = {
    "tools/lib/bitmap.zig": "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; do not restate bitmap alias, fill-tail, cross-word scnprintf, or zero-bit helper anchors that current master no longer ships directly.",
    "tools/lib/find_bit.zig": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias, Linux-style alias, or tail-word skip anchors, or committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families.",
    "tools/lib/rbtree.zig": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; until another committed cached-root field lands, insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors.",
    "tools/lib/string.zig": "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default.",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    expected = line.strip()
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == expected)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    if actual != expected:
        return [f"{label}:expected={expected!r}:actual={actual!r}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (LANE_NOTE_REL, MANIFEST_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    lane_note_text = load_text(root, LANE_NOTE_REL)
    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    for label, line in EXPECTED_NEXT_SAFE_STEP_LINES.items():
        failures.extend(
            require_exact_line(
                lane_note_text,
                f"{LANE_NOTE_REL.as_posix()}:{label}",
                line,
            )
        )

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        failures.append(
            f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}"
        )
        return failures

    for helper_path, expected_note in EXPECTED_NEXT_SAFE_STEP_NOTES.items():
        helper_entry = review_anchors.get(helper_path)
        if not isinstance(helper_entry, dict):
            failures.append(
                f"{MANIFEST_REL.as_posix()}:review_anchors.{helper_path}:expected=dict:actual={type(helper_entry).__name__}"
            )
            continue
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.{helper_path}.next_safe_step_note",
                helper_entry.get("next_safe_step_note"),
                expected_note,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "review_anchors": {
                    helper_path: {"next_safe_step_note": note}
                    for helper_path, note in EXPECTED_NEXT_SAFE_STEP_NOTES.items()
                }
            },
            indent=2,
        )
        + "\n"
    )


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        LANE_NOTE_REL,
        "# sample\n\n" + "\n".join(EXPECTED_NEXT_SAFE_STEP_LINES.values()) + "\n",
    )
    write_file(root, MANIFEST_REL, sample_manifest())


def run_self_test() -> int:
    cases: list[tuple[str, str, str, str]] = [("success", "", "", "")]
    for label, line in EXPECTED_NEXT_SAFE_STEP_LINES.items():
        cases.append((f"missing_lane_{label}", "lane", label, "remove"))
        cases.append((f"duplicate_lane_{label}", "lane", label, "duplicate"))
    for helper_path in EXPECTED_NEXT_SAFE_STEP_NOTES:
        cases.append((f"manifest_{helper_path}", "manifest", helper_path, "drift"))

    for name, target_kind, target_key, operation in cases:
        safe_name = name.replace("/", "_")
        with tempfile.TemporaryDirectory(prefix=f"phase1-next-safe-step-{safe_name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if target_kind == "lane":
                target = root / LANE_NOTE_REL
                line = EXPECTED_NEXT_SAFE_STEP_LINES[target_key]
                text = target.read_text(encoding="utf-8")
                if operation == "remove":
                    target.write_text(text.replace(line + "\n", "", 1), encoding="utf-8")
                elif operation == "duplicate":
                    target.write_text(text.replace(line, line + "\n" + line, 1), encoding="utf-8")
            elif target_kind == "manifest":
                target = root / MANIFEST_REL
                manifest = json.loads(target.read_text(encoding="utf-8"))
                manifest["review_anchors"][target_key]["next_safe_step_note"] += " drift"
                target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for item in failures:
                        print(item)
                    return 1
                continue

            if not failures:
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

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-next-safe-step-notes:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
