#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
README_REL = Path("scripts/zigux/README.md")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")

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

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

EXPECTED_BLOCKER_EVIDENCE = (
    "Focused 2026-05-17 scratch replay of `zig build test --build-file "
    "zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` because the "
    "committed fixture expects `true` while `tools/lib/slab.zig` still produced `false`."
)

EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that "
    "current master no longer ships beside the Phase 1 `.zig` ports."
)

README_REQUIRED_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "`zigux/Makefile` is current repo evidence again from the scripts root too",
    "the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)

README_FORBIDDEN_MARKERS = (
    "`scripts/zigux/check-phase1-parity.py --self-test` replay the shipped bounded Phase 1",
    "`scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py` keep the shipped parity-fixture",
)

EXPECTED_FIXTURE_VALUES = {
    ("string", "strtobool_invalid"): 184,
    ("slab", "zero_after_kmalloc"): True,
}

SELF_TEST_CASES = (
    "good_root",
    "missing_required_file",
    "artifact_diff_api_drift",
    "artifact_diff_behavior_drift",
    "fixture_section_drift",
    "fixture_value_drift",
    "manifest_split_drift",
    "blocker_payload_drift",
    "readme_marker_drift",
    "readme_forbidden_marker",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> object:
    return json.loads(_read_text(path))


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _load_artifact_diff(root: Path) -> object:
    module_path = root / ARTIFACT_DIFF_REL
    spec = importlib.util.spec_from_file_location("zigux_artifact_diff_module", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _artifact_diff_issues(root: Path) -> list[str]:
    try:
        module = _load_artifact_diff(root)
    except Exception as exc:
        return [f"artifact_diff_import:{exc}"]

    compare = getattr(module, "compare", None)
    mode_choices = getattr(module, "MODE_CHOICES", None)
    aliases = getattr(module, "LEGACY_MODE_ALIASES", None)
    self_test_cases = getattr(module, "SELF_TEST_CASES", None)
    if not callable(compare):
        return ["artifact_diff_missing:compare"]
    if mode_choices != ("text", "json", "bytes"):
        return [f"artifact_diff_modes:{mode_choices!r}"]
    if not isinstance(aliases, dict) or aliases.get("sha256") != "bytes":
        return [f"artifact_diff_aliases:{aliases!r}"]
    if not isinstance(self_test_cases, list) or "legacy_sha256_alias" not in self_test_cases:
        return ["artifact_diff_self_test_catalog"]

    fixture = root / FIXTURE_REL
    blockers = root / BLOCKERS_REL
    readme = root / README_REL
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_") as tmp_dir:
        tmp = Path(tmp_dir)

        fixture_drift = tmp / "fixture_drift.json"
        fixture_payload = _read_json(fixture)
        if isinstance(fixture_payload, dict) and isinstance(fixture_payload.get("string"), dict):
            fixture_payload["string"] = dict(fixture_payload["string"])
            fixture_payload["string"]["strtobool_invalid"] = 22
            _write_text(fixture_drift, json.dumps(fixture_payload, indent=2) + "\n")
        else:
            _write_text(fixture_drift, "{\"string\": {\"strtobool_invalid\": 22}}\n")

        readme_drift = tmp / "README_drift.md"
        _write_text(readme_drift, _read_text(readme) + "\nphase1 drift\n")

        blockers_drift = tmp / "blockers_drift.json"
        blocker_payload = _read_json(blockers)
        assert isinstance(blocker_payload, dict)
        blocker_payload["status"] = "open"
        _write_text(blockers_drift, json.dumps(blocker_payload, indent=2) + "\n")

        if compare("json", fixture, fixture).ok is not True:
            issues.append("artifact_diff_json_pass")
        if compare("json", fixture, fixture_drift).ok is not False:
            issues.append("artifact_diff_json_drift")
        if compare("text", readme, readme).ok is not True:
            issues.append("artifact_diff_text_pass")
        if compare("text", readme, readme_drift).ok is not False:
            issues.append("artifact_diff_text_drift")

        bytes_pass = compare("bytes", blockers, blockers)
        if bytes_pass.ok is not True or len(bytes_pass.extra_lines) != 1:
            issues.append("artifact_diff_bytes_pass")
        bytes_drift = compare("bytes", blockers, blockers_drift)
        if bytes_drift.ok is not False or len(bytes_drift.extra_lines) != 2:
            issues.append("artifact_diff_bytes_drift")

        missing = tmp / "missing.json"
        missing_case = compare("json", missing, fixture)
        if missing_case.ok is not False or missing_case.extra_lines != [
            "EXPECTED_EXISTS=False",
            "ACTUAL_EXISTS=True",
        ]:
            issues.append("artifact_diff_missing_case")

    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    required_paths = (
        ARTIFACT_DIFF_REL,
        README_REL,
        FIXTURE_REL,
        MANIFEST_REL,
        BLOCKERS_REL,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            issues.append(f"missing:{rel.as_posix()}")
    if issues:
        return issues

    issues.extend(_artifact_diff_issues(root))

    readme_text = _read_text(root / README_REL)
    for marker in README_REQUIRED_MARKERS:
        if marker not in readme_text:
            issues.append(f"readme_marker:{marker}")
    for marker in README_FORBIDDEN_MARKERS:
        if marker in readme_text:
            issues.append(f"readme_forbidden:{marker}")

    fixture_payload = _read_json(root / FIXTURE_REL)
    if not isinstance(fixture_payload, dict):
        issues.append("fixture:not_object")
    else:
        if tuple(fixture_payload.keys()) != EXPECTED_SECTIONS:
            issues.append("fixture_sections")
        for (section, key), expected in EXPECTED_FIXTURE_VALUES.items():
            section_payload = fixture_payload.get(section)
            if not isinstance(section_payload, dict):
                issues.append(f"fixture_section:{section}")
                continue
            if section_payload.get(key) != expected:
                issues.append(f"fixture_value:{section}.{key}")

    manifest_payload = _read_json(root / MANIFEST_REL)
    if not isinstance(manifest_payload, dict):
        issues.append("manifest:not_object")
    else:
        if manifest_payload.get("phase") != "Phase 1":
            issues.append("manifest_phase")
        if manifest_payload.get("status") != "closed":
            issues.append("manifest_status")
        if manifest_payload.get("helper_count") != len(EXPECTED_HELPERS):
            issues.append("manifest_helper_count")
        if manifest_payload.get("helpers") != list(EXPECTED_HELPERS):
            issues.append("manifest_helpers")
        lane = manifest_payload.get("lane_sequencing")
        if not isinstance(lane, dict):
            issues.append("manifest_lane")
        else:
            if lane.get("shared_replay_parked_helpers") != list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS):
                issues.append("manifest_shared_helpers")
            if lane.get("direct_anchor_followup_helpers") != list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS):
                issues.append("manifest_direct_helpers")
            if lane.get("rule_summary") != EXPECTED_RULE_SUMMARY:
                issues.append("manifest_rule_summary")
            if lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
                issues.append("manifest_anti_overlap")

    blockers_payload = _read_json(root / BLOCKERS_REL)
    if not isinstance(blockers_payload, dict):
        issues.append("blockers:not_object")
    else:
        if blockers_payload.get("status") != "parked":
            issues.append("blockers_status")
        lane = blockers_payload.get("lane_sequencing")
        if not isinstance(lane, dict):
            issues.append("blockers_lane")
        else:
            if lane.get("manifest") != MANIFEST_REL.as_posix():
                issues.append("blockers_manifest")
            if lane.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS):
                issues.append("blockers_shared_count")
            if lane.get("shared_replay_parked_helpers") != list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS):
                issues.append("blockers_shared_helpers")
            if lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS):
                issues.append("blockers_direct_count")
            if lane.get("direct_anchor_followup_helpers") != list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS):
                issues.append("blockers_direct_helpers")
            if lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
                issues.append("blockers_anti_overlap")

        replay = blockers_payload.get("replay")
        if not isinstance(replay, dict):
            issues.append("blockers_replay")
        else:
            if replay.get("path") != REPLAY_REL.as_posix():
                issues.append("blockers_replay_path")
            if replay.get("state") != "blocked":
                issues.append("blockers_replay_state")
            blocker_list = replay.get("blockers")
            if not isinstance(blocker_list, list) or len(blocker_list) != 1:
                issues.append("blockers_replay_list")
            else:
                blocker = blocker_list[0]
                if blocker.get("id") != "phase1_helpers_zig_slab_zero_after_kmalloc":
                    issues.append("blockers_replay_id")
                if blocker.get("kind") != "fixture_mismatch":
                    issues.append("blockers_replay_kind")
                if blocker.get("path") != "tools/lib/slab.zig":
                    issues.append("blockers_replay_path_field")
                if blocker.get("field") != "slab.zero_after_kmalloc":
                    issues.append("blockers_replay_field")
                if blocker.get("expected") is not True or blocker.get("actual") is not False:
                    issues.append("blockers_replay_expected_actual")
                if blocker.get("evidence") != EXPECTED_BLOCKER_EVIDENCE:
                    issues.append("blockers_replay_evidence")

        c_harness = blockers_payload.get("c_harness")
        if not isinstance(c_harness, dict):
            issues.append("blockers_c_harness")
        else:
            if c_harness.get("path") != "zigux/tests/fixtures/phase1_helpers_c_harness.c":
                issues.append("blockers_c_harness_path")
            if c_harness.get("state") != "blocked":
                issues.append("blockers_c_harness_state")
            if c_harness.get("reason") != EXPECTED_C_HARNESS_REASON:
                issues.append("blockers_c_harness_reason")
            if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
                issues.append("blockers_c_harness_helper_count")
            if c_harness.get("helpers") != list(EXPECTED_HELPERS):
                issues.append("blockers_c_harness_helpers")
            if c_harness.get("blocker_id") != "phase1_helpers_c_harness_missing_c_sources":
                issues.append("blockers_c_harness_id")

    replay_path = root / REPLAY_REL
    replay_state = "present" if replay_path.exists() else "parked"
    if replay_state not in ("present", "parked"):
        issues.append("replay_state")

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
    print(f"PHASE1_PARITY_REPLAY={'present' if (root / REPLAY_REL).exists() else 'parked'}")
    print("PHASE1_PARITY_BLOCKER_COUNT=2")
    print(
        "PHASE1_PARITY_BLOCKER_IDS="
        "phase1_helpers_zig_slab_zero_after_kmalloc,"
        "phase1_helpers_c_harness_missing_c_sources"
    )
    return 0


def _sample_fixture_json() -> str:
    return (
        "{\"find_bit\":{\"first\":5},\"bitmap\":{\"weight\":3},\"string\":{\"strtobool_invalid\":184},"
        "\"rbtree\":{\"empty_root\":true},\"argv_split\":{\"argc\":3},\"cmdline\":{\"decimal_k\":{}},"
        "\"ctype\":{\"mask_A\":65},\"hweight\":{\"w8\":4},\"list_sort\":{\"tri_sorted_keys\":[1,1,2,3,3]},"
        "\"zalloc\":{\"zeroed\":true},\"str_error_r\":{\"enoent\":\"No such file or directory\"},"
        "\"slab\":{\"zero_after_kmalloc\":true},\"vsprintf\":{\"scnprintf_len\":7}}\n"
    )


def _sample_manifest_json() -> str:
    return json.dumps(
        {
            "phase": "Phase 1",
            "status": "closed",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "lane_sequencing": {
                "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
                "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
                "rule_summary": EXPECTED_RULE_SUMMARY,
                "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
            },
        },
        indent=2,
    ) + "\n"


def _sample_blockers_json() -> str:
    return json.dumps(
        {
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
                        "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
                        "kind": "fixture_mismatch",
                        "path": "tools/lib/slab.zig",
                        "field": "slab.zero_after_kmalloc",
                        "expected": True,
                        "actual": False,
                        "evidence": EXPECTED_BLOCKER_EVIDENCE,
                    }
                ],
            },
            "c_harness": {
                "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
                "state": "blocked",
                "reason": EXPECTED_C_HARNESS_REASON,
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": list(EXPECTED_HELPERS),
                "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
            },
        },
        indent=2,
    ) + "\n"


def _sample_artifact_diff_text() -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass

MODE_CHOICES = (\"text\", \"json\", \"bytes\")
LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}
SELF_TEST_CASES = [\"legacy_sha256_alias\"]

@dataclass(frozen=True)
class ComparisonResult:
    ok: bool
    extra_lines: list[str]

def compare(mode, expected, actual):
    expected_exists = expected.exists()
    actual_exists = actual.exists()
    if not expected_exists or not actual_exists:
        return ComparisonResult(False, [f\"EXPECTED_EXISTS={expected_exists}\", f\"ACTUAL_EXISTS={actual_exists}\"])
    if mode == \"json\":
        return ComparisonResult(expected.read_text() == actual.read_text(), [])
    if mode == \"text\":
        return ComparisonResult(expected.read_text() == actual.read_text(), [])
    if mode == \"bytes\":
        if expected.read_bytes() == actual.read_bytes():
            return ComparisonResult(True, [\"SHA256=ok\"])
        return ComparisonResult(False, [\"EXPECTED_SHA256=a\", \"ACTUAL_SHA256=b\"])
    raise ValueError(mode)
"""


def _sample_readme_text() -> str:
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "## Phase 1",
            "",
            "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
            "- `zigux/Makefile` is current repo evidence again from the scripts root too",
            "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
        )
    ) + "\n"


def _build_sample_root(root: Path) -> None:
    _write_text(root / ARTIFACT_DIFF_REL, _sample_artifact_diff_text())
    _write_text(root / README_REL, _sample_readme_text())
    _write_text(root / FIXTURE_REL, _sample_fixture_json())
    _write_text(root / MANIFEST_REL, _sample_manifest_json())
    _write_text(root / BLOCKERS_REL, _sample_blockers_json())


def run_self_test() -> int:
    results: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_selftest_") as tmp_dir:
        tmp = Path(tmp_dir)

        good_root = tmp / "good"
        _build_sample_root(good_root)
        results.append(("good_root", run_check(good_root) == 0))

        missing_root = tmp / "missing"
        _build_sample_root(missing_root)
        (missing_root / README_REL).unlink()
        results.append(("missing_required_file", run_check(missing_root) != 0))

        api_drift_root = tmp / "api_drift"
        _build_sample_root(api_drift_root)
        _write_text(api_drift_root / ARTIFACT_DIFF_REL, _sample_artifact_diff_text().replace("def compare", "def compare_artifacts", 1))
        results.append(("artifact_diff_api_drift", run_check(api_drift_root) != 0))

        behavior_drift_root = tmp / "behavior_drift"
        _build_sample_root(behavior_drift_root)
        _write_text(
            behavior_drift_root / ARTIFACT_DIFF_REL,
            _sample_artifact_diff_text().replace('return ComparisonResult(False, [\"EXPECTED_SHA256=a\", \"ACTUAL_SHA256=b\"])', 'return ComparisonResult(False, [\"EXPECTED_SHA256=a\"])', 1),
        )
        results.append(("artifact_diff_behavior_drift", run_check(behavior_drift_root) != 0))

        fixture_section_root = tmp / "fixture_section"
        _build_sample_root(fixture_section_root)
        _write_text(fixture_section_root / FIXTURE_REL, json.dumps({"find_bit": {}}, indent=2) + "\n")
        results.append(("fixture_section_drift", run_check(fixture_section_root) != 0))

        fixture_value_root = tmp / "fixture_value"
        _build_sample_root(fixture_value_root)
        payload = json.loads(_sample_fixture_json())
        payload["slab"]["zero_after_kmalloc"] = False
        _write_text(fixture_value_root / FIXTURE_REL, json.dumps(payload, indent=2) + "\n")
        results.append(("fixture_value_drift", run_check(fixture_value_root) != 0))

        manifest_split_root = tmp / "manifest_split"
        _build_sample_root(manifest_split_root)
        payload = json.loads(_sample_manifest_json())
        payload["lane_sequencing"]["direct_anchor_followup_helpers"] = ["tools/lib/slab.zig"]
        _write_text(manifest_split_root / MANIFEST_REL, json.dumps(payload, indent=2) + "\n")
        results.append(("manifest_split_drift", run_check(manifest_split_root) != 0))

        blocker_root = tmp / "blocker"
        _build_sample_root(blocker_root)
        payload = json.loads(_sample_blockers_json())
        payload["replay"]["blockers"][0]["actual"] = True
        _write_text(blocker_root / BLOCKERS_REL, json.dumps(payload, indent=2) + "\n")
        results.append(("blocker_payload_drift", run_check(blocker_root) != 0))

        readme_root = tmp / "readme"
        _build_sample_root(readme_root)
        _write_text(readme_root / README_REL, _sample_readme_text().replace(README_REQUIRED_MARKERS[1], "", 1))
        results.append(("readme_marker_drift", run_check(readme_root) != 0))

        forbidden_root = tmp / "forbidden"
        _build_sample_root(forbidden_root)
        _write_text(forbidden_root / README_REL, _sample_readme_text() + README_FORBIDDEN_MARKERS[0] + "\n")
        results.append(("readme_forbidden_marker", run_check(forbidden_root) != 0))

    failed = [name for name, ok in results if not ok]
    if failed:
        print("PHASE1_PARITY_SELF_TEST=fail")
        for name in failed:
            print(f"PHASE1_PARITY_SELF_TEST_FAILED_CASE={name}")
        return 1
    print("PHASE1_PARITY_SELF_TEST=pass")
    print(f"PHASE1_PARITY_SELF_TEST_CASE_COUNT={len(results)}")
    print("PHASE1_PARITY_SELF_TEST_CASES=" + ",".join(name for name, _ in results))
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
