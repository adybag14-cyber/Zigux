#!/usr/bin/env python3
"""Fail closed on the landed Phase 13 Landlock syscalls packet surface."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = "scripts/zigux/check-phase13-landlock-syscalls-packet.py"
GOVERNANCE_PATH = "Documentation/zigux/phase13-landlock-syscalls-governance.md"
SLICE_PATH = "Documentation/zigux/phase13-landlock-syscalls-slice.md"
SURVEY_PATH = "Documentation/zigux/phase13-landlock-syscalls-survey.md"
MANIFEST_PATH = "zigux/tests/phase13_landlock_syscalls_manifest.json"
TEST_PATH = "zigux/tests/phase13_landlock_syscalls.zig"
REVIEWABILITY_PATH = "zigux/tests/phase13_landlock_syscalls_reviewability.zig"
SOURCE_PATH = "security/landlock/syscalls.zig"

REQUIRED_FILES = (
    SCRIPT_PATH,
    GOVERNANCE_PATH,
    SLICE_PATH,
    SURVEY_PATH,
    MANIFEST_PATH,
    TEST_PATH,
    REVIEWABILITY_PATH,
    SOURCE_PATH,
)

REQUIRED_GOVERNANCE_MARKERS = (
    "# Phase 13 Landlock Syscalls Governance",
    "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter.",
    "the release-side `fop_ruleset_release()` ownership drop",
    "the combined `ruleset_fops` wrapper contract",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "live file-descriptor installation",
)

REQUIRED_SLICE_MARKERS = (
    "# Phase 13 Landlock Syscalls Slice",
    "`security/landlock/syscalls.c`",
    "`landlock_create_ruleset()`",
    "`landlock_restrict_self()`",
    "`landlock_add_rule()`",
    "`fop_ruleset_release()`",
    "`ruleset_fops`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_build.zig`",
)

REQUIRED_SURVEY_MARKERS = (
    "# Phase 13 Landlock Syscalls Survey",
    "master-readback-2026-05-13",
    "`security/landlock/syscalls.zig`",
    "`Documentation/zigux/phase13-landlock-syscalls-slice.md`",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "shared `phase13_build.zig` route still remains absent",
    "planFopRulesetRelease()",
    "planRulesetFops()",
)

REQUIRED_MANIFEST_MARKERS = (
    '"lane_key": "P13-L17"',
    '"anchor": "security/landlock/syscalls.c"',
    '"id": "phase13-landlock-syscalls-helper-starter"',
    '"id": "phase13-landlock-syscalls-direct-test-gate"',
    '"id": "phase13-landlock-syscalls-reviewability-gate"',
    '"status": "starter_landed"',
    '"status": "blocked_on_live_fd_installation"',
    '"status": "blocked_on_live_credential_state"',
    '"status": "blocked_on_live_ruleset_state"',
    "ruleset_fops",
)

REQUIRED_TEST_MARKERS = (
    'try std.testing.expect(descriptor.provides_ruleset_release_planning);',
    'try std.testing.expect(descriptor.provides_ruleset_fops_planning);',
    'const plan = try syscalls.SyscallsHelperLab.planRulesetFops(.{});',
    'try std.testing.expect(plan.release.invokes_landlock_put_ruleset);',
    'try expectContains(manifest_text, "\\\"id\\\": \\\"phase13-landlock-syscalls-reviewability-gate\\\"");',
    'try expectContains(manifest_text, "ruleset_fops");',
)

REQUIRED_REVIEWABILITY_MARKERS = (
    'try std.testing.expectEqualStrings("P13-L17", manifest.lane_key);',
    'try std.testing.expect(std.mem.indexOf(u8, syscalls_source, "pub fn planFopRulesetRelease(") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, syscalls_source, "pub fn planRulesetFops(") != null);',
    'try expectGap(',
    '"phase13-landlock-live-fd-installation"',
    '"phase13-landlock-live-ruleset-state"',
)

REQUIRED_SOURCE_MARKERS = (
    '.provides_ruleset_release_planning = true,',
    '.provides_ruleset_fops_planning = true,',
    "pub fn planFopRulesetRelease(request: RulesetReleaseRequest) !RulesetReleasePlan {",
    "pub fn planRulesetFops(request: RulesetReleaseRequest) !RulesetFopsPlan {",
    ".invokes_landlock_put_ruleset = true,",
    ".read_returns_einval = true,",
    ".write_returns_einval = true,",
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> list[str]:
    return [f"missing-marker:{label}:{marker}" for marker in markers if marker not in text]


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            issues.append(f"missing-file:{rel_path}")
    if issues:
        return issues

    checks = (
        ("governance", GOVERNANCE_PATH, REQUIRED_GOVERNANCE_MARKERS),
        ("slice", SLICE_PATH, REQUIRED_SLICE_MARKERS),
        ("survey", SURVEY_PATH, REQUIRED_SURVEY_MARKERS),
        ("manifest", MANIFEST_PATH, REQUIRED_MANIFEST_MARKERS),
        ("test", TEST_PATH, REQUIRED_TEST_MARKERS),
        ("reviewability", REVIEWABILITY_PATH, REQUIRED_REVIEWABILITY_MARKERS),
        ("source", SOURCE_PATH, REQUIRED_SOURCE_MARKERS),
    )
    for label, rel_path, markers in checks:
        issues.extend(require_markers(label, read_text(root, rel_path), markers))
    return issues


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    write_text(root, GOVERNANCE_PATH, "\n".join(REQUIRED_GOVERNANCE_MARKERS) + "\n")
    write_text(root, SLICE_PATH, "\n".join(REQUIRED_SLICE_MARKERS) + "\n")
    write_text(root, SURVEY_PATH, "\n".join(REQUIRED_SURVEY_MARKERS) + "\n")
    write_text(root, MANIFEST_PATH, "\n".join(REQUIRED_MANIFEST_MARKERS) + "\n")
    write_text(root, TEST_PATH, "\n".join(REQUIRED_TEST_MARKERS) + "\n")
    write_text(root, REVIEWABILITY_PATH, "\n".join(REQUIRED_REVIEWABILITY_MARKERS) + "\n")
    write_text(root, SOURCE_PATH, "\n".join(REQUIRED_SOURCE_MARKERS) + "\n")


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_landlock_syscalls_packet_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            ("governance", GOVERNANCE_PATH, REQUIRED_GOVERNANCE_MARKERS[2]),
            ("slice", SLICE_PATH, REQUIRED_SLICE_MARKERS[7]),
            ("survey", SURVEY_PATH, REQUIRED_SURVEY_MARKERS[8]),
            ("manifest", MANIFEST_PATH, REQUIRED_MANIFEST_MARKERS[6]),
            ("test", TEST_PATH, REQUIRED_TEST_MARKERS[2]),
            ("reviewability", REVIEWABILITY_PATH, REQUIRED_REVIEWABILITY_MARKERS[1]),
            ("source", SOURCE_PATH, REQUIRED_SOURCE_MARKERS[2]),
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
