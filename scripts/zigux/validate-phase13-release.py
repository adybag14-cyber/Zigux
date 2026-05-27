#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_MARKERS = {
    "Documentation/zigux/phase13-contributor-workflow-guide.md": [
        "stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`",
        "Degraded-read fallback rule: if local checkout access or authenticated blob reads are unavailable, reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and only the exact helper-local Phase 13 note you are touching through authenticated GitHub reads first and raw GitHub fallback second, then keep any still-absent route or helper in the repo-reality-gap bucket instead of promoting it into shipped evidence.",
        "Shared contributor edit loop: reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first, update at most one shared reminder surface plus the smallest helper-local packet note in the same change, rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py`, and keep any absent route, replay, or helper recorded as a repo-reality gap instead of promoted shipped evidence.",
    ],
    "Documentation/zigux/phase13-release-coordination-matrix.md": [
        "This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.",
        "shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.",
        "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`",
    ],
    "Documentation/zigux/phase13-release-notes-survey.md": [
        "This note keeps the shared Phase 13 release summary honest against the live current-`master` packet.",
        "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:",
        "`scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "`Documentation/zigux/phase13-devres-iounmap-planner.md`",
        "`Documentation/zigux/phase13-devres-iomap-planner.md`",
        "`scripts/zigux/check-phase13-devres-iounmap-planner.py`",
        "`scripts/zigux/check-phase13-devres-iomap-planner.py`",
        "`zigux/tests/phase13_devres_iounmap_planner.zig`",
        "`zigux/tests/phase13_devres_iounmap_planner_manifest.json`",
        "`zigux/tests/phase13_devres_iomap_planner.zig`",
        "`zigux/tests/phase13_devres_iomap_planner_manifest.json`",
        "Fresh direct readback now shows the broader reminder packet is no longer split across the shared reminder surfaces.",
        "The still-missing direct Landlock syscall replay companions `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` remain separate repo-reality gaps rather than shipped evidence.",
        "Current `master` now also materializes `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, so keep the returned Landlock ruleset survey, syscall breadcrumb, and checker surfaces explicit beside the still-missing direct ruleset ownership and slice notes plus the direct syscall replay companions rather than listing those returned helper-local surfaces as release-facing gaps.",
        "Current `master` also now materializes `scripts/zigux/validate-phase13-release.py`, so keep that shared release-discipline validator explicit beside the shipped shared-summary guard and the stable contributor-facing handle while the remaining same-lane follow-through stays narrowed to still-missing direct companions or any future broader reminder drift.",
    ],
    "Documentation/zigux/phase13-roadmap-traceability.md": [
        "This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.",
        "- stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface",
        "`Documentation/zigux/phase13-devres-iomap-planner.md`",
        "`scripts/zigux/check-phase13-devres-iomap-planner.py`",
        "`zigux/tests/phase13_devres_iomap_planner.zig`",
        "`zigux/tests/phase13_devres_iomap_planner_manifest.json`",
        "Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, still-missing direct Landlock syscall companions, older direct devres companions, and missing notifier-chain companion.",
        "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`",
    ],
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md": [
        "shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`",
        "`landlock/ruleset` keeps the shipped survey, helper starter, direct replay, manifest-backed packet, and dedicated checker explicit through `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, while `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, the shared `zigux/tests/phase13_build.zig` route, and broader tree plus hierarchy state stay recorded as repo-reality gaps on current `master`",
        "do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence",
        "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`",
    ],
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md": [
        "- `scripts/zigux/check-phase13-tests-readme-alignment.py`",
        "- `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "keep `scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit as the shipped shared-summary guard beside that stable handle",
        "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`",
    ],
    "Documentation/zigux/phase13-shared-summary-guard-gap.md": [
        "This note records the closure of the old missing-checker gap.",
        "The shipped guard is `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`.",
        "What remains open inside this shared-subsystems lane has narrowed again: `Documentation/zigux/phase13-release-notes-survey.md` no longer carries the older tests-root validator-gap claim, so the stable contributor-facing handle and the broader release-facing reminder now agree that `scripts/zigux/validate-phase13-release.py` is shipped current-`master` release-discipline support. Keep `Documentation/zigux/phase13-libfs-survey.md` and `zigux/tests/phase13_libfs_addressability.zig` recorded as repo-reality gaps while treating the next same-lane follow-through as a fresh reread for any remaining broader reminder drift or checker-local exactness miss.",
    ],
    "scripts/zigux/README.md": [
        "- Phase 13 flow - the current scripts-root shared-helper reminder should keep the stable contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, keep the shared-summary and tests-root alignment guards plus the shipped release-discipline validator explicit, and keep the live `libfs`, `devres`, `landlock`, and adjacent notifier packet split truthful without promoting the still-missing Phase 13 Makefile routes into the entrypoint",
        "`scripts/zigux/check-phase13-shared-summary-surfaces.py`, `scripts/zigux/check-phase13-tests-readme-alignment.py`, and `scripts/zigux/validate-phase13-release.py` keep the shared-summary, tests-root alignment, and release-discipline packet explicit from the scripts root without pretending a broader validator-first or convenience-route replay has returned",
        "`Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `include/zigux/abi.h`, and `drivers/tty/hvc/hvc_console.h` keep adjacent notifier evidence explicit from the scripts root without promoting it into a fifth helper family, while `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and `scripts/zigux/check-phase13-notifier-priority-signal.py` stay repo-reality gaps",
    ],
    "zigux/tests/README.md": [
        "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
        "Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.",
        "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    ],
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase13-release-notes-survey.md": [
        "- `scripts/zigux/validate-phase13-release.py`",
        "But the whole broader reminder packet is still not fully aligned on that wider set: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still stop at the older direct DMA-boundary plus `dmam_alloc_coherent()` and scatterlist subset and do not yet mirror the helper-first `devm_iounmap()` or `devm_of_iomap()` planner note-and-manifest pairings.",
        "- `Documentation/zigux/phase13-landlock-syscalls-survey.md`",
        "- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    ],
    "Documentation/zigux/phase13-shared-summary-guard-gap.md": [
        "That closes the older scripts-root reminder gap too, so the next same-lane follow-through should stay parked until a fresh reread identifies a new one-file drift across the broader Phase 13 reminder packet.",
        "What remains open inside this shared-subsystems lane is therefore narrower again: current direct readback still returns missing for `Documentation/zigux/phase13-libfs-survey.md` and `zigux/tests/phase13_libfs_addressability.zig`, but the remaining broader shared reminder drift has contracted to one stale scripts-root repo-reality-gap sentence that still lists returned `scripts/zigux/validate-phase13-release.py` as missing even though the same Phase 13 scripts-root section otherwise keeps that validator explicit as shipped release-discipline support.",
    ],
    "scripts/zigux/README.md": [
        "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
    ],
    "zigux/tests/README.md": [
        "Keep `make -C zigux phase13-validate` as the stable contributor-facing handle until the shared build companion lands",
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
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-release-validator-"))
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
        print("PHASE13_RELEASE_VALIDATOR_SELF_TEST=pass")
        print(f"PHASE13_RELEASE_VALIDATOR_SELF_TEST_CASE_COUNT={total_cases}")
        return 0
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 13 release-planning reminder packet across docs, scripts, and tests surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in fixture self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE13_RELEASE_VALIDATOR=fail")
        print("PHASE13_RELEASE_VALIDATOR_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE13_RELEASE_VALIDATOR_FAILURES_END")
        return 1

    print("PHASE13_RELEASE_VALIDATOR=pass")
    print(f"PHASE13_RELEASE_VALIDATOR_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE13_RELEASE_VALIDATOR_MARKER_COUNT=" f"{sum(len(v) for v in REQUIRED_MARKERS.values())}")
    print("PHASE13_RELEASE_VALIDATOR_FORBIDDEN_COUNT=" f"{sum(len(v) for v in FORBIDDEN_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
