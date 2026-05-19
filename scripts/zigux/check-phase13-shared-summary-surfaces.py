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
        "Keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`.",
    ],
    "Documentation/zigux/phase13-release-coordination-matrix.md": [
        "shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "keep the Makefile-backed route family recorded as repo-reality gaps",
        "The active shared packet stays contributor-facing and review-first. Helper-local proof remains owned by the `libfs`, `devres`, and `landlock` packets, while notifier evidence stays adjacent release-surface support through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`.",
        "- adjacent notifier support: keep `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` truthful as support evidence without promoting them into a fifth helper lane",
    ],
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md": [
        "shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence",
        "`landlock/syscalls` owns the syscall governance, slice, and helper starter surface through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `security/landlock/syscalls.zig`, while `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`",
        "- adjacent notifier evidence owns only release-surface truthfulness through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`, not a fifth helper family",
    ],
    "Documentation/zigux/phase13-shared-summary-guard-gap.md": [
        "This note records the closure of the old missing-checker gap.",
        "The shipped guard is `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`.",
    ],
    "Documentation/zigux/phase13-notifier-summary-gap.md": [
        "Broad Phase 13 reminder work should therefore keep the checker-backed adjacent packet explicit, keep `zigux/Makefile` distinct from the still-missing route names, and keep `zigux/helpers/notifier_chain_view.zig` plus `scripts/zigux/check-phase13-notifier-priority-signal.py` recorded as repo-reality gaps until a future reread proves they returned.",
        "If the same notifier or list family needs follow-through again, refresh `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, and `scripts/zigux/check-phase13-shared-summary-surfaces.py` so they treat `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, and `zigux/tests/phase13_notifier_list_reviewability.zig` as shipped adjacent evidence while still keeping `zigux/helpers/notifier_chain_view.zig` and the missing Phase 13 build-route names in the repo-reality-gap bucket.",
    ],
    "Documentation/zigux/phase13-roadmap-traceability.md": [
        "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep the returned `zigux/Makefile` file distinct from the still-missing `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` names instead of treating that Phase 2-only wrapper file as a materialized shared Phase 13 surface.",
        "Current `master` now materializes `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, and `Documentation/zigux/phase13-notifier-list-survey.md` alongside the narrower bounded devres coordination packet, so keep those surfaces aligned as shipped shared evidence while the missing validator-first checker packet, the absent shared build companion, the still-missing direct Landlock syscall companions, the older direct devres companions, and the missing notifier-chain companion stay recorded here as repo-reality gaps.",
        "`devres` stays mapped through `Documentation/zigux/phase13-devres-slice.md`, the shipped DMA-boundary checker pair `scripts/zigux/check-phase13-devres-dma-boundary.py` and `scripts/zigux/check-phase13-devres-mmio-packet.py`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`.",
        "Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, ruleset-fd install planning, and ruleset-fd stub discipline planning, and keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` framed as repo-reality gaps until current `master` materializes them again so the reminder packet does not overstate the live syscall helper surface.",
    ],
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md": [
        "- keep the shared contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, while keeping `scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit as the shipped shared-summary guard beside that stable handle, while keeping `zigux/Makefile` explicit only as the returned file and keeping `make -C zigux phase13-validate` plus blocked convenience route `make -C zigux phase13` framed as the still-missing shared build routes on current `master`",
        "- treat notifier evidence as adjacent release-surface support rather than a fifth shared-helper anchor, and keep the shipped `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` explicit while `zigux/helpers/notifier_chain_view.zig` remains a separate adjacent repo-reality gap",
    ],
    "scripts/zigux/README.md": [
        "keep `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` explicit as returned shared-summary and adjacent notifier evidence on current `master` instead of leaving them in the repo-reality-gap list",
        "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
        "current `master` still does not materialize `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, and `include/zigux/notifier_abi.h`, so treat those validator-first, build, helper, header, and notifier-route companions as repo-reality gaps rather than direct scripts-root evidence",
    ],
    "zigux/tests/README.md": [
        "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/review-checklist.md` and `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md` aligned with that stable handle as supporting shared reminder surfaces rather than treating the missing Makefile-backed route family as the shared entrypoint.",
        "Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.",
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
    "`Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "`landlock/syscalls` owns the syscall governance, slice, survey, and focused helper-local replay packet through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`",
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


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-shared-summary-surfaces-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        (tempdir / "scripts/zigux/check-phase13-shared-summary-surfaces.py").unlink()
        issues = collect_issues(tempdir)
        assert "missing_file:scripts/zigux/check-phase13-shared-summary-surfaces.py" in issues
        populate_repo(tempdir)
        checks_run += 1

        workflow_path = tempdir / "Documentation/zigux/phase13-contributor-workflow-guide.md"
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        contributor_sync_path = tempdir / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"
        contributor_sync_path.write_text(
            contributor_sync_path.read_text(encoding="utf-8").replace(
                "- keep the shared contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, while keeping `scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit as the shipped shared-summary guard beside that stable handle, while keeping `zigux/Makefile` explicit only as the returned file and keeping `make -C zigux phase13-validate` plus blocked convenience route `make -C zigux phase13` framed as the still-missing shared build routes on current `master`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md:- keep the shared contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, while keeping `scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit as the shipped shared-summary guard beside that stable handle, while keeping `zigux/Makefile` explicit only as the returned file and keeping `make -C zigux phase13-validate` plus blocked convenience route `make -C zigux phase13` framed as the still-missing shared build routes on current `master`"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        gap_path = tempdir / "Documentation/zigux/phase13-shared-summary-guard-gap.md"
        gap_path.write_text(
            gap_path.read_text(encoding="utf-8")
            + "`scripts/zigux/check-phase13-shared-summary-surfaces.py` is still absent on current `master`\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-shared-summary-guard-gap.md:`scripts/zigux/check-phase13-shared-summary-surfaces.py` is still absent on current `master`"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        scripts_readme = tempdir / "scripts/zigux/README.md"
        scripts_readme.write_text(
            scripts_readme.read_text(encoding="utf-8")
            + "scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_build.zig`\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:scripts/zigux/README.md:scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_build.zig`"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        scripts_readme.write_text(
            scripts_readme.read_text(encoding="utf-8")
            + "`zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/abi.h`, and `drivers/tty/hvc/hvc_console.h` stay explicit as adjacent notifier evidence rather than a fifth helper family\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:scripts/zigux/README.md:`zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/abi.h`, and `drivers/tty/hvc/hvc_console.h` stay explicit as adjacent notifier evidence rather than a fifth helper family"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        roadmap_path = tempdir / "Documentation/zigux/phase13-roadmap-traceability.md"
        roadmap_path.write_text(
            roadmap_path.read_text(encoding="utf-8").replace(
                "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep the returned `zigux/Makefile` file distinct from the still-missing `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` names instead of treating that Phase 2-only wrapper file as a materialized shared Phase 13 surface.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep the returned `zigux/Makefile` file distinct from the still-missing `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` names instead of treating that Phase 2-only wrapper file as a materialized shared Phase 13 surface."
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        notifier_gap_path = tempdir / "Documentation/zigux/phase13-notifier-summary-gap.md"
        notifier_gap_path.write_text(
            notifier_gap_path.read_text(encoding="utf-8").replace(
                "Broad Phase 13 reminder work should therefore keep the checker-backed adjacent packet explicit, keep `zigux/Makefile` distinct from the still-missing route names, and keep `zigux/helpers/notifier_chain_view.zig` plus `scripts/zigux/check-phase13-notifier-priority-signal.py` recorded as repo-reality gaps until a future reread proves they returned.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-notifier-summary-gap.md:Broad Phase 13 reminder work should therefore keep the checker-backed adjacent packet explicit, keep `zigux/Makefile` distinct from the still-missing route names, and keep `zigux/helpers/notifier_chain_view.zig` plus `scripts/zigux/check-phase13-notifier-priority-signal.py` recorded as repo-reality gaps until a future reread proves they returned."
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        tests_readme = tempdir / "zigux/tests/README.md"
        tests_readme.write_text(
            tests_readme.read_text(encoding="utf-8").replace(
                "Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:zigux/tests/README.md:Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps."
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        tests_readme.write_text(
            tests_readme.read_text(encoding="utf-8")
            + "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:zigux/tests/README.md:Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        roadmap_path.write_text(
            roadmap_path.read_text(encoding="utf-8")
            + "Older `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay explicit repo-reality gaps instead of the current active devres packet.\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-roadmap-traceability.md:Older `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay explicit repo-reality gaps instead of the current active devres packet."
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8")
            + "`Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:`Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        sequencing_path = tempdir / "Documentation/zigux/phase13-shared-helper-lane-sequencing.md"
        sequencing_path.write_text(
            sequencing_path.read_text(encoding="utf-8").replace(
                "`landlock/syscalls` owns the syscall governance, slice, and helper starter surface through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `security/landlock/syscalls.zig`, while `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-shared-helper-lane-sequencing.md:`landlock/syscalls` owns the syscall governance, slice, and helper starter surface through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `security/landlock/syscalls.zig`, while `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`"
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        matrix_path = tempdir / "Documentation/zigux/phase13-release-coordination-matrix.md"
        matrix_path.write_text(
            matrix_path.read_text(encoding="utf-8").replace(
                "The active shared packet stays contributor-facing and review-first. Helper-local proof remains owned by the `libfs`, `devres`, and `landlock` packets, while notifier evidence stays adjacent release-surface support through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-release-coordination-matrix.md:The active shared packet stays contributor-facing and review-first. Helper-local proof remains owned by the `libfs`, `devres`, and `landlock` packets, while notifier evidence stays adjacent release-surface support through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`."
            in issues
        )
        populate_repo(tempdir)
        checks_run += 1

        sequencing_path.write_text(
            sequencing_path.read_text(encoding="utf-8").replace(
                "- adjacent notifier evidence owns only release-surface truthfulness through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`, not a fifth helper family\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-shared-helper-lane-sequencing.md:- adjacent notifier evidence owns only release-surface truthfulness through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`, not a fifth helper family"
            in issues
        )
        populate_repo(tempdir)
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
