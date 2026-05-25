#!/usr/bin/env python3
"""Guard the current Phase 1 parity-fixture plus artifact-diff packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HELPER_TO_SECTION = {
    "tools/lib/argv_split.zig": "argv_split",
    "tools/lib/bitmap.zig": "bitmap",
    "tools/lib/cmdline.zig": "cmdline",
    "tools/lib/ctype.zig": "ctype",
    "tools/lib/find_bit.zig": "find_bit",
    "tools/lib/hweight.zig": "hweight",
    "tools/lib/list_sort.zig": "list_sort",
    "tools/lib/rbtree.zig": "rbtree",
    "tools/lib/slab.zig": "slab",
    "tools/lib/str_error_r.zig": "str_error_r",
    "tools/lib/string.zig": "string",
    "tools/lib/vsprintf.zig": "vsprintf",
    "tools/lib/zalloc.zig": "zalloc",
}
HELPER_PATHS = list(HELPER_TO_SECTION)
FIXTURE_SECTIONS = [HELPER_TO_SECTION[path] for path in HELPER_PATHS]
SHARED_HELPERS = [
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
DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]
ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)
ARTIFACT_DIFF_MARKERS = [
    'MODE_CHOICES = ("text", "json", "bytes")',
    'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
    '"usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test]"',
    '"json_pass"',
    '"bytes_pass"',
    '"legacy_sha256_alias"',
]
README_PRESENT_MARKERS = [
    "python3 scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "bitmap, find_bit, rbtree, and string",
]
README_REQUIRED_GAPS = [
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
]
CLOSURE_REQUIRED_GAPS = [
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
]
FIXTURE_KEY_REQUIREMENTS = {
    "bitmap": ["partial_xor_nbits", "partial_xor_masked_values"],
    "find_bit": ["inclusive_boundary_next", "tail_clamped_last"],
    "list_sort": ["tri_sorted_keys", "bool_sorted_keys"],
    "rbtree": ["cached_leftmost_return_serials"],
    "slab": ["zero_after_kmalloc"],
    "string": ["replace_char_cstr_bytes", "memchr_inv_index"],
}
REPLAY_BLOCKER_EVIDENCE = {
    "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
    "kind": "fixture_mismatch",
    "path": "tools/lib/slab.zig",
    "field": "slab.zero_after_kmalloc",
    "expected": True,
    "actual": False,
}
C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
C_HARNESS_REASON_MARKER = (
    "current master no longer ships beside the Phase 1 `.zig` ports."
)
SELF_TEST_CASES = [
    "sample_root_pass",
    "sample_root_writer",
    "missing_artifact_marker",
    "helper_count_drift",
    "shared_helper_drift",
    "direct_helper_drift",
    "blocker_helper_mismatch",
    "blocker_state_drift",
    "blocker_anti_overlap_rule_drift",
    "replay_blocker_evidence_drift",
    "c_harness_reason_drift",
    "fixture_section_missing",
    "fixture_key_missing",
    "readme_gap_missing",
    "closure_gap_packet_missing",
    "closure_gap_missing",
]

PHASE1_CURRENT_GAP_PACKET_LINE = (
    "PHASE1_CURRENT_GAP_PACKET=" + ",".join(CLOSURE_REQUIRED_GAPS)
)


class CheckFailure(Exception):
    pass


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def ensure_markers(text: str, markers: list[str], *, label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    ensure(not missing, f"{label} missing markers: {', '.join(missing)}")


def check_artifact_diff(root: Path) -> None:
    ensure_markers(
        read_text(root / "scripts/zigux/artifact_diff.py"),
        ARTIFACT_DIFF_MARKERS,
        label="artifact_diff",
    )


def check_manifest(root: Path) -> dict[str, object]:
    manifest = read_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json")
    ensure(isinstance(manifest, dict), "phase1_helper_manifest.json must be an object")
    ensure(manifest.get("phase") == "Phase 1", "phase1 helper manifest phase drifted")
    ensure(manifest.get("status") == "closed", "phase1 helper manifest status drifted")
    ensure(manifest.get("helper_count") == len(HELPER_PATHS), "phase1 helper count drifted")
    ensure(manifest.get("helpers") == HELPER_PATHS, "phase1 helper roster drifted")

    lane = manifest.get("lane_sequencing")
    ensure(isinstance(lane, dict), "lane_sequencing missing from helper manifest")
    ensure(
        lane.get("shared_replay_parked_helpers") == SHARED_HELPERS,
        "shared helper packet drifted",
    )
    ensure(
        lane.get("direct_anchor_followup_helpers") == DIRECT_HELPERS,
        "direct helper packet drifted",
    )
    ensure(
        lane.get("anti_overlap_rule") == ANTI_OVERLAP_RULE,
        "manifest anti-overlap rule drifted",
    )
    return manifest


def check_replay_blockers(root: Path, manifest: dict[str, object]) -> None:
    blockers = read_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json")
    ensure(isinstance(blockers, dict), "phase1_replay_blockers.json must be an object")
    ensure(blockers.get("status") == "parked", "phase1 replay blocker status drifted")

    lane = blockers.get("lane_sequencing")
    ensure(isinstance(lane, dict), "phase1 replay blocker lane sequencing missing")
    ensure(
        lane.get("manifest") == "zigux/tests/fixtures/phase1_helper_manifest.json",
        "phase1 replay blocker manifest path drifted",
    )
    ensure(
        lane.get("shared_replay_parked_helper_count") == len(SHARED_HELPERS),
        "phase1 replay blocker shared helper count drifted",
    )
    ensure(
        lane.get("direct_anchor_followup_helper_count") == len(DIRECT_HELPERS),
        "phase1 replay blocker direct helper count drifted",
    )
    ensure(
        lane.get("shared_replay_parked_helpers")
        == manifest["lane_sequencing"]["shared_replay_parked_helpers"],
        "phase1 replay blocker shared helper roster drifted",
    )
    ensure(
        lane.get("direct_anchor_followup_helpers")
        == manifest["lane_sequencing"]["direct_anchor_followup_helpers"],
        "phase1 replay blocker direct helper roster drifted",
    )
    ensure(
        lane.get("anti_overlap_rule") == ANTI_OVERLAP_RULE,
        "phase1 replay blocker anti-overlap rule drifted",
    )

    replay = blockers.get("replay")
    ensure(isinstance(replay, dict), "phase1 replay blocker replay stanza missing")
    ensure(replay.get("path") == "zigux/tests/phase1_helpers.zig", "phase1 replay path drifted")
    ensure(replay.get("state") == "blocked", "phase1 replay state drifted")
    replay_blockers = replay.get("blockers")
    ensure(
        isinstance(replay_blockers, list) and len(replay_blockers) == 1,
        "phase1 replay blocker evidence roster drifted",
    )
    evidence = replay_blockers[0]
    ensure(isinstance(evidence, dict), "phase1 replay blocker evidence entry missing")
    for key, expected_value in REPLAY_BLOCKER_EVIDENCE.items():
        ensure(
            evidence.get(key) == expected_value,
            f"phase1 replay blocker evidence drifted at {key}",
        )
    evidence_text = str(evidence.get("evidence", ""))
    ensure(
        "committed fixture expects `true` while `tools/lib/slab.zig` still produced `false`"
        in evidence_text,
        "phase1 replay blocker evidence summary drifted",
    )

    c_harness = blockers.get("c_harness")
    ensure(isinstance(c_harness, dict), "phase1 replay blocker c_harness stanza missing")
    ensure(
        c_harness.get("path") == "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        "phase1 c_harness path drifted",
    )
    ensure(c_harness.get("state") == "blocked", "phase1 c_harness state drifted")
    ensure(c_harness.get("helper_count") == len(HELPER_PATHS), "phase1 c_harness count drifted")
    ensure(c_harness.get("helpers") == manifest.get("helpers"), "phase1 c_harness roster drifted")
    ensure(
        c_harness.get("blocker_id") == C_HARNESS_BLOCKER_ID,
        "phase1 c_harness blocker id drifted",
    )
    ensure(
        C_HARNESS_REASON_MARKER in str(c_harness.get("reason", "")),
        "phase1 c_harness blocker reason drifted",
    )


def check_fixture(root: Path, manifest: dict[str, object]) -> None:
    fixture = read_json(root / "zigux/tests/fixtures/phase1_helpers.json")
    ensure(isinstance(fixture, dict), "phase1_helpers.json must be an object")
    ensure(sorted(fixture.keys()) == sorted(FIXTURE_SECTIONS), "phase1 fixture sections drifted")
    ensure(len(fixture) == len(manifest["helpers"]), "phase1 fixture section count drifted")
    for section, required_keys in FIXTURE_KEY_REQUIREMENTS.items():
        value = fixture.get(section)
        ensure(isinstance(value, dict), f"phase1 fixture section {section} missing or invalid")
        for key in required_keys:
            ensure(key in value, f"phase1 fixture section {section} missing key {key}")
    ensure(
        fixture["slab"]["zero_after_kmalloc"] is True,
        "phase1 slab.zero_after_kmalloc drifted",
    )


def check_readme(root: Path) -> None:
    readme = read_text(root / "scripts/zigux/README.md")
    ensure_markers(readme, README_PRESENT_MARKERS, label="phase1 readme packet")
    ensure_markers(readme, README_REQUIRED_GAPS, label="phase1 readme gaps")


def check_closure_note(root: Path) -> None:
    closure = read_text(root / "Documentation/zigux/phase1-closure.md")
    ensure(
        "The older validator-first and replay-side closure companions remain broader closure-stack references"
        in closure,
        "phase1 closure broader-companion summary drifted",
    )
    ensure_markers(closure, CLOSURE_REQUIRED_GAPS, label="phase1 closure gaps")
    ensure(
        PHASE1_CURRENT_GAP_PACKET_LINE in closure,
        "phase1 closure gap packet drifted",
    )


def check_root(root: Path) -> dict[str, int]:
    manifest = check_manifest(root)
    check_artifact_diff(root)
    check_replay_blockers(root, manifest)
    check_fixture(root, manifest)
    check_readme(root)
    check_closure_note(root)
    return {
        "artifact_mode_count": 3,
        "closure_gap_count": len(CLOSURE_REQUIRED_GAPS),
        "direct_helper_count": len(DIRECT_HELPERS),
        "fixture_section_count": len(FIXTURE_SECTIONS),
        "helper_count": len(HELPER_PATHS),
        "present_file_count": 6,
        "readme_gap_count": len(README_REQUIRED_GAPS),
        "replay_blocker_count": 1,
        "shared_helper_count": len(SHARED_HELPERS),
    }


def sample_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(HELPER_PATHS),
        "helpers": HELPER_PATHS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": SHARED_HELPERS,
            "direct_anchor_followup_helpers": DIRECT_HELPERS,
            "rule_summary": (
                "Phase 1 helper follow-up stays parked on shared replay for the nine helpers "
                "above, while bitmap, find_bit, rbtree, and string keep the only bounded "
                "direct helper-local follow-up anchors on current master."
            ),
            "anti_overlap_rule": ANTI_OVERLAP_RULE,
        },
    }


def sample_replay_blockers() -> dict[str, object]:
    return {
        "status": "parked",
        "lane_sequencing": {
            "manifest": "zigux/tests/fixtures/phase1_helper_manifest.json",
            "shared_replay_parked_helper_count": len(SHARED_HELPERS),
            "shared_replay_parked_helpers": SHARED_HELPERS,
            "direct_anchor_followup_helper_count": len(DIRECT_HELPERS),
            "direct_anchor_followup_helpers": DIRECT_HELPERS,
            "anti_overlap_rule": ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": "zigux/tests/phase1_helpers.zig",
            "state": "blocked",
            "blockers": [
                {
                    **REPLAY_BLOCKER_EVIDENCE,
                    "evidence": (
                        "Focused 2026-05-17 scratch replay of `zig build test --build-file "
                        "zigux/tests/build.zig --summary all` failed because the committed "
                        "fixture expects `true` while `tools/lib/slab.zig` still produced "
                        "`false`."
                    ),
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": (
                "The old host-side parity route still depends on helper `tools/lib/*.c` inputs "
                "that current master no longer ships beside the Phase 1 `.zig` ports."
            ),
            "helper_count": len(HELPER_PATHS),
            "helpers": HELPER_PATHS,
            "blocker_id": C_HARNESS_BLOCKER_ID,
        },
    }


def sample_fixture() -> dict[str, object]:
    return {
        "argv_split": {"argc": 3},
        "bitmap": {"partial_xor_nbits": 4, "partial_xor_masked_values": [14]},
        "cmdline": {"decimal_k": {"value": 65536}},
        "ctype": {"isdigit_7": True},
        "find_bit": {"inclusive_boundary_next": 63, "tail_clamped_last": 67},
        "hweight": {"w64": 32},
        "list_sort": {"tri_sorted_keys": [1, 1, 2, 3, 3], "bool_sorted_keys": [1, 1, 2, 3, 3]},
        "rbtree": {"cached_leftmost_return_serials": [0, -1, 2, -1]},
        "slab": {"zero_after_kmalloc": True},
        "str_error_r": {"enoent": "No such file or directory"},
        "string": {"replace_char_cstr_bytes": [97, 95, 0, 45, 122], "memchr_inv_index": 4},
        "vsprintf": {"scnprintf_len": 7},
        "zalloc": {"zeroed": True},
    }


def sample_readme() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            "## Phase 1",
            "",
            "- python3 scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, and scripts/zigux/check-phase1-shared-reminder-packet.py keep the shipped closure-side packet explicit.",
            "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys.",
            "- repeated authenticated reads on current master still return missing for scripts/zigux/validate-phase1.py, scripts/zigux/check-phase1-parity.py, zigux/tests/phase1_helpers.zig, and zigux/tests/fixtures/phase1_helpers_c_harness.c, so treat those older parity and replay routes as historical packet members.",
            "",
        ]
    )


def sample_closure_note() -> str:
    return "\n".join(
        [
            "# Phase 1 Closure",
            "",
            "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.",
            "",
            "- scripts/zigux/validate-phase1.py",
            "- scripts/zigux/check-phase1-parity.py",
            "- zigux/tests/phase1_helpers.zig",
            "- zigux/tests/phase1_bench.zig",
            "- zigux/tests/fixtures/phase1_bench_expectations.json",
            "- zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "",
            f"- {PHASE1_CURRENT_GAP_PACKET_LINE}",
            "",
        ]
    )


def sample_artifact_diff() -> str:
    return "\n".join(
        [
            '#!/usr/bin/env python3',
            'MODE_CHOICES = ("text", "json", "bytes")',
            'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
            '"usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test]"',
            '"json_pass"',
            '"bytes_pass"',
            '"legacy_sha256_alias"',
            "",
        ]
    )


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_sample_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    write_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", sample_manifest())
    write_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", sample_replay_blockers())
    write_json(root / "zigux/tests/fixtures/phase1_helpers.json", sample_fixture())
    artifact_diff = root / "scripts/zigux/artifact_diff.py"
    artifact_diff.parent.mkdir(parents=True, exist_ok=True)
    artifact_diff.write_text(sample_artifact_diff(), encoding="utf-8")
    (root / "scripts/zigux/README.md").write_text(sample_readme(), encoding="utf-8")
    closure_note = root / "Documentation/zigux/phase1-closure.md"
    closure_note.parent.mkdir(parents=True, exist_ok=True)
    closure_note.write_text(sample_closure_note(), encoding="utf-8")


def expect_failure(case: str, root: Path, path: Path, old: str, new: str) -> None:
    path.write_text(new, encoding="utf-8")
    try:
        check_root(root)
    except CheckFailure:
        return
    finally:
        path.write_text(old, encoding="utf-8")
    raise AssertionError(case)


def run_self_test() -> int:
    covered: list[str] = []
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(prefix="zigux_phase1_artifact_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        counts = check_root(root)
        ensure(counts["helper_count"] == 13, "sample_root_pass")
        covered.append("sample_root_pass")

        rewritten = root / "written"
        write_sample_root(rewritten)
        counts = check_root(rewritten)
        ensure(counts["artifact_mode_count"] == 3, "sample_root_writer")
        covered.append("sample_root_writer")

        artifact_path = root / "scripts/zigux/artifact_diff.py"
        expect_failure(
            "missing_artifact_marker",
            root,
            artifact_path,
            read_text(artifact_path),
            sample_artifact_diff().replace('"legacy_sha256_alias"', '"legacy_sha256_ALIAS"'),
        )
        covered.append("missing_artifact_marker")

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        old_manifest = read_text(manifest_path)
        manifest = json.loads(old_manifest)
        manifest["helper_count"] = 12
        expect_failure(
            "helper_count_drift",
            root,
            manifest_path,
            old_manifest,
            json.dumps(manifest, indent=2) + "\n",
        )
        covered.append("helper_count_drift")

        manifest = json.loads(old_manifest)
        manifest["lane_sequencing"]["shared_replay_parked_helpers"] = SHARED_HELPERS[:-1]
        expect_failure(
            "shared_helper_drift",
            root,
            manifest_path,
            old_manifest,
            json.dumps(manifest, indent=2) + "\n",
        )
        covered.append("shared_helper_drift")

        manifest = json.loads(old_manifest)
        manifest["lane_sequencing"]["direct_anchor_followup_helpers"] = DIRECT_HELPERS[:-1]
        expect_failure(
            "direct_helper_drift",
            root,
            manifest_path,
            old_manifest,
            json.dumps(manifest, indent=2) + "\n",
        )
        covered.append("direct_helper_drift")

        blockers_path = root / "zigux/tests/fixtures/phase1_replay_blockers.json"
        old_blockers = read_text(blockers_path)
        blockers = json.loads(old_blockers)
        blockers["c_harness"]["helpers"] = HELPER_PATHS[:-1]
        expect_failure(
            "blocker_helper_mismatch",
            root,
            blockers_path,
            old_blockers,
            json.dumps(blockers, indent=2) + "\n",
        )
        covered.append("blocker_helper_mismatch")

        blockers = json.loads(old_blockers)
        blockers["replay"]["state"] = "ready"
        expect_failure(
            "blocker_state_drift",
            root,
            blockers_path,
            old_blockers,
            json.dumps(blockers, indent=2) + "\n",
        )
        covered.append("blocker_state_drift")

        blockers = json.loads(old_blockers)
        blockers["lane_sequencing"]["anti_overlap_rule"] = "drifted"
        expect_failure(
            "blocker_anti_overlap_rule_drift",
            root,
            blockers_path,
            old_blockers,
            json.dumps(blockers, indent=2) + "\n",
        )
        covered.append("blocker_anti_overlap_rule_drift")

        blockers = json.loads(old_blockers)
        blockers["replay"]["blockers"][0]["actual"] = True
        expect_failure(
            "replay_blocker_evidence_drift",
            root,
            blockers_path,
            old_blockers,
            json.dumps(blockers, indent=2) + "\n",
        )
        covered.append("replay_blocker_evidence_drift")

        blockers = json.loads(old_blockers)
        blockers["c_harness"]["reason"] = "drifted"
        expect_failure(
            "c_harness_reason_drift",
            root,
            blockers_path,
            old_blockers,
            json.dumps(blockers, indent=2) + "\n",
        )
        covered.append("c_harness_reason_drift")

        fixture_path = root / "zigux/tests/fixtures/phase1_helpers.json"
        old_fixture = read_text(fixture_path)
        fixture = json.loads(old_fixture)
        fixture.pop("vsprintf")
        expect_failure(
            "fixture_section_missing",
            root,
            fixture_path,
            old_fixture,
            json.dumps(fixture, indent=2) + "\n",
        )
        covered.append("fixture_section_missing")

        fixture = json.loads(old_fixture)
        del fixture["bitmap"]["partial_xor_nbits"]
        expect_failure(
            "fixture_key_missing",
            root,
            fixture_path,
            old_fixture,
            json.dumps(fixture, indent=2) + "\n",
        )
        covered.append("fixture_key_missing")

        readme_path = root / "scripts/zigux/README.md"
        old_readme = read_text(readme_path)
        expect_failure(
            "readme_gap_missing",
            root,
            readme_path,
            old_readme,
            old_readme.replace("scripts/zigux/check-phase1-parity.py, ", "", 1),
        )
        covered.append("readme_gap_missing")

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        old_closure = read_text(closure_path)
        expect_failure(
            "closure_gap_packet_missing",
            root,
            closure_path,
            old_closure,
            old_closure.replace(PHASE1_CURRENT_GAP_PACKET_LINE, "PHASE1_CURRENT_GAP_PACKET=drifted", 1),
        )
        covered.append("closure_gap_packet_missing")

        expect_failure(
            "closure_gap_missing",
            root,
            closure_path,
            old_closure,
            old_closure
            .replace("- zigux/tests/phase1_bench.zig\n", "", 1)
            .replace("zigux/tests/phase1_bench.zig,", "", 1),
        )
        covered.append("closure_gap_missing")

    ensure(covered == SELF_TEST_CASES, "self_test_case_order drifted")
    print("PHASE1_PARITY_ARTIFACT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_PARITY_ARTIFACT_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE1_PARITY_ARTIFACT_PACKET_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 1 parity-fixture plus artifact-diff packet."
    )
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    parser.add_argument(
        "--write-sample-root",
        metavar="PATH",
        help="Write a current-like sample root for focused replay validation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(Path(args.write_sample_root))
        return 0

    counts = check_root(Path(args.root))
    print("PHASE1_PARITY_ARTIFACT_PACKET=pass")
    for key in sorted(counts):
        print(f"PHASE1_PARITY_ARTIFACT_PACKET_{key.upper()}={counts[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())