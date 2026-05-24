#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase1-closure.py")
MIN_CASE_COUNT = 25
SAMPLE_CASE_COUNT = 29

REQUIRED_WORKFLOW_MARKERS = (
    "- name: Self-test current Phase 1 closure validator",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "- name: Check current Phase 1 closure packet",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
)

REQUIRED_VALIDATOR_MARKERS = (
    "def run_self_test() -> int:",
    'print("PHASE1_CLOSURE_SELF_TEST=pass")',
    'print(f"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}")',
    '("baseline", None),',
    '("missing_restore_state",',
    '("old_next_step_marker",',
    '("forbidden_old_marker",',
    '("missing_find_bit_bench_guard",',
    '("bad_helper_count",',
    '("stale_lane_rule_summary",',
    '("stale_anti_overlap_rule",',
    '("duplicate_manifest_helper_count",',
    '("duplicate_manifest_lane_rule_summary",',
    '("missing_find_bit_andnot_contract",',
    '("stale_find_bit_review_summary",',
    '("missing_rbtree_cached_root_alias_anchor",',
    '("stale_rbtree_shared_replay_summary",',
    '("missing_bitmap_or_window_anchor",',
    '("missing_bitmap_copy_raw_alias_anchor",',
    '("stale_bitmap_empty_buffer_anchor",',
    '("stale_bitmap_next_safe_step_note",',
    '("stale_string_sysfs_review_summary",',
    '("stale_string_next_safe_step_note",',
    '("missing_string_checker",',
    '("failing_direct_owner_checker",',
    '("missing_makefile_marker",',
    '("forbidden_phase1_makefile_route",',
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_root(root: Path) -> tuple[str, object]:
    workflow_file = root / WORKFLOW_PATH
    validator_file = root / VALIDATOR_PATH

    missing_files = [str(path) for path in (workflow_file, validator_file) if not path.is_file()]
    if missing_files:
        return ("missing_files", missing_files)

    workflow_text = read_text(workflow_file)
    validator_text = read_text(validator_file)

    missing_workflow = [marker for marker in REQUIRED_WORKFLOW_MARKERS if marker not in workflow_text]
    if missing_workflow:
        return ("missing_workflow_markers", missing_workflow)

    missing_validator = [marker for marker in REQUIRED_VALIDATOR_MARKERS if marker not in validator_text]
    if missing_validator:
        return ("missing_validator_markers", missing_validator)

    case_count = validator_text.count('(\"')
    if case_count < MIN_CASE_COUNT:
        return ("case_count_too_small", {"expected_min": MIN_CASE_COUNT, "actual": case_count})

    return ("pass", {"case_count": case_count})


def write_sample_root(root: Path) -> None:
    (root / WORKFLOW_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / VALIDATOR_PATH.parent).mkdir(parents=True, exist_ok=True)

    workflow_text = """name: zigux-bootstrap
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 1 closure validator
        run: python3 scripts/zigux/validate-phase1-closure.py --self-test
      - name: Check current Phase 1 closure packet
        run: python3 scripts/zigux/validate-phase1-closure.py
"""

    validator_lines = [
        "#!/usr/bin/env python3",
        "def run_self_test() -> int:",
        '    cases: list[tuple[str, object | None]] = [',
        '        ("baseline", None),',
        '        ("missing_restore_state", None),',
        '        ("old_next_step_marker", None),',
        '        ("forbidden_old_marker", None),',
        '        ("missing_find_bit_bench_guard", None),',
        '        ("bad_helper_count", None),',
        '        ("stale_lane_rule_summary", None),',
        '        ("stale_anti_overlap_rule", None),',
        '        ("duplicate_manifest_helper_count", None),',
        '        ("duplicate_manifest_lane_rule_summary", None),',
        '        ("missing_find_bit_andnot_contract", None),',
        '        ("stale_find_bit_review_summary", None),',
        '        ("missing_rbtree_cached_root_alias_anchor", None),',
        '        ("stale_rbtree_shared_replay_summary", None),',
        '        ("missing_bitmap_or_window_anchor", None),',
        '        ("missing_bitmap_copy_raw_alias_anchor", None),',
        '        ("stale_bitmap_empty_buffer_anchor", None),',
        '        ("stale_bitmap_next_safe_step_note", None),',
        '        ("stale_string_sysfs_review_summary", None),',
        '        ("stale_string_next_safe_step_note", None),',
        '        ("missing_string_checker", None),',
        '        ("failing_direct_owner_checker", None),',
        '        ("missing_makefile_marker", None),',
        '        ("forbidden_phase1_makefile_route", None),',
        '        ("filler_case_0", None),',
        '        ("filler_case_1", None),',
        '        ("filler_case_2", None),',
        '        ("filler_case_3", None),',
        "    ]",
        '    print("PHASE1_CLOSURE_SELF_TEST=pass")',
        '    print(f"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}")',
        "    return 0",
    ]

    (root / WORKFLOW_PATH).write_text(workflow_text, encoding="utf-8")
    (root / VALIDATOR_PATH).write_text("\n".join(validator_lines) + "\n", encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane16-phase1-closure-selftest-") as tmp:
        root = Path(tmp)
        write_sample_root(root)

        kind, payload = validate_root(root)
        assert kind == "pass", (kind, payload)
        assert payload == {"case_count": SAMPLE_CASE_COUNT}
        case_count += 1

        workflow_text = read_text(root / WORKFLOW_PATH).replace(
            "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
            "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
            1,
        )
        (root / WORKFLOW_PATH).write_text(workflow_text, encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "missing_workflow_markers", (kind, payload)
        assert payload == ["run: python3 scripts/zigux/validate-phase1-closure.py --self-test"]
        case_count += 1

        write_sample_root(root)
        validator_text = read_text(root / VALIDATOR_PATH).replace(
            '        ("missing_find_bit_bench_guard", None),\n',
            "",
            1,
        )
        (root / VALIDATOR_PATH).write_text(validator_text, encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "missing_validator_markers", (kind, payload)
        assert payload == ['("missing_find_bit_bench_guard",']
        case_count += 1

        write_sample_root(root)
        (root / VALIDATOR_PATH).unlink()
        kind, payload = validate_root(root)
        assert kind == "missing_files", (kind, payload)
        assert payload == [str(root / VALIDATOR_PATH)]
        case_count += 1

    print("PHASE1_CLOSURE_SELFTEST_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_SELFTEST_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shipped Phase 1 closure validator keeps its self-test contract explicit."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    kind, payload = validate_root(args.root)
    if kind != "pass":
        print("PHASE1_CLOSURE_SELFTEST_PACKET=fail")
        print(f"PHASE1_CLOSURE_SELFTEST_PACKET_REASON={kind}")
        print(payload)
        return 1

    case_count = payload["case_count"]
    print("PHASE1_CLOSURE_SELFTEST_PACKET=pass")
    print("PHASE1_CLOSURE_SELFTEST_PACKET_REQUIRED_FILE_COUNT=2")
    print(
        f"PHASE1_CLOSURE_SELFTEST_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_VALIDATOR_MARKERS)}"
    )
    print(f"PHASE1_CLOSURE_SELFTEST_PACKET_CASE_COUNT_MIN={MIN_CASE_COUNT}")
    print(f"PHASE1_CLOSURE_SELFTEST_PACKET_CASE_COUNT={case_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
