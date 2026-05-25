#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_REL = Path("zigux") / "tests" / "fixtures" / "phase1_helpers.json"
BLOCKERS_REL = Path("zigux") / "tests" / "fixtures" / "phase1_replay_blockers.json"

EXPECTED_HELPER_PATHS = [
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
EXPECTED_FIXTURE_KEYS = [
    "argv_split",
    "bitmap",
    "cmdline",
    "ctype",
    "find_bit",
    "hweight",
    "list_sort",
    "rbtree",
    "slab",
    "str_error_r",
    "string",
    "vsprintf",
    "zalloc",
]
SLAB_BLOCKER = {
    "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
    "kind": "fixture_mismatch",
    "path": "tools/lib/slab.zig",
    "field": "slab.zero_after_kmalloc",
    "expected": True,
    "actual": False,
}
SELF_TEST_CASES = [
    "round_trip",
    "fixture_helper_set_drift",
    "fixture_slab_expected_drift",
    "blocker_expected_drift",
    "blocker_actual_drift",
    "replay_path_drift",
    "replay_state_drift",
    "c_harness_helper_count_drift",
    "c_harness_helper_roster_drift",
    "c_harness_blocker_id_drift",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check the live Phase 1 parity fixture against the parked replay-blocker "
            "packet."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def sample_fixture_payload() -> dict[str, object]:
    return {
        "find_bit": {"tail_clamped_last": 67, "tail_clamped_empty_last": 69},
        "bitmap": {"weight": 3, "full_after_fill": True},
        "string": {"strtobool_y": True, "strtobool_invalid": 184},
        "rbtree": {"empty_root": True, "cached_leftmost_return_serials": [0, -1, 2, -1]},
        "argv_split": {"argc": 3, "blank_argc": 0},
        "cmdline": {"decimal_k": {"value": 65536, "rest": " rest"}},
        "ctype": {"mask_A": 65, "toupper_z": 90},
        "hweight": {"w64": 32},
        "list_sort": {"tri_sorted_keys": [1, 1, 2, 3, 3]},
        "zalloc": {"zeroed": True, "freed_is_null": True},
        "str_error_r": {"enoent": "No such file or directory"},
        "slab": {
            "null_without_reclaim": True,
            "alloc_count_after_kmalloc": 1,
            "zero_after_kmalloc": True,
            "alloc_count_after_kmalloc_free": 0,
            "array_zeroed": True,
            "alloc_count_after_kmalloc_array": 1,
            "alloc_count_after_kmalloc_array_free": 0,
            "slab_is_available": True,
        },
        "vsprintf": {"scnprintf_text": "zigux:7", "scnprintf_len": 7},
    }


def sample_blockers_payload() -> dict[str, object]:
    return {
        "status": "parked",
        "lane_sequencing": {
            "manifest": "zigux/tests/fixtures/phase1_helper_manifest.json",
            "shared_replay_parked_helper_count": 9,
            "direct_anchor_followup_helper_count": 4,
        },
        "replay": {
            "path": "zigux/tests/phase1_helpers.zig",
            "state": "blocked",
            "blockers": [
                {
                    **SLAB_BLOCKER,
                    "evidence": (
                        "Focused 2026-05-17 scratch replay of `zig build test --build-file "
                        "zigux/tests/build.zig --summary all` failed at "
                        "`phase1_helpers.zig:595` because the committed fixture expects "
                        "`true` while `tools/lib/slab.zig` still produced `false`."
                    ),
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": (
                "The old host-side parity route still depends on helper `tools/lib/*.c` "
                "inputs that current master no longer ships beside the Phase 1 `.zig` ports."
            ),
            "helper_count": len(EXPECTED_HELPER_PATHS),
            "helpers": EXPECTED_HELPER_PATHS,
            "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
        },
    }


def write_sample_root(root: Path) -> None:
    write_text(
        root / FIXTURE_REL,
        json.dumps(sample_fixture_payload(), separators=(",", ":"), ensure_ascii=True) + "\n",
    )
    write_text(
        root / BLOCKERS_REL,
        json.dumps(sample_blockers_payload(), indent=2, ensure_ascii=True) + "\n",
    )


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(root: Path) -> list[str]:
    fixture_path = root / FIXTURE_REL
    blockers_path = root / BLOCKERS_REL
    ensure(fixture_path.exists(), f"missing required file: {FIXTURE_REL}")
    ensure(blockers_path.exists(), f"missing required file: {BLOCKERS_REL}")

    fixture = load_json(fixture_path)
    blockers = load_json(blockers_path)

    ensure(isinstance(fixture, dict), "fixture must be a JSON object")
    ensure(isinstance(blockers, dict), "blockers must be a JSON object")

    fixture_keys = list(fixture.keys())
    ensure(len(fixture_keys) == len(EXPECTED_FIXTURE_KEYS), "fixture helper count drifted")
    ensure(set(fixture_keys) == set(EXPECTED_FIXTURE_KEYS), "fixture helper set drifted")

    slab = fixture.get("slab")
    ensure(isinstance(slab, dict), "fixture slab payload must be an object")
    ensure(slab.get("zero_after_kmalloc") is True, "fixture slab zero_after_kmalloc drifted")

    replay = blockers.get("replay")
    ensure(isinstance(replay, dict), "replay must be an object")
    ensure(replay.get("path") == "zigux/tests/phase1_helpers.zig", "replay path drifted")
    ensure(replay.get("state") == "blocked", "replay state drifted")

    replay_blockers = replay.get("blockers")
    ensure(isinstance(replay_blockers, list) and replay_blockers, "replay blockers missing")
    replay_slab = replay_blockers[0]
    ensure(isinstance(replay_slab, dict), "replay slab blocker must be an object")
    for key, value in SLAB_BLOCKER.items():
        ensure(replay_slab.get(key) == value, f"replay slab blocker drifted: {key}")
    ensure(
        "committed fixture expects `true`" in str(replay_slab.get("evidence")),
        "replay slab evidence lost fixture-expects marker",
    )
    ensure(
        "still produced `false`" in str(replay_slab.get("evidence")),
        "replay slab evidence lost actual-false marker",
    )

    c_harness = blockers.get("c_harness")
    ensure(isinstance(c_harness, dict), "c_harness must be an object")
    ensure(c_harness.get("state") == "blocked", "c_harness state drifted")
    ensure(
        c_harness.get("path") == "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        "c_harness path drifted",
    )
    ensure(
        c_harness.get("helper_count") == len(EXPECTED_HELPER_PATHS),
        "c_harness helper count drifted",
    )
    ensure(c_harness.get("helpers") == EXPECTED_HELPER_PATHS, "c_harness helper roster drifted")
    ensure(
        c_harness.get("blocker_id") == "phase1_helpers_c_harness_missing_c_sources",
        "c_harness blocker id drifted",
    )

    return [
        "PHASE1_FIXTURE_BLOCKER_ALIGNMENT=pass",
        f"PHASE1_FIXTURE_BLOCKER_ALIGNMENT_FIXTURE_HELPER_COUNT={len(EXPECTED_FIXTURE_KEYS)}",
        f"PHASE1_FIXTURE_BLOCKER_ALIGNMENT_REPLAY_HELPER_COUNT={len(EXPECTED_HELPER_PATHS)}",
        "PHASE1_FIXTURE_BLOCKER_ALIGNMENT_SLAB_EXPECTED=true",
        "PHASE1_FIXTURE_BLOCKER_ALIGNMENT_SLAB_ACTUAL=false",
        "PHASE1_FIXTURE_BLOCKER_ALIGNMENT_C_HARNESS_STATE=blocked",
    ]


def expect_failure(label: str, callback) -> None:
    try:
        callback()
    except AssertionError:
        return
    raise AssertionError(f"expected failure for {label}")


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_fixture_blocker_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        expected_lines = [
            "PHASE1_FIXTURE_BLOCKER_ALIGNMENT=pass",
            "PHASE1_FIXTURE_BLOCKER_ALIGNMENT_FIXTURE_HELPER_COUNT=13",
            "PHASE1_FIXTURE_BLOCKER_ALIGNMENT_REPLAY_HELPER_COUNT=13",
            "PHASE1_FIXTURE_BLOCKER_ALIGNMENT_SLAB_EXPECTED=true",
            "PHASE1_FIXTURE_BLOCKER_ALIGNMENT_SLAB_ACTUAL=false",
            "PHASE1_FIXTURE_BLOCKER_ALIGNMENT_C_HARNESS_STATE=blocked",
        ]
        ensure(validate(root) == expected_lines, "round-trip validation drifted")
        covered.append("round_trip")

        fixture_path = root / FIXTURE_REL
        blockers_path = root / BLOCKERS_REL
        original_fixture = load_json(fixture_path)
        original_blockers = load_json(blockers_path)

        drift = json.loads(json.dumps(original_fixture))
        drift["phase1_helpers"] = drift.pop("slab")
        write_text(fixture_path, json.dumps(drift, separators=(",", ":")) + "\n")
        expect_failure("fixture_helper_set_drift", lambda: validate(root))
        write_text(fixture_path, json.dumps(original_fixture, separators=(",", ":")) + "\n")
        covered.append("fixture_helper_set_drift")

        drift = json.loads(json.dumps(original_fixture))
        drift["slab"]["zero_after_kmalloc"] = False
        write_text(fixture_path, json.dumps(drift, separators=(",", ":")) + "\n")
        expect_failure("fixture_slab_expected_drift", lambda: validate(root))
        write_text(fixture_path, json.dumps(original_fixture, separators=(",", ":")) + "\n")
        covered.append("fixture_slab_expected_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["replay"]["blockers"][0]["expected"] = False
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("blocker_expected_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("blocker_expected_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["replay"]["blockers"][0]["actual"] = True
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("blocker_actual_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("blocker_actual_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["replay"]["path"] = "zigux/tests/phase1_helper_ports.zig"
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("replay_path_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("replay_path_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["replay"]["state"] = "ready"
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("replay_state_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("replay_state_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["c_harness"]["helper_count"] = 12
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("c_harness_helper_count_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("c_harness_helper_count_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["c_harness"]["helpers"] = EXPECTED_HELPER_PATHS[:-1]
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("c_harness_helper_roster_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("c_harness_helper_roster_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["c_harness"]["blocker_id"] = "phase1_helpers_c_harness_reopened"
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("c_harness_blocker_id_drift", lambda: validate(root))
        covered.append("c_harness_blocker_id_drift")

    ensure(covered == SELF_TEST_CASES, f"self-test catalog drifted: {covered}")
    print("PHASE1_FIXTURE_BLOCKER_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_FIXTURE_BLOCKER_ALIGNMENT_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print(
        "PHASE1_FIXTURE_BLOCKER_ALIGNMENT_SELF_TEST_CASES="
        + ",".join(SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0
    if args.self_test:
        return run_self_test()
    for line in validate(args.root.resolve()):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
