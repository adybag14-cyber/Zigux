#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


SURVEYED_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_FILES = [
    "security/landlock/syscalls.zig",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_build.zig",
    "zigux/Makefile",
    "Documentation/zigux/phase13-landlock-syscalls-slice.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
]

SYSCALLS_MARKERS = [
    "pub const ruleset_fd_flags: u32 = open_rdwr | open_cloexec;",
    ".provides_ruleset_fops_planning = true,",
    ".provides_path_beneath_handoff_planning = true,",
    ".provides_net_port_handoff_planning = true,",
    "pub fn planGetRulesetFromFd",
    "pub fn planCreateRulesetFd",
    "pub fn planRulesetFops",
    "pub fn planGetPathFromFd",
    "pub fn planAddRulePathBeneath",
    "pub fn planAddRuleNetPort",
]

TEST_MARKERS = [
    'test "phase13 landlock syscalls reviewability ties helper, survey, manifest, and build wiring together"',
    'test "phase13 landlock syscalls ruleset fd creation plan captures file-operations contract"',
    'test "phase13 landlock ruleset fops planner keeps release and dummy handler contracts explicit"',
    'try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_reviewability_present);',
    'try std.testing.expectEqual(@as(usize, 16), manifest.gaps.len);',
]

REVIEWABILITY_MARKERS = [
    'try std.testing.expectEqualStrings("P13-L16", manifest.lane_key);',
    'try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);',
    "try std.testing.expect(descriptor.provides_ruleset_fops_planning);",
    'try expectContains(build_file, "phase13-landlock-syscalls-reviewability-tests");',
    "try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_reviewability_present);",
]

SURVEY_MARKERS = [
    "PHASE13_SLICE=landlock-syscalls-helper-pure-handoff-boundary",
    "dedicated reviewability gate now ties the helper surface, manifest, survey note, and shared Phase 13 build wiring together",
    "landed `phase13-landlock-syscalls-reviewability-gate`",
    "manifest-backed reviewability gate",
    "ruleset-FD creation handoff",
    "ruleset file-operations contract",
]

SLICE_MARKERS = [
    "adds one in-memory ruleset-FD creation handoff planner",
    "makes the dedicated `ruleset_fops` contract explicit",
    "The next honest bounded step in this same lane is to stay parked at the current syscall-helper boundary",
]

BUILD_MARKERS = [
    "phase13_landlock_syscalls.zig",
    "phase13-landlock-syscalls-tests",
    "phase13_landlock_syscalls_reviewability.zig",
    "phase13-landlock-syscalls-reviewability-tests",
]

MAKE_MARKERS = [
    "phase13-validate:",
    "scripts/zigux/check-phase13-landlock-syscalls-packet.py --self-test",
    "scripts/zigux/check-phase13-landlock-syscalls-packet.py",
    "scripts/zigux/validate-phase13-release.py",
]

EXPECTED_LANDED = {
    "phase13-build-gate",
    "phase13-make-target",
    "phase13-landlock-syscalls-starter",
    "phase13-landlock-syscalls-test-gate",
    "phase13-landlock-syscalls-reviewability-gate",
    "phase13-landlock-syscalls-slice-note",
    "phase13-landlock-syscalls-survey-note",
    "phase13-landlock-initialization-gate-followup",
    "phase13-landlock-copy-min-struct-followup",
    "phase13-landlock-add-rule-followup",
    "phase13-landlock-ruleset-fd-mode-followup",
    "phase13-landlock-path-fd-followup",
    "phase13-landlock-path-beneath-handoff-followup",
    "phase13-landlock-net-port-import-followup",
    "phase13-landlock-ruleset-fd-creation-handoff-followup",
    "phase13-landlock-restrict-self-credential-handoff-followup",
    "phase13-landlock-ruleset-fops-followup",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def _check_repo(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(f"missing_file:{rel}")
    if missing:
        return missing

    syscalls_text = _read(root / "security/landlock/syscalls.zig")
    tests_text = _read(root / "zigux/tests/phase13_landlock_syscalls.zig")
    reviewability_text = _read(root / "zigux/tests/phase13_landlock_syscalls_reviewability.zig")
    survey_text = _read(root / "Documentation/zigux/phase13-landlock-syscalls-survey.md")
    slice_text = _read(root / "Documentation/zigux/phase13-landlock-syscalls-slice.md")
    build_text = _read(root / "zigux/tests/phase13_build.zig")
    make_text = _read(root / "zigux/Makefile")

    _require_markers(missing, "syscalls", syscalls_text, SYSCALLS_MARKERS)
    _require_markers(missing, "tests", tests_text, TEST_MARKERS)
    _require_markers(missing, "reviewability", reviewability_text, REVIEWABILITY_MARKERS)
    _require_markers(missing, "survey", survey_text, SURVEY_MARKERS)
    _require_markers(missing, "slice", slice_text, SLICE_MARKERS)
    _require_markers(missing, "build", build_text, BUILD_MARKERS)
    _require_markers(missing, "make", make_text, MAKE_MARKERS)

    manifest = json.loads(_read(root / "zigux/tests/phase13_landlock_syscalls_manifest.json"))
    if manifest.get("lane_key") != "P13-L16":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 13":
        missing.append("manifest:phase")
    if manifest.get("anchor") != "security/landlock/syscalls.c":
        missing.append("manifest:anchor")
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not SURVEYED_COMMIT_RE.fullmatch(surveyed_commit):
        missing.append("manifest:surveyed_commit")
    else:
        if f"PHASE13_SURVEYED_COMMIT={surveyed_commit}" not in survey_text:
            missing.append("survey:surveyed_commit")
        if surveyed_commit not in tests_text:
            missing.append("tests:surveyed_commit")
        if surveyed_commit not in reviewability_text:
            missing.append("reviewability:surveyed_commit")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        missing.append("manifest:survey_summary")
    else:
        for flag in (
            "preexisting_phase13_build_present",
            "preexisting_phase13_make_target_present",
            "preexisting_syscalls_zig_present",
            "preexisting_phase13_landlock_syscalls_test_present",
            "preexisting_phase13_landlock_syscalls_reviewability_present",
            "preexisting_phase13_landlock_syscalls_slice_note_present",
            "preexisting_phase13_landlock_syscalls_survey_note_present",
        ):
            if summary.get(flag) is not True:
                missing.append(f"manifest:survey_summary:{flag}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append("manifest:gaps")
        return missing

    landed_ids = {
        gap.get("id")
        for gap in gaps
        if isinstance(gap, dict) and gap.get("status") == "starter_landed"
    }
    if landed_ids != EXPECTED_LANDED:
        missing.append("manifest:starter_landed_set")

    return missing


def _run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel in (
            "security/landlock",
            "zigux/tests",
            "zigux",
            "Documentation/zigux",
        ):
            (root / rel).mkdir(parents=True, exist_ok=True)

        surveyed_commit = "9c17b0790799d8240ef9f964903f5ce2db64af89"
        (root / "security/landlock/syscalls.zig").write_text("\n".join(SYSCALLS_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_landlock_syscalls.zig").writeText = None
        (root / "zigux/tests/phase13_landlock_syscalls.zig").write_text(
            f'const expected_surveyed_commit = "{surveyed_commit}"\n' + "\n".join(TEST_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "zigux/tests/phase13_landlock_syscalls_reviewability.zig").write_text(
            f'const expected_surveyed_commit = "{surveyed_commit}"\n' + "\n".join(REVIEWABILITY_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "Documentation/zigux/phase13-landlock-syscalls-survey.md").write_text(
            f"PHASE13_SURVEYED_COMMIT={surveyed_commit}\n" + "\n".join(SURVEY_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "Documentation/zigux/phase13-landlock-syscalls-slice.md").write_text(
            "\n".join(SLICE_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "zigux/tests/phase13_build.zig").write_text("\n".join(BUILD_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/Makefile").write_text("\n".join(MAKE_MARKERS) + "\n", encoding="utf-8")
        manifest = {
            "lane_key": "P13-L16",
            "phase": "Phase 13",
            "surveyed_commit": surveyed_commit,
            "anchor": "security/landlock/syscalls.c",
            "survey_summary": {
                "preexisting_phase13_build_present": True,
                "preexisting_phase13_make_target_present": True,
                "preexisting_syscalls_zig_present": True,
                "preexisting_phase13_landlock_syscalls_test_present": True,
                "preexisting_phase13_landlock_syscalls_reviewability_present": True,
                "preexisting_phase13_landlock_syscalls_slice_note_present": True,
                "preexisting_phase13_landlock_syscalls_survey_note_present": True,
            },
            "gaps": [{"id": item, "status": "starter_landed"} for item in sorted(EXPECTED_LANDED)],
        }
        (root / "zigux/tests/phase13_landlock_syscalls_manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        missing = _check_repo(root)
        if missing:
            print("PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST=fail")
            for item in missing:
                print(item)
            return 1

    print("PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    if args.self_test:
        return _run_self_test()

    missing = _check_repo(Path(args.root).resolve())
    if missing:
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET=fail")
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_MISSING_END")
        return 1

    print("PHASE13_LANDLOCK_SYSCALLS_PACKET=pass")
    print(f"PHASE13_LANDLOCK_SYSCALLS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE13_LANDLOCK_SYSCALLS_MARKER_COUNT="
        f"{len(SYSCALLS_MARKERS) + len(TEST_MARKERS) + len(REVIEWABILITY_MARKERS) + len(SURVEY_MARKERS) + len(SLICE_MARKERS) + len(BUILD_MARKERS) + len(MAKE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
