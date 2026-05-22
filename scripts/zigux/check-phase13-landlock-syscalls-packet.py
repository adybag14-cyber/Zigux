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
        "provides_ruleset_fd_install_planning",
        "provides_ruleset_fd_stub_planning",
        "provides_ruleset_release_planning",
        "ruleset_fops_present",
        "planInstallRulesetFd",
        "planRulesetFdStub",
        "planFopRulesetRelease",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-slice.md": [
        "`scripts/zigux/check-phase13-landlock-syscalls-packet.py`",
        "helper-local packet companions",
        "repo-reality gaps",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-governance.md": [
        "`scripts/zigux/check-phase13-landlock-syscalls-packet.py`",
        "helper-local packet companions through:",
        "shared-build companions still absent",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-survey-gap.md": [
        "`scripts/zigux/check-phase13-landlock-syscalls-packet.py`",
        "repo-reality gaps",
        "Leave this lane parked",
    ],
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase13-landlock-syscalls-slice.md": [
        "materialized on current `master`, while `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps",
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
            path.write_text(text.replace(marker, "", 1), encoding="utf-8")
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