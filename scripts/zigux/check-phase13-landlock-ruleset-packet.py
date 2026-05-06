#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "Documentation/zigux/phase13-landlock-ruleset-slice.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md",
    "security/landlock/ruleset.zig",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/Makefile",
]

SLICE_MARKERS = [
    "landlock_create_ruleset()",
    "rb_link_node()",
    "rb_replace_node()",
]

SURVEY_MARKERS = [
    "`PHASE13_LANE_KEY=P13-L12`",
    "phase13-landlock-ruleset-ownership.md",
    "phase13-landlock-tree-replacement-followup",
    "rb_replace_node()",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
]

OWNERSHIP_MARKERS = [
    "`PHASE13_LANE_KEY=P13-L12`",
    "matched-rule replacement planning",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "manifest, survey, slice, and test gate move together",
    "live-tree blocker",
]

HELPER_MARKERS = [
    "provides_rule_tree_search_planning = true,",
    "provides_rule_tree_link_planning = true,",
    "provides_rule_tree_replacement_planning = true,",
    "touches_live_object_trees = false,",
    "pub fn planRuleTreeSearch(",
    "pub fn planRuleTreeLink(",
    "pub fn planRuleTreeReplacement(",
]

BUILD_MARKERS = [
    'b.path("../../security/landlock/ruleset.zig")',
    'b.path("phase13_landlock_ruleset.zig")',
    'const phase13_landlock_ruleset_tests = b.addTest(.{',
    "test_step.dependOn(&run_phase13_landlock_ruleset_tests.step);",
]

TEST_MARKERS = [
    'try std.testing.expectEqualStrings("P13-L12", manifest.lane_key);',
    'try std.testing.expectEqualStrings("security/landlock/ruleset.c", manifest.anchor);',
    'try std.testing.expect(std.mem.indexOf(u8, ownership_note, "PHASE13_LANE_KEY=P13-L12") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, ownership_note, "phase13_landlock_ruleset_manifest.json") != null);',
    'try std.testing.expect(descriptor.provides_rule_tree_replacement_planning);',
    'ruleset.RulesetHelperLab.planRuleTreeReplacement(',
]

MAKE_MARKERS = [
    "phase13-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py",
]

SUMMARY_KEYS = [
    "preexisting_phase13_build_present",
    "preexisting_phase13_make_target_present",
    "preexisting_ruleset_zig_present",
    "preexisting_phase13_landlock_test_present",
    "preexisting_phase13_landlock_slice_note_present",
    "preexisting_phase13_landlock_survey_note_present",
]

GAP_STATUSES = {
    "phase13-landlock-ruleset-starter": "starter_landed",
    "phase13-landlock-rule-layer-merge-followup": "starter_landed",
    "phase13-landlock-tree-search-followup": "starter_landed",
    "phase13-landlock-tree-link-followup": "starter_landed",
    "phase13-landlock-tree-replacement-followup": "starter_landed",
    "phase13-landlock-live-tree-state-blocker": "blocked_on_live_lsm_state",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_missing(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate_manifest(text: str) -> list[str]:
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"phase13-landlock-ruleset-manifest:json:{exc.msg}"]

    issues: list[str] = []
    if manifest.get("phase") != "Phase 13":
        issues.append("phase13-landlock-ruleset-manifest:phase")
    if manifest.get("anchor") != "security/landlock/ruleset.c":
        issues.append("phase13-landlock-ruleset-manifest:anchor")

    summary = manifest.get("survey_summary", {})
    for key in SUMMARY_KEYS:
        if summary.get(key) is not True:
            issues.append(f"phase13-landlock-ruleset-manifest-summary:{key}")

    statuses = {
        gap.get("id"): gap.get("status")
        for gap in manifest.get("gaps", [])
        if isinstance(gap, dict)
    }
    for gap_id, expected_status in GAP_STATUSES.items():
        if gap_id not in statuses:
            issues.append(f"phase13-landlock-ruleset-manifest-gap:{gap_id}")
        elif statuses[gap_id] != expected_status:
            issues.append(f"phase13-landlock-ruleset-manifest-gap-status:{gap_id}")
    return issues


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    checks = [
        ("Documentation/zigux/phase13-landlock-ruleset-slice.md", SLICE_MARKERS, "phase13-landlock-ruleset-slice"),
        ("Documentation/zigux/phase13-landlock-ruleset-survey.md", SURVEY_MARKERS, "phase13-landlock-ruleset-survey"),
        ("Documentation/zigux/phase13-landlock-ruleset-ownership.md", OWNERSHIP_MARKERS, "phase13-landlock-ruleset-ownership"),
        ("security/landlock/ruleset.zig", HELPER_MARKERS, "landlock-ruleset-helper"),
        ("zigux/tests/phase13_build.zig", BUILD_MARKERS, "phase13-build"),
        ("zigux/tests/phase13_landlock_ruleset.zig", TEST_MARKERS, "phase13-landlock-ruleset-test"),
        ("zigux/Makefile", MAKE_MARKERS, "makefile"),
    ]
    for rel, markers, prefix in checks:
        issues.extend(collect_missing(read_text(root / rel), markers, prefix))

    issues.extend(validate_manifest(read_text(root / "zigux/tests/phase13_landlock_ruleset_manifest.json")))
    return issues


def seed_fixture_tree(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, "// stub\n")

    writes = {
        "Documentation/zigux/phase13-landlock-ruleset-slice.md": "\n".join(SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase13-landlock-ruleset-survey.md": "\n".join(SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase13-landlock-ruleset-ownership.md": "\n".join(OWNERSHIP_MARKERS) + "\n",
        "security/landlock/ruleset.zig": "\n".join(HELPER_MARKERS) + "\n",
        "zigux/tests/phase13_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/tests/phase13_landlock_ruleset.zig": "\n".join(TEST_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        "zigux/tests/phase13_landlock_ruleset_manifest.json": json.dumps(
            {
                "lane_key": "P13-L12",
                "phase": "Phase 13",
                "surveyed_commit": "64617ec0339f3f52accf5614bc918a940a503f7a",
                "anchor": "security/landlock/ruleset.c",
                "survey_summary": {key: True for key in SUMMARY_KEYS},
                "gaps": [
                    {"id": gap_id, "status": status}
                    for gap_id, status in GAP_STATUSES.items()
                ],
            },
            indent=2,
        )
        + "\n",
    }
    for rel, text in writes.items():
        write_text(root / rel, text)


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        got_text = ",".join(got) or "none"
        want_text = ",".join(want) or "none"
        raise SystemExit(f"phase13-landlock-ruleset-self-test:{label}:got={got_text}:want={want_text}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_landlock_ruleset_packet_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        write_text(root / "Documentation/zigux/phase13-landlock-ruleset-survey.md", "`PHASE13_LANE_KEY=P13-L12`\n")
        assert_only(
            validate(root),
            [
                "phase13-landlock-ruleset-survey:phase13-landlock-ruleset-ownership.md",
                "phase13-landlock-ruleset-survey:phase13-landlock-tree-replacement-followup",
                "phase13-landlock-ruleset-survey:rb_replace_node()",
                "phase13-landlock-ruleset-survey:scripts/zigux/check-phase13-landlock-ruleset-packet.py",
            ],
            "survey_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "Documentation/zigux/phase13-landlock-ruleset-ownership.md", "live-tree blocker\n")
        assert_only(
            validate(root),
            [
                "phase13-landlock-ruleset-ownership:`PHASE13_LANE_KEY=P13-L12`",
                "phase13-landlock-ruleset-ownership:matched-rule replacement planning",
                "phase13-landlock-ruleset-ownership:scripts/zigux/check-phase13-landlock-ruleset-packet.py",
                "phase13-landlock-ruleset-ownership:manifest, survey, slice, and test gate move together",
            ],
            "ownership_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "security/landlock/ruleset.zig", "pub fn planRuleTreeSearch(\n")
        assert_only(
            validate(root),
            [
                "landlock-ruleset-helper:provides_rule_tree_search_planning = true,",
                "landlock-ruleset-helper:provides_rule_tree_link_planning = true,",
                "landlock-ruleset-helper:provides_rule_tree_replacement_planning = true,",
                "landlock-ruleset-helper:touches_live_object_trees = false,",
                "landlock-ruleset-helper:pub fn planRuleTreeLink(",
                "landlock-ruleset-helper:pub fn planRuleTreeReplacement(",
            ],
            "helper_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(root / "zigux/Makefile", "phase13-validate:\n")
        assert_only(
            validate(root),
            ["makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py"],
            "make_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(
            root / "zigux/tests/phase13_landlock_ruleset_manifest.json",
            json.dumps({"lane_key": "P13-L12", "survey_summary": {}}, indent=2) + "\n",
        )
        assert_only(
            validate(root),
            [
                "phase13-landlock-ruleset-manifest:phase",
                "phase13-landlock-ruleset-manifest:anchor",
                "phase13-landlock-ruleset-manifest-summary:preexisting_phase13_build_present",
                "phase13-landlock-ruleset-manifest-summary:preexisting_phase13_make_target_present",
                "phase13-landlock-ruleset-manifest-summary:preexisting_ruleset_zig_present",
                "phase13-landlock-ruleset-manifest-summary:preexisting_phase13_landlock_test_present",
                "phase13-landlock-ruleset-manifest-summary:preexisting_phase13_landlock_slice_note_present",
                "phase13-landlock-ruleset-manifest-summary:preexisting_phase13_landlock_survey_note_present",
                "phase13-landlock-ruleset-manifest-gap:phase13-landlock-ruleset-starter",
                "phase13-landlock-ruleset-manifest-gap:phase13-landlock-rule-layer-merge-followup",
                "phase13-landlock-ruleset-manifest-gap:phase13-landlock-tree-search-followup",
                "phase13-landlock-ruleset-manifest-gap:phase13-landlock-tree-link-followup",
                "phase13-landlock-ruleset-manifest-gap:phase13-landlock-tree-replacement-followup",
                "phase13-landlock-ruleset-manifest-gap:phase13-landlock-live-tree-state-blocker",
            ],
            "manifest_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        (root / "zigux/tests/phase13_landlock_ruleset.zig").unlink()
        assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase13_landlock_ruleset.zig"],
            "required_file_guard_failed",
        )
        case_count += 1

    print("PHASE13_LANDLOCK_RULESET_PACKET=pass")
    print(f"PHASE13_LANDLOCK_RULESET_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shipped Phase 13 landlock ruleset packet.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(f"PHASE13_LANDLOCK_RULESET_PACKET_ISSUE={issue}")
        return 1

    print("PHASE13_LANDLOCK_RULESET_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
