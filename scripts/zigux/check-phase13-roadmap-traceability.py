#!/usr/bin/env python3
"""Guard the shipped Phase 13 roadmap-traceability note."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


ROADMAP_NOTE = "Documentation/zigux/phase13-roadmap-traceability.md"

REQUIRED_MARKERS = [
    "The roadmap keeps that tranche bounded to four Linux anchors:",
    "Keep `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit as the stable contributor-facing handle.",
    "- refresh basis: current `master` direct readback on `2026-05-24`",
    "- dedicated roadmap-traceability guard: `python3 scripts/zigux/check-phase13-roadmap-traceability.py`",
    "- stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "- shared tests-root alignment guard: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`",
    "- shared release-discipline validator: `python3 scripts/zigux/validate-phase13-release.py`",
    "Current `master` now materializes `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, and the surrounding shared reminder packet, while the Phase 13 Makefile route family still remains missing.",
    "- `lib/devres.c`: `devres` stays mapped through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, the shipped DMA-boundary checker pair `scripts/zigux/check-phase13-devres-dma-boundary.py` and the historically named `scripts/zigux/check-phase13-devres-mmio-packet.py`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `scripts/zigux/check-phase13-devres-scatterlist-planner.py`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, while `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` remain repo-reality gaps on current `master`.",
    "Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, keep the survey-gap note framed only as a historical breadcrumb inside that helper-local packet, and keep `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion framed as repo-reality gaps until current `master` materializes them again.",
    "- `scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "- `zigux/helpers/notifier_chain_view.zig`",
]

FORBIDDEN_MARKERS = [
    "- refresh basis: current `master` direct readback on `2026-05-18`",
    "- refresh basis: current `master` direct readback on `2026-05-21`",
    "treating that Phase 2-only wrapper file as a materialized shared Phase 13 build handle.",
    "`Documentation/zigux/phase13-notifier-list-survey.md` still does not materialize on current `master`",
    "Older `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay explicit repo-reality gaps instead of the current active devres packet.",
    "stable shared-summary guard: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`",
]


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: str, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        text = read_text(root, ROADMAP_NOTE)
    except SystemExit as exc:
        return [str(exc)]

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(f"missing_marker:{ROADMAP_NOTE}:{marker}")

    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            issues.append(f"forbidden_marker:{ROADMAP_NOTE}:{marker}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_ROADMAP_TRACEABILITY=fail")
    print("PHASE13_ROADMAP_TRACEABILITY_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_ROADMAP_TRACEABILITY_ISSUES_END")
    return 1


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-roadmap-traceability-"))
    checks_run = 0
    try:
        source_note = Path(__file__).resolve().parents[2] / ROADMAP_NOTE
        write_text(tempdir, ROADMAP_NOTE, source_note.read_text(encoding="utf-8"))
        assert collect_issues(tempdir) == []
        checks_run += 1

        note_path = tempdir / ROADMAP_NOTE
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "- dedicated roadmap-traceability guard: `python3 scripts/zigux/check-phase13-roadmap-traceability.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:- dedicated roadmap-traceability guard: `python3 scripts/zigux/check-phase13-roadmap-traceability.py`"
            in issues
        )
        write_text(tempdir, ROADMAP_NOTE, source_note.read_text(encoding="utf-8"))
        checks_run += 1

        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "- `zigux/helpers/notifier_chain_view.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:- `zigux/helpers/notifier_chain_view.zig`"
            in issues
        )
        write_text(tempdir, ROADMAP_NOTE, source_note.read_text(encoding="utf-8"))
        checks_run += 1

        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "`Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, ",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:Current `master` now materializes `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, and the surrounding shared reminder packet, while the Phase 13 Makefile route family still remains missing."
            in issues
        )
        write_text(tempdir, ROADMAP_NOTE, source_note.read_text(encoding="utf-8"))
        checks_run += 1

        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, keep the survey-gap note framed only as a historical breadcrumb inside that helper-local packet, and keep `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion framed as repo-reality gaps until current `master` materializes them again.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, keep the survey-gap note framed only as a historical breadcrumb inside that helper-local packet, and keep `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the older shared `zigux/tests/phase13_build.zig` companion framed as repo-reality gaps until current `master` materializes them again."
            in issues
        )
        write_text(tempdir, ROADMAP_NOTE, source_note.read_text(encoding="utf-8"))
        checks_run += 1

        note_path.write_text(
            note_path.read_text(encoding="utf-8")
            + "stable shared-summary guard: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-roadmap-traceability.md:stable shared-summary guard: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`"
            in issues
        )
        write_text(tempdir, ROADMAP_NOTE, source_note.read_text(encoding="utf-8"))
        checks_run += 1

        note_path.write_text(
            note_path.read_text(encoding="utf-8")
            + "- refresh basis: current `master` direct readback on `2026-05-21`\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-roadmap-traceability.md:- refresh basis: current `master` direct readback on `2026-05-21`"
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
        description="Keep the shipped Phase 13 roadmap-traceability note aligned."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_ROADMAP_TRACEABILITY=pass")
    print(f"PHASE13_ROADMAP_TRACEABILITY_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
