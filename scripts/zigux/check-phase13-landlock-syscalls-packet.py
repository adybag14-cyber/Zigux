#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_MARKERS = {
    "security/landlock/syscalls.zig": [
        "provides_abi_errata_query_planning",
        "provides_ruleset_fd_lookup_planning",
        "provides_ruleset_fd_install_planning",
        "provides_ruleset_fd_stub_planning",
        "provides_ruleset_release_planning",
        "LANDLOCK_CREATE_RULESET_ERRATA",
        "LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON",
        "LANDLOCK_RESTRICT_SELF_TSYNC",
        "planLandlockCreateRuleset",
        "planGetRulesetFromFd",
        "planLandlockRestrictSelf",
        "planLandlockAddRule",
        "planInstallRulesetFd",
        "planRulesetFdStub",
        "planFopRulesetRelease",
        "ruleset_fops_present",
        "required_ruleset_fd_mode_bits",
        "FMODE_CAN_READ",
        "FMODE_CAN_WRITE",
    ],
    "zigux/tests/phase13_landlock_syscalls.zig": [
        "phase13 landlock syscalls create-handle path reuses the fd install planner",
        "phase13 landlock syscalls restrict-self planner keeps logging and tsync flags explicit",
        "phase13 landlock syscalls add-rule planner reuses fd lookup and delegated tree helpers",
        "phase13 landlock syscalls stub and release helpers stay planning-only",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-slice.md": [
        "active materialized helper-local, direct replay, and reviewability packet companions",
        "`zigux/tests/phase13_landlock_syscalls.zig`",
        "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "historical breadcrumb for older lane notes and review references, not as active packet evidence",
        "`zigux/tests/phase13_landlock_syscalls_manifest.json` and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-governance.md": [
        "helper-local packet plus the direct replay and direct reviewability companions",
        "`zigux/tests/phase13_landlock_syscalls.zig`",
        "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-survey.md": [
        "Current `master` now materializes this helper-local, direct replay, and reviewability packet through:",
        "`zigux/tests/phase13_landlock_syscalls.zig`",
        "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "historical breadcrumb for older lane notes and review references, not as active packet evidence",
        "Current `master` still leaves these directly coupled companions absent:",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-survey-gap.md": [
        "`zigux/tests/phase13_landlock_syscalls.zig` as a returned direct replay companion",
        "`zigux/tests/phase13_landlock_syscalls_reviewability.zig` as a returned reviewability companion",
        "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    ],
    "Documentation/zigux/phase13-roadmap-traceability.md": [
        "current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions",
        "`zigux/tests/phase13_landlock_syscalls.zig`",
        "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    ],
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig": [
        "phase13 landlock syscalls direct replay covers the current planner packet",
        "active materialized helper-local, direct replay, and reviewability packet companions",
        "historical breadcrumb for older lane notes and review references, not as active packet evidence",
        "Current `master` now materializes this helper-local, direct replay, and reviewability packet through:",
        "current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions",
    ],
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase13-landlock-syscalls-slice.md": [
        "`zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-governance.md": [
        "`zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and `zigux/tests/phase13_build.zig`",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-survey.md": [
        "Current `master` still leaves these directly coupled companions absent:\n- `zigux/tests/phase13_landlock_syscalls.zig`",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-survey-gap.md": [
        "The remaining directly coupled gaps stay outside this bounded helper-local step:\n- `zigux/tests/phase13_landlock_syscalls.zig`",
    ],
    "Documentation/zigux/phase13-roadmap-traceability.md": [
        "## Repo-Reality Gaps\n\nKeep the remaining current gaps explicit:\n- docs-root `Documentation/zigux/README.md` still lacks a dedicated Phase 13 reminder block\n- `make -C zigux phase13-validate`\n- `make -C zigux phase13`\n- `zigux/tests/phase13_build.zig`\n- `zigux/tests/phase13_devres.zig`\n- `zigux/tests/phase13_devres_reviewability.zig`\n- `zigux/tests/phase13_devres_boundary_evidence.zig`\n- `zigux/tests/phase13_devres_manifest.json`\n- `scripts/zigux/check-phase13-devres-packet.py`\n- `scripts/zigux/check-phase13-devres-packet-alignment.py`\n- `zigux/tests/phase13_landlock_syscalls.zig`",
    ],
}

REQUIRED_FILES = sorted(set(REQUIRED_MARKERS) | set(FORBIDDEN_MARKERS))


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for relpath in REQUIRED_FILES:
        path = root / relpath
        if not path.exists():
            failures.append(f"missing_file:{relpath}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in REQUIRED_MARKERS.get(relpath, []):
            if marker not in text:
                failures.append(f"missing_marker:{relpath}:{marker}")
        for marker in FORBIDDEN_MARKERS.get(relpath, []):
            if marker in text:
                failures.append(f"forbidden_marker:{relpath}:{marker}")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_text(relpath: str) -> str:
    markers = REQUIRED_MARKERS.get(relpath, [])
    title = relpath.split("/")[-1]
    body = "\n".join(markers) if markers else "fixture"
    return f"# {title}\n\n{body}\n"


def populate_fixture(root: Path) -> None:
    for relpath in REQUIRED_FILES:
        write_text(root / relpath, fixture_text(relpath))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected} actual={failures!r}")


def remove_marker_once(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise SystemExit(f"marker not found in fixture text: {marker}")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-landlock-syscalls-packet-"))
    try:
        populate_fixture(tempdir)
        failures = validate(tempdir)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for relpath in REQUIRED_FILES:
            populate_fixture(tempdir)
            (tempdir / relpath).unlink()
            expect_failure(tempdir, f"missing_file:{relpath}")

        marker_cases = [
            (relpath, marker)
            for relpath, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for relpath, marker in marker_cases:
            populate_fixture(tempdir)
            path = tempdir / relpath
            text = path.read_text(encoding="utf-8")
            path.write_text(remove_marker_once(text, marker), encoding="utf-8")
            expect_failure(tempdir, f"missing_marker:{relpath}:{marker}")

        forbidden_cases = [
            (relpath, marker)
            for relpath, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for relpath, marker in forbidden_cases:
            populate_fixture(tempdir)
            path = tempdir / relpath
            text = path.read_text(encoding="utf-8")
            path.write_text(text + marker + "\n", encoding="utf-8")
            expect_failure(tempdir, f"forbidden_marker:{relpath}:{marker}")

        total_cases = len(REQUIRED_FILES) + len(marker_cases) + len(forbidden_cases)
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST=pass")
        print(f"PHASE13_LANDLOCK_SYSCALLS_PACKET_SELF_TEST_CASE_COUNT={total_cases}")
        return 0
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current materialized Phase 13 Landlock syscalls helper packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in fixture self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET=fail")
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE13_LANDLOCK_SYSCALLS_PACKET_FAILURES_END")
        return 1

    print("PHASE13_LANDLOCK_SYSCALLS_PACKET=pass")
    print(f"PHASE13_LANDLOCK_SYSCALLS_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE13_LANDLOCK_SYSCALLS_PACKET_MARKER_COUNT=" f"{sum(len(v) for v in REQUIRED_MARKERS.values())}")
    print("PHASE13_LANDLOCK_SYSCALLS_PACKET_FORBIDDEN_COUNT=" f"{sum(len(v) for v in FORBIDDEN_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
