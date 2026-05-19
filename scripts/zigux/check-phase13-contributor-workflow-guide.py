#!/usr/bin/env python3
"""Guard the Phase 13 contributor workflow guide."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

GUIDE = Path("Documentation/zigux/phase13-contributor-workflow-guide.md")

REQUIRED_MARKERS = (
    "Use this guide when a change touches the active Phase 13 shared-helper packet and the review needs one contributor-facing workflow note instead of reconstructing the packet from scattered reminder surfaces.",
    "Keep broad contributor wording aligned with the active Phase 13 helper packet centered on four roadmap-owned Linux anchors:",
    "- `fs/libfs.c`",
    "- `lib/devres.c`",
    "- `security/landlock/ruleset.c`",
    "- `security/landlock/syscalls.c`",
    "Keep the contributor-facing shared handle aligned through:",
    "1. `Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "2. `scripts/zigux/README.md`",
    "3. `zigux/tests/README.md`",
    "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`",
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the file itself distinct from those missing Phase 13 route names and keep only the route names recorded as repo-reality gaps until the shared build handle returns.",
    "When shared Phase 13 wording changes, reread these contributor-facing and support surfaces together:",
    "- `Documentation/zigux/phase13-release-coordination-matrix.md`",
    "- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "- `Documentation/zigux/phase13-release-notes-survey.md`",
    "- `Documentation/zigux/phase13-roadmap-traceability.md`",
    "- `Documentation/zigux/phase13-shared-summary-guard-gap.md`",
    "- `Documentation/zigux/phase13-notifier-summary-gap.md`",
    "- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`",
    "- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "- `scripts/zigux/check-phase13-tests-readme-alignment.py`",
    "Keep helper-local ownership explicit instead of flattening the packet into a single generic Phase 13 summary.",
    "### `libfs`",
    "- `Documentation/zigux/phase13-libfs-survey.md`",
    "- `fs/libfs.zig`",
    "- `zigux/tests/phase13_libfs.zig`",
    "- `zigux/tests/phase13_libfs_reviewability.zig`",
    "- `zigux/tests/phase13_libfs_manifest.json`",
    "### `devres`",
    "- `Documentation/zigux/phase13-devres-slice.md`",
    "- `Documentation/zigux/phase13-devres-survey.md`",
    "- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`",
    "- `Documentation/zigux/phase13-devres-scatterlist-slice.md`",
    "- `scripts/zigux/check-phase13-devres-dma-boundary.py`",
    "- `scripts/zigux/check-phase13-devres-mmio-packet.py`",
    "- `zigux/tests/phase13_devres_dma_coherent.zig`",
    "- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`",
    "- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`",
    "- `lib/devres.zig`",
    "- `lib/devres_scatterlist.zig`",
    "- `zigux/tests/phase13_devres_scatterlist.zig`",
    "- `zigux/tests/phase13_devres_scatterlist_build.zig`",
    "### `landlock/ruleset`",
    "- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "- `Documentation/zigux/phase13-landlock-ruleset-slice.md`",
    "- `Documentation/zigux/phase13-landlock-ruleset-survey.md`",
    "- `security/landlock/ruleset.zig`",
    "- `zigux/tests/phase13_landlock_ruleset.zig`",
    "- `zigux/tests/phase13_landlock_ruleset_manifest.json`",
    "### `landlock/syscalls`",
    "- `Documentation/zigux/phase13-landlock-syscalls-governance.md`",
    "- `Documentation/zigux/phase13-landlock-syscalls-slice.md`",
    "- `security/landlock/syscalls.zig`",
    "Keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "Keep notifier evidence explicit as adjacent release-surface support through:",
    "- `Documentation/zigux/phase13-notifier-list-survey.md`",
    "- `zigux/bindings/notifier_abi.zig`",
    "- `zigux/helpers/list_view.zig`",
    "- `zigux/helpers/hlist_view.zig`",
    "- `include/zigux/abi.h`",
    "- `drivers/tty/hvc/hvc_console.h`",
    "Keep `zigux/helpers/notifier_chain_view.zig`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, and `include/zigux/notifier_abi.h` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "Before landing a broad Phase 13 reminder change, check that:",
    "- the contributor-facing handle still runs through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
    "- the stable shared-summary guard remains `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "- the shipped tests-root alignment companion remains `python3 scripts/zigux/check-phase13-tests-readme-alignment.py` so the broader contributor wording and the tests-root reminder stay on the same Phase 13 packet",
    "- helper-local owner maps for `libfs`, `devres`, and `landlock` remain explicit",
    "- adjacent notifier evidence stays adjacent rather than becoming a fifth helper family",
    "- `zigux/helpers/notifier_chain_view.zig` stays recorded as a repo-reality gap, while `zigux/Makefile` stays distinguished from the still-missing `make -C zigux phase13-validate` and `make -C zigux phase13` route names instead of promoting that partial build surface into shipped current-`master` Phase 13 evidence",
    "This guide does not:",
    "- close the Phase 13 tranche",
    "- add a new replay route",
    "- widen Phase 13 into runtime HVC parity or broader security-policy ownership",
    "- promote adjacent notifier evidence into a fifth helper family",
)

FORBIDDEN_MARKERS = (
    "stable shared-summary guard: `python3 scripts/zigux/check-phase13-contributor-workflow-guide.py`",
    "tests-root alignment companion: `python3 scripts/zigux/check-phase13-contributor-workflow-guide.py`",
    "Keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "Keep notifier evidence explicit as a fifth helper family through:",
    "Keep `zigux/helpers/notifier_chain_view.zig` explicit as shipped adjacent evidence on current `master`.",
    "`zigux/Makefile` is present on current `master`, and it now exposes `make -C zigux phase13-validate` and `make -C zigux phase13`",
)


def read_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath.as_posix()}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: Path, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    text = read_text(root, GUIDE)
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


def build_self_test_text() -> str:
    return "\n".join(REQUIRED_MARKERS) + "\n"


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 6

    with tempfile.TemporaryDirectory(prefix="phase13-contributor-workflow-guide-") as tmp_dir:
        root = Path(tmp_dir)
        write_text(root, GUIDE, build_self_test_text())
        assert collect_issues(root) == []
        checks_run += 1

        guide_path = root / GUIDE
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8").replace(
                "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "missing_marker:stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`"
            in issues
        )
        checks_run += 1

        write_text(root, GUIDE, build_self_test_text())
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8").replace(
                "- `zigux/helpers/hlist_view.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert "missing_marker:- `zigux/helpers/hlist_view.zig`" in issues
        checks_run += 1

        write_text(root, GUIDE, build_self_test_text())
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8")
            + "stable shared-summary guard: `python3 scripts/zigux/check-phase13-contributor-workflow-guide.py`\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "forbidden_marker:stable shared-summary guard: `python3 scripts/zigux/check-phase13-contributor-workflow-guide.py`"
            in issues
        )
        checks_run += 1

        write_text(root, GUIDE, build_self_test_text())
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8").replace(
                "- adjacent notifier evidence stays adjacent rather than becoming a fifth helper family\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "missing_marker:- adjacent notifier evidence stays adjacent rather than becoming a fifth helper family"
            in issues
        )
        checks_run += 1

        write_text(root, GUIDE, build_self_test_text())
        guide_path.write_text(
            guide_path.read_text(encoding="utf-8")
            + "`zigux/Makefile` is present on current `master`, and it now exposes `make -C zigux phase13-validate` and `make -C zigux phase13`\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "forbidden_marker:`zigux/Makefile` is present on current `master`, and it now exposes `make -C zigux phase13-validate` and `make -C zigux phase13`"
            in issues
        )
        checks_run += 1

    print("PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_SELF_TEST=pass")
    print(f"PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_SELF_TEST_CASE_COUNT={checks_run}")
    if checks_run != expected_case_count:
        raise AssertionError(
            f"expected {expected_case_count} self-test cases, ran {checks_run}"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 13 contributor workflow guide."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run checker self-tests",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE=pass")
    print(f"PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
