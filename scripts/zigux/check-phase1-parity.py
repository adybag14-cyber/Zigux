#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
README_REL = Path("scripts/zigux/README.md")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")
HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")

EXPECTED_SECTIONS = (
    "find_bit",
    "bitmap",
    "string",
    "rbtree",
    "argv_split",
    "cmdline",
    "ctype",
    "hweight",
    "list_sort",
    "zalloc",
    "str_error_r",
    "slab",
    "vsprintf",
)

EXPECTED_HELPERS = (
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
)

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = (
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

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

EXPECTED_LANE_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_FIXTURE_VALUES = {
    ("string", "strtobool_invalid"): 184,
    ("slab", "zero_after_kmalloc"): True,
    ("bitmap", "truncated_scnprintf_len"): 7,
    ("find_bit", "tail_clamped_last"): 67,
    ("rbtree", "cached_leftmost_return_serials"): [0, -1, 2, -1],
    ("list_sort", "bool_sorted_ordinals"): [1, 3, 0, 2, 4],
}

EXPECTED_REPLAY_BLOCKER_IDS = (
    "phase1_helpers_zig_slab_zero_after_kmalloc",
    "phase1_helpers_c_harness_missing_c_sources",
)

README_REQUIRED_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
    "current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    "the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)

README_FORBIDDEN_MARKERS = (
    "`scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def ensure(condition: bool, issue: str, issues: list[str]) -> None:
    if not condition:
        issues.append(issue)


def run_python(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def artifact_diff_contract_issues(root: Path) -> list[str]:
    issues: list[str] = []
    artifact_diff = root / ARTIFACT_DIFF_REL

    self_test = run_python(artifact_diff, "--self-test")
    ensure(self_test.returncode == 0, "artifact_diff:self_test:returncode", issues)
    ensure(
        "ARTIFACT_DIFF_SELF_TEST=pass" in self_test.stdout,
        "artifact_diff:self_test:missing_pass",
        issues,
    )
    ensure(
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23" in self_test.stdout,
        "artifact_diff:self_test:missing_case_count",
        issues,
    )

    with tempfile.TemporaryDirectory(prefix="phase1_parity_artifact_diff_") as tmp_dir:
        tmp = Path(tmp_dir)
        text_expected = tmp / "expected.txt"
        text_actual = tmp / "actual.txt"
        text_drift = tmp / "drift.txt"
        json_expected = tmp / "expected.json"
        json_actual = tmp / "actual.json"
        json_drift = tmp / "drift.json"
        bytes_expected = tmp / "expected.bin"
        bytes_actual = tmp / "actual.bin"
        bytes_drift = tmp / "drift.bin"

        text_expected.write_text("alpha\nbeta\n", encoding="utf-8")
        text_actual.write_text("alpha\nbeta\n", encoding="utf-8")
        text_drift.write_text("alpha\nBETA\n", encoding="utf-8")

        json_expected.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding="utf-8")
        json_actual.write_text('{"beta": [2, 3], "alpha": 1}\n', encoding="utf-8")
        json_drift.write_text('{"alpha": 1, "beta": [2, 4]}\n', encoding="utf-8")

        bytes_expected.write_bytes(b"zigux-parity")
        bytes_actual.write_bytes(b"zigux-parity")
        bytes_drift.write_bytes(b"zigux-drift!")

        cases = (
            ("text_pass", ["--mode", "text", str(text_expected), str(text_actual)], 0, "ARTIFACT_DIFF=pass", "MODE=text"),
            ("text_fail", ["--mode", "text", str(text_expected), str(text_drift)], 1, "ARTIFACT_DIFF=fail", "MODE=text"),
            ("json_pass", ["--mode", "json", str(json_expected), str(json_actual)], 0, "ARTIFACT_DIFF=pass", "MODE=json"),
            ("json_fail", ["--mode", "json", str(json_expected), str(json_drift)], 1, "ARTIFACT_DIFF=fail", "MODE=json"),
            ("bytes_pass", ["--mode", "bytes", str(bytes_expected), str(bytes_actual)], 0, "ARTIFACT_DIFF=pass", "MODE=bytes"),
            ("bytes_fail", ["--mode", "bytes", str(bytes_expected), str(bytes_drift)], 1, "ARTIFACT_DIFF=fail", "MODE=bytes"),
            ("sha256_alias", ["--mode", "sha256", str(bytes_expected), str(bytes_actual)], 0, "ARTIFACT_DIFF=pass", "MODE=bytes"),
        )
        for name, argv, expected_rc, marker_a, marker_b in cases:
            result = run_python(artifact_diff, *argv)
            ensure(result.returncode == expected_rc, f"artifact_diff:{name}:returncode", issues)
            ensure(marker_a in result.stdout, f"artifact_diff:{name}:status", issues)
            ensure(marker_b in result.stdout, f"artifact_diff:{name}:mode", issues)

    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in (ARTIFACT_DIFF_REL, README_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL):
        ensure((root / rel).exists(), f"missing:{rel.as_posix()}", issues)
    if issues:
        return issues

    issues.extend(artifact_diff_contract_issues(root))

    readme_text = read_text(root / README_REL)
    for marker in README_REQUIRED_MARKERS:
        ensure(marker in readme_text, f"readme:missing:{marker}", issues)
    for marker in README_FORBIDDEN_MARKERS:
        ensure(marker not in readme_text, f"readme:forbidden:{marker}", issues)

    fixture_payload = read_json(root / FIXTURE_REL)
    ensure(isinstance(fixture_payload, dict), "fixture:not_object", issues)
    if isinstance(fixture_payload, dict):
        ensure(tuple(fixture_payload.keys()) == EXPECTED_SECTIONS, "fixture:sections", issues)
        for (section, key), expected_value in EXPECTED_FIXTURE_VALUES.items():
            section_payload = fixture_payload.get(section)
            ensure(isinstance(section_payload, dict), f"fixture:{section}:not_object", issues)
            if isinstance(section_payload, dict):
                ensure(
                    section_payload.get(key) == expected_value,
                    f"fixture:{section}.{key}:{section_payload.get(key)!r}!={expected_value!r}",
                    issues,
                )

    manifest_payload = read_json(root / MANIFEST_REL)
    ensure(isinstance(manifest_payload, dict), "manifest:not_object", issues)
    if isinstance(manifest_payload, dict):
        ensure(manifest_payload.get("phase") == "Phase 1", "manifest:phase", issues)
        ensure(manifest_payload.get("status") == "closed", "manifest:status", issues)
        ensure(manifest_payload.get("helper_count") == len(EXPECTED_HELPERS), "manifest:helper_count", issues)
        ensure(tuple(manifest_payload.get("helpers", ())) == EXPECTED_HELPERS, "manifest:helpers", issues)
        lane = manifest_payload.get("lane_sequencing")
        ensure(isinstance(lane, dict), "manifest:lane:not_object", issues)
        if isinstance(lane, dict):
            ensure(
                tuple(lane.get("shared_replay_parked_helpers", ())) == EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                "manifest:shared_replay_parked_helpers",
                issues,
            )
            ensure(
                tuple(lane.get("direct_anchor_followup_helpers", ())) == EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                "manifest:direct_anchor_followup_helpers",
                issues,
            )
            ensure(lane.get("rule_summary") == EXPECTED_LANE_RULE_SUMMARY, "manifest:rule_summary", issues)
            ensure(lane.get("anti_overlap_rule") == EXPECTED_ANTI_OVERLAP_RULE, "manifest:anti_overlap_rule", issues)

    blockers_payload = read_json(root / BLOCKERS_REL)
    ensure(isinstance(blockers_payload, dict), "blockers:not_object", issues)
    if isinstance(blockers_payload, dict):
        ensure(blockers_payload.get("status") == "parked", "blockers:status", issues)
        replay = blockers_payload.get("replay")
        ensure(isinstance(replay, dict), "blockers:replay:not_object", issues)
        if isinstance(replay, dict):
            ensure(replay.get("path") == REPLAY_REL.as_posix(), "blockers:replay:path", issues)
            ensure(replay.get("state") == "blocked", "blockers:replay:state", issues)
            blocker_list = replay.get("blockers")
            ensure(isinstance(blocker_list, list) and len(blocker_list) == 1, "blockers:replay:list", issues)
            if isinstance(blocker_list, list) and len(blocker_list) == 1 and isinstance(blocker_list[0], dict):
                blocker = blocker_list[0]
                ensure(blocker.get("id") == EXPECTED_REPLAY_BLOCKER_IDS[0], "blockers:replay:id", issues)
                ensure(blocker.get("field") == "slab.zero_after_kmalloc", "blockers:replay:field", issues)
                ensure(blocker.get("expected") is True, "blockers:replay:expected", issues)
                ensure(blocker.get("actual") is False, "blockers:replay:actual", issues)
        harness = blockers_payload.get("c_harness")
        ensure(isinstance(harness, dict), "blockers:c_harness:not_object", issues)
        if isinstance(harness, dict):
            ensure(harness.get("path") == HARNESS_REL.as_posix(), "blockers:c_harness:path", issues)
            ensure(harness.get("state") == "blocked", "blockers:c_harness:state", issues)
            ensure(harness.get("helper_count") == len(EXPECTED_HELPERS), "blockers:c_harness:helper_count", issues)
            ensure(tuple(harness.get("helpers", ())) == EXPECTED_HELPERS, "blockers:c_harness:helpers", issues)
            ensure(harness.get("blocker_id") == EXPECTED_REPLAY_BLOCKER_IDS[1], "blockers:c_harness:blocker_id", issues)

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_PARITY=fail")
        for issue in issues:
            print(f"PHASE1_PARITY_ISSUE={issue}")
        return 1

    print("PHASE1_PARITY=pass")
    print(f"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}")
    print(f"PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print("PHASE1_PARITY_REPLAY=" + ("present" if (root / REPLAY_REL).exists() else "parked"))
    print(f"PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}")
    print("PHASE1_PARITY_BLOCKER_IDS=" + ",".join(EXPECTED_REPLAY_BLOCKER_IDS))
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    artifact_diff_text = """#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SELF_TEST_CASES = (
    \"text_pass\",
    \"text_mismatch\",
    \"json_pass\",
    \"json_mismatch\",
    \"json_invalid_expected\",
    \"json_invalid_actual\",
    \"json_invalid_both\",
    \"json_missing_expected\",
    \"json_missing_actual\",
    \"json_missing_both\",
    \"bytes_pass\",
    \"bytes_drift\",
    \"text_missing_expected\",
    \"text_missing_actual\",
    \"text_missing_both\",
    \"bytes_missing_expected\",
    \"bytes_missing_actual\",
    \"bytes_missing_both\",
    \"legacy_sha256_alias\",
    \"missing_mode_value_rejected\",
    \"missing_positional_arguments_rejected\",
    \"invalid_mode_rejected\",
    \"extra_positional_rejected\",
)

def read_bytes(path: Path) -> bytes:
    return path.read_bytes()

def compare(mode: str, expected: Path, actual: Path):
    mode = \"bytes\" if mode == \"sha256\" else mode
    if not expected.exists() or not actual.exists():
        return False, [f\"EXPECTED_EXISTS={expected.exists()}\", f\"ACTUAL_EXISTS={actual.exists()}\"], mode
    if mode == \"text\":
        ok = expected.read_text(encoding=\"utf-8\") == actual.read_text(encoding=\"utf-8\")
        return ok, [], mode
    if mode == \"json\":
        ok = json.loads(expected.read_text(encoding=\"utf-8\")) == json.loads(actual.read_text(encoding=\"utf-8\"))
        return ok, [], mode
    if mode == \"bytes\":
        expected_sha = hashlib.sha256(read_bytes(expected)).hexdigest()
        actual_sha = hashlib.sha256(read_bytes(actual)).hexdigest()
        if expected_sha == actual_sha:
            return True, [f\"SHA256={expected_sha}\"], mode
        return False, [f\"EXPECTED_SHA256={expected_sha}\", f\"ACTUAL_SHA256={actual_sha}\"], mode
    raise SystemExit(2)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(\"--mode\")
    parser.add_argument(\"--self-test\", action=\"store_true\")
    parser.add_argument(\"expected\", nargs=\"?\")
    parser.add_argument(\"actual\", nargs=\"?\")
    args = parser.parse_args()
    if args.self_test:
        print(\"ARTIFACT_DIFF_SELF_TEST=pass\")
        print(f\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}\")
        print(\"ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES))
        return 0
    ok, extra, mode = compare(args.mode, Path(args.expected), Path(args.actual))
    print(\"ARTIFACT_DIFF=pass\" if ok else \"ARTIFACT_DIFF=fail\")
    print(f\"MODE={mode}\")
    print(f\"EXPECTED={Path(args.expected)}\")
    print(f\"ACTUAL={Path(args.actual)}\")
    for line in extra:
        print(line)
    return 0 if ok else 1

if __name__ == \"__main__\":
    raise SystemExit(main())
"""
    fixture_payload = {
        "find_bit": {
            "tail_clamped_last": 67,
        },
        "bitmap": {
            "truncated_scnprintf_len": 7,
        },
        "string": {
            "strtobool_invalid": 184,
        },
        "rbtree": {
            "cached_leftmost_return_serials": [0, -1, 2, -1],
        },
        "argv_split": {},
        "cmdline": {},
        "ctype": {},
        "hweight": {},
        "list_sort": {
            "bool_sorted_ordinals": [1, 3, 0, 2, 4],
        },
        "zalloc": {},
        "str_error_r": {},
        "slab": {
            "zero_after_kmalloc": True,
        },
        "vsprintf": {},
    }
    manifest_payload = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "rule_summary": EXPECTED_LANE_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }
    blockers_payload = {
        "status": "parked",
        "lane_sequencing": {
            "manifest": MANIFEST_REL.as_posix(),
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": REPLAY_REL.as_posix(),
            "state": "blocked",
            "blockers": [
                {
                    "id": EXPECTED_REPLAY_BLOCKER_IDS[0],
                    "kind": "fixture_mismatch",
                    "path": "tools/lib/slab.zig",
                    "field": "slab.zero_after_kmalloc",
                    "expected": True,
                    "actual": False,
                    "evidence": "Focused replay still diverges on the slab fixture field.",
                }
            ],
        },
        "c_harness": {
            "path": HARNESS_REL.as_posix(),
            "state": "blocked",
            "reason": "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that current master no longer ships beside the Phase 1 `.zig` ports.",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "blocker_id": EXPECTED_REPLAY_BLOCKER_IDS[1],
        },
    }
    readme_text = "\n".join(
        [
            "# scripts/zigux",
            "",
            "## Phase 1",
            "",
            f"- {README_REQUIRED_MARKERS[0]}",
            f"- {README_REQUIRED_MARKERS[1]}",
            f"- {README_REQUIRED_MARKERS[2]}",
        ]
    ) + "\n"

    write_text(root / ARTIFACT_DIFF_REL, artifact_diff_text)
    write_text(root / README_REL, readme_text)
    write_text(root / FIXTURE_REL, json.dumps(fixture_payload, indent=2) + "\n")
    write_text(root / MANIFEST_REL, json.dumps(manifest_payload, indent=2) + "\n")
    write_text(root / BLOCKERS_REL, json.dumps(blockers_payload, indent=2) + "\n")


def mutate_json(path: Path, mutate) -> None:
    payload = json.loads(read_text(path))
    mutate(payload)
    write_text(path, json.dumps(payload, indent=2) + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="phase1_parity_selftest_") as tmp_dir:
        tmp = Path(tmp_dir)

        good = tmp / "good"
        build_sample_root(good)
        cases.append(("good", run_check(good) == 0))

        missing_artifact = tmp / "missing_artifact"
        build_sample_root(missing_artifact)
        (missing_artifact / ARTIFACT_DIFF_REL).unlink()
        cases.append(("missing_artifact", run_check(missing_artifact) != 0))

        readme_drift = tmp / "readme_drift"
        build_sample_root(readme_drift)
        write_text(readme_drift / README_REL, "# scripts/zigux\n")
        cases.append(("readme_drift", run_check(readme_drift) != 0))

        fixture_drift = tmp / "fixture_drift"
        build_sample_root(fixture_drift)
        mutate_json(fixture_drift / FIXTURE_REL, lambda payload: payload["string"].update({"strtobool_invalid": 22}))
        cases.append(("fixture_drift", run_check(fixture_drift) != 0))

        manifest_drift = tmp / "manifest_drift"
        build_sample_root(manifest_drift)
        mutate_json(manifest_drift / MANIFEST_REL, lambda payload: payload.update({"status": "open"}))
        cases.append(("manifest_drift", run_check(manifest_drift) != 0))

        blocker_drift = tmp / "blocker_drift"
        build_sample_root(blocker_drift)
        mutate_json(
            blocker_drift / BLOCKERS_REL,
            lambda payload: payload["replay"]["blockers"][0].update({"actual": True}),
        )
        cases.append(("blocker_drift", run_check(blocker_drift) != 0))

    failed = [name for name, ok in cases if not ok]
    if failed:
        print("PHASE1_PARITY_SELF_TEST=fail")
        for name in failed:
            print(f"PHASE1_PARITY_SELF_TEST_FAILED_CASE={name}")
        return 1

    print("PHASE1_PARITY_SELF_TEST=pass")
    print(f"PHASE1_PARITY_SELF_TEST_CASE_COUNT={len(cases)}")
    print("PHASE1_PARITY_SELF_TEST_CASES=" + ",".join(name for name, _ in cases))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 09 Phase 1 parity packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
