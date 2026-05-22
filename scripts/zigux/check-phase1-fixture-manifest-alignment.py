#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

EXPECTED_PHASE = "Phase 1"
EXPECTED_MANIFEST_STATUS = "closed"
EXPECTED_BLOCKERS_STATUS = "parked"

EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_SHARED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

REVIEW_KEY_FIELDS = (
    "parity_fixture_keys",
    "partial_xor_review_fields",
    "tail_clamp_fixture_keys",
    "cached_leftmost_fixture_keys",
    "traversal_replay_keys",
    "duplicate_search_replay_keys",
)

SELF_TEST_CASES = [
    "happy_path",
    "missing_fixture_file",
    "missing_manifest_file",
    "missing_blockers_file",
    "fixture_is_directory",
    "manifest_json_error",
    "fixture_duplicate_key",
    "manifest_duplicate_key",
    "blockers_duplicate_key",
    "manifest_helper_count_drift",
    "fixture_section_drift",
    "lane_overlap_drift",
    "blocker_manifest_pointer_drift",
    "blocker_anti_overlap_rule_drift",
    "missing_review_anchor_fixture_key",
]


def section_name(helper_path: str) -> str:
    return Path(helper_path).stem


def expected_sections() -> set[str]:
    return {section_name(helper) for helper in EXPECTED_HELPERS}


def reject_duplicate_object_pairs(path: Path):
    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"json_duplicate_key:{path.as_posix()}:{key}")
            result[key] = value
        return result

    return hook


def load_json(path: Path) -> tuple[object | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return None, f"utf8_decode:{path.as_posix()}:{exc.start + 1}:{exc.reason}"

    try:
        return json.loads(text, object_pairs_hook=reject_duplicate_object_pairs(path)), None
    except json.JSONDecodeError as exc:
        return None, f"json_decode:{path.as_posix()}:{exc.lineno}:{exc.colno}:{exc.msg}"
    except ValueError as exc:
        return None, str(exc)


def write_json(path: Path, payload: object) -> None:
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def check_required_path(path: Path, rel: Path) -> str | None:
    if not path.exists():
        return f"missing:{rel.as_posix()}"
    if not path.is_file():
        return f"not_file:{rel.as_posix()}"
    return None


def review_key_issues(
    helper: str,
    fixture_section: dict[str, object],
    review_anchor: dict[str, object],
) -> list[str]:
    issues: list[str] = []
    for field in REVIEW_KEY_FIELDS:
        if field not in review_anchor:
            continue
        keys = review_anchor[field]
        if not isinstance(keys, list):
            issues.append(f"review_anchor_field_type:{helper}:{field}")
            continue
        for key in keys:
            if not isinstance(key, str):
                issues.append(f"review_anchor_key_type:{helper}:{field}")
                continue
            if key not in fixture_section:
                issues.append(f"fixture_key_missing:{helper}:{field}:{key}")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    fixture_path = root / FIXTURE_REL
    manifest_path = root / MANIFEST_REL
    blockers_path = root / BLOCKERS_REL

    for path, rel in (
        (fixture_path, FIXTURE_REL),
        (manifest_path, MANIFEST_REL),
        (blockers_path, BLOCKERS_REL),
    ):
        issue = check_required_path(path, rel)
        if issue is not None:
            issues.append(issue)
    if issues:
        return issues

    fixture, fixture_error = load_json(fixture_path)
    manifest, manifest_error = load_json(manifest_path)
    blockers, blockers_error = load_json(blockers_path)
    for error in (fixture_error, manifest_error, blockers_error):
        if error is not None:
            return [error]

    assert fixture is not None
    assert manifest is not None
    assert blockers is not None

    if not isinstance(fixture, dict):
        return [f"fixture_type:{type(fixture).__name__}"]
    if not isinstance(manifest, dict):
        return [f"manifest_type:{type(manifest).__name__}"]
    if not isinstance(blockers, dict):
        return [f"blockers_type:{type(blockers).__name__}"]

    if manifest.get("phase") != EXPECTED_PHASE:
        issues.append(f"manifest_phase:{manifest.get('phase')!r}")
    if manifest.get("status") != EXPECTED_MANIFEST_STATUS:
        issues.append(f"manifest_status:{manifest.get('status')!r}")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append(f"manifest_helper_count:{manifest.get('helper_count')!r}")

    helpers = manifest.get("helpers")
    if helpers != EXPECTED_HELPERS:
        issues.append("manifest_helpers")

    fixture_sections = set(fixture.keys())
    missing_sections = sorted(expected_sections() - fixture_sections)
    unexpected_sections = sorted(fixture_sections - expected_sections())
    if missing_sections or unexpected_sections:
        issues.append(
            "fixture_sections:"
            + f"missing={','.join(missing_sections) or '-'}:"
            + f"unexpected={','.join(unexpected_sections) or '-'}"
        )

    manifest_lane = manifest.get("lane_sequencing")
    if not isinstance(manifest_lane, dict):
        return issues + ["manifest_lane_sequencing_type"]

    shared_helpers = manifest_lane.get("shared_replay_parked_helpers")
    direct_helpers = manifest_lane.get("direct_anchor_followup_helpers")
    if shared_helpers != EXPECTED_SHARED_HELPERS:
        issues.append("manifest_shared_helpers")
    if direct_helpers != EXPECTED_DIRECT_HELPERS:
        issues.append("manifest_direct_helpers")

    if isinstance(shared_helpers, list) and isinstance(direct_helpers, list):
        overlap = sorted(set(shared_helpers) & set(direct_helpers))
        combined = sorted(set(shared_helpers) | set(direct_helpers))
        if overlap:
            issues.append("lane_overlap:" + ",".join(overlap))
        if sorted(EXPECTED_HELPERS) != combined:
            issues.append("lane_union")

    if blockers.get("status") != EXPECTED_BLOCKERS_STATUS:
        issues.append(f"blockers_status:{blockers.get('status')!r}")

    blockers_lane = blockers.get("lane_sequencing")
    if not isinstance(blockers_lane, dict):
        return issues + ["blockers_lane_sequencing_type"]

    if blockers_lane.get("manifest") != MANIFEST_REL.as_posix():
        issues.append(f"blockers_manifest:{blockers_lane.get('manifest')!r}")
    if blockers_lane.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_HELPERS):
        issues.append("blockers_shared_helper_count")
    if blockers_lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
        issues.append("blockers_direct_helper_count")
    if blockers_lane.get("shared_replay_parked_helpers") != EXPECTED_SHARED_HELPERS:
        issues.append("blockers_shared_helpers")
    if blockers_lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        issues.append("blockers_direct_helpers")
    if blockers_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        issues.append("blockers_anti_overlap_rule")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return issues + ["manifest_review_anchors_type"]

    for helper in EXPECTED_HELPERS:
        anchor = review_anchors.get(helper)
        if not isinstance(anchor, dict):
            continue
        section = fixture.get(section_name(helper))
        if not isinstance(section, dict):
            issues.append(f"fixture_section_type:{helper}")
            continue
        issues.extend(review_key_issues(helper, section, anchor))

    return issues


def build_sample_root(root: Path) -> None:
    fixture = {
        "argv_split": {"argc": 3, "argv": ["alpha", "beta", "gamma"], "blank_argc": 0},
        "bitmap": {
            "scnprintf": "1-3,7,10-11",
            "truncated_scnprintf_len": 7,
            "truncated_scnprintf": "1-3,7,1",
            "terminator_only_scnprintf_len": 0,
            "terminator_only_nul": 0,
            "zero_length_scnprintf_len": 0,
            "partial_xor_nbits": 4,
            "partial_xor_masked_values": [14],
        },
        "cmdline": {"decimal_k": {"value": 65536, "rest": " rest"}},
        "ctype": {"mask_A": 65},
        "find_bit": {
            "tail_clamped_first": 67,
            "tail_clamped_next": 69,
            "tail_zero_clamped_first": 69,
            "tail_zero_clamped_next": 69,
            "tail_and_clamped_first": 67,
            "tail_and_clamped_next": 69,
            "tail_clamped_last": 67,
            "tail_clamped_empty_last": 69,
        },
        "hweight": {"w64": 32},
        "list_sort": {
            "tri_sorted_keys": [1, 1, 2, 3, 3],
            "tri_sorted_ordinals": [1, 3, 0, 2, 4],
            "bool_sorted_keys": [1, 1, 2, 3, 3],
            "bool_sorted_ordinals": [1, 3, 0, 2, 4],
        },
        "rbtree": {
            "empty_root": True,
            "insert_order": [5, 10, 15, 20, 25],
            "reverse_order": [25, 20, 15, 10, 5],
            "replace_order": [5, 10, 15, 25],
            "erase_init_order": [5, 15, 25],
            "postorder_count": 3,
            "erase_init_node_empty": True,
            "cleared_node_empty": True,
            "find_found_key": 15,
            "find_missing": True,
            "find_first_serial": 0,
            "next_match_serials": [0, 2, 4],
            "match_iterator_serials": [0, 2, 4],
            "cached_leftmost_return_serials": [0, -1, 2, -1],
            "next_match_terminal_null": True,
        },
        "slab": {"zero_after_kmalloc": True},
        "str_error_r": {"enoent": "No such file or directory"},
        "string": {
            "strtobool_y": True,
            "strtobool_on": True,
            "strtobool_zero": False,
            "strtobool_off": False,
            "strtobool_invalid": 184,
            "strlcpy_len": 5,
            "strlcpy_buffer": "hel",
            "skip_spaces": "hello",
            "trim_spaces": "hi",
            "remove_spaces": "abc",
            "replace_char": "a_b",
            "replace_char_end": 3,
            "replace_char_cstr_end": 2,
            "replace_char_cstr_bytes": [97, 95, 0, 45, 122],
            "memchr_inv_index": 4,
            "memchr_inv_none": True,
        },
        "vsprintf": {"scnprintf_text": "zigux:7"},
        "zalloc": {"zeroed": True},
    }
    manifest = {
        "phase": EXPECTED_PHASE,
        "status": EXPECTED_MANIFEST_STATUS,
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
        },
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "parity_fixture_keys": [
                    "scnprintf",
                    "truncated_scnprintf_len",
                    "truncated_scnprintf",
                    "terminator_only_scnprintf_len",
                    "terminator_only_nul",
                    "zero_length_scnprintf_len",
                ],
                "partial_xor_review_fields": [
                    "partial_xor_nbits",
                    "partial_xor_masked_values",
                ],
            },
            "tools/lib/find_bit.zig": {
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
            },
            "tools/lib/list_sort.zig": {
                "parity_fixture_keys": [
                    "tri_sorted_keys",
                    "tri_sorted_ordinals",
                    "bool_sorted_keys",
                    "bool_sorted_ordinals",
                ],
            },
            "tools/lib/rbtree.zig": {
                "parity_fixture_keys": [
                    "empty_root",
                    "insert_order",
                    "reverse_order",
                    "replace_order",
                    "erase_init_order",
                    "postorder_count",
                    "erase_init_node_empty",
                    "cleared_node_empty",
                    "find_found_key",
                    "find_missing",
                    "find_first_serial",
                    "next_match_serials",
                    "next_match_terminal_null",
                ],
                "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
                "duplicate_search_replay_keys": [
                    "find_found_key",
                    "find_missing",
                    "find_first_serial",
                    "next_match_serials",
                    "match_iterator_serials",
                    "next_match_terminal_null",
                ],
            },
            "tools/lib/string.zig": {
                "parity_fixture_keys": [
                    "strtobool_y",
                    "strtobool_on",
                    "strtobool_zero",
                    "strtobool_off",
                    "strtobool_invalid",
                    "strlcpy_len",
                    "strlcpy_buffer",
                    "skip_spaces",
                    "trim_spaces",
                    "remove_spaces",
                    "replace_char",
                    "replace_char_end",
                    "replace_char_cstr_end",
                    "replace_char_cstr_bytes",
                    "memchr_inv_index",
                    "memchr_inv_none",
                ],
            },
        },
    }
    blockers = {
        "status": EXPECTED_BLOCKERS_STATUS,
        "lane_sequencing": {
            "manifest": MANIFEST_REL.as_posix(),
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_HELPERS),
            "shared_replay_parked_helpers": EXPECTED_SHARED_HELPERS,
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_HELPERS),
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }
    write_json(root / FIXTURE_REL, fixture)
    write_json(root / MANIFEST_REL, manifest)
    write_json(root / BLOCKERS_REL, blockers)


def assert_case(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)


def write_text(path: Path, text: str) -> None:
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_fixture_manifest_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        assert_case("happy_path", collect_issues(root) == [])
        covered.append("happy_path")

        (root / FIXTURE_REL).unlink()
        assert_case("missing_fixture_file", collect_issues(root) == [f"missing:{FIXTURE_REL.as_posix()}"])
        covered.append("missing_fixture_file")

        build_sample_root(root)
        (root / MANIFEST_REL).unlink()
        assert_case("missing_manifest_file", collect_issues(root) == [f"missing:{MANIFEST_REL.as_posix()}"])
        covered.append("missing_manifest_file")

        build_sample_root(root)
        (root / BLOCKERS_REL).unlink()
        assert_case("missing_blockers_file", collect_issues(root) == [f"missing:{BLOCKERS_REL.as_posix()}"])
        covered.append("missing_blockers_file")

        build_sample_root(root)
        (root / FIXTURE_REL).unlink()
        (root / FIXTURE_REL).mkdir(parents=True)
        assert_case("fixture_is_directory", collect_issues(root) == [f"not_file:{FIXTURE_REL.as_posix()}"])
        covered.append("fixture_is_directory")

        build_sample_root(root)
        (root / MANIFEST_REL).write_text("{\n", encoding="utf-8")
        assert_case(
            "manifest_json_error",
            collect_issues(root)
            == [
                f"json_decode:{(root / MANIFEST_REL).as_posix()}:2:1:Expecting property name enclosed in double quotes"
            ],
        )
        covered.append("manifest_json_error")

        build_sample_root(root)
        write_text(root / FIXTURE_REL, '{\n  "argv_split": {"argc": 3},\n  "argv_split": {"argc": 4}\n}\n')
        assert_case(
            "fixture_duplicate_key",
            collect_issues(root) == [f"json_duplicate_key:{(root / FIXTURE_REL).as_posix()}:argv_split"],
        )
        covered.append("fixture_duplicate_key")

        build_sample_root(root)
        write_text(
            root / MANIFEST_REL,
            '{\n  "phase": "Phase 1",\n  "phase": "Phase 2"\n}\n',
        )
        assert_case(
            "manifest_duplicate_key",
            collect_issues(root) == [f"json_duplicate_key:{(root / MANIFEST_REL).as_posix()}:phase"],
        )
        covered.append("manifest_duplicate_key")

        build_sample_root(root)
        write_text(
            root / BLOCKERS_REL,
            '{\n  "status": "parked",\n  "status": "drifted"\n}\n',
        )
        assert_case(
            "blockers_duplicate_key",
            collect_issues(root) == [f"json_duplicate_key:{(root / BLOCKERS_REL).as_posix()}:status"],
        )
        covered.append("blockers_duplicate_key")

        build_sample_root(root)
        manifest = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        assert isinstance(manifest, dict)
        manifest["helper_count"] = 12
        write_json(root / MANIFEST_REL, manifest)
        assert_case("manifest_helper_count_drift", collect_issues(root) == ["manifest_helper_count:12"])
        covered.append("manifest_helper_count_drift")

        build_sample_root(root)
        fixture = json.loads((root / FIXTURE_REL).read_text(encoding="utf-8"))
        assert isinstance(fixture, dict)
        del fixture["vsprintf"]
        write_json(root / FIXTURE_REL, fixture)
        assert_case(
            "fixture_section_drift",
            collect_issues(root) == ["fixture_sections:missing=vsprintf:unexpected=-"],
        )
        covered.append("fixture_section_drift")

        build_sample_root(root)
        manifest = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        assert isinstance(manifest, dict)
        manifest["lane_sequencing"]["direct_anchor_followup_helpers"] = EXPECTED_DIRECT_HELPERS + [EXPECTED_SHARED_HELPERS[0]]  # type: ignore[index]
        write_json(root / MANIFEST_REL, manifest)
        issues = collect_issues(root)
        assert_case(
            "lane_overlap_drift",
            issues == [
                "manifest_direct_helpers",
                "lane_overlap:tools/lib/argv_split.zig",
            ],
        )
        covered.append("lane_overlap_drift")

        build_sample_root(root)
        blockers = json.loads((root / BLOCKERS_REL).read_text(encoding="utf-8"))
        assert isinstance(blockers, dict)
        blockers["lane_sequencing"]["manifest"] = "zigux/tests/fixtures/wrong.json"  # type: ignore[index]
        write_json(root / BLOCKERS_REL, blockers)
        assert_case(
            "blocker_manifest_pointer_drift",
            collect_issues(root) == ["blockers_manifest:'zigux/tests/fixtures/wrong.json'"],
        )
        covered.append("blocker_manifest_pointer_drift")

        build_sample_root(root)
        blockers = json.loads((root / BLOCKERS_REL).read_text(encoding="utf-8"))
        assert isinstance(blockers, dict)
        blockers["lane_sequencing"]["anti_overlap_rule"] = "drifted anti-overlap rule"  # type: ignore[index]
        write_json(root / BLOCKERS_REL, blockers)
        assert_case(
            "blocker_anti_overlap_rule_drift",
            collect_issues(root) == ["blockers_anti_overlap_rule"],
        )
        covered.append("blocker_anti_overlap_rule_drift")

        build_sample_root(root)
        manifest = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        assert isinstance(manifest, dict)
        manifest["review_anchors"]["tools/lib/string.zig"]["parity_fixture_keys"].append("missing_field")  # type: ignore[index]
        write_json(root / MANIFEST_REL, manifest)
        assert_case(
            "missing_review_anchor_fixture_key",
            collect_issues(root)
            == ["fixture_key_missing:tools/lib/string.zig:parity_fixture_keys:missing_field"],
        )
        covered.append("missing_review_anchor_fixture_key")

    assert_case("self_test_case_order", covered == SELF_TEST_CASES)
    print("PHASE1_FIXTURE_MANIFEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE1_FIXTURE_MANIFEST_ALIGNMENT_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 1 fixture, manifest, and blocker packets stay aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in self-test suite.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE1_FIXTURE_MANIFEST_ALIGNMENT=fail")
        print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_ROOT={args.root.resolve()}")
        for issue in issues:
            print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_ISSUE={issue}")
        return 1

    print("PHASE1_FIXTURE_MANIFEST_ALIGNMENT=pass")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_ROOT={args.root.resolve()}")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
