#!/usr/bin/env python3
"""Guard the current Phase 1 find_bit direct-owner packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")

EXPECTED_DIRECT_OWNER_LINE = "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, `getValue8()`, and `findLastBit()` byte-clump and backward-scan coverage, plus the public, Linux-style, and underscore andnot coverage including the shipped `findFirstAndNotBit()`, `findNextAndNotBit()`, `find_first_andnot_bit()`, `find_next_andnot_bit()`, `_find_first_andnot_bit()`, and `_find_next_andnot_bit()` entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary `find_bit` replay fields already preserved in `zigux/tests/fixtures/phase1_helpers.json`. Reopen shared replay only if that committed tail-clamped or tail-inclusive-boundary packet drifts.`"
EXPECTED_NEXT_STEP_LINE = "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`"
EXPECTED_CLOSURE_PARAGRAPH = "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts."
EXPECTED_MANIFEST_FIELDS = {
    "andnot_scan_entrypoints": [
        "findFirstAndNotBit",
        "find_first_andnot_bit",
        "_find_first_andnot_bit",
        "findNextAndNotBit",
        "find_next_andnot_bit",
        "_find_next_andnot_bit",
    ],
    "andnot_scan_entrypoint_contract": "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.",
    "tail_clamp_fixture_keys": [
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_clamped_last",
        "tail_clamped_empty_last",
    ],
    "tail_inclusive_boundary_fixture_keys": [
        "tail_inclusive_boundary_next",
        "tail_inclusive_boundary_zero",
        "tail_inclusive_boundary_and",
    ],
}
EXPECTED_FIXTURE_VALUES = {
    "tail_clamped_first": 67,
    "tail_clamped_next": 69,
    "tail_zero_clamped_first": 69,
    "tail_zero_clamped_next": 69,
    "tail_and_clamped_first": 67,
    "tail_and_clamped_next": 69,
    "tail_clamped_last": 67,
    "tail_clamped_empty_last": 69,
    "tail_inclusive_boundary_next": 68,
    "tail_inclusive_boundary_zero": 68,
    "tail_inclusive_boundary_and": 68,
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def read_json(root: Path, rel: Path) -> object:
    return json.loads(read_text(root, rel))


def require_exact_line(text: str, label: str, expected: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == expected.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected_current_packet"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (LANE_NOTE_REL, CLOSURE_NOTE_REL, MANIFEST_REL, FIXTURE_REL):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    lane_text = read_text(root, LANE_NOTE_REL)
    closure_text = read_text(root, CLOSURE_NOTE_REL)
    manifest = read_json(root, MANIFEST_REL)
    fixture = read_json(root, FIXTURE_REL)

    failures.extend(require_exact_line(lane_text, "direct_owner_line", EXPECTED_DIRECT_OWNER_LINE))
    failures.extend(require_exact_line(lane_text, "next_step_line", EXPECTED_NEXT_STEP_LINE))
    failures.extend(require_exact_line(closure_text, "closure_paragraph", EXPECTED_CLOSURE_PARAGRAPH))

    packet = manifest.get("review_anchors", {}).get("tools/lib/find_bit.zig") if isinstance(manifest, dict) else None
    if not isinstance(packet, dict):
        return failures + ["manifest:tools/lib/find_bit.zig"]
    for key, expected in EXPECTED_MANIFEST_FIELDS.items():
        failures.extend(require_exact_value(f"manifest:{key}", packet.get(key), expected))

    find_bit_fixture = fixture.get("find_bit") if isinstance(fixture, dict) else None
    if not isinstance(find_bit_fixture, dict):
        return failures + ["fixture:find_bit"]
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"fixture:{key}", find_bit_fixture.get(key), expected))

    return failures


def write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write(root, LANE_NOTE_REL, EXPECTED_DIRECT_OWNER_LINE + "\n" + EXPECTED_NEXT_STEP_LINE + "\n")
    write(root, CLOSURE_NOTE_REL, EXPECTED_CLOSURE_PARAGRAPH + "\n")
    write(
        root,
        MANIFEST_REL,
        json.dumps({"review_anchors": {"tools/lib/find_bit.zig": EXPECTED_MANIFEST_FIELDS}}, indent=2) + "\n",
    )
    write(root, FIXTURE_REL, json.dumps({"find_bit": EXPECTED_FIXTURE_VALUES}, indent=2) + "\n")


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        ("missing_direct_owner_line", lambda root: write(root, LANE_NOTE_REL, EXPECTED_NEXT_STEP_LINE + "\n")),
        ("missing_next_step_line", lambda root: write(root, LANE_NOTE_REL, EXPECTED_DIRECT_OWNER_LINE + "\n")),
        ("missing_closure_paragraph", lambda root: write(root, CLOSURE_NOTE_REL, "")),
        (
            "manifest_drift",
            lambda root: write(
                root,
                MANIFEST_REL,
                json.dumps(
                    {
                        "review_anchors": {
                            "tools/lib/find_bit.zig": {
                                **EXPECTED_MANIFEST_FIELDS,
                                "andnot_scan_entrypoints": ["findFirstAndNotBit"],
                            }
                        }
                    },
                    indent=2,
                ) + "\n",
            ),
        ),
        (
            "fixture_drift",
            lambda root: write(
                root,
                FIXTURE_REL,
                json.dumps({"find_bit": {**EXPECTED_FIXTURE_VALUES, "tail_clamped_last": 0}}, indent=2) + "\n",
            ),
        ),
    ]
    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-find-bit-owner-") as td:
            root = Path(td)
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
    print("PHASE1_FIND_BIT_DIRECT_OWNER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_DIRECT_OWNER_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run self-test cases")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_DIRECT_OWNER_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1
    print("PHASE1_FIND_BIT_DIRECT_OWNER_PACKET=pass")
    print(f"PHASE1_FIND_BIT_DIRECT_OWNER_PACKET_LANE_NOTE={LANE_NOTE_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_DIRECT_OWNER_PACKET_CLOSURE_NOTE={CLOSURE_NOTE_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_DIRECT_OWNER_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_DIRECT_OWNER_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
