#!/usr/bin/env python3
"""Guard the Phase 1 closure validator's current find_bit tail-inclusive packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")

EXPECTED_VALIDATOR_LINES = [
    '"tail_inclusive_boundary_fixture_keys": [',
    '        "tail_inclusive_boundary_next",',
    '        "tail_inclusive_boundary_zero",',
    '        "tail_inclusive_boundary_and",',
    '    ],',
    '"review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",',
    '"next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families.",',
]

EXPECTED_MANIFEST_FIELDS = {
    "tail_inclusive_boundary_fixture_keys": [
        "tail_inclusive_boundary_next",
        "tail_inclusive_boundary_zero",
        "tail_inclusive_boundary_and",
    ],
    "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",
    "next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families.",
}

EXPECTED_CLOSURE_LINE = (
    "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: "
    "keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed "
    "same-word start-mask, head-word or tail-word inclusive-boundary, zero-window, zero-sized "
    "short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, "
    "Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped "
    "replay fields, and do not reopen older validator-first cues or neighboring helper families "
    "by default."
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_value(label: str, actual: Any, expected: Any) -> list[str]:
    return [] if actual == expected else [f"{label}:expected_current_packet"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (VALIDATOR_REL, MANIFEST_REL, CLOSURE_REL):
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    validator_text = load_text(root, VALIDATOR_REL)
    for marker in EXPECTED_VALIDATOR_LINES:
        failures.extend(require_exact_occurrence(validator_text, f"validator:{marker}", marker))

    closure_text = load_text(root, CLOSURE_REL)
    failures.extend(require_exact_occurrence(closure_text, "closure:find_bit_tiebreaker", EXPECTED_CLOSURE_LINE))

    manifest = load_json(root, MANIFEST_REL)
    review_anchors = manifest.get("review_anchors") if isinstance(manifest, dict) else None
    if not isinstance(review_anchors, dict):
        return ["manifest:review_anchors"]
    packet = review_anchors.get("tools/lib/find_bit.zig")
    if not isinstance(packet, dict):
        return ["manifest:tools/lib/find_bit.zig"]

    for field, expected in EXPECTED_MANIFEST_FIELDS.items():
        failures.extend(require_exact_value(f"manifest:{field}", packet.get(field), expected))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, VALIDATOR_REL, "\n".join(EXPECTED_VALIDATOR_LINES) + "\n")
    write_text(root, CLOSURE_REL, EXPECTED_CLOSURE_LINE + "\n")
    write_text(
        root,
        MANIFEST_REL,
        json.dumps({"review_anchors": {"tools/lib/find_bit.zig": EXPECTED_MANIFEST_FIELDS}}, indent=2) + "\n",
    )


def run_self_test() -> int:
    cases = [
        ("missing_validator", "missing_file:scripts/zigux/validate-phase1-closure.py"),
        (
            "missing_tail_inclusive_keys",
            "validator:        \"tail_inclusive_boundary_next\",:expected=1:actual=0",
        ),
        (
            "duplicate_tail_inclusive_keys",
            "validator:        \"tail_inclusive_boundary_next\",:expected=1:actual=2",
        ),
        ("missing_closure_line", "closure:find_bit_tiebreaker:expected=1:actual=0"),
        ("manifest_summary_drift", "manifest:review_packet_summary:expected_current_packet"),
        ("manifest_tail_keys_drift", "manifest:tail_inclusive_boundary_fixture_keys:expected_current_packet"),
    ]

    with tempfile.TemporaryDirectory(prefix="phase1_find_bit_tail_inclusive_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        if cases[0][1] not in collect_failures(tmp_root):
            raise SystemExit("self-test:missing_validator")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("self-test:baseline")

        validator_text = load_text(tmp_root, VALIDATOR_REL).replace('        \"tail_inclusive_boundary_next\",\n', "", 1)
        write_text(tmp_root, VALIDATOR_REL, validator_text)
        if cases[1][1] not in collect_failures(tmp_root):
            raise SystemExit("self-test:missing_tail_inclusive_keys")

        build_sample_repo(tmp_root)
        duplicated = load_text(tmp_root, VALIDATOR_REL).replace(
            '        \"tail_inclusive_boundary_next\",\n',
            '        \"tail_inclusive_boundary_next\",\n        \"tail_inclusive_boundary_next\",\n',
            1,
        )
        write_text(tmp_root, VALIDATOR_REL, duplicated)
        if cases[2][1] not in collect_failures(tmp_root):
            raise SystemExit("self-test:duplicate_tail_inclusive_keys")

        build_sample_repo(tmp_root)
        write_text(tmp_root, CLOSURE_REL, "")
        if cases[3][1] not in collect_failures(tmp_root):
            raise SystemExit("self-test:missing_closure_line")

        build_sample_repo(tmp_root)
        manifest = load_json(tmp_root, MANIFEST_REL)
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["review_packet_summary"] = "older summary"
        write_text(tmp_root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if cases[4][1] not in collect_failures(tmp_root):
            raise SystemExit("self-test:manifest_summary_drift")

        build_sample_repo(tmp_root)
        manifest = load_json(tmp_root, MANIFEST_REL)
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_inclusive_boundary_fixture_keys"] = [
            "tail_inclusive_boundary_next"
        ]
        write_text(tmp_root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if cases[5][1] not in collect_failures(tmp_root):
            raise SystemExit("self-test:manifest_tail_keys_drift")

    print("PHASE1_FIND_BIT_TAIL_INCLUSIVE_CHECK_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_TAIL_INCLUSIVE_CHECK_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_TAIL_INCLUSIVE_CHECK=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_TAIL_INCLUSIVE_CHECK=pass")
    print("PHASE1_FIND_BIT_TAIL_INCLUSIVE_CHECK_REQUIRED_FILE_COUNT=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
