#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

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

EXPECTED_MANIFEST_STATUS = "closed"

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
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

EXPECTED_FIXTURE_VALUES = {
    ("string", "strtobool_invalid"): 184,
    ("slab", "zero_after_kmalloc"): True,
}

EXPECTED_REPLAY_BLOCKER_IDS = (
    "phase1_helpers_zig_slab_zero_after_kmalloc",
    "phase1_helpers_c_harness_missing_c_sources",
)

REPLAY_IMPORTS = (
    'const argv_split = @import("argv_split");',
    'const bitmap = @import("bitmap");',
    'const cmdline = @import("cmdline");',
    'const ctype = @import("ctype");',
    'const find_bit = @import("find_bit");',
    'const hweight = @import("hweight");',
    'const list_sort = @import("list_sort");',
    'const rbtree = @import("rbtree");',
    'const slab = @import("slab");',
    'const str_error_r = @import("str_error_r");',
    'const string = @import("string");',
    'const vsprintf = @import("vsprintf");',
    'const zalloc = @import("zalloc");',
)

REPLAY_ANCHORS = (
    '@embedFile("fixtures/phase1_helpers.json")',
    ".ignore_unknown_fields = true,",
    'test "phase 1 helper modules import cleanly"',
    'test "phase 1 helper ports match committed parity fixture"',
)

ARTIFACT_DIFF_MARKERS = (
    "ARTIFACT_DIFF_SELF_TEST=pass",
    "MODE=text",
    "MODE=json",
    "MODE=sha256",
)

README_REQUIRED_MARKERS = (
    "`python3 scripts/zigux/artifact_diff.py --self-test`, `python3 scripts/zigux/check-phase1-parity.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, and `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test` replay the shipped bounded Phase 1 parity, artifact-diff, bench, and reminder checks",
    "`scripts/zigux/artifact_diff.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-string-review-packet.py`, and `scripts/zigux/check-phase1-direct-owner-markers.py` keep the shipped parity-fixture, artifact-diff, bench, string-review, and direct-owner marker packet explicit from the scripts root",
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_helpers.json`, and `zigux/tests/fixtures/phase1_replay_blockers.json` remain the current reminder-surface companions for that packet",
    "`zigux/tests/fixtures/phase1_replay_blockers.json` keeps the currently parked replay state explicit: the focused `phase1_helpers.zig` rerun still diverges on `slab.zero_after_kmalloc`, and the older C harness route now names the exact thirteen helper ports whose former `tools/lib/*.c` inputs no longer ship beside the Phase 1 `.zig` ports on current `master`",
    "current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
)

README_FORBIDDEN_MARKERS = (
    "`scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> object:
    return json.loads(_read_text(path))


def _expected_blockers_payload() -> dict[str, object]:
    return {
        "status": "parked",
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
                    "evidence": "Focused 2026-05-17 scratch replay of `zig build test --build-file zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` because the committed fixture expects `true` while `tools/lib/slab.zig` still produced `false`.",
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that current master no longer ships beside the Phase 1 `.zig` ports.",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "blocker_id": EXPECTED_REPLAY_BLOCKER_IDS[1],
        },
    }


def _load_artifact_diff_module(root: Path) -> object:
    module_path = root / ARTIFACT_DIFF_REL
    spec = importlib.util.spec_from_file_location(
        "zigux_phase1_artifact_diff", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load artifact diff module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _artifact_diff_contract_issues(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        module = _load_artifact_diff_module(root)
    except Exception as exc:
        return [f"artifact_diff_import:{exc}"]

    compare = getattr(module, "compare_artifacts", None)
    render = getattr(module, "render_result_lines", None)
    if not callable(compare):
        issues.append("artifact_diff_missing_callable:compare_artifacts")
    if not callable(render):
        issues.append("artifact_diff_missing_callable:render_result_lines")
    if issues:
        return issues

    fixture = root / FIXTURE_REL
    readme = root / README_REL
    blockers = root / BLOCKERS_REL

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_artifact_diff_") as tmp:
        tmp_root = Path(tmp)

        drift_fixture = tmp_root / "fixture_drift.json"
        fixture_payload = _read_json(fixture)
        assert isinstance(fixture_payload, dict)
        fixture_payload["string"] = {"strtobool_invalid": 22}
        drift_fixture.write_text(
            json.dumps(fixture_payload, indent=2) + "\n", encoding="utf-8"
        )

        drift_readme = tmp_root / "README_drift.md"
        drift_readme.write_text(
            _read_text(readme) + "\nartifact drift\n", encoding="utf-8"
        )

        drift_blockers = tmp_root / "blockers_drift.json"
        drift_blockers.write_text(_read_text(blockers) + "\n", encoding="utf-8")

        pass_cases = (
            ("json_fixture_pass", "json", fixture, fixture),
            ("text_readme_pass", "text", readme, readme),
            ("sha256_blockers_pass", "sha256", blockers, blockers),
        )
        for case_name, mode, expected_path, actual_path in pass_cases:
            matched, details = compare(mode, expected_path, actual_path)
            if matched is not True:
                issues.append(f"artifact_diff_case:{case_name}:matched={matched!r}")
                continue
            lines = render(matched, details)
            expected_prefix = [
                "ARTIFACT_DIFF=pass",
                f"MODE={mode}",
                f"EXPECTED={expected_path}",
                f"ACTUAL={actual_path}",
            ]
            if lines[:4] != expected_prefix:
                issues.append(f"artifact_diff_case:{case_name}:lines")
            if mode == "sha256":
                if len(lines) != 5 or not lines[4].startswith("SHA256="):
                    issues.append(f"artifact_diff_case:{case_name}:sha256")
            elif len(lines) != 4:
                issues.append(
                    f"artifact_diff_case:{case_name}:line_count={len(lines)}"
                )

        fail_cases = (
            ("json_fixture_drift", "json", fixture, drift_fixture),
            ("text_readme_drift", "text", readme, drift_readme),
            ("sha256_blockers_drift", "sha256", blockers, drift_blockers),
        )
        for case_name, mode, expected_path, actual_path in fail_cases:
            matched, details = compare(mode, expected_path, actual_path)
            if matched is not False:
                issues.append(f"artifact_diff_case:{case_name}:matched={matched!r}")
                continue
            lines = render(matched, details)
            expected_prefix = [
                "ARTIFACT_DIFF=fail",
                f"MODE={mode}",
                f"EXPECTED={expected_path}",
                f"ACTUAL={actual_path}",
            ]
            if lines[:4] != expected_prefix:
                issues.append(f"artifact_diff_case:{case_name}:lines")
            if mode == "sha256":
                if (
                    len(lines) != 6
                    or not lines[4].startswith("EXPECTED_SHA256=")
                    or not lines[5].startswith("ACTUAL_SHA256=")
                    or lines[4] == lines[5]
                ):
                    issues.append(f"artifact_diff_case:{case_name}:sha256")
            elif len(lines) != 4:
                issues.append(
                    f"artifact_diff_case:{case_name}:line_count={len(lines)}"
                )

    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    artifact_diff = root / ARTIFACT_DIFF_REL
    readme = root / README_REL
    fixture = root / FIXTURE_REL
    manifest = root / MANIFEST_REL
    blockers = root / BLOCKERS_REL
    replay = root / REPLAY_REL

    for rel in (
        ARTIFACT_DIFF_REL,
        README_REL,
        FIXTURE_REL,
        MANIFEST_REL,
        BLOCKERS_REL,
    ):
        if not (root / rel).exists():
            issues.append(f"missing:{rel.as_posix()}")

    if issues:
        return issues

    artifact_diff_text = _read_text(artifact_diff)
    for marker in ARTIFACT_DIFF_MARKERS:
        if marker not in artifact_diff_text:
            issues.append(f"artifact_diff_marker:{marker}")
    issues.extend(_artifact_diff_contract_issues(root))

    readme_text = _read_text(readme)
    for marker in README_REQUIRED_MARKERS:
        if marker not in readme_text:
            issues.append(f"readme_marker:{marker}")
    for marker in README_FORBIDDEN_MARKERS:
        if marker in readme_text:
            issues.append(f"readme_forbidden:{marker}")

    fixture_payload = _read_json(fixture)
    if not isinstance(fixture_payload, dict):
        issues.append("fixture:not_json_object")
    else:
        actual_sections = tuple(fixture_payload.keys())
        if actual_sections != EXPECTED_SECTIONS:
            issues.append(
                "fixture_sections:"
                + ",".join(actual_sections)
                + "!="
                + ",".join(EXPECTED_SECTIONS)
            )
        for (section, key), expected in EXPECTED_FIXTURE_VALUES.items():
            actual_section = fixture_payload.get(section)
            if not isinstance(actual_section, dict):
                issues.append(f"fixture_section:{section}")
                continue
            actual_value = actual_section.get(key)
            if actual_value != expected:
                issues.append(
                    f"fixture_value:{section}.{key}={actual_value!r}!={expected!r}"
                )

    manifest_payload = _read_json(manifest)
    if not isinstance(manifest_payload, dict):
        issues.append("manifest:not_json_object")
    else:
        if manifest_payload.get("phase") != "Phase 1":
            issues.append(f"manifest_phase:{manifest_payload.get('phase')!r}")
        if manifest_payload.get("status") != EXPECTED_MANIFEST_STATUS:
            issues.append(f"manifest_status:{manifest_payload.get('status')!r}")
        if manifest_payload.get("helper_count") != len(EXPECTED_HELPERS):
            issues.append(
                f"manifest_helper_count:{manifest_payload.get('helper_count')}"
            )
        helpers = manifest_payload.get("helpers")
        if helpers != list(EXPECTED_HELPERS):
            issues.append("manifest_helpers")

        lane_sequencing = manifest_payload.get("lane_sequencing")
        if not isinstance(lane_sequencing, dict):
            issues.append("manifest_lane_sequencing:not_json_object")
        else:
            parked_helpers = lane_sequencing.get("shared_replay_parked_helpers")
            if parked_helpers != list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS):
                issues.append("manifest_shared_replay_parked_helpers")

            direct_helpers = lane_sequencing.get("direct_anchor_followup_helpers")
            if direct_helpers != list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS):
                issues.append("manifest_direct_anchor_followup_helpers")

            if lane_sequencing.get("rule_summary") != EXPECTED_LANE_RULE_SUMMARY:
                issues.append("manifest_lane_rule_summary")

            if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
                issues.append("manifest_lane_anti_overlap_rule")

            if isinstance(parked_helpers, list) and isinstance(direct_helpers, list):
                if sorted(parked_helpers + direct_helpers) != list(EXPECTED_HELPERS):
                    issues.append("manifest_lane_helper_partition")

    blockers_payload = _read_json(blockers)
    expected_blockers = _expected_blockers_payload()
    if blockers_payload != expected_blockers:
        if not isinstance(blockers_payload, dict):
            issues.append("blockers:not_json_object")
        else:
            if blockers_payload.get("status") != expected_blockers["status"]:
                issues.append(f"blockers_status:{blockers_payload.get('status')!r}")

            replay_blockers = blockers_payload.get("replay")
            if not isinstance(replay_blockers, dict):
                issues.append("blockers_replay:not_json_object")
            else:
                if replay_blockers.get("path") != REPLAY_REL.as_posix():
                    issues.append(
                        f"blockers_replay_path:{replay_blockers.get('path')!r}"
                    )
                if replay_blockers.get("state") != "blocked":
                    issues.append(
                        f"blockers_replay_state:{replay_blockers.get('state')!r}"
                    )
                blocker_list = replay_blockers.get("blockers")
                if not isinstance(blocker_list, list) or len(blocker_list) != 1:
                    issues.append("blockers_replay_list")
                else:
                    blocker = blocker_list[0]
                    if blocker.get("id") != EXPECTED_REPLAY_BLOCKER_IDS[0]:
                        issues.append(f"blockers_replay_id:{blocker.get('id')!r}")
                    if blocker.get("field") != "slab.zero_after_kmalloc":
                        issues.append(
                            f"blockers_replay_field:{blocker.get('field')!r}"
                        )
                    if blocker.get("expected") is not True:
                        issues.append(
                            f"blockers_replay_expected:{blocker.get('expected')!r}"
                        )
                    if blocker.get("actual") is not False:
                        issues.append(
                            f"blockers_replay_actual:{blocker.get('actual')!r}"
                        )

            harness_blocker = blockers_payload.get("c_harness")
            if not isinstance(harness_blocker, dict):
                issues.append("blockers_c_harness:not_json_object")
            else:
                if (
                    harness_blocker.get("path")
                    != "zigux/tests/fixtures/phase1_helpers_c_harness.c"
                ):
                    issues.append(
                        f"blockers_c_harness_path:{harness_blocker.get('path')!r}"
                    )
                if harness_blocker.get("state") != "blocked":
                    issues.append(
                        f"blockers_c_harness_state:{harness_blocker.get('state')!r}"
                    )
                if harness_blocker.get("helper_count") != len(EXPECTED_HELPERS):
                    issues.append(
                        "blockers_c_harness_helper_count:"
                        f"{harness_blocker.get('helper_count')!r}"
                    )
                if harness_blocker.get("helpers") != list(EXPECTED_HELPERS):
                    issues.append("blockers_c_harness_helpers")
                if (
                    harness_blocker.get("blocker_id")
                    != EXPECTED_REPLAY_BLOCKER_IDS[1]
                ):
                    issues.append(
                        "blockers_c_harness_id:"
                        f"{harness_blocker.get('blocker_id')!r}"
                    )

    if replay.exists():
        replay_text = _read_text(replay)
        for marker in REPLAY_IMPORTS:
            if marker not in replay_text:
                issues.append(f"replay_import:{marker}")
        for marker in REPLAY_ANCHORS:
            if marker not in replay_text:
                issues.append(f"replay_anchor:{marker}")

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_PARITY=fail")
        for issue in issues:
            print(f"PHASE1_PARITY_ISSUE={issue}")
        return 1

    blocker_ids = ",".join(EXPECTED_REPLAY_BLOCKER_IDS)
    print("PHASE1_PARITY=pass")
    print(f"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}")
    print(f"PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(
        "PHASE1_PARITY_REPLAY="
        + ("present" if (root / REPLAY_REL).exists() else "parked")
    )
    print(f"PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}")
    print(f"PHASE1_PARITY_BLOCKER_IDS={blocker_ids}")
    return 0


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_json() -> str:
    payload = {section: {} for section in EXPECTED_SECTIONS}
    payload["string"] = {"strtobool_invalid": 184}
    payload["slab"] = {"zero_after_kmalloc": True}
    return json.dumps(payload, indent=2) + "\n"


def make_manifest_json() -> str:
    payload = {
        "phase": "Phase 1",
        "status": EXPECTED_MANIFEST_STATUS,
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "rule_summary": EXPECTED_LANE_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def make_blockers_json() -> str:
    return json.dumps(_expected_blockers_payload(), indent=2) + "\n"


def make_replay_text() -> str:
    imports = "\n".join(REPLAY_IMPORTS)
    anchors = "\n".join(
        (
            "fn loadFixture() void {",
            f"    _ = {REPLAY_ANCHORS[0]};",
            f"    _ = {REPLAY_ANCHORS[1]}",
            "}",
            "",
            f"{REPLAY_ANCHORS[2]} {{}}",
            f"{REPLAY_ANCHORS[3]} {{}}",
        )
    )
    return imports + "\n\n" + anchors + "\n"


def make_artifact_diff_text() -> str:
    return """#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

SELF_TEST_MARKER = \"ARTIFACT_DIFF_SELF_TEST=pass\"
TEXT_MARKER = \"MODE=text\"
JSON_MARKER = \"MODE=json\"
SHA_MARKER = \"MODE=sha256\"

def read_text(path: Path) -> str:
    return path.read_text(encoding=\"utf-8\")

def canonical_json(path: Path):
    return json.loads(read_text(path))

def sha256_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compare_artifacts(mode: str, expected: Path, actual: Path):
    details = {\"mode\": mode, \"expected\": str(expected), \"actual\": str(actual)}
    if not expected.exists() or not actual.exists():
        details[\"expected_exists\"] = expected.exists()
        details[\"actual_exists\"] = actual.exists()
        return False, details
    if mode == \"text\":
        expected_value = read_text(expected)
        actual_value = read_text(actual)
    elif mode == \"json\":
        expected_value = canonical_json(expected)
        actual_value = canonical_json(actual)
    elif mode == \"sha256\":
        expected_value = sha256_digest(expected)
        actual_value = sha256_digest(actual)
        details[\"expected_sha256\"] = expected_value
        details[\"actual_sha256\"] = actual_value
    else:
        raise ValueError(f\"unsupported artifact diff mode: {mode}\")
    return expected_value == actual_value, details

def render_result_lines(matched: bool, details: dict[str, object]) -> list[str]:
    lines = [\"ARTIFACT_DIFF=pass\" if matched else \"ARTIFACT_DIFF=fail\"]
    lines.append(f\"MODE={details['mode']}\")
    lines.append(f\"EXPECTED={details['expected']}\")
    lines.append(f\"ACTUAL={details['actual']}\")
    if matched and \"expected_sha256\" in details:
        lines.append(f\"SHA256={details['expected_sha256']}\")
    elif not matched and \"expected_sha256\" in details:
        lines.append(f\"EXPECTED_SHA256={details['expected_sha256']}\")
        lines.append(f\"ACTUAL_SHA256={details['actual_sha256']}\")
    elif not matched and \"expected_exists\" in details:
        lines.append(f\"EXPECTED_EXISTS={details['expected_exists']}\")
        lines.append(f\"ACTUAL_EXISTS={details['actual_exists']}\")
    return lines
"""


def make_readme_text() -> str:
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "This directory holds shipped Zigux validation helpers and compact reminder surfaces.",
            "",
            "## Phase 1",
            "",
            "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live parity-fixture, artifact-diff, bench, owner-map, and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
            f"- {README_REQUIRED_MARKERS[0]}",
            f"- {README_REQUIRED_MARKERS[1]}",
            f"- {README_REQUIRED_MARKERS[2]}",
            "- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
            "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, bench-expectation, and helper-replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
            f"- {README_REQUIRED_MARKERS[3]}",
            f"- {README_REQUIRED_MARKERS[4]}",
            "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
        )
    ) + "\n"


def build_case_root(base: Path) -> Path:
    write_file(base / ARTIFACT_DIFF_REL, make_artifact_diff_text())
    write_file(base / README_REL, make_readme_text())
    write_file(base / FIXTURE_REL, make_fixture_json())
    write_file(base / MANIFEST_REL, make_manifest_json())
    write_file(base / BLOCKERS_REL, make_blockers_json())
    return base


def run_self_test() -> int:
    cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)

        good_root = build_case_root(tmp_root / "good")
        cases.append(("good", run_check(good_root) == 0))

        missing_artifact_diff_root = build_case_root(tmp_root / "missing_artifact_diff")
        (missing_artifact_diff_root / ARTIFACT_DIFF_REL).unlink()
        cases.append(
            ("missing_artifact_diff", run_check(missing_artifact_diff_root) != 0)
        )

        artifact_diff_contract_root = build_case_root(tmp_root / "artifact_diff_contract")
        write_file(
            artifact_diff_contract_root / ARTIFACT_DIFF_REL,
            make_artifact_diff_text().replace(
                "def render_result_lines", "def render_result_rows", 1
            ),
        )
        cases.append(
            ("artifact_diff_contract", run_check(artifact_diff_contract_root) != 0)
        )

        fixture_drift_root = build_case_root(tmp_root / "fixture_drift")
        write_file(
            fixture_drift_root / FIXTURE_REL,
            json.dumps({"find_bit": {}, "bitmap": {}}, indent=2) + "\n",
        )
        cases.append(("fixture_drift", run_check(fixture_drift_root) != 0))

        fixture_string_drift_root = build_case_root(tmp_root / "fixture_string_drift")
        write_file(
            fixture_string_drift_root / FIXTURE_REL,
            json.dumps(
                {
                    **json.loads(make_fixture_json()),
                    "string": {"strtobool_invalid": 22},
                },
                indent=2,
            )
            + "\n",
        )
        cases.append(
            ("fixture_string_drift", run_check(fixture_string_drift_root) != 0)
        )

        fixture_slab_drift_root = build_case_root(tmp_root / "fixture_slab_drift")
        write_file(
            fixture_slab_drift_root / FIXTURE_REL,
            json.dumps(
                {
                    **json.loads(make_fixture_json()),
                    "slab": {"zero_after_kmalloc": False},
                },
                indent=2,
            )
            + "\n",
        )
        cases.append(("fixture_slab_drift", run_check(fixture_slab_drift_root) != 0))

        manifest_status_drift_root = build_case_root(tmp_root / "manifest_status_drift")
        write_file(
            manifest_status_drift_root / MANIFEST_REL,
            json.dumps(
                {
                    "phase": "Phase 1",
                    "status": "open",
                    "helper_count": len(EXPECTED_HELPERS),
                    "helpers": list(EXPECTED_HELPERS),
                },
                indent=2,
            )
            + "\n",
        )
        cases.append(
            ("manifest_status_drift", run_check(manifest_status_drift_root) != 0)
        )

        manifest_drift_root = build_case_root(tmp_root / "manifest_drift")
        write_file(
            manifest_drift_root / MANIFEST_REL,
            json.dumps(
                {
                    "phase": "Phase 1",
                    "status": EXPECTED_MANIFEST_STATUS,
                    "helper_count": len(EXPECTED_HELPERS),
                    "helpers": list(EXPECTED_HELPERS[:-1]),
                    "lane_sequencing": {
                        "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
                        "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
                        "rule_summary": EXPECTED_LANE_RULE_SUMMARY,
                        "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
                    },
                },
                indent=2,
            )
            + "\n",
        )
        cases.append(("manifest_drift", run_check(manifest_drift_root) != 0))

        manifest_lane_split_drift_root = build_case_root(tmp_root / "manifest_lane_split_drift")
        payload = json.loads(make_manifest_json())
        payload["lane_sequencing"]["shared_replay_parked_helpers"] = payload["lane_sequencing"]["shared_replay_parked_helpers"][1:]
        payload["lane_sequencing"]["direct_anchor_followup_helpers"] = [
            EXPECTED_SHARED_REPLAY_PARKED_HELPERS[0],
            *payload["lane_sequencing"]["direct_anchor_followup_helpers"],
        ]
        write_file(
            manifest_lane_split_drift_root / MANIFEST_REL,
            json.dumps(payload, indent=2) + "\n",
        )
        cases.append(
            ("manifest_lane_split_drift", run_check(manifest_lane_split_drift_root) != 0)
        )

        manifest_lane_rule_drift_root = build_case_root(tmp_root / "manifest_lane_rule_drift")
        payload = json.loads(make_manifest_json())
        payload["lane_sequencing"]["anti_overlap_rule"] = "Do not reopen Phase 1 without rereading the helper split first."
        write_file(
            manifest_lane_rule_drift_root / MANIFEST_REL,
            json.dumps(payload, indent=2) + "\n",
        )
        cases.append(
            ("manifest_lane_rule_drift", run_check(manifest_lane_rule_drift_root) != 0)
        )

        readme_marker_root = build_case_root(tmp_root / "readme_marker")
        write_file(
            readme_marker_root / README_REL,
            make_readme_text().replace(README_REQUIRED_MARKERS[3], "", 1),
        )
        cases.append(("readme_marker", run_check(readme_marker_root) != 0))

        readme_forbidden_root = build_case_root(tmp_root / "readme_forbidden")
        write_file(
            readme_forbidden_root / README_REL,
            make_readme_text()
            + "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`\n",
        )
        cases.append(("readme_forbidden", run_check(readme_forbidden_root) != 0))

        blockers_missing_root = build_case_root(tmp_root / "blockers_missing")
        (blockers_missing_root / BLOCKERS_REL).unlink()
        cases.append(("blockers_missing", run_check(blockers_missing_root) != 0))

        blockers_drift_root = build_case_root(tmp_root / "blockers_drift")
        payload = json.loads(make_blockers_json())
        payload["replay"]["blockers"][0]["actual"] = True
        write_file(
            blockers_drift_root / BLOCKERS_REL,
            json.dumps(payload, indent=2) + "\n",
        )
        cases.append(("blockers_drift", run_check(blockers_drift_root) != 0))

        blockers_helpers_drift_root = build_case_root(tmp_root / "blockers_helpers_drift")
        payload = json.loads(make_blockers_json())
        payload["c_harness"]["helpers"] = payload["c_harness"]["helpers"][:-1]
        write_file(
            blockers_helpers_drift_root / BLOCKERS_REL,
            json.dumps(payload, indent=2) + "\n",
        )
        cases.append(
            ("blockers_helpers_drift", run_check(blockers_helpers_drift_root) != 0)
        )

        replay_anchor_root = build_case_root(tmp_root / "replay_anchor")
        write_file(replay_anchor_root / REPLAY_REL, make_replay_text())
        cases.append(("replay_present", run_check(replay_anchor_root) == 0))
        write_file(
            replay_anchor_root / REPLAY_REL,
            "\n".join(REPLAY_IMPORTS) + "\n",
        )
        cases.append(("replay_anchor", run_check(replay_anchor_root) != 0))

    failed = [name for name, ok in cases if not ok]
    if failed:
        print("PHASE1_PARITY_SELF_TEST=fail")
        for name in failed:
            print(f"PHASE1_PARITY_SELF_TEST_FAILED_CASE={name}")
        return 1

    print("PHASE1_PARITY_SELF_TEST=pass")
    print(f"PHASE1_PARITY_SELF_TEST_CASE_COUNT={len(cases)}")
    print(
        "PHASE1_PARITY_SELF_TEST_CASES="
        + ",".join(name for name, _ in cases)
    )
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
