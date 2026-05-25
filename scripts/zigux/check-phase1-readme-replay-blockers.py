#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
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
EXPECTED_SHARED_HELPER_COUNT = 9
EXPECTED_DIRECT_HELPER_COUNT = 4
EXPECTED_REPLAY_BLOCKER_FIELD = "slab.zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_EXPECTED = True
EXPECTED_REPLAY_BLOCKER_ACTUAL = False
SELF_TEST_CASES = [
    "round_trip",
    "missing_readme_marker",
    "readme_is_directory",
    "blockers_is_directory",
    "blockers_invalid_json",
    "blockers_duplicate_key",
    "replay_state_drift",
    "c_harness_path_drift",
    "helper_count_drift",
    "blocker_evidence_drift",
]


class DuplicateKeyError(ValueError):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check the scripts-root Phase 1 replay-blocker contract."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def unique_object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


def load_json_object(path: Path) -> object:
    return json.loads(load_text(path), object_pairs_hook=unique_object_pairs)


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def validate(root: Path) -> list[str]:
    readme_path = root / README_REL
    blockers_path = root / BLOCKERS_REL
    require(readme_path.exists(), f"missing:{README_REL.as_posix()}")
    require(readme_path.is_file(), f"not_a_file:{README_REL.as_posix()}")
    require(blockers_path.exists(), f"missing:{BLOCKERS_REL.as_posix()}")
    require(blockers_path.is_file(), f"not_a_file:{BLOCKERS_REL.as_posix()}")

    readme_text = load_text(readme_path)
    try:
        blockers = load_json_object(blockers_path)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid_json:{BLOCKERS_REL.as_posix()}:{exc.lineno}:{exc.colno}:{exc.msg}"
        ) from exc
    except DuplicateKeyError as exc:
        raise ValueError(f"duplicate_key:{BLOCKERS_REL.as_posix()}:{exc}") from exc

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
    require(len(shared_helpers) == EXPECTED_SHARED_HELPER_COUNT, "shared_helper_size")
    require(len(direct_helpers) == EXPECTED_DIRECT_HELPER_COUNT, "direct_helper_size")
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
        first_blocker.get("field") == EXPECTED_REPLAY_BLOCKER_FIELD,
        "replay_blocker_field",
    )
    require(
        first_blocker.get("expected") is EXPECTED_REPLAY_BLOCKER_EXPECTED,
        "replay_blocker_expected",
    )
    require(
        first_blocker.get("actual") is EXPECTED_REPLAY_BLOCKER_ACTUAL,
        "replay_blocker_actual",
    )
    evidence = first_blocker.get("evidence")
    require(isinstance(evidence, str), "replay_blocker_evidence_type")
    require("phase1_helpers.zig:595" in evidence, "replay_blocker_evidence")
    require("tools/lib/slab.zig" in evidence, "replay_blocker_evidence_path")
    require("expects `true`" in evidence, "replay_blocker_evidence_expected")
    require("produced `false`" in evidence, "replay_blocker_evidence_actual")

    require(c_harness.get("path") == C_HARNESS_REL, "c_harness_path")
    require(c_harness.get("state") == "blocked", "c_harness_state")
    c_harness_helpers = c_harness.get("helpers")
    require(isinstance(c_harness_helpers, list), "c_harness_helpers_type")
    require(c_harness.get("helper_count") == len(c_harness_helpers), "c_harness_helper_count")
    require(
        c_harness.get("helper_count") == len(shared_helpers) + len(direct_helpers),
        "c_harness_total_helper_count",
    )
    require(
        "tools/lib/*.c" in c_harness.get("reason", ""),
        "c_harness_reason",
    )
    require(
        sorted(c_harness_helpers) == sorted(shared_helpers + direct_helpers),
        "c_harness_helper_roster",
    )

    return [
        "PHASE1_README_REPLAY_BLOCKERS_GAP_COUNT=4",
        f"PHASE1_README_REPLAY_BLOCKERS_SHARED_HELPER_COUNT={len(shared_helpers)}",
        f"PHASE1_README_REPLAY_BLOCKERS_DIRECT_HELPER_COUNT={len(direct_helpers)}",
        f"PHASE1_README_REPLAY_BLOCKERS_REPLAY_STATE={replay['state']}",
        f"PHASE1_README_REPLAY_BLOCKERS_C_HARNESS_STATE={c_harness['state']}",
    ]


def phase1_readme_text() -> str:
    return """# scripts/zigux

## Phase 1

- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence
"""


def replay_blockers_text() -> str:
    return """{
  "status": "parked",
  "lane_sequencing": {
    "manifest": "zigux/tests/fixtures/phase1_helper_manifest.json",
    "shared_replay_parked_helper_count": 9,
    "shared_replay_parked_helpers": [
      "tools/lib/argv_split.zig",
      "tools/lib/cmdline.zig",
      "tools/lib/ctype.zig",
      "tools/lib/hweight.zig",
      "tools/lib/list_sort.zig",
      "tools/lib/slab.zig",
      "tools/lib/str_error_r.zig",
      "tools/lib/vsprintf.zig",
      "tools/lib/zalloc.zig"
    ],
    "direct_anchor_followup_helper_count": 4,
    "direct_anchor_followup_helpers": [
      "tools/lib/bitmap.zig",
      "tools/lib/find_bit.zig",
      "tools/lib/rbtree.zig",
      "tools/lib/string.zig"
    ],
    "anti_overlap_rule": "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys."
  },
  "replay": {
    "path": "zigux/tests/phase1_helpers.zig",
    "state": "blocked",
    "blockers": [
      {
        "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
        "kind": "fixture_mismatch",
        "path": "tools/lib/slab.zig",
        "field": "slab.zero_after_kmalloc",
        "expected": true,
        "actual": false,
        "evidence": "Focused 2026-05-17 scratch replay of `zig build test --build-file zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` because the committed fixture expects `true` while `tools/lib/slab.zig` still produced `false`."
      }
    ]
  },
  "c_harness": {
    "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "state": "blocked",
    "reason": "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that current master no longer ships beside the Phase 1 `.zig` ports.",
    "helper_count": 13,
    "helpers": [
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
      "tools/lib/zalloc.zig"
    ],
    "blocker_id": "phase1_helpers_c_harness_missing_c_sources"
  }
}
"""


def write_sample_root(root: Path, *, readme_text: str, blockers_text: str) -> None:
    (root / README_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / BLOCKERS_REL.parent).mkdir(parents=True, exist_ok=True)
    for path in (root / README_REL, root / BLOCKERS_REL):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
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

        write_sample_root(root, readme_text=readme_text, blockers_text=blockers_text)
        (root / README_REL).unlink()
        (root / README_REL).mkdir()
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc) == f"not_a_file:{README_REL.as_posix()}", "readme_is_directory")
        else:
            raise AssertionError("readme_is_directory")
        covered.append("readme_is_directory")

        write_sample_root(root, readme_text=readme_text, blockers_text=blockers_text)
        (root / BLOCKERS_REL).unlink()
        (root / BLOCKERS_REL).mkdir()
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc) == f"not_a_file:{BLOCKERS_REL.as_posix()}", "blockers_is_directory")
        else:
            raise AssertionError("blockers_is_directory")
        covered.append("blockers_is_directory")

        write_sample_root(
            root,
            readme_text=readme_text,
            blockers_text='{"status": "parked", "replay": {"path": "zigux/tests/phase1_helpers.zig", }',
        )
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc).startswith(f"invalid_json:{BLOCKERS_REL.as_posix()}:"), "blockers_invalid_json")
        else:
            raise AssertionError("blockers_invalid_json")
        covered.append("blockers_invalid_json")

        write_sample_root(
            root,
            readme_text=readme_text,
            blockers_text='{"status":"parked","status":"blocked","lane_sequencing":{},"replay":{},"c_harness":{}}',
        )
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc).startswith(f"duplicate_key:{BLOCKERS_REL.as_posix()}:"), "blockers_duplicate_key")
        else:
            raise AssertionError("blockers_duplicate_key")
        covered.append("blockers_duplicate_key")

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

        write_sample_root(
            root,
            readme_text=readme_text,
            blockers_text=blockers_text.replace("phase1_helpers.zig:595", "phase1_helpers.zig:594", 1),
        )
        try:
            validate(root)
        except ValueError as exc:
            require(str(exc) == "replay_blocker_evidence", "blocker_evidence_drift")
        else:
            raise AssertionError("blocker_evidence_drift")
        covered.append("blocker_evidence_drift")

    require(covered == SELF_TEST_CASES, "self_test_catalog")
    print("PHASE1_README_REPLAY_BLOCKERS_SELF_TEST=pass")
    print(f"PHASE1_README_REPLAY_BLOCKERS_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE1_README_REPLAY_BLOCKERS_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        return run_self_test()
    try:
        lines = validate(args.root.resolve())
    except ValueError as exc:
        print("PHASE1_README_REPLAY_BLOCKERS=fail")
        print(f"PHASE1_README_REPLAY_BLOCKERS_ROOT={args.root.resolve()}")
        print(f"PHASE1_README_REPLAY_BLOCKERS_ISSUE={exc}")
        return 1
    print("PHASE1_README_REPLAY_BLOCKERS=pass")
    print(f"PHASE1_README_REPLAY_BLOCKERS_ROOT={args.root.resolve()}")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
