#!/usr/bin/env python3
"""Fail closed on the bounded Phase 13 Landlock syscalls packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

MANIFEST_PATH = "zigux/tests/phase13_landlock_syscalls_manifest.json"
SLICE_PATH = "Documentation/zigux/phase13-landlock-syscalls-slice.md"
SURVEY_PATH = "Documentation/zigux/phase13-landlock-syscalls-survey.md"
GOVERNANCE_PATH = "Documentation/zigux/phase13-landlock-syscalls-governance.md"
HELPER_PATH = "security/landlock/syscalls.zig"
DIRECT_TEST_PATH = "zigux/tests/phase13_landlock_syscalls.zig"
REVIEWABILITY_PATH = "zigux/tests/phase13_landlock_syscalls_reviewability.zig"

REQUIRED_FILES = (
    MANIFEST_PATH,
    SLICE_PATH,
    SURVEY_PATH,
    GOVERNANCE_PATH,
    HELPER_PATH,
    DIRECT_TEST_PATH,
    REVIEWABILITY_PATH,
)

SLICE_MARKERS = (
    "`landlock_restrict_self()` credential gate explicit",
    "`landlock_add_rule()` reviewable",
    "`fop_ruleset_release()` lifetime drop explicit",
    "`ruleset_fops` wrapper contract explicit",
    "`zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "`zigux/tests/phase13_build.zig` surface remains absent",
)

SURVEY_MARKERS = (
    "reviewed against live `master` `master-readback-2026-05-12`",
    "`security/landlock/syscalls.zig` helper starter",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "shared `zigux/tests/phase13_build.zig` route",
    "blocked `phase13-landlock-live-fd-installation`",
    "blocked `phase13-landlock-live-credential-state`",
    "blocked `phase13-landlock-live-ruleset-state`",
)

GOVERNANCE_MARKERS = (
    "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter.",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "`zigux/tests/phase13_build.zig`",
    "live file-descriptor installation",
    "release-side `fop_ruleset_release()` ownership drop",
    "combined `ruleset_fops` wrapper contract",
)

HELPER_MARKERS = (
    ".provides_ruleset_release_planning = true",
    ".provides_ruleset_fops_planning = true",
    ".validates_credential_gate = true",
    "pub fn planRestrictSelf(",
    "pub fn planAddRule(",
    "pub fn planLandlockAddRule(",
    "pub fn planFopRulesetRelease(",
    "pub fn planRulesetFops(",
)

DIRECT_TEST_MARKERS = (
    'test "phase13 landlock syscalls keeps restrict-self logging and detached updates explicit" {',
    "const plan = try syscalls.SyscallsHelperLab.planRestrictSelf(.{",
    'test "phase13 landlock syscalls keeps add-rule dispatch explicit for both helper branches" {',
    "const path_plan = try syscalls.SyscallsHelperLab.planLandlockAddRule(.{",
    'test "phase13 landlock syscalls keeps release-side helper discipline explicit" {',
    "const plan = try syscalls.SyscallsHelperLab.planRulesetFops(.{});",
    '\\"id\\": \\"phase13-landlock-syscalls-reviewability-gate\\"',
)

REVIEWABILITY_MARKERS = (
    'try std.testing.expectEqualStrings("P13-L13", manifest.lane_key);',
    'try std.testing.expectEqualStrings("master-readback-2026-05-12", manifest.surveyed_commit);',
    "try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_reviewability_present);",
    "try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_manifest_present);",
    'try expectGap(',
    '"phase13-landlock-syscalls-reviewability-gate",',
    '"phase13-landlock-live-fd-installation",',
    '"phase13-landlock-live-credential-state",',
    '"phase13-landlock-live-ruleset-state",',
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_file(root: Path, rel_path: str, errors: list[str]) -> Path | None:
    path = root / rel_path
    if not path.is_file():
        errors.append(f"missing-file:{rel_path}")
        return None
    return path


def require_markers(source: str, label: str, markers: tuple[str, ...], errors: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            errors.append(f"missing-marker:{label}:{marker}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    manifest_path = require_file(root, MANIFEST_PATH, errors)
    slice_path = require_file(root, SLICE_PATH, errors)
    survey_path = require_file(root, SURVEY_PATH, errors)
    governance_path = require_file(root, GOVERNANCE_PATH, errors)
    helper_path = require_file(root, HELPER_PATH, errors)
    direct_test_path = require_file(root, DIRECT_TEST_PATH, errors)
    reviewability_path = require_file(root, REVIEWABILITY_PATH, errors)
    if errors:
        return errors

    manifest_text = read_text(manifest_path)
    slice_text = read_text(slice_path)
    survey_text = read_text(survey_path)
    governance_text = read_text(governance_path)
    helper_text = read_text(helper_path)
    direct_test_text = read_text(direct_test_path)
    reviewability_text = read_text(reviewability_path)

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"manifest-json:{exc.msg}"]

    if manifest.get("lane_key") != "P13-L13":
        errors.append(f"manifest-lane-key:{manifest.get('lane_key')!r}")
    if manifest.get("surveyed_commit") != "master-readback-2026-05-12":
        errors.append(f"manifest-surveyed-commit:{manifest.get('surveyed_commit')!r}")
    if manifest.get("anchor") != "security/landlock/syscalls.c":
        errors.append(f"manifest-anchor:{manifest.get('anchor')!r}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        errors.append("manifest-summary:missing")
    else:
        for key, expected in (
            ("preexisting_phase13_build_present", False),
            ("preexisting_phase13_make_target_present", True),
            ("preexisting_syscalls_zig_present", True),
            ("preexisting_phase13_landlock_syscalls_test_present", True),
            ("preexisting_phase13_landlock_syscalls_slice_present", True),
            ("preexisting_phase13_landlock_syscalls_reviewability_present", True),
            ("preexisting_phase13_landlock_syscalls_survey_present", True),
            ("preexisting_phase13_landlock_syscalls_manifest_present", True),
        ):
            if summary.get(key) is not expected:
                errors.append(f"manifest-summary:{key}:{summary.get(key)!r}")

    gap_ids = {gap.get("id") for gap in manifest.get("gaps", []) if isinstance(gap, dict)}
    for required_gap in (
        "phase13-build-gate",
        "phase13-landlock-syscalls-helper-starter",
        "phase13-landlock-syscalls-direct-test-gate",
        "phase13-landlock-syscalls-reviewability-gate",
        "phase13-landlock-live-fd-installation",
        "phase13-landlock-live-credential-state",
        "phase13-landlock-live-ruleset-state",
    ):
        if required_gap not in gap_ids:
            errors.append(f"manifest-gap:{required_gap}")

    require_markers(slice_text, "slice", SLICE_MARKERS, errors)
    require_markers(survey_text, "survey", SURVEY_MARKERS, errors)
    require_markers(governance_text, "governance", GOVERNANCE_MARKERS, errors)
    require_markers(helper_text, "helper", HELPER_MARKERS, errors)
    require_markers(direct_test_text, "direct-test", DIRECT_TEST_MARKERS, errors)
    require_markers(reviewability_text, "reviewability", REVIEWABILITY_MARKERS, errors)

    return errors


def seed_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "P13-L13",
                "surveyed_commit": "master-readback-2026-05-12",
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
                    {"id": "phase13-build-gate"},
                    {"id": "phase13-landlock-syscalls-helper-starter"},
                    {"id": "phase13-landlock-syscalls-direct-test-gate"},
                    {"id": "phase13-landlock-syscalls-reviewability-gate"},
                    {"id": "phase13-landlock-live-fd-installation"},
                    {"id": "phase13-landlock-live-credential-state"},
                    {"id": "phase13-landlock-live-ruleset-state"},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / SLICE_PATH, "\n".join(SLICE_MARKERS) + "\n")
    write_text(root / SURVEY_PATH, "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / GOVERNANCE_PATH, "\n".join(GOVERNANCE_MARKERS) + "\n")
    write_text(root / HELPER_PATH, "\n".join(HELPER_MARKERS) + "\n")
    write_text(root / DIRECT_TEST_PATH, "\n".join(DIRECT_TEST_MARKERS) + "\n")
    write_text(root / REVIEWABILITY_PATH, "\n".join(REVIEWABILITY_MARKERS) + "\n")


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        raise SystemExit(
            f"phase13-landlock-syscalls-packet-self-test:{label}:got={got!r}:want={want!r}"
        )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_landlock_syscalls_packet_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline")
        case_count += 1

        write_text(root / SLICE_PATH, "\n".join(SLICE_MARKERS[1:]) + "\n")
        assert_only(
            validate(root),
            ["missing-marker:slice:`landlock_restrict_self()` credential gate explicit"],
            "missing-slice-marker",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SURVEY_PATH, "\n".join(SURVEY_MARKERS[:-1]) + "\n")
        assert_only(
            validate(root),
            ["missing-marker:survey:blocked `phase13-landlock-live-ruleset-state`"],
            "missing-survey-marker",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / GOVERNANCE_PATH, "\n".join(GOVERNANCE_MARKERS[1:]) + "\n")
        assert_only(
            validate(root),
            [
                "missing-marker:governance:Current `master` materializes a small `security/landlock/syscalls.zig` helper starter."
            ],
            "missing-governance-marker",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, "\n".join(HELPER_MARKERS[:-1]) + "\n")
        assert_only(
            validate(root),
            ["missing-marker:helper:pub fn planRulesetFops("],
            "missing-helper-marker",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / DIRECT_TEST_PATH, "\n".join(DIRECT_TEST_MARKERS[:-1]) + "\n")
        assert_only(
            validate(root),
            ['missing-marker:direct-test:\\"id\\": \\"phase13-landlock-syscalls-reviewability-gate\\"'],
            "missing-direct-test-marker",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / REVIEWABILITY_PATH, "\n".join(REVIEWABILITY_MARKERS[:-1]) + "\n")
        assert_only(
            validate(root),
            ['missing-marker:reviewability:"phase13-landlock-live-ruleset-state",'],
            "missing-reviewability-marker",
        )
        case_count += 1

        seed_fixture_tree(root)
        manifest = json.loads(read_text(root / MANIFEST_PATH))
        manifest["lane_key"] = "P13-LXX"
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        assert_only(
            validate(root),
            ["manifest-lane-key:'P13-LXX'"],
            "bad-manifest-lane-key",
        )
        case_count += 1

    print("PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST=pass")
    print(f"PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 13 Landlock syscalls packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET=fail")
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_ERRORS_START")
        for error in errors:
            print(error)
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_ERRORS_END")
        return 1

    print("PHASE13_LANDLOCK_SYSCALLS_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())