#!/usr/bin/env python3
"""Guard the shipped Phase 13 contributor workflow guide."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


GUIDE_PATH = Path("Documentation/zigux/phase13-contributor-workflow-guide.md")

REQUIRED_MARKERS = (
    "Use this guide when a change touches the active Phase 13 shared-helper packet and the review needs one contributor-facing workflow note instead of reconstructing the packet from scattered reminder surfaces.",
    "Keep the contributor-facing shared handle aligned through:",
    "1. `Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "2. `scripts/zigux/README.md`",
    "3. `zigux/tests/README.md`",
    "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`",
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the file itself distinct from those missing Phase 13 route names and keep only the route names recorded as repo-reality gaps until the shared build handle returns.",
    "Keep `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "Keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "Keep notifier evidence explicit as adjacent release-surface support through:",
    "- `Documentation/zigux/phase13-notifier-list-survey.md`",
    "- `scripts/zigux/check-phase13-notifier-packet.py`",
    "- `zigux/tests/phase13_notifier_list_manifest.json`",
    "- `zigux/tests/phase13_notifier_list_reviewability.zig`",
    "- `zigux/bindings/notifier_abi.zig`",
    "- `zigux/helpers/list_view.zig`",
    "- `zigux/helpers/hlist_view.zig`",
    "- `include/zigux/abi.h`",
    "- `drivers/tty/hvc/hvc_console.h`",
    "Keep `zigux/helpers/notifier_chain_view.zig`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, and `include/zigux/notifier_abi.h` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "- adjacent notifier evidence stays adjacent rather than becoming a fifth helper family",
    "- promote adjacent notifier evidence into a fifth helper family",
)

FORBIDDEN_MARKERS = (
    "Keep `make -C zigux phase13-validate` explicit as the stable contributor-facing handle until the shared build companion lands.",
    "`landlock/syscalls` owns the syscall governance, slice, survey, and focused helper-local replay packet through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "Adjacent notifier evidence has become a fifth helper family.",
)


def read_text(root: Path) -> str:
    path = root / GUIDE_PATH
    if not path.exists():
        raise SystemExit(f"required file missing: {GUIDE_PATH.as_posix()}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: Path, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    text = read_text(root)
    issues: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(f"missing_marker:{marker}")

    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            issues.append(f"forbidden_marker:{marker}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE=fail")
    print("PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    write_text(root, GUIDE_PATH, "\n".join(REQUIRED_MARKERS) + "\n")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-contributor-workflow-guide-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        guide_path = tempdir / GUIDE_PATH
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8").replace(
                "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        guide_path.write_text(
            guide_path.read_text(encoding="utf-8").replace(
                "Keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`."
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        guide_path.write_text(
            guide_path.read_text(encoding="utf-8").replace(
                "- `zigux/tests/phase13_notifier_list_reviewability.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert "missing_marker:- `zigux/tests/phase13_notifier_list_reviewability.zig`" in issues
        populate_repo(tempdir)
        checks_run += 1

        guide_path.write_text(
            guide_path.read_text(encoding="utf-8")
            + "Keep `make -C zigux phase13-validate` explicit as the stable contributor-facing handle until the shared build companion lands.\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Keep `make -C zigux phase13-validate` explicit as the stable contributor-facing handle until the shared build companion lands."
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        guide_path.write_text(
            guide_path.read_text(encoding="utf-8")
            + "Adjacent notifier evidence has become a fifth helper family.\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Adjacent notifier evidence has become a fifth helper family."
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        guide_path.unlink()
        try:
            collect_issues(tempdir)
        except SystemExit as exc:
            assert str(exc) == f"required file missing: {GUIDE_PATH.as_posix()}"
            checks_run += 1
        else:
            raise AssertionError("missing guide did not abort")
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_SELF_TEST=pass")
    print(f"PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shipped Phase 13 contributor workflow guide aligned."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE=pass")
    print(f"PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
