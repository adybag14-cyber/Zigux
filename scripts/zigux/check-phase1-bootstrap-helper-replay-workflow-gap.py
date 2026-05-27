#!/usr/bin/env python3
"""Guard the documented Phase 1 bootstrap helper-replay workflow gap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

GAP_NOTE_REL = Path("Documentation/zigux/phase1-bootstrap-helper-replay-workflow-gap.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
HELPER_BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")

FOCUSED_REPLAY_CMD = "zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig"
SHARED_SMOKE_CMD = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"
HELPER_STEP_NAME = '.name = "phase1-helpers"'
HELPER_STEP_LABEL = '"phase1-helpers"'

REQUIRED_NOTE_MARKERS = (
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zigux/tests/phase1_helpers_build.zig`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/README.md`",
    f"`{FOCUSED_REPLAY_CMD}`",
    f"`{SHARED_SMOKE_CMD}`",
    "focused `phase1-helpers` step",
    "still does not run",
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(resolve(root, GAP_NOTE_REL))
    workflow_text = read_text(resolve(root, WORKFLOW_REL))
    helper_build_text = read_text(resolve(root, HELPER_BUILD_REL))
    tests_readme_text = read_text(resolve(root, TESTS_README_REL))
    scripts_readme_text = read_text(resolve(root, SCRIPTS_README_REL))

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKER", marker))

    if SHARED_SMOKE_CMD not in workflow_text:
        issues.append(("MISSING_SHARED_SMOKE_ROUTE", SHARED_SMOKE_CMD))

    if FOCUSED_REPLAY_CMD in workflow_text:
        issues.append(("WORKFLOW_NO_LONGER_GAPS_FOCUSED_REPLAY", FOCUSED_REPLAY_CMD))

    if HELPER_STEP_NAME not in helper_build_text or HELPER_STEP_LABEL not in helper_build_text:
        issues.append(("MISSING_HELPER_BUILD_ROUTE_MARKER", "phase1-helpers"))

    if FOCUSED_REPLAY_CMD not in tests_readme_text:
        issues.append(("TESTS_README_MISSING_FOCUSED_ROUTE", FOCUSED_REPLAY_CMD))

    if FOCUSED_REPLAY_CMD not in scripts_readme_text:
        issues.append(("SCRIPTS_README_MISSING_FOCUSED_ROUTE", FOCUSED_REPLAY_CMD))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE1_BOOTSTRAP_HELPER_REPLAY_WORKFLOW_GAP=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    note = f"""# Phase 1 Bootstrap Helper-Replay Workflow Gap

This note records the current Lane 09 truthfulness gap between the focused
Phase 1 helper replay route already shipped in the tests root and the narrower
bootstrap workflow packet still checked in on current `master`.

## Current Live Packet

- authority packet:
  - `.github/workflows/zigux-bootstrap.yml`
  - `zigux/tests/phase1_helpers_build.zig`
  - `zigux/tests/README.md`
  - `scripts/zigux/README.md`
- focused helper replay route:
  - `{FOCUSED_REPLAY_CMD}`
- current shared bootstrap Phase 1 replay route:
  - `{SHARED_SMOKE_CMD}`

## Current Mismatch

- `zigux/tests/phase1_helpers_build.zig` directly exposes the focused
  `phase1-helpers` step as the focused `phase1-helpers` step
- `zigux/tests/README.md` already treats
  `{FOCUSED_REPLAY_CMD}`
  as current tests-root replay evidence
- `scripts/zigux/README.md` already treats the same focused helper replay as
  current scripts-root reminder evidence
- `.github/workflows/zigux-bootstrap.yml` still does not run
  `{FOCUSED_REPLAY_CMD}`
  on current `master`
"""
    workflow = f"""jobs:
  bootstrap:
    steps:
      - name: Run current Phase 1 shared tests-root smoke
        run: {SHARED_SMOKE_CMD}
"""
    helper_build = """const tests = b.addTest(.{
    .name = \"phase1-helpers\",
    .root_module = root_module,
});

const phase1_helpers = b.step(
    \"phase1-helpers\",
    \"Run the focused Phase 1 helper replay anchor from zigux/tests\",
);
"""
    tests_readme = f"- current focused Phase 1 helper replay route: `{FOCUSED_REPLAY_CMD}`\n"
    scripts_readme = f"- `{FOCUSED_REPLAY_CMD}` restores a focused fixture-backed helper replay anchor on current `master`\n"

    write_text(resolve(root, GAP_NOTE_REL), note)
    write_text(resolve(root, WORKFLOW_REL), workflow)
    write_text(resolve(root, HELPER_BUILD_REL), helper_build)
    write_text(resolve(root, TESTS_README_REL), tests_readme)
    write_text(resolve(root, SCRIPTS_README_REL), scripts_readme)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bootstrap_helper_gap_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve(root, WORKFLOW_REL)
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8") + f"      - name: Focused replay\\n        run: {FOCUSED_REPLAY_CMD}\\n",
            encoding="utf-8",
        )
        assert ("WORKFLOW_NO_LONGER_GAPS_FOCUSED_REPLAY", FOCUSED_REPLAY_CMD) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        tests_readme_path = resolve(root, TESTS_README_REL)
        tests_readme_path.write_text("- current focused Phase 1 helper replay route: `zig build something-else`\n", encoding="utf-8")
        assert ("TESTS_README_MISSING_FOCUSED_ROUTE", FOCUSED_REPLAY_CMD) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        helper_build_path = resolve(root, HELPER_BUILD_REL)
        helper_build_path.write_text(helper_build_path.read_text(encoding="utf-8").replace(HELPER_STEP_NAME, '.name = \"different-step\"'), encoding="utf-8")
        assert ("MISSING_HELPER_BUILD_ROUTE_MARKER", "phase1-helpers") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        note_path = resolve(root, GAP_NOTE_REL)
        note_path.write_text(note_path.read_text(encoding="utf-8").replace("still does not run", "now runs", 1), encoding="utf-8")
        assert ("MISSING_NOTE_MARKER", "still does not run") in collect_issues(root)
        checks_run += 1

    print("PHASE1_BOOTSTRAP_HELPER_REPLAY_WORKFLOW_GAP_SELF_TEST=pass")
    print(f"PHASE1_BOOTSTRAP_HELPER_REPLAY_WORKFLOW_GAP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(destination: Path) -> int:
    build_self_test_root(destination.resolve())
    print(
        "PHASE1_BOOTSTRAP_HELPER_REPLAY_WORKFLOW_GAP_SAMPLE_ROOT="
        + str(destination.resolve())
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the documented Phase 1 bootstrap helper-replay workflow gap."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample tree for focused validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE1_BOOTSTRAP_HELPER_REPLAY_WORKFLOW_GAP=pass")
    print(f"PHASE1_BOOTSTRAP_HELPER_REPLAY_WORKFLOW_GAP_SHARED_SMOKE_ROUTE={SHARED_SMOKE_CMD}")
    print(f"PHASE1_BOOTSTRAP_HELPER_REPLAY_WORKFLOW_GAP_FOCUSED_REPLAY_ROUTE={FOCUSED_REPLAY_CMD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
