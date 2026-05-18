#!/usr/bin/env python3
"""Fail-closed checker for the Phase 13 roadmap traceability note."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path


ROADMAP_TRACEABILITY = Path("Documentation/zigux/phase13-roadmap-traceability.md")
MAKEFILE = Path("zigux/Makefile")

REQUIRED_PRESENT_PATHS = (
    "Documentation/zigux/phase13-devres-slice.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "fs/libfs.zig",
    "lib/devres_scatterlist.zig",
    "scripts/zigux/check-phase13-devres-dma-boundary.py",
    "scripts/zigux/check-phase13-devres-mmio-packet.py",
    "security/landlock/syscalls.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/helpers/list_view.zig",
    "zigux/Makefile",
)

REQUIRED_ABSENT_PATHS = (
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "lib/devres.zig",
    "scripts/zigux/validate-phase13-release.py",
    "zigux/helpers/notifier_chain_view.zig",
    "zigux/tests/phase13_landlock_syscalls.zig",
)

REQUIRED_MARKERS = (
    "This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.",
    "- `fs/libfs.c`",
    "- `lib/devres.c`",
    "- `security/landlock/ruleset.c`",
    "- `security/landlock/syscalls.c`",
    "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep the returned `zigux/Makefile` file distinct from the still-missing `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` names instead of treating that Phase 2-only wrapper file as a materialized shared Phase 13 surface.",
    "`devres` stays mapped through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, the shipped DMA-boundary checker pair `scripts/zigux/check-phase13-devres-dma-boundary.py` and `scripts/zigux/check-phase13-devres-mmio-packet.py`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`",
    "Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, ruleset-fd install planning, and ruleset-fd stub discipline planning, and keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` framed as repo-reality gaps until current `master` materializes them again so the reminder packet does not overstate the live syscall helper surface.",
    "Keep `zigux/helpers/notifier_chain_view.zig` framed as a repo-reality gap here too, and keep the returned `zigux/Makefile` file distinct from `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` while the missing shared build companion keeps the broader make-route handle from qualifying as current adjacent evidence.",
    "- `scripts/zigux/validate-phase13-release.py`",
    "- `lib/devres.zig`",
    "- `Documentation/zigux/phase13-landlock-syscalls-survey.md`",
    "- `zigux/tests/phase13_landlock_syscalls.zig`",
    "- `zigux/helpers/notifier_chain_view.zig`",
)

FORBIDDEN_MARKERS = (
    "`zigux/helpers/notifier_chain_view.zig` framed as shipped adjacent evidence",
    "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
    "Current `master` now materializes `scripts/zigux/validate-phase13-release.py`",
    "Current `master` now materializes `zigux/tests/phase13_landlock_syscalls.zig`",
)

FORBIDDEN_MAKE_TARGETS = (
    "phase13-validate",
    "phase13",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def has_make_target(text: str, target: str) -> bool:
    phony_pattern = rf"(?m)^[.]?PHONY:.*(?:^|\\s){re.escape(target)}(?:\\s|$)"
    target_pattern = rf"(?m)^{re.escape(target)}:"
    return re.search(phony_pattern, text) is not None or re.search(target_pattern, text) is not None


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    roadmap_path = root / ROADMAP_TRACEABILITY
    makefile_path = root / MAKEFILE

    if not roadmap_path.exists():
        return [f"missing_required_file:{ROADMAP_TRACEABILITY.as_posix()}"]
    if not makefile_path.exists():
        return [f"missing_required_file:{MAKEFILE.as_posix()}"]

    roadmap_text = read_text(roadmap_path)
    makefile_text = read_text(makefile_path)

    for marker in REQUIRED_MARKERS:
        if marker not in roadmap_text:
            issues.append(f"missing_marker:{marker}")

    for marker in FORBIDDEN_MARKERS:
        if marker in roadmap_text:
            issues.append(f"forbidden_marker:{marker}")

    for relpath in REQUIRED_PRESENT_PATHS:
        if not (root / relpath).exists():
            issues.append(f"missing_present_path:{relpath}")

    for relpath in REQUIRED_ABSENT_PATHS:
        if (root / relpath).exists():
            issues.append(f"unexpected_present_gap:{relpath}")

    for target in FORBIDDEN_MAKE_TARGETS:
        if has_make_target(makefile_text, target):
            issues.append(f"unexpected_make_target:{target}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_ROADMAP_TRACEABILITY=fail")
    print("PHASE13_ROADMAP_TRACEABILITY_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_ROADMAP_TRACEABILITY_ISSUES_END")
    return 1


def populate_root(root: Path) -> None:
    roadmap_text = """# Phase 13 Roadmap Traceability

This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.

It is a traceability document only. It does not create a new helper lane, a new replay route, or a tranche-closure claim.

## Roadmap Fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche.

The roadmap keeps that tranche bounded to four Linux anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

## Shared Packet Surfaces

Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep the returned `zigux/Makefile` file distinct from the still-missing `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` names instead of treating that Phase 2-only wrapper file as a materialized shared Phase 13 surface.

## Anchor Map

- `devres` stays mapped through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, the shipped DMA-boundary checker pair `scripts/zigux/check-phase13-devres-dma-boundary.py` and `scripts/zigux/check-phase13-devres-mmio-packet.py`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`.
- `landlock/syscalls` stays mapped through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and the shipped `security/landlock/syscalls.zig` starter. Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, ruleset-fd install planning, and ruleset-fd stub discipline planning, and keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` framed as repo-reality gaps until current `master` materializes them again so the reminder packet does not overstate the live syscall helper surface.

## Adjacent Evidence

Keep `zigux/helpers/notifier_chain_view.zig` framed as a repo-reality gap here too, and keep the returned `zigux/Makefile` file distinct from `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` while the missing shared build companion keeps the broader make-route handle from qualifying as current adjacent evidence.

## Repo-Reality Gaps

- `scripts/zigux/validate-phase13-release.py`
- `lib/devres.zig`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/helpers/notifier_chain_view.zig`
"""
    write_text(root / ROADMAP_TRACEABILITY, roadmap_text)

    makefile_text = """.PHONY: phase2 phase3 phase12
phase2:
\t@true
phase3:
\t@true
"""
    write_text(root / MAKEFILE, makefile_text)

    for relpath in REQUIRED_PRESENT_PATHS:
        write_text(root / relpath, "present\n")


def run_self_test() -> int:
    checks_run = 0
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-roadmap-traceability-"))
    try:
        populate_root(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        (tempdir / "zigux/helpers/list_view.zig").unlink()
        issues = collect_issues(tempdir)
        assert "missing_present_path:zigux/helpers/list_view.zig" in issues
        populate_root(tempdir)
        checks_run += 1

        write_text(tempdir / "lib/devres.zig", "unexpected\n")
        issues = collect_issues(tempdir)
        assert "unexpected_present_gap:lib/devres.zig" in issues
        populate_root(tempdir)
        checks_run += 1

        makefile_path = tempdir / MAKEFILE
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8") + "phase13-validate:\n\t@true\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert "unexpected_make_target:phase13-validate" in issues
        populate_root(tempdir)
        checks_run += 1

        roadmap_path = tempdir / ROADMAP_TRACEABILITY
        roadmap_path.write_text(
            roadmap_path.read_text(encoding="utf-8")
            + "\nCurrent `master` still exposes `make -C zigux phase13` through `zigux/Makefile`\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`"
            in issues
        )
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_ROADMAP_TRACEABILITY_SELF_TEST=pass")
    print(f"PHASE13_ROADMAP_TRACEABILITY_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 13 roadmap-traceability note aligned with current repo reality."
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_ROADMAP_TRACEABILITY=pass")
    print(f"PHASE13_ROADMAP_TRACEABILITY_PRESENT_COUNT={len(REQUIRED_PRESENT_PATHS)}")
    print(f"PHASE13_ROADMAP_TRACEABILITY_ABSENT_COUNT={len(REQUIRED_ABSENT_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
