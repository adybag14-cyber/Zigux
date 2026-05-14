#!/usr/bin/env python3
"""Fail closed on the current Phase 13 Landlock syscalls packet."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = "scripts/zigux/check-phase13-landlock-syscalls-packet.py"
HELPER_PATH = "security/landlock/syscalls.zig"
SLICE_PATH = "Documentation/zigux/phase13-landlock-syscalls-slice.md"
SURVEY_PATH = "Documentation/zigux/phase13-landlock-syscalls-survey.md"
GOVERNANCE_PATH = "Documentation/zigux/phase13-landlock-syscalls-governance.md"
REPLAY_PATH = "zigux/tests/phase13_landlock_syscalls.zig"
REVIEWABILITY_PATH = "zigux/tests/phase13_landlock_syscalls_reviewability.zig"
MANIFEST_PATH = "zigux/tests/phase13_landlock_syscalls_manifest.json"

REQUIRED_FILES = (
    SCRIPT_PATH,
    HELPER_PATH,
    SLICE_PATH,
    SURVEY_PATH,
    GOVERNANCE_PATH,
    REPLAY_PATH,
    REVIEWABILITY_PATH,
    MANIFEST_PATH,
)

HELPER_MARKERS = (
    ".provides_create_ruleset_planning = true",
    ".provides_restrict_self_planning = true",
    ".provides_add_rule_planning = true",
    ".provides_ruleset_release_planning = true",
    ".provides_ruleset_fops_planning = true",
    ".validates_create_ruleset_flags = true",
    ".validates_restrict_self_logging = true",
    "pub const AddRuleAction = enum {",
    "path_beneath,",
    "net_port,",
    "pub fn planCreateRuleset(",
    "pub fn planRestrictSelf(",
    "pub fn planAddRule(",
    "pub fn planLandlockAddRule(",
    "pub fn planFopRulesetRelease(",
    "pub fn planRulesetFops(",
)

SLICE_MARKERS = (
    "# Phase 13 Landlock Syscalls Slice",
    "`landlock_create_ruleset()`",
    "`landlock_restrict_self()`",
    "`landlock_add_rule()`",
    "`fop_ruleset_release()`",
    "`ruleset_fops`",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
)

SURVEY_MARKERS = (
    "# Phase 13 Landlock Syscalls Survey",
    "`security/landlock/syscalls.zig`",
    "`Documentation/zigux/phase13-landlock-syscalls-slice.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-survey.md`",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "path_beneath",
    "net_port",
    "shared `phase13_build.zig` route still remains absent",
)

GOVERNANCE_MARKERS = (
    "# Phase 13 Landlock Syscalls Governance",
    "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter.",
    "the release-side `fop_ruleset_release()` ownership drop",
    "the combined `ruleset_fops` wrapper contract",
    "`Documentation/zigux/phase13-landlock-syscalls-slice.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-survey.md`",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
)

REPLAY_MARKERS = (
    "test \"phase13 landlock syscalls keeps add-rule dispatch explicit for both helper branches\" {",
    "const path_plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{",
    "rule_type = syscalls.rule_type_path_beneath,",
    "const net_plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{",
    "rule_type = syscalls.rule_type_net_port,",
    "test \"phase13 landlock syscalls keeps release-side helper discipline explicit\" {",
    "test \"phase13 landlock syscalls manifest records the bounded syscall helper packet\" {",
    "\"\\\"lane_key\\\": \\\"P13-L17\\\"\"",
)

REVIEWABILITY_MARKERS = (
    "try std.testing.expectEqualStrings(\"P13-L17\", manifest.lane_key);",
    "try std.testing.expectEqualStrings(\"master-readback-2026-05-13\", manifest.surveyed_commit);",
    "try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);",
    "\"phase13-landlock-syscalls-helper-starter\"",
    "\"phase13-landlock-syscalls-reviewability-gate\"",
    "\"phase13-landlock-live-fd-installation\"",
    "\"phase13-landlock-live-credential-state\"",
    "\"phase13-landlock-live-ruleset-state\"",
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(text: str, label: str, markers: tuple[str, ...], problems: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            problems.append(f"missing-marker:{label}:{marker}")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    helper_text = read_text(root, HELPER_PATH)
    slice_text = read_text(root, SLICE_PATH)
    survey_text = read_text(root, SURVEY_PATH)
    governance_text = read_text(root, GOVERNANCE_PATH)
    replay_text = read_text(root, REPLAY_PATH)
    reviewability_text = read_text(root, REVIEWABILITY_PATH)
    manifest_text = read_text(root, MANIFEST_PATH)

    require_markers(helper_text, "helper", HELPER_MARKERS, problems)
    require_markers(slice_text, "slice", SLICE_MARKERS, problems)
    require_markers(survey_text, "survey", SURVEY_MARKERS, problems)
    require_markers(governance_text, "governance", GOVERNANCE_MARKERS, problems)
    require_markers(replay_text, "replay", REPLAY_MARKERS, problems)
    require_markers(reviewability_text, "reviewability", REVIEWABILITY_MARKERS, problems)

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"manifest:json:{exc.msg}"]

    if manifest.get("lane_key") != "P13-L17":
        problems.append(f"manifest:lane_key:{manifest.get('lane_key')}")
    if manifest.get("phase") != "Phase 13":
        problems.append(f"manifest:phase:{manifest.get('phase')}")
    if manifest.get("surveyed_commit") != "master-readback-2026-05-13":
        problems.append(f"manifest:surveyed_commit:{manifest.get('surveyed_commit')}")
    if manifest.get("anchor") != "security/landlock/syscalls.c":
        problems.append(f"manifest:anchor:{manifest.get('anchor')}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        problems.append("manifest:missing-survey-summary")
    else:
        expected_summary = {
            "preexisting_phase13_build_present": False,
            "preexisting_phase13_make_target_present": True,
            "preexisting_syscalls_zig_present": True,
            "preexisting_phase13_landlock_syscalls_test_present": True,
            "preexisting_phase13_landlock_syscalls_slice_present": True,
            "preexisting_phase13_landlock_syscalls_reviewability_present": True,
            "preexisting_phase13_landlock_syscalls_survey_present": True,
            "preexisting_phase13_landlock_syscalls_manifest_present": True,
        }
        for key, expected in expected_summary.items():
            if summary.get(key) is not expected:
                problems.append(f"manifest:summary:{key}:{summary.get(key)}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != 7:
        problems.append(f"manifest:gaps:{len(gaps) if isinstance(gaps, list) else 'missing'}")
    else:
        gap_index = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
        expected_gaps = {
            "phase13-build-gate": "blocked_on_missing_shared_build_surface",
            "phase13-landlock-syscalls-helper-starter": "starter_landed",
            "phase13-landlock-syscalls-direct-test-gate": "starter_landed",
            "phase13-landlock-syscalls-reviewability-gate": "starter_landed",
            "phase13-landlock-live-fd-installation": "blocked_on_live_fd_installation",
            "phase13-landlock-live-credential-state": "blocked_on_live_credential_state",
            "phase13-landlock-live-ruleset-state": "blocked_on_live_ruleset_state",
        }
        for gap_id, expected_status in expected_gaps.items():
            gap = gap_index.get(gap_id)
            if gap is None:
                problems.append(f"manifest:missing-gap:{gap_id}")
                continue
            if gap.get("status") != expected_status:
                problems.append(f"manifest:gap-status:{gap_id}:{gap.get('status')}")

    return problems


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    write_text(root, HELPER_PATH, "\n".join(HELPER_MARKERS) + "\n")
    write_text(root, SLICE_PATH, "\n".join(SLICE_MARKERS) + "\n")
    write_text(root, SURVEY_PATH, "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root, GOVERNANCE_PATH, "\n".join(GOVERNANCE_MARKERS) + "\n")
    write_text(root, REPLAY_PATH, "\n".join(REPLAY_MARKERS) + "\n")
    write_text(root, REVIEWABILITY_PATH, "\n".join(REVIEWABILITY_MARKERS) + "\n")
    write_text(
        root,
        MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "P13-L17",
                "phase": "Phase 13",
                "surveyed_commit": "master-readback-2026-05-13",
                "anchor": "security/landlock/syscalls.c",
                "survey_summary": {
                    "preexisting_phase13_build_present": False,
                    "preexisting_phase13_make_target_present": True,
                    "preexisting_syscalls_zig_present": True,
                    "preexisting_phase13_landlock_syscalls_test_present": True,
                    "preexisting_phase13_landlock_syscalls_slice_present": True,
                    "preexisting_phase13_landlock_syscalls_reviewability_present": True,
                    "preexisting_phase13_landlock_syscalls_survey_present": True,
                    "preexisting_phase13_landlock_syscalls_manifest_present": True,
                },
                "gaps": [
                    {"id": "phase13-build-gate", "status": "blocked_on_missing_shared_build_surface"},
                    {"id": "phase13-landlock-syscalls-helper-starter", "status": "starter_landed"},
                    {"id": "phase13-landlock-syscalls-direct-test-gate", "status": "starter_landed"},
                    {"id": "phase13-landlock-syscalls-reviewability-gate", "status": "starter_landed"},
                    {"id": "phase13-landlock-live-fd-installation", "status": "blocked_on_live_fd_installation"},
                    {"id": "phase13-landlock-live-credential-state", "status": "blocked_on_live_credential_state"},
                    {"id": "phase13-landlock-live-ruleset-state", "status": "blocked_on_live_ruleset_state"},
                ],
            },
            indent=2,
        )
        + "\n",
    )


def assert_missing_case(root: Path, label: str, rel_path: str, needle: str) -> None:
    text = read_text(root, rel_path)
    if needle not in text:
        raise SystemExit(f"self-test-fixture-missing:{label}")
    write_text(root, rel_path, text.replace(needle, "", 1))
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{label}")
    expected = f"missing-marker:{label}:{needle}"
    actual = result.stdout.strip() or result.stderr.strip() or "no_output"
    if expected not in actual:
        raise SystemExit(f"self-test-mismatch:{label}:{actual}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="phase13_landlock_syscalls_packet_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            ("helper", HELPER_PATH, HELPER_MARKERS[0]),
            ("helper", HELPER_PATH, HELPER_MARKERS[-1]),
            ("slice", SLICE_PATH, SLICE_MARKERS[5]),
            ("survey", SURVEY_PATH, SURVEY_MARKERS[8]),
            ("governance", GOVERNANCE_PATH, GOVERNANCE_MARKERS[1]),
            ("replay", REPLAY_PATH, REPLAY_MARKERS[3]),
            ("reviewability", REVIEWABILITY_PATH, REVIEWABILITY_MARKERS[2]),
        )
        for label, rel_path, needle in mutations:
            case_root = Path(tmp) / f"{label}_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, label, rel_path, needle)
            cases += 1

    print("PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST=pass")
    print(f"PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET=fail")
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_PROBLEMS_END")
        return 1

    print("PHASE13_LANDLOCK_SYSCALLS_PACKET=pass")
    print(f"PHASE13_LANDLOCK_SYSCALLS_PACKET_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
