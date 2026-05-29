#!/usr/bin/env python3
"""Fail-close the current Phase 1 helper parity scoreboard evidence."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
PARITY_CHECKER_REL = Path("scripts/zigux/check-phase1-parity.py")
DIRECT_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-helper-parity.py")

EXPECTED_DIRECT_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

EXPECTED_PARKED_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)

EXPECTED_FIXTURE_SECTION = {
    "tools/lib/bitmap.zig": "bitmap",
    "tools/lib/find_bit.zig": "find_bit",
    "tools/lib/rbtree.zig": "rbtree",
    "tools/lib/string.zig": "string",
}

EXPECTED_REVIEW_FIXTURE_FIELDS = {
    "tools/lib/bitmap.zig": (
        "parity_fixture_keys",
        "shared_logical_fixture_keys",
        "shared_range_fixture_keys",
        "partial_xor_review_fields",
    ),
    "tools/lib/find_bit.zig": (
        "tail_clamp_fixture_keys",
        "tail_inclusive_boundary_fixture_keys",
    ),
    "tools/lib/rbtree.zig": (
        "parity_fixture_keys",
        "cached_leftmost_fixture_keys",
        "cached_root_transition_fixture_keys",
    ),
    "tools/lib/string.zig": (
        "parity_fixture_keys",
    ),
}

EXPECTED_PARKED_REVIEW_FIELDS = (
    "helper_test_anchors",
    "next_safe_step_note",
)

EXPECTED_PARITY_CHECKER_MARKERS = (
    "PHASE1_PARITY=pass",
    "PHASE1_PARITY_HELPER_COUNT=",
    "PHASE1_PARITY_DIRECT_REVIEW_HELPER_COUNT=",
    "PHASE1_PARITY_BLOCKER_IDS=",
    "EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS",
    "EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS",
)

EXPECTED_DIRECT_CHECKER_MARKERS = (
    "PHASE1_DIRECT_HELPER_PARITY=pass",
    "EXPECTED_DIRECT_HELPERS",
    "EXPECTED_MANIFEST_KEYS",
    "SOURCE_MARKERS",
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def read_json(root: Path, rel: Path) -> object:
    return json.loads(read_text(root, rel))


def expect(condition: bool, issue: str, issues: list[str]) -> None:
    if not condition:
        issues.append(issue)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in (MANIFEST_REL, FIXTURE_REL, PARITY_CHECKER_REL, DIRECT_CHECKER_REL):
        expect((root / rel).is_file(), f"missing:{rel.as_posix()}", issues)
    if issues:
        return issues

    manifest = read_json(root, MANIFEST_REL)
    fixture = read_json(root, FIXTURE_REL)
    expect(isinstance(manifest, dict), "manifest:not_object", issues)
    expect(isinstance(fixture, dict), "fixture:not_object", issues)
    if not isinstance(manifest, dict) or not isinstance(fixture, dict):
        return issues

    lane = manifest.get("lane_sequencing")
    expect(isinstance(lane, dict), "manifest:lane_sequencing:not_object", issues)
    if isinstance(lane, dict):
        expect(
            tuple(lane.get("direct_anchor_followup_helpers", ())) == EXPECTED_DIRECT_HELPERS,
            "manifest:lane_sequencing:direct_anchor_followup_helpers:drift",
            issues,
        )
        expect(
            tuple(lane.get("shared_replay_parked_helpers", ())) == EXPECTED_PARKED_HELPERS,
            "manifest:lane_sequencing:shared_replay_parked_helpers:drift",
            issues,
        )

    review_anchors = manifest.get("review_anchors")
    expect(isinstance(review_anchors, dict), "manifest:review_anchors:not_object", issues)
    if isinstance(review_anchors, dict):
        for helper in EXPECTED_DIRECT_HELPERS:
            payload = review_anchors.get(helper)
            expect(isinstance(payload, dict), f"manifest:review_anchors:{helper}:not_object", issues)
            section_name = EXPECTED_FIXTURE_SECTION[helper]
            section = fixture.get(section_name)
            expect(isinstance(section, dict), f"fixture:{section_name}:not_object", issues)
            if not isinstance(payload, dict) or not isinstance(section, dict):
                continue
            for field in EXPECTED_REVIEW_FIXTURE_FIELDS[helper]:
                values = payload.get(field)
                expect(isinstance(values, list), f"manifest:review_anchors:{helper}:{field}:not_list", issues)
                if not isinstance(values, list):
                    continue
                for value in values:
                    expect(
                        isinstance(value, str),
                        f"manifest:review_anchors:{helper}:{field}:non_string:{value!r}",
                        issues,
                    )
                    if isinstance(value, str) and field.endswith("fixture_keys"):
                        expect(
                            value in section,
                            f"fixture:{section_name}:missing_scoreboard_key:{value}",
                            issues,
                        )

        for helper in EXPECTED_PARKED_HELPERS:
            payload = review_anchors.get(helper)
            expect(isinstance(payload, dict), f"manifest:review_anchors:{helper}:parked_not_object", issues)
            if not isinstance(payload, dict):
                continue
            for field in EXPECTED_PARKED_REVIEW_FIELDS:
                expect(field in payload, f"manifest:review_anchors:{helper}:parked_missing:{field}", issues)

    parity_checker = read_text(root, PARITY_CHECKER_REL)
    for marker in EXPECTED_PARITY_CHECKER_MARKERS:
        expect(marker in parity_checker, f"parity_checker:missing_marker:{marker}", issues)

    direct_checker = read_text(root, DIRECT_CHECKER_REL)
    for marker in EXPECTED_DIRECT_CHECKER_MARKERS:
        expect(marker in direct_checker, f"direct_checker:missing_marker:{marker}", issues)

    return issues


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    review_anchors: dict[str, dict[str, object]] = {}
    for helper, fields in EXPECTED_REVIEW_FIXTURE_FIELDS.items():
        review_anchors[helper] = {field: [f"{field}_sample"] for field in fields}
    for helper in EXPECTED_PARKED_HELPERS:
        review_anchors[helper] = {
            "helper_test_anchors": [f"test {helper}"],
            "next_safe_step_note": f"Keep {helper} parked unless its shared replay drifts.",
        }
    return json.dumps(
        {
            "lane_sequencing": {
                "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_HELPERS),
                "shared_replay_parked_helpers": list(EXPECTED_PARKED_HELPERS),
            },
            "review_anchors": review_anchors,
        },
        indent=2,
    ) + "\n"


def sample_fixture() -> str:
    fixture = {
        section: {
            f"{field}_sample": True
            for field in EXPECTED_REVIEW_FIXTURE_FIELDS[helper]
            if field.endswith("fixture_keys")
        }
        for helper, section in EXPECTED_FIXTURE_SECTION.items()
    }
    return json.dumps(fixture, indent=2) + "\n"


def build_sample_root(root: Path) -> None:
    write_text(root, MANIFEST_REL, sample_manifest())
    write_text(root, FIXTURE_REL, sample_fixture())
    write_text(root, PARITY_CHECKER_REL, "\n".join(EXPECTED_PARITY_CHECKER_MARKERS) + "\n")
    write_text(root, DIRECT_CHECKER_REL, "\n".join(EXPECTED_DIRECT_CHECKER_MARKERS) + "\n")


def mutate_json(root: Path, rel: Path, callback) -> None:
    path = root / rel
    payload = json.loads(path.read_text(encoding="utf-8"))
    callback(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = (
        ("baseline", None, False),
        (
            "missing_direct_review_anchor",
            lambda root: mutate_json(
                root,
                MANIFEST_REL,
                lambda payload: payload["review_anchors"].pop("tools/lib/bitmap.zig"),
            ),
            True,
        ),
        (
            "missing_fixture_key",
            lambda root: mutate_json(root, FIXTURE_REL, lambda payload: payload["bitmap"].clear()),
            True,
        ),
        (
            "missing_parity_output_marker",
            lambda root: write_text(
                root,
                PARITY_CHECKER_REL,
                "\n".join(EXPECTED_PARITY_CHECKER_MARKERS[:-1]) + "\n",
            ),
            True,
        ),
        (
            "parked_helper_drift",
            lambda root: mutate_json(
                root,
                MANIFEST_REL,
                lambda payload: payload["lane_sequencing"].__setitem__(
                    "shared_replay_parked_helpers",
                    list(EXPECTED_PARKED_HELPERS[:-1]),
                ),
            ),
            True,
        ),
    )
    for name, mutate, should_fail in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-helper-parity-scoreboard-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutate is not None:
                mutate(root)
            issues = collect_issues(root)
            if should_fail and not issues:
                print(f"phase1-helper-parity-scoreboard:{name}:expected_failure")
                return 1
            if not should_fail and issues:
                print(f"phase1-helper-parity-scoreboard:{name}:unexpected={issues}")
                return 1

    print("PHASE1_HELPER_PARITY_SCOREBOARD_SELF_TEST=pass")
    print(f"PHASE1_HELPER_PARITY_SCOREBOARD_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(Path(args.root).resolve())
    if issues:
        print("PHASE1_HELPER_PARITY_SCOREBOARD=fail")
        for issue in issues:
            print(f"PHASE1_HELPER_PARITY_SCOREBOARD_ISSUE={issue}")
        return 1

    print("PHASE1_HELPER_PARITY_SCOREBOARD=pass")
    print(f"PHASE1_HELPER_PARITY_SCOREBOARD_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    print(f"PHASE1_HELPER_PARITY_SCOREBOARD_PARKED_HELPER_COUNT={len(EXPECTED_PARKED_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
