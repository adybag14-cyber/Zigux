#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
README_REL = Path("scripts") / "zigux" / "README.md"
BLOCKERS_REL = Path("zigux") / "tests" / "fixtures" / "phase1_replay_blockers.json"
MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json"
REPLAY_REL = "zigux/tests/phase1_helpers.zig"
C_HARNESS_REL = "zigux/tests/fixtures/phase1_helpers_c_harness.c"
README_REQUIRED_MARKERS = [
    "`scripts/zigux/validate-phase1.py`",
    "`scripts/zigux/check-phase1-parity.py`",
    "`zigux/tests/phase1_helpers.zig`",
    "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "older validator-first, parity, and replay routes as historical packet members",
]
SELF_TEST_CASES = [
    "round_trip",
    "missing_readme_marker",
    "summary_marker_drift",
    "replay_state_drift",
    "c_harness_path_drift",
    "helper_count_drift",
]


def phase1_readme_text() -> str:
    return """# scripts/zigux

## Phase 1

- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence
"""


def replay_blockers_text() -> str:
    return """{
  \"status\": \"parked\",
  \"lane_sequencing\": {
    \"manifest\": \"zigux/tests/fixtures/phase1_helper_manifest.json\",
    \"shared_replay_parked_helper_count\": 9,
    \"shared_replay_parked_helpers\": [
      \"tools/lib/argv_split.zig\",
      \"tools/lib/cmdline.zig\",
      \"tools/lib/ctype.zig\",
      \"tools/lib/hweight.zig\",
      \"tools/lib/list_sort.zig\",
      \"tools/lib/slab.zig\",
      \"tools/lib/str_error_r.zig\",
      \"tools/lib/vsprintf.zig\",
      \"tools/lib/zalloc.zig\"
    ],
    \"direct_anchor_followup_helper_count\": 4,
    \"direct_anchor_followup_helpers\": [
      \"tools/lib/bitmap.zig\",
      \"tools/lib/find_bit.zig\",
      \"tools/lib/rbtree.zig\",
      \"tools/lib/string.zig\"
    ],
    \"anti_overlap_rule\": \"Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.\"
  },
  \"replay\": {
    \"path\": \"zigux/tests/phase1_helpers.zig\",
    \"state\": \"blocked\",
    \"blockers\": [
      {
        \"id\": \"phase1_helpers_zig_slab_zero_after_kmalloc\",
        \"kind\": \"fixture_mismatch\",
        \"path\": \"tools/lib/slab.zig\",
        \"field\": \"slab.zero_after_kmalloc\",
        \"expected\": true,
        \"actual\": false
      }
    ]
  },
  \"c_harness\": {
    \"path\": \"zigux/tests/fixtures/phase1_helpers_c_harness.c\",
    \"state\": \"blocked\",
    \"reason\": \"The old host-side parity route still depends on helper `tools/lib/*.c` inputs that current master no longer ships beside the Phase 1 `.zig` ports.\",
    \"helper_count\": 13,
    \"helpers\": [
      \"tools/lib/argv_split.zig\",
      \"tools/lib/bitmap.zig\",
      \"tools/lib/cmdline.zig\",
      \"tools/lib/ctype.zig\",
      \"tools/lib/find_bit.zig\",
      \"tools/lib/hweight.zig\",
      \"tools/lib/list_sort.zig\",
      \"tools/lib/rbtree.zig\",
      \"tools/lib/slab.zig\",
      \"tools/lib/str_error_r.zig\",
      \"tools/lib/string.zig\",
      \"tools/lib/vsprintf.zig\",
      \"tools/lib/zalloc.zig\"
    ],
    \"blocker_id\": \"phase1_helpers_c_harness_missing_c_sources\"
  }
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> object:
    return json.loads(load_text(path))


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def validate(root: Path) -> list[str]:
    readme_path = root / README_REL
    blockers_path = root / BLOCKERS_REL
    readme_text = load_text(readme_path)
    blockers = load_json(blockers_path)
    require(isinstance(blockers, dict), "phase1_replay_blockers_type")

    for marker in README_REQUIRED_MARKERS:
        require(marker in readme_text, f"readme_marker_missing:{marker}")

    lane_sequencing = blockers.get("lane_sequencing")
    replay = blockers.get("replay")
    c_harness = blockers.get("c_harness")
    require(isinstance(lane_sequencing, dict), "lane_sequencing_type")
    require(isinstance(replay, dict), "replay_type")
    require(isinstance(c_harness, dict), "c_harness_type")

    shared_helpers = lane_sequencing.get("shared_replay_parked_helpers")
    direct_helpers = lane_sequencing.get("direct_anchor_followup_helpers")
    require(lane_sequencing.get("manifest") == MANIFEST_REL, "manifest_path")
    require(isinstance(shared_helpers, list), "shared_helpers_type")
    require(isinstance(direct_helpers, list), "direct_helpers_type")
    require(
        lane_sequencing.get("shared_replay_parked_helper_count") == len(shared_helpers),
        "shared_helper_count",
    )
    require(
        lane_sequencing.get("direct_anchor_followup_helper_count") == len(direct_helpers),
        "direct_helper_count",
    )
    require(
        "shared-replay parked helpers reopen only for packet drift"
        in lane_sequencing.get("anti_overlap_rule", ""),
        "anti_overlap_rule_summary",
    )

    require(replay.get("path") == REPLAY_REL, "replay_path")
    require(replay.get("state") == "blocked", "replay_state")
    replay_blockers = replay.get("blockers")
    require(isinstance(replay_blockers, list) and replay_blockers, "replay_blockers")
    first_blocker = replay_blockers[0]
    require(isinstance(first_blocker, dict), "replay_blocker_type")
    require(first_blocker.get("path") == "tools/lib/slab.zig", "replay_blocker_path")
    require(
        first_blocker.get("field") == "slab.zero_after_kmalloc",
        "replay_blocker_field",
    )
    require(first_blocker.get("expected") is True, "replay_blocker_expected")
    require(first_blocker.get("actual") is False, "replay_blocker_actual")

    require(c_harness.get("path") == C_HARNESS_REL, "c_harness_path")
    require(c_harness.get("state") == "blocked", "c_harness_state")
    c_harness_helpers = c_harness.get("helpers")
    require(isinstance(c_harness_helpers, list), "c_harness_helpers_type")
    require(c_harness.get("helper_count") == len(c_harness_helpers), "c_harness_helper_count")
    require(
        "tools/lib/*.c" in c_harness.get("reason", ""),
        "c_harness_reason",
    )

    return [
        f"PHASE1_README_REPLAY_BLOCKERS_GAP_COUNT=4",
        f"PHASE1_README_REPLAY_BLOCKERS_SHARED_HELPER_COUNT={len(shared_helpers)}",
        f"PHASE1_README_REPLAY_BLOCKERS_DIRECT_HELPER_COUNT={len(direct_helpers)}",
        f"PHASE1_README_REPLAY_BLOCKERS_REPLAY_STATE={replay['state']}",
        f"PHASE1_README_REPLAY_BLOCKERS_C_HARNESS_STATE={c_harness['state']}",
    ]


def write_sample_root(root: Path, *, readme_text: str, blockers_text: str) -> None:
    (root / README_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / BLOCKERS_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / README_REL).write_text(readme_text, encoding="utf-8")
    (root / BLOCKERS_REL).write_text(blockers_text, encoding="utf-8")


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_readme_blockers_") as tmp_dir:
        root = Path(tmp_dir)
        readme_text = phase1_readme_text()
        blockers_text = replay_blockers_text()
        write_sample_root(root, readme_text=readme_text, blockers_text=blockers_text)
        require(validate(root)[0] == "PHASE1_README_REPLAY_BLOCKERS_GAP_COUNT=4", "round_trip")
        covered.append("round_trip")

        write_sample_root(
            root,
            readme_text=readme_text.replace("`scripts/zigux/check-phase1-parity.py`, ", "", 1),
            blockers_text=blockers_text,
        )
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc).startswith("readme_marker_missing:"), "missing_readme_marker")
        else:
            raise AssertionError("missing_readme_marker")
        covered.append("missing_readme_marker")

        write_sample_root(
            root,
            readme_text=readme_text.replace(
                "older validator-first, parity, and replay routes as historical packet members",
                "older validator-first and parity routes as historical packet members",
                1,
            ),
            blockers_text=blockers_text,
        )
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc).startswith("readme_marker_missing:"), "summary_marker_drift")
        else:
            raise AssertionError("summary_marker_drift")
        covered.append("summary_marker_drift")

        write_sample_root(
            root,
            readme_text=readme_text,
            blockers_text=blockers_text.replace('"state": "blocked"', '"state": "present"', 1),
        )
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc) == "replay_state", "replay_state_drift")
        else:
            raise AssertionError("replay_state_drift")
        covered.append("replay_state_drift")

        write_sample_root(
            root,
            readme_text=readme_text,
            blockers_text=blockers_text.replace(C_HARNESS_REL, "zigux/tests/fixtures/phase1_helpers_legacy.c", 1),
        )
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc) == "c_harness_path", "c_harness_path_drift")
        else:
            raise AssertionError("c_harness_path_drift")
        covered.append("c_harness_path_drift")

        write_sample_root(
            root,
            readme_text=readme_text,
            blockers_text=blockers_text.replace('"helper_count": 13', '"helper_count": 12', 1),
        )
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc) == "c_harness_helper_count", "helper_count_drift")
        else:
            raise AssertionError("helper_count_drift")
        covered.append("helper_count_drift")

    require(covered == SELF_TEST_CASES, "self_test_catalog")
    print("PHASE1_README_REPLAY_BLOCKERS_SELF_TEST=pass")
    print(f"PHASE1_README_REPLAY_BLOCKERS_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print(
        "PHASE1_README_REPLAY_BLOCKERS_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    for line in ["PHASE1_README_REPLAY_BLOCKERS=pass", *validate(args.root)]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
