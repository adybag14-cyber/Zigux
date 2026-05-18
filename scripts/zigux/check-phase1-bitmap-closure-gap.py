#!/usr/bin/env python3
"""Check the current Phase 1 bitmap closure-gap packet for drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    CLOSURE_NOTE_REL,
    MANIFEST_REL,
)

LANE_MARKERS = {
    "bitmap_direct_owner": (
        "- `tools/lib/bitmap.zig` owns its helper-local bitmap anchors and the committed bitmap "
        "replay keys in `zigux/tests/fixtures/phase1_helpers.json`."
    ),
    "bitmap_next_safe_step": (
        "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new "
        "direct-anchor drift or committed shared replay drift; do not reopen older closure-side "
        "or validator-route cue names by default`"
    ),
}

CLOSURE_MARKERS = {
    "closure_validator": (
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`"
    ),
    "next_safe_step": (
        "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family "
        "tie-breaker against the restored closure note, closure validator, shared tests-root "
        "smoke route, and the helper-specific next_safe_step_note entries in "
        "zigux/tests/fixtures/phase1_helper_manifest.json`"
    ),
}

EXPECTED_BITMAP_PACKET = {
    "first_word_boundary_anchor": (
        'test "bitmap range helpers preserve edges across whole-word spans"'
    ),
    "final_partial_word_anchor": (
        'test "bitmap range helpers preserve edges across whole-word spans"'
    ),
    "fill_tail_clamp_anchor": (
        'test "bitmap full empty and weight ignore out-of-range tail bits"'
    ),
    "predicate_tail_mask_anchor": (
        'test "bitmap tail-masked helpers ignore out-of-range differences"'
    ),
    "zero_bit_noop_anchor": "",
    "linux_alias_anchor": "",
    "next_safe_step_note": (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
        "direct-anchor drift inside the current helper-local packet or committed shared replay "
        "drift in the bitmap parity fields; current master still ships direct fill-tail clamp, "
        "copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors "
        "here, while zero-bit and Linux-style alias follow-through no longer live in the "
        "helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is "
        "still outstanding, treat that as the only other bitmap follow-through."
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    if count == 1:
        return []
    return [f"{label}:expected_once:{needle}:actual_count={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    if actual == expected:
        return []
    return [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    lane_text = load_text(root, LANE_NOTE_REL)
    for label, marker in LANE_MARKERS.items():
        failures.extend(require_exact_occurrence(lane_text, label, marker))

    closure_text = load_text(root, CLOSURE_NOTE_REL)
    for label, marker in CLOSURE_MARKERS.items():
        failures.extend(require_exact_occurrence(closure_text, label, marker))

    manifest = json.loads(load_text(root, MANIFEST_REL))
    failures.extend(require_exact_value("manifest.status", manifest.get("status"), "closed"))
    failures.extend(
        require_exact_value("manifest.helper_count", manifest.get("helper_count"), 13)
    )

    bitmap_packet = manifest.get("review_anchors", {}).get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_packet, dict):
        failures.append("manifest.bitmap_packet:missing")
        return failures

    for label, expected in EXPECTED_BITMAP_PACKET.items():
        failures.extend(
            require_exact_value(f"manifest.bitmap.{label}", bitmap_packet.get(label), expected)
        )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, needle: str, replacement: str) -> str:
    if needle not in text:
        raise ValueError(f"needle not found: {needle}")
    return text.replace(needle, replacement, 1)


def make_fixture_tree(root: Path) -> None:
    write_text(
        root / LANE_NOTE_REL,
        "# Phase 1 Host-Helper Lane Sequencing\n\n"
        + LANE_MARKERS["bitmap_direct_owner"]
        + "\n"
        + LANE_MARKERS["bitmap_next_safe_step"]
        + "\n",
    )
    write_text(
        root / CLOSURE_NOTE_REL,
        "# Phase 1 Closure\n\n"
        + CLOSURE_MARKERS["closure_validator"]
        + "\n"
        + CLOSURE_MARKERS["next_safe_step"]
        + "\n",
    )
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": 13,
                "review_anchors": {
                    "tools/lib/bitmap.zig": EXPECTED_BITMAP_PACKET,
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases = [
        ("baseline", None, True),
        (
            "missing_lane_marker",
            lambda root: write_text(
                root / LANE_NOTE_REL,
                replace_once(load_text(root, LANE_NOTE_REL), LANE_MARKERS["bitmap_next_safe_step"], ""),
            ),
            False,
        ),
        (
            "missing_closure_marker",
            lambda root: write_text(
                root / CLOSURE_NOTE_REL,
                replace_once(load_text(root, CLOSURE_NOTE_REL), CLOSURE_MARKERS["next_safe_step"], ""),
            ),
            False,
        ),
        (
            "missing_file",
            lambda root: (root / MANIFEST_REL).unlink(),
            False,
        ),
        (
            "bad_manifest_final_partial_anchor",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": 13,
                        "review_anchors": {
                            "tools/lib/bitmap.zig": EXPECTED_BITMAP_PACKET
                            | {"final_partial_word_anchor": "drift"},
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "bad_manifest_zero_bit_anchor",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": 13,
                        "review_anchors": {
                            "tools/lib/bitmap.zig": EXPECTED_BITMAP_PACKET
                            | {"zero_bit_noop_anchor": "drift"},
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "bad_manifest_linux_alias_anchor",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": 13,
                        "review_anchors": {
                            "tools/lib/bitmap.zig": EXPECTED_BITMAP_PACKET
                            | {"linux_alias_anchor": "drift"},
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "bad_manifest_next_safe_step_note",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": 13,
                        "review_anchors": {
                            "tools/lib/bitmap.zig": EXPECTED_BITMAP_PACKET
                            | {"next_safe_step_note": "drift"},
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
    ]

    for name, mutate, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bitmap-closure-gap-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"phase1-bitmap-closure-gap-self-test:{name}:unexpected={failures}")
                return 1

    print("PHASE1_BITMAP_CLOSURE_GAP_CHECK_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_CLOSURE_GAP_CHECK_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BITMAP_CLOSURE_GAP_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
