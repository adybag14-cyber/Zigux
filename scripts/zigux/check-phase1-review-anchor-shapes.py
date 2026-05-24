#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
]

HELPER_TO_FIXTURE = {
    "tools/lib/argv_split.zig": "argv_split",
    "tools/lib/bitmap.zig": "bitmap",
    "tools/lib/find_bit.zig": "find_bit",
    "tools/lib/list_sort.zig": "list_sort",
    "tools/lib/rbtree.zig": "rbtree",
    "tools/lib/string.zig": "string",
}

EXPECTED_REVIEW_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def required_file_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.exists():
            issues.append(f"missing_file:{relative_path}")
        elif not path.is_file():
            issues.append(f"required_file_not_regular:{relative_path}")
    return issues


def validate_string_field(
    helper_path: str,
    field_name: str,
    value: object,
    issues: list[str],
    *,
    prefix: str | None = None,
) -> None:
    if not isinstance(value, str) or not value.strip():
        issues.append(
            f"review_anchor:{helper_path}:{field_name}:expected=non_empty_string:actual={type(value).__name__}"
        )
        return
    if prefix is not None and not value.startswith(prefix):
        issues.append(
            f"review_anchor:{helper_path}:{field_name}:expected_prefix={prefix!r}:actual={value!r}"
        )


def validate_string_list_field(
    helper_path: str,
    field_name: str,
    value: object,
    issues: list[str],
    *,
    prefix: str | None = None,
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            f"review_anchor:{helper_path}:{field_name}:expected=non_empty_list:actual={type(value).__name__}"
        )
        return
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            issues.append(
                f"review_anchor:{helper_path}:{field_name}[{index}]:expected=non_empty_string:actual={type(item).__name__}"
            )
            continue
        if prefix is not None and not item.startswith(prefix):
            issues.append(
                f"review_anchor:{helper_path}:{field_name}[{index}]:expected_prefix={prefix!r}:actual={item!r}"
            )


def validate_fixture_reference_field(
    helper_path: str,
    field_name: str,
    value: object,
    helper_fixture: dict[str, object],
    issues: list[str],
) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            f"review_anchor:{helper_path}:{field_name}:expected=non_empty_list:actual={type(value).__name__}"
        )
        return
    missing = [item for item in value if not isinstance(item, str) or item not in helper_fixture]
    if missing:
        issues.append(
            f"review_anchor:{helper_path}:{field_name}:missing_fixture_fields={missing!r}"
        )


def collect_review_anchor_issues(
    manifest: dict[str, object], fixture: dict[str, object]
) -> list[str]:
    issues: list[str] = []

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"manifest:review_anchors:expected=dict:actual={type(review_anchors).__name__}"]

    actual_helpers = sorted(review_anchors.keys())
    if actual_helpers != EXPECTED_REVIEW_HELPERS:
        issues.append(
            f"manifest:review_anchor_helpers:expected={EXPECTED_REVIEW_HELPERS!r}:actual={actual_helpers!r}"
        )

    for helper_path in EXPECTED_REVIEW_HELPERS:
        helper_anchor = review_anchors.get(helper_path)
        if not isinstance(helper_anchor, dict):
            issues.append(
                f"review_anchor:{helper_path}:expected=dict:actual={type(helper_anchor).__name__}"
            )
            continue

        fixture_key = HELPER_TO_FIXTURE[helper_path]
        helper_fixture = fixture.get(fixture_key)
        if not isinstance(helper_fixture, dict):
            issues.append(
                f"fixture:{fixture_key}:expected=dict:actual={type(helper_fixture).__name__}"
            )
            continue

        for field_name, value in helper_anchor.items():
            if field_name.endswith("_anchor"):
                validate_string_field(
                    helper_path, field_name, value, issues, prefix='test "'
                )
            elif field_name.endswith("_anchors"):
                validate_string_list_field(
                    helper_path, field_name, value, issues, prefix='test "'
                )
            elif field_name.endswith(("_summary", "_note", "_rule", "_contract")):
                validate_string_field(helper_path, field_name, value, issues)
            elif field_name.endswith(("_keys", "_fields")):
                validate_fixture_reference_field(
                    helper_path, field_name, value, helper_fixture, issues
                )
            elif field_name.endswith("_entrypoints"):
                validate_string_list_field(helper_path, field_name, value, issues)

    return issues


def validate_root(root: Path) -> list[str]:
    issues = required_file_issues(root)
    if issues:
        return issues

    manifest = load_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json")
    fixture = load_json(root / "zigux/tests/fixtures/phase1_helpers.json")

    if manifest.get("phase") != "Phase 1":
        issues.append(f"manifest:phase:expected='Phase 1':actual={manifest.get('phase')!r}")
    if manifest.get("status") != "closed":
        issues.append(f"manifest:status:expected='closed':actual={manifest.get('status')!r}")

    issues.extend(collect_review_anchor_issues(manifest, fixture))
    return issues


def build_self_test_root(root: Path) -> None:
    write_text(
        root / "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "review_anchors": {
                    "tools/lib/argv_split.zig": {
                        "phase1_helper_replay_anchor": 'test "phase1 argv split replay"',
                        "shared_replay_summary": "argv split summary",
                        "next_safe_step_note": "argv split note",
                    },
                    "tools/lib/bitmap.zig": {
                        "helper_test_anchors": ['test "bitmap helper packet"'],
                        "parity_fixture_keys": ["weight", "scnprintf"],
                        "partial_xor_review_fields": [
                            "partial_xor_nbits",
                            "partial_xor_masked_values",
                        ],
                        "review_packet_summary": "bitmap summary",
                    },
                    "tools/lib/find_bit.zig": {
                        "tail_clamp_fixture_keys": ["tail_clamped_first"],
                        "tail_inclusive_boundary_fixture_keys": [
                            "tail_inclusive_boundary_next"
                        ],
                        "andnot_scan_entrypoints": ["findFirstAndNotBit"],
                        "tail_word_inclusive_boundary_contract": "find bit contract",
                    },
                    "tools/lib/list_sort.zig": {
                        "helper_test_anchors": ['test "list sort helper packet"'],
                        "parity_fixture_keys": ["tri_sorted_keys"],
                        "review_packet_summary": "list sort summary",
                    },
                    "tools/lib/rbtree.zig": {
                        "helper_test_anchors": ['test "rbtree helper packet"'],
                        "parity_fixture_keys": ["insert_order"],
                        "duplicate_search_replay_keys": ["find_found_key"],
                        "cached_root_direct_review_summary": "rbtree summary",
                    },
                    "tools/lib/string.zig": {
                        "helper_test_anchors": ['test "string helper packet"'],
                        "parity_fixture_keys": ["strtobool_y"],
                        "memparse_review_anchors": ['test "memparse packet"'],
                        "prefix_suffix_review_summary": "string summary",
                    },
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / "zigux/tests/fixtures/phase1_helpers.json",
        json.dumps(
            {
                "argv_split": {
                    "argc": 3,
                    "argv": ["alpha", "beta", "gamma"],
                    "blank_argc": 0,
                },
                "bitmap": {
                    "weight": 3,
                    "scnprintf": "1-3",
                    "partial_xor_nbits": 4,
                    "partial_xor_masked_values": [14],
                },
                "find_bit": {
                    "tail_clamped_first": 67,
                    "tail_inclusive_boundary_next": 68,
                },
                "list_sort": {
                    "tri_sorted_keys": [1, 2, 3],
                },
                "rbtree": {
                    "insert_order": [5, 10, 15],
                    "find_found_key": 15,
                },
                "string": {
                    "strtobool_y": True,
                },
            },
            indent=2,
        )
        + "\n",
    )


def mutate_manifest(root: Path, mutate) -> None:
    manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    manifest = load_json(manifest_path)
    mutate(manifest)
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    cases = [
        ("success", None, []),
        (
            "missing_fixture",
            lambda root: (root / "zigux/tests/fixtures/phase1_helpers.json").unlink(),
            ["missing_file:zigux/tests/fixtures/phase1_helpers.json"],
        ),
        (
            "review_helper_key_drift",
            lambda root: mutate_manifest(
                root, lambda manifest: manifest["review_anchors"].pop("tools/lib/string.zig")
            ),
            ["manifest:review_anchor_helpers"],
        ),
        (
            "anchor_prefix_drift",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"]["tools/lib/bitmap.zig"].__setitem__(
                    "helper_test_anchors", ["bitmap drift"]
                ),
            ),
            ["review_anchor:tools/lib/bitmap.zig:helper_test_anchors[0]:expected_prefix='test \"'"],
        ),
        (
            "summary_type_drift",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"]["tools/lib/string.zig"].__setitem__(
                    "prefix_suffix_review_summary", []
                ),
            ),
            ["review_anchor:tools/lib/string.zig:prefix_suffix_review_summary:expected=non_empty_string"],
        ),
        (
            "fixture_reference_drift",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"]["tools/lib/find_bit.zig"].__setitem__(
                    "tail_clamp_fixture_keys", ["missing"]
                ),
            ),
            ["review_anchor:tools/lib/find_bit.zig:tail_clamp_fixture_keys:missing_fixture_fields="],
        ),
    ]

    for case_name, mutate, expected_markers in cases:
        with tempfile.TemporaryDirectory(prefix="phase1_review_anchor_shapes_") as tmp_dir:
            root = Path(tmp_dir)
            build_self_test_root(root)
            if mutate is not None:
                mutate(root)
            issues = validate_root(root)
            if case_name == "success":
                if issues:
                    raise AssertionError(f"{case_name}: unexpected issues: {issues}")
                continue
            if not issues:
                raise AssertionError(f"{case_name}: expected failure")
            for marker in expected_markers:
                if not any(marker in issue for issue in issues):
                    raise AssertionError(f"{case_name}: missing marker {marker!r} in {issues!r}")

    print("PHASE1_REVIEW_ANCHOR_SHAPES_SELF_TEST=pass")
    print(f"PHASE1_REVIEW_ANCHOR_SHAPES_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 1 review-anchor field shapes stay aligned with the committed fixture packet."
    )
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else ROOT
    issues = validate_root(root)
    if issues:
        print("PHASE1_REVIEW_ANCHOR_SHAPES=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_REVIEW_ANCHOR_SHAPES=pass")
    print(f"PHASE1_REVIEW_ANCHOR_SHAPES_HELPER_COUNT={len(EXPECTED_REVIEW_HELPERS)}")
    print(
        "PHASE1_REVIEW_ANCHOR_SHAPES_FIELD_FAMILY_COUNT=5"
    )
    print("PHASE1_REVIEW_ANCHOR_SHAPES_REQUIRED_FILE_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
