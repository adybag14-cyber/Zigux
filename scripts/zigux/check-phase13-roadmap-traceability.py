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
    "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep the returned `zigux/Makefile` file distinct from the still-missing `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` names instead of treating that Phase 2-only wrapper file as a materialized shared Phase 13 surface.",
    "- refresh basis: current `master` direct readback on `2026-05-18`",
    "- stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "- `lib/devres.c`: shipped narrower DMA-boundary, planner, and scatterlist packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, while the older broader direct `phase13_devres` helper packet stays recorded as a repo-reality gap.",
    "- `security/landlock/syscalls.c`: shipped governance, slice, and starter packet through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `security/landlock/syscalls.zig`.",
    "Current `master` now materializes `Documentation/zigux/phase13-notifier-list-survey.md`, so keep that note together with the checker-backed adjacent notifier packet and the bounded list, hlist, and ABI companions explicit as adjacent notifier evidence through:",
    "- `scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "- `zigux/helpers/notifier_chain_view.zig`",
    "That gap set is also what keeps `make -C zigux phase13` framed as blocked convenience wiring rather than a stable shared replay handle.",
]

FORBIDDEN_MARKERS = [
    "treating that Phase 2-only wrapper file as a materialized shared Phase 13 build handle.",
    "`Documentation/zigux/phase13-notifier-list-survey.md` still does not materialize on current `master`",
    "Older `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay explicit repo-reality gaps instead of the current active devres packet.",
    "repo-reality gap instead of the current active devres packet.",
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


def populate_repo(root: Path) -> None:
    write_text(root, ROADMAP_NOTE, "\n".join(REQUIRED_MARKERS) + "\n")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-roadmap-traceability-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        note_path = tempdir / ROADMAP_NOTE
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "- stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:- stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`"
            in issues
        )
        populate_repo(tempdir)
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
        populate_repo(tempdir)
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
        populate_repo(tempdir)
        checks_run += 1

        note_path.write_text(
            note_path.read_text(encoding="utf-8")
            + "treating that Phase 2-only wrapper file as a materialized shared Phase 13 build handle.\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-roadmap-traceability.md:treating that Phase 2-only wrapper file as a materialized shared Phase 13 build handle."
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
    print("PHASE13_ROADMAP_TRACEABILITY_MARKER_COUNT=10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
