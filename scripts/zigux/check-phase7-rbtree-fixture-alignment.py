#!/usr/bin/env python3
"""Validate the current Phase 7 rbtree JSON fixture and C harness stay aligned."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

JSON_PATH = "zigux/tests/fixtures/phase7_rbtree.json"
HARNESS_PATH = "zigux/tests/fixtures/phase7_rbtree_c_harness.c"
REQUIRED_FILES = [JSON_PATH, HARNESS_PATH]

EXPECTED_PACKET = "phase7-rbtree-parity-fixture"
EXPECTED_ANCHOR = "lib/rbtree.c"
EXPECTED_JSON_STATE = "ordered-duplicate-cached-postorder-reverse"
EXPECTED_HARNESS_STATE = "ordered-duplicate-cached-postorder-reverse-c-harness"
EXPECTED_SCENARIOS = (
    "ordered_duplicate_range",
    "cached_leftmost_promotion",
    "postorder_null_stop",
    "reverse_alias_detached",
)

SELF_TEST_CASE_COUNT = 8


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(root: Path) -> None:
    write(
        root / JSON_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "anchor": EXPECTED_ANCHOR,
                "current_master_state": EXPECTED_JSON_STATE,
                "scenarios": [
                    {"key": "ordered_duplicate_range"},
                    {"key": "cached_leftmost_promotion"},
                    {"key": "postorder_null_stop"},
                    {"key": "reverse_alias_detached"},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / HARNESS_PATH,
        "\n".join(
            [
                "// SPDX-License-Identifier: GPL-2.0-only",
                "struct phase7_rbtree_c_harness {",
                "    const char *packet;",
                "    const char *anchor;",
                "    const char *current_master_state;",
                "    struct ordered_duplicate_range_case ordered_duplicate_range;",
                "    struct cached_leftmost_promotion_case cached_leftmost_promotion;",
                "    struct postorder_null_stop_case postorder_null_stop;",
                "    struct reverse_alias_detached_case reverse_alias_detached;",
                "};",
                "",
                "const struct phase7_rbtree_c_harness phase7_rbtree_c_harness = {",
                f'    .packet = "{EXPECTED_PACKET}",',
                f'    .anchor = "{EXPECTED_ANCHOR}",',
                f'    .current_master_state = "{EXPECTED_HARNESS_STATE}",',
                "    .ordered_duplicate_range = { 0 },",
                "    .cached_leftmost_promotion = { 0 },",
                "    .postorder_null_stop = { 0 },",
                "    .reverse_alias_detached = { 0 },",
                "};",
                "",
            ]
        ),
    )


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_errors(root: Path) -> list[str]:
    json_text = read_text(root / JSON_PATH)
    harness_text = read_text(root / HARNESS_PATH)
    parsed = json.loads(json_text)
    errors: list[str] = []

    if parsed.get("packet") != EXPECTED_PACKET:
        errors.append(
            f'{JSON_PATH}: expected "packet" to equal "{EXPECTED_PACKET}", found {parsed.get("packet")!r}'
        )
    if parsed.get("anchor") != EXPECTED_ANCHOR:
        errors.append(
            f'{JSON_PATH}: expected "anchor" to equal "{EXPECTED_ANCHOR}", found {parsed.get("anchor")!r}'
        )
    if parsed.get("current_master_state") != EXPECTED_JSON_STATE:
        errors.append(
            f'{JSON_PATH}: expected "current_master_state" to equal "{EXPECTED_JSON_STATE}", found '
            f'{parsed.get("current_master_state")!r}'
        )

    scenario_keys = [item.get("key") for item in parsed.get("scenarios", [])]
    if scenario_keys != list(EXPECTED_SCENARIOS):
        errors.append(
            f"{JSON_PATH}: expected scenario keys {list(EXPECTED_SCENARIOS)!r}, found {scenario_keys!r}"
        )

    required_harness_markers = [
        f'.packet = "{EXPECTED_PACKET}",',
        f'.anchor = "{EXPECTED_ANCHOR}",',
        f'.current_master_state = "{EXPECTED_HARNESS_STATE}",',
        "struct phase7_rbtree_c_harness {",
        "phase7_rbtree_c_harness = {",
        ".ordered_duplicate_range =",
        ".cached_leftmost_promotion =",
        ".postorder_null_stop =",
        ".reverse_alias_detached =",
    ]
    for marker in required_harness_markers:
        if marker not in harness_text:
            errors.append(f"{HARNESS_PATH}: missing marker {marker!r}")

    return errors


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return missing_files, collect_errors(root)


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, errors = validate(tmp_root)
    assert errors == [], case
    assert missing_files == [rel], case


def expect_error(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, errors = validate(tmp_root)
    assert missing_files == [], case
    assert errors == [expected], case


def replace_once(path: Path, old: str, new: str) -> None:
    text = read_text(path)
    assert old in text, old
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_fixture_alignment_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])
        cases_run = 0

        (tmp_root / HARNESS_PATH).unlink()
        expect_missing_file("missing_c_harness", tmp_root, HARNESS_PATH)
        cases_run += 1
        write_fixture_root(tmp_root)

        replace_once(tmp_root / JSON_PATH, EXPECTED_PACKET, "phase7-rbtree-bad-packet")
        expect_error(
            "json_packet_drift",
            tmp_root,
            f'{JSON_PATH}: expected "packet" to equal "{EXPECTED_PACKET}", found \'phase7-rbtree-bad-packet\'',
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replace_once(tmp_root / JSON_PATH, EXPECTED_ANCHOR, "tools/lib/rbtree.c")
        expect_error(
            "json_anchor_drift",
            tmp_root,
            f'{JSON_PATH}: expected "anchor" to equal "{EXPECTED_ANCHOR}", found \'tools/lib/rbtree.c\'',
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replace_once(tmp_root / JSON_PATH, EXPECTED_JSON_STATE, "ordered-duplicate-cached-postorder")
        expect_error(
            "json_state_drift",
            tmp_root,
            f'{JSON_PATH}: expected "current_master_state" to equal "{EXPECTED_JSON_STATE}", found '
            "'ordered-duplicate-cached-postorder'",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replace_once(tmp_root / JSON_PATH, '"key": "reverse_alias_detached"', '"key": "reverse_alias_missing"')
        expect_error(
            "json_scenario_drift",
            tmp_root,
            f"{JSON_PATH}: expected scenario keys {list(EXPECTED_SCENARIOS)!r}, found "
            "['ordered_duplicate_range', 'cached_leftmost_promotion', 'postorder_null_stop', 'reverse_alias_missing']",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replace_once(tmp_root / HARNESS_PATH, f'.packet = "{EXPECTED_PACKET}",', '.packet = "phase7-rbtree-bad-packet",')
        expect_error(
            "harness_packet_drift",
            tmp_root,
            f"{HARNESS_PATH}: missing marker '.packet = \"{EXPECTED_PACKET}\",'",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replace_once(tmp_root / HARNESS_PATH, f'.current_master_state = "{EXPECTED_HARNESS_STATE}",', "")
        expect_error(
            "harness_state_missing",
            tmp_root,
            f"{HARNESS_PATH}: missing marker '.current_master_state = \"{EXPECTED_HARNESS_STATE}\",'",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replace_once(tmp_root / HARNESS_PATH, ".reverse_alias_detached =", ".reverse_alias_missing =")
        expect_error(
            "harness_scenario_missing",
            tmp_root,
            f"{HARNESS_PATH}: missing marker '.reverse_alias_detached ='",
        )
        cases_run += 1

        assert cases_run == SELF_TEST_CASE_COUNT, cases_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        print("PHASE7_RBTREE_FIXTURE_ALIGNMENT_SELF_TEST=pass")
        print(f"PHASE7_RBTREE_FIXTURE_ALIGNMENT_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
        return 0

    missing_files, errors = validate(args.repo_root)
    if not missing_files and not errors:
        print("PHASE7_RBTREE_FIXTURE_ALIGNMENT=pass")
        print(f"PHASE7_RBTREE_FIXTURE_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
        print(f"PHASE7_RBTREE_FIXTURE_ALIGNMENT_SCENARIO_COUNT={len(EXPECTED_SCENARIOS)}")
        return 0

    print("PHASE7_RBTREE_FIXTURE_ALIGNMENT=fail")
    if missing_files:
        print("MISSING_PHASE7_RBTREE_FIXTURE_ALIGNMENT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_RBTREE_FIXTURE_ALIGNMENT_FILES_END")
    if errors:
        print("MISMATCHED_PHASE7_RBTREE_FIXTURE_ALIGNMENT_MARKERS_START")
        for item in errors:
            print(item)
        print("MISMATCHED_PHASE7_RBTREE_FIXTURE_ALIGNMENT_MARKERS_END")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
