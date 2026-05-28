#!/usr/bin/env python3
"""Guard the shipped Phase 13 shared-summary contributor surfaces."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_MARKERS = {
    "Documentation/zigux/phase13-contributor-workflow-guide.md": [
        "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the file itself distinct from those missing Phase 13 route names and keep only the route names recorded as repo-reality gaps until the shared build handle returns.",
        "Keep `zigux/tests/phase13_landlock_syscalls_manifest.json` and `zigux/tests/phase13_build.zig` recorded as repo-reality gaps until they rematerialize on current `master`, while the direct replay and reviewability companions stay explicit as shipped current-`master` evidence.",
        "Keep `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` aligned as PMO coordination companions when shared contributor wording also changes release-facing or cross-phase wording rather than treating either note as a replacement for the stable contributor-facing handle.",
        "Release-facing companion rule: reread `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` beside the workflow-guide, scripts-root, and tests-root trio when release-facing or cross-phase wording moves, and keep those two notes as PMO coordination companions rather than as the contributor-facing handle.",
        "Contributor quick-start loop: open the workflow-guide, scripts-root, and tests-root trio first, reread the packet index plus the Phase 12 to Phase 13 handoff note when release-facing wording moves, keep the change to one shared reminder surface plus the smallest helper-local note, rerun the shared-summary, tests-root, and release-validator trio, and leave missing routes or helpers in the repo-reality-gap bucket.",
        "Shared contributor edit loop: reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first, reread `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` when release-facing or cross-phase wording moves, update at most one shared reminder surface plus the smallest helper-local packet note in the same change, rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py`, and keep any absent route, replay, or helper recorded as a repo-reality gap instead of promoted shipped evidence.",
        "`Documentation/zigux/phase13-release-packet-index.md`",
        "`Documentation/zigux/phase12-phase13-release-handoff.md`",
        "`scripts/zigux/check-phase13-devres-scatterlist-planner.py`",
    ],
    "Documentation/zigux/phase13-release-coordination-matrix.md": [
        "shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.",
        "The active shared packet stays contributor-facing and review-first. Helper-local proof remains owned by the `libfs`, `devres`, and `landlock` packets, while notifier evidence stays adjacent release-surface support through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`.",
        "- adjacent notifier support: keep `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` truthful as support evidence without promoting them into a fifth helper lane",
        "Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support beside the shared-summary guard and tests-root alignment companion instead of carrying it in the repo-reality-gap bucket.",
        "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`",
    ],
    "Documentation/zigux/phase13-release-notes-survey.md": [
        "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:",
        "`Documentation/zigux/phase13-release-coordination-matrix.md`",
        "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
        "`Documentation/zigux/phase13-roadmap-traceability.md`",
        "`scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "Keep broad release wording tied to that reminder packet while the missing validator-first helpers, adjacent notifier companion, and route surfaces stay explicit as repo-reality gaps.",
    ],
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md": [
        "shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence",
        "`landlock/syscalls` owns the narrower syscall governance, slice, helper-local survey packet, historical survey-gap breadcrumb, focused packet checker, helper starter, direct replay companion, and direct reviewability companion through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`",
        "- adjacent notifier evidence owns only release-surface truthfulness through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`, not a fifth helper family",
        "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`",
    ],
    "Documentation/zigux/phase13-shared-summary-guard-gap.md": [
        "This note records the closure of the old missing-checker gap.",
        "The shipped guard is `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`.",
        "The shipped tests-root packet should therefore keep the returned helper-local Landlock survey-and-checker packet plus the direct Landlock replay and reviewability companions explicit while still recording the manifest and shared-build-route companions as repo-reality gaps rather than shipped evidence.",
    ],
    "Documentation/zigux/phase13-notifier-summary-gap.md": [
        "Current reread also shows the broader contributor-facing reminder surfaces already keep the checker-backed adjacent packet explicit, keep `zigux/Makefile` distinct from the still-missing route names, keep `scripts/zigux/validate-phase13-release.py` explicit as a shipped shared release companion, and keep `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and `scripts/zigux/check-phase13-notifier-priority-signal.py` recorded as repo-reality gaps.",
        "If the same notifier or list family needs follow-through again, first compare `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `scripts/zigux/check-phase13-tests-readme-alignment.py`, and `Documentation/zigux/phase13-notifier-list-survey.md` together, then land at most one reminder-surface refresh only if one of them stops treating `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, and `scripts/zigux/validate-phase13-release.py` as shipped adjacent evidence while `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and the missing Phase 13 build-route names stay in the repo-reality-gap bucket.",
    ],
    "Documentation/zigux/phase13-roadmap-traceability.md": [
        "Keep `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` explicit as the stable contributor-facing handle.",
        "Current `master` now materializes `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`",
        "`devres` stays mapped through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, the shipped DMA-boundary checker pair `scripts/zigux/check-phase13-devres-dma-boundary.py` and the historically named `scripts/zigux/check-phase13-devres-mmio-packet.py`",
        "Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning",
        "current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_manifest.json`, the older shared `zigux/tests/phase13_build.zig` companion, and the live file-descriptor installation, credential replacement, and ruleset-state surfaces stay repo-reality gaps on current `master`.",
        "Current `master` also now materializes `scripts/zigux/check-phase13-roadmap-traceability.py`, so keep that checker explicit as the note-level guard for this roadmap-to-repo owner map rather than treating traceability as a reminder-only surface with no dedicated replay.",
        "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`",
    ],
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md": [
        "- keep the shared contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, keep `Documentation/zigux/phase13-release-coordination-matrix.md` plus `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` explicit as supporting coordination companions rather than as the stable handle itself, keep `scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit as the shipped shared-summary guard beside that stable handle, keep `zigux/Makefile` explicit only as the returned file, and keep `make -C zigux phase13-validate` plus blocked convenience route `make -C zigux phase13` framed as the still-missing shared build routes on current `master`",
        "- treat notifier evidence as adjacent release-surface support rather than a fifth shared-helper anchor, and keep the shipped `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` explicit while `zigux/helpers/notifier_chain_view.zig` remains a separate adjacent repo-reality gap; keep `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, and `zigux/tests/phase13_notifier_list_reviewability.zig` visible as the focused adjacent checker packet without promoting notifier support into a fifth helper lane.",
        "`scripts/zigux/check-phase13-devres-scatterlist-planner.py`",
        "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`",
    ],
    "Documentation/zigux/review-checklist.md": [
        "* if the change touches the shared Phase 13 shared-helper packet, do `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, and `scripts/zigux/check-phase13-tests-readme-alignment.py` still agree on the stable contributor-facing handle;",
        "keep adjacent notifier evidence explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`;",
        "and keep validator-first, deeper `devres` replay, direct Landlock syscall replay, adjacent notifier-chain and notifier-header companions `zigux/helpers/notifier_chain_view.zig` and `include/zigux/notifier_abi.h`, and notifier-priority surfaces framed as repo-reality gaps until current `master` rematerializes them?",
        "`scripts/zigux/check-phase13-devres-scatterlist-planner.py`",
    ],
    "scripts/zigux/README.md": [
        "`Documentation/zigux/phase13-shared-summary-guard-gap.md`",
        "`Documentation/zigux/phase13-notifier-summary-gap.md`",
        "keep `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` explicit as returned shared-summary and adjacent notifier evidence on current `master` instead of leaving them in the repo-reality-gap list",
        "`zigux/Makefile` is present on current `master`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
        "`scripts/zigux/check-phase13-shared-summary-surfaces.py`, `scripts/zigux/check-phase13-tests-readme-alignment.py`, and `scripts/zigux/validate-phase13-release.py` keep the shared-summary, tests-root alignment, and release-discipline packet explicit from the scripts root without pretending a broader validator-first or convenience-route replay has returned",
        "`scripts/zigux/check-phase13-devres-scatterlist-planner.py`",
    ],
    "zigux/tests/README.md": [
        "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, and `Documentation/zigux/phase13-notifier-summary-gap.md` aligned with that stable handle as supporting shared reminder surfaces. Keep `Documentation/zigux/phase13-release-coordination-matrix.md` and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` explicit as supporting coordination companions, and keep `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, and `Documentation/zigux/phase13-notifier-summary-gap.md` aligned as broader same-lane reminder surfaces rather than treating the missing Makefile-backed route family as the shared entrypoint.",
        "Current `master` also materializes the adjacent notifier survey plus the focused checker-backed packet `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those nine paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.",
        "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    ],
}

FORBIDDEN_MARKERS = (
    "`scripts/zigux/check-phase13-shared-summary-surfaces.py` is still absent on current `master`",
    "missing guard path: `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "Keep only `scripts/zigux/check-phase13-shared-summary-surfaces.py` recorded as a shared-summary repo-reality gap",
    "scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_build.zig`",
    "`zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/abi.h`, and `drivers/tty/hvc/hvc_console.h` stay explicit as adjacent notifier evidence rather than a fifth helper family",
    "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
    "Keep `make -C zigux phase13-validate` as the stable contributor-facing handle until the shared build companion lands",
    "Current `master` still does not materialize `Documentation/zigux/phase13-notifier-list-survey.md`, so keep that note framed as an adjacent repo-reality gap rather than as shipped tests-root evidence.",
    "Current `master` still does not materialize `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, or `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep those validator-first and checker names framed as repo-reality gaps rather than shipped tests-root evidence.",
    "Current `master` still does not materialize `zigux/Makefile`, `make -C zigux phase13-validate`, or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    "Older `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay explicit repo-reality gaps instead of the current active devres packet.",
    "`Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "`landlock/syscalls` owns the syscall governance, slice, survey, and focused helper-local replay packet through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.",
    "Keep `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "while `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`",
)


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
    script_path = root / "scripts/zigux/check-phase13-shared-summary-surfaces.py"
    if not script_path.exists():
        issues.append("missing_file:scripts/zigux/check-phase13-shared-summary-surfaces.py")

    for relpath, markers in REQUIRED_MARKERS.items():
        try:
            text = read_text(root, relpath)
        except SystemExit as exc:
            issues.append(str(exc))
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{relpath}:{marker}")
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                issues.append(f"forbidden_marker:{relpath}:{marker}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_SHARED_SUMMARY_SURFACES=fail")
    print("PHASE13_SHARED_SUMMARY_SURFACES_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_SHARED_SUMMARY_SURFACES_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    write_text(
        root,
        "scripts/zigux/check-phase13-shared-summary-surfaces.py",
        "#!/usr/bin/env python3\nprint('placeholder')\n",
    )
    for relpath, markers in REQUIRED_MARKERS.items():
        write_text(root, relpath, "\n".join(markers) + "\n")


def expect_issue(issues: list[str], expected: str) -> None:
    assert expected in issues, f"missing expected issue: {expected}"


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-shared-summary-surfaces-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        (tempdir / "scripts/zigux/check-phase13-shared-summary-surfaces.py").unlink()
        expect_issue(
            collect_issues(tempdir),
            "missing_file:scripts/zigux/check-phase13-shared-summary-surfaces.py",
        )
        checks_run += 1

        populate_repo(tempdir)
        contributor_guide_path = tempdir / "Documentation/zigux/phase13-contributor-workflow-guide.md"
        contributor_guide_path.write_text(
            contributor_guide_path.read_text(encoding="utf-8").replace(
                "Keep `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` aligned as PMO coordination companions when shared contributor wording also changes release-facing or cross-phase wording rather than treating either note as a replacement for the stable contributor-facing handle.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:Keep `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` aligned as PMO coordination companions when shared contributor wording also changes release-facing or cross-phase wording rather than treating either note as a replacement for the stable contributor-facing handle.",
        )
        checks_run += 1

        populate_repo(tempdir)
        contributor_guide_path = tempdir / "Documentation/zigux/phase13-contributor-workflow-guide.md"
        contributor_guide_path.write_text(
            contributor_guide_path.read_text(encoding="utf-8").replace(
                "Release-facing companion rule: reread `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` beside the workflow-guide, scripts-root, and tests-root trio when release-facing or cross-phase wording moves, and keep those two notes as PMO coordination companions rather than as the contributor-facing handle.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:Release-facing companion rule: reread `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` beside the workflow-guide, scripts-root, and tests-root trio when release-facing or cross-phase wording moves, and keep those two notes as PMO coordination companions rather than as the contributor-facing handle.",
        )
        checks_run += 1

        populate_repo(tempdir)
        contributor_guide_path = tempdir / "Documentation/zigux/phase13-contributor-workflow-guide.md"
        contributor_guide_path.write_text(
            contributor_guide_path.read_text(encoding="utf-8").replace(
                "Contributor quick-start loop: open the workflow-guide, scripts-root, and tests-root trio first, reread the packet index plus the Phase 12 to Phase 13 handoff note when release-facing wording moves, keep the change to one shared reminder surface plus the smallest helper-local note, rerun the shared-summary, tests-root, and release-validator trio, and leave missing routes or helpers in the repo-reality-gap bucket.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:Contributor quick-start loop: open the workflow-guide, scripts-root, and tests-root trio first, reread the packet index plus the Phase 12 to Phase 13 handoff note when release-facing wording moves, keep the change to one shared reminder surface plus the smallest helper-local note, rerun the shared-summary, tests-root, and release-validator trio, and leave missing routes or helpers in the repo-reality-gap bucket.",
        )
        checks_run += 1

        populate_repo(tempdir)
        contributor_guide_path = tempdir / "Documentation/zigux/phase13-contributor-workflow-guide.md"
        contributor_guide_path.write_text(
            contributor_guide_path.read_text(encoding="utf-8").replace(
                "Shared contributor edit loop: reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first, reread `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` when release-facing or cross-phase wording moves, update at most one shared reminder surface plus the smallest helper-local packet note in the same change, rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py`, and keep any absent route, replay, or helper recorded as a repo-reality gap instead of promoted shipped evidence.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:Shared contributor edit loop: reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first, reread `Documentation/zigux/phase13-release-packet-index.md` and `Documentation/zigux/phase12-phase13-release-handoff.md` when release-facing or cross-phase wording moves, update at most one shared reminder surface plus the smallest helper-local packet note in the same change, rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py`, and keep any absent route, replay, or helper recorded as a repo-reality gap instead of promoted shipped evidence.",
        )
        checks_run += 1

        populate_repo(tempdir)
        contributor_guide_path = tempdir / "Documentation/zigux/phase13-contributor-workflow-guide.md"
        contributor_guide_path.write_text(
            contributor_guide_path.read_text(encoding="utf-8").replace(
                "Keep `zigux/tests/phase13_landlock_syscalls_manifest.json` and `zigux/tests/phase13_build.zig` recorded as repo-reality gaps until they rematerialize on current `master`, while the direct replay and reviewability companions stay explicit as shipped current-`master` evidence.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:Keep `zigux/tests/phase13_landlock_syscalls_manifest.json` and `zigux/tests/phase13_build.zig` recorded as repo-reality gaps until they rematerialize on current `master`, while the direct replay and reviewability companions stay explicit as shipped current-`master` evidence.",
        )
        checks_run += 1

        populate_repo(tempdir)
        release_notes_path = tempdir / "Documentation/zigux/phase13-release-notes-survey.md"
        release_notes_path.write_text(
            release_notes_path.read_text(encoding="utf-8").replace(
                "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:",
        )
        checks_run += 1

        populate_repo(tempdir)
        release_notes_path = tempdir / "Documentation/zigux/phase13-release-notes-survey.md"
        release_notes_path.write_text(
            release_notes_path.read_text(encoding="utf-8").replace(
                "`Documentation/zigux/phase13-roadmap-traceability.md`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:`Documentation/zigux/phase13-roadmap-traceability.md`",
        )
        checks_run += 1

        populate_repo(tempdir)
        release_notes_path = tempdir / "Documentation/zigux/phase13-release-notes-survey.md"
        release_notes_path.write_text(
            release_notes_path.read_text(encoding="utf-8").replace(
                "`scripts/zigux/validate-phase13-release.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:`scripts/zigux/validate-phase13-release.py`",
        )
        checks_run += 1

        populate_repo(tempdir)
        release_matrix_path = tempdir / "Documentation/zigux/phase13-release-coordination-matrix.md"
        release_matrix_path.write_text(
            release_matrix_path.read_text(encoding="utf-8").replace(
                "Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support beside the shared-summary guard and tests-root alignment companion instead of carrying it in the repo-reality-gap bucket.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-release-coordination-matrix.md:Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support beside the shared-summary guard and tests-root alignment companion instead of carrying it in the repo-reality-gap bucket.",
        )
        checks_run += 1

        populate_repo(tempdir)
        roadmap_path = tempdir / "Documentation/zigux/phase13-roadmap-traceability.md"
        roadmap_path.write_text(
            roadmap_path.read_text(encoding="utf-8").replace(
                "Current `master` also now materializes `scripts/zigux/check-phase13-roadmap-traceability.py`, so keep that checker explicit as the note-level guard for this roadmap-to-repo owner map rather than treating traceability as a reminder-only surface with no dedicated replay.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:Current `master` also now materializes `scripts/zigux/check-phase13-roadmap-traceability.py`, so keep that checker explicit as the note-level guard for this roadmap-to-repo owner map rather than treating traceability as a reminder-only surface with no dedicated replay.",
        )
        checks_run += 1

        populate_repo(tempdir)
        roadmap_path = tempdir / "Documentation/zigux/phase13-roadmap-traceability.md"
        roadmap_path.write_text(
            roadmap_path.read_text(encoding="utf-8").replace(
                "current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_manifest.json`, the older shared `zigux/tests/phase13_build.zig` companion, and the live file-descriptor installation, credential replacement, and ruleset-state surfaces stay repo-reality gaps on current `master`.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:current `master` materializes the helper-local packet plus the direct replay and direct reviewability companions through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_manifest.json`, the older shared `zigux/tests/phase13_build.zig` companion, and the live file-descriptor installation, credential replacement, and ruleset-state surfaces stay repo-reality gaps on current `master`.",
        )
        checks_run += 1

        populate_repo(tempdir)
        contributor_sync_path = tempdir / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"
        contributor_sync_path.write_text(
            contributor_sync_path.read_text(encoding="utf-8").replace(
                "`scripts/zigux/check-phase13-devres-scatterlist-planner.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md:`scripts/zigux/check-phase13-devres-scatterlist-planner.py`",
        )
        checks_run += 1

        populate_repo(tempdir)
        checklist_path = tempdir / "Documentation/zigux/review-checklist.md"
        checklist_path.write_text(
            checklist_path.read_text(encoding="utf-8").replace(
                "keep adjacent notifier evidence explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`;\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/review-checklist.md:keep adjacent notifier evidence explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`;",
        )
        checks_run += 1

        populate_repo(tempdir)
        checklist_path = tempdir / "Documentation/zigux/review-checklist.md"
        checklist_path.write_text(
            checklist_path.read_text(encoding="utf-8").replace(
                "`scripts/zigux/check-phase13-devres-scatterlist-planner.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/review-checklist.md:`scripts/zigux/check-phase13-devres-scatterlist-planner.py`",
        )
        checks_run += 1

        populate_repo(tempdir)
        scripts_readme_path = tempdir / "scripts/zigux/README.md"
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(
                "`Documentation/zigux/phase13-shared-summary-guard-gap.md`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:scripts/zigux/README.md:`Documentation/zigux/phase13-shared-summary-guard-gap.md`",
        )
        checks_run += 1

        populate_repo(tempdir)
        scripts_readme_path = tempdir / "scripts/zigux/README.md"
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(
                "`Documentation/zigux/phase13-notifier-summary-gap.md`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:scripts/zigux/README.md:`Documentation/zigux/phase13-notifier-summary-gap.md`",
        )
        checks_run += 1

        populate_repo(tempdir)
        scripts_readme_path = tempdir / "scripts/zigux/README.md"
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(
                "`scripts/zigux/check-phase13-devres-scatterlist-planner.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:scripts/zigux/README.md:`scripts/zigux/check-phase13-devres-scatterlist-planner.py`",
        )
        checks_run += 1

        populate_repo(tempdir)
        tests_path = tempdir / "zigux/tests/README.md"
        tests_path.write_text(
            tests_path.read_text(encoding="utf-8").replace(
                "Current `master` also materializes the adjacent notifier survey plus the focused checker-backed packet `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those nine paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:zigux/tests/README.md:Current `master` also materializes the adjacent notifier survey plus the focused checker-backed packet `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those nine paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.",
        )
        checks_run += 1

        populate_repo(tempdir)
        gap_path = tempdir / "Documentation/zigux/phase13-shared-summary-guard-gap.md"
        gap_path.write_text(
            gap_path.read_text(encoding="utf-8").replace(
                "This note records the closure of the old missing-checker gap.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/phase13-shared-summary-guard-gap.md:This note records the closure of the old missing-checker gap.",
        )
        checks_run += 1

        populate_repo(tempdir)
        notifier_gap_path = tempdir / "Documentation/zigux/phase13-notifier-summary-gap.md"
        notifier_gap_path.write_text(
            notifier_gap_path.read_text(encoding="utf-8")
            + "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`\n",
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "forbidden_marker:Documentation/zigux/phase13-notifier-summary-gap.md:Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
        )
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_SHARED_SUMMARY_SURFACES_SELF_TEST=pass")
    print(f"PHASE13_SHARED_SUMMARY_SURFACES_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shipped Phase 13 shared-summary contributor surfaces aligned."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_SHARED_SUMMARY_SURFACES=pass")
    print(f"PHASE13_SHARED_SUMMARY_SURFACE_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
