#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("Documentation/zigux/README.md")

PHASE12_HEADING = "Phase 12 notes -"
PHASE13_HEADING = "Phase 13 notes -"
PHASE14_HEADING = "Phase 14 notes -"

REQUIRED_MARKERS = (
    "Phase 13 notes - `Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "keep the bounded Phase 13 docs-root packet explicit through the stable contributor-facing handle, the shared sequencing and release companions, the roadmap-traceability note, the shared-summary and notifier-gap notes, and the shipped shared-summary, tests-root alignment, and release-discipline validators instead of leaving the docs root to jump from the Phase 12 release packet straight to the Phase 14 study-only packet.",
    "* the current docs-root Phase 13 reminder packet should stay parked on `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `scripts/zigux/check-phase13-tests-readme-alignment.py`, and `scripts/zigux/validate-phase13-release.py`",
    "* keep the stable contributor-facing handle explicit here too: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` remain the review-first entrypoint for the shared-helper packet",
    "* keep the four roadmap anchors explicit here too: `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c` remain the bounded Phase 13 shared-helper anchors",
    "* keep the helper-local split explicit here too: `libfs` stays mapped through `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`",
    "* `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` keep adjacent notifier evidence explicit from the docs root",
    "* `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`",
    "* `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py` keep the current docs-root Phase 13 reminder packet aligned without widening it into helper-local replay or closure claims.",
)


def _readme_text(root: Path) -> str:
    return (root / README_PATH).read_text(encoding="utf-8")


def collect_missing_markers(root: Path) -> list[str]:
    readme = _readme_text(root)
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in readme:
            missing.append(marker)
    return missing


def section_order_ok(root: Path) -> bool:
    readme = _readme_text(root)
    phase12_idx = readme.find(PHASE12_HEADING)
    phase13_idx = readme.find(PHASE13_HEADING)
    phase14_idx = readme.find(PHASE14_HEADING)
    return -1 not in (phase12_idx, phase13_idx, phase14_idx) and phase12_idx < phase13_idx < phase14_idx


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return "\n".join(
        (
            "# Zigux Documentation",
            PHASE12_HEADING,
            "placeholder phase12",
            "Phase 13 notes - `Documentation/zigux/phase13-contributor-workflow-guide.md` - `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` - `Documentation/zigux/phase13-release-coordination-matrix.md` - `Documentation/zigux/phase13-release-notes-survey.md` - `Documentation/zigux/phase13-roadmap-traceability.md` - `Documentation/zigux/phase13-shared-summary-guard-gap.md` - `Documentation/zigux/phase13-notifier-summary-gap.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` - `scripts/zigux/check-phase13-shared-summary-surfaces.py` - `scripts/zigux/check-phase13-tests-readme-alignment.py` - `scripts/zigux/validate-phase13-release.py` keep the bounded Phase 13 docs-root packet explicit through the stable contributor-facing handle, the shared sequencing and release companions, the roadmap-traceability note, the shared-summary and notifier-gap notes, and the shipped shared-summary, tests-root alignment, and release-discipline validators instead of leaving the docs root to jump from the Phase 12 release packet straight to the Phase 14 study-only packet.",
            "* the current docs-root Phase 13 reminder packet should stay parked on `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `scripts/zigux/check-phase13-tests-readme-alignment.py`, and `scripts/zigux/validate-phase13-release.py` so the docs root matches the same shared helper packet already described by the workflow guide, the release-coordination matrix, the roadmap-traceability note, the shared-summary gap handoff, the notifier-gap note, the scripts-root reminder, and the tests-root reminder.",
            "* keep the stable contributor-facing handle explicit here too: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` remain the review-first entrypoint for the shared-helper packet, while `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, and `Documentation/zigux/phase13-notifier-summary-gap.md` stay the PMO coordination companions for that same entrypoint instead of becoming a second handle of their own.",
            "* keep the four roadmap anchors explicit here too: `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c` remain the bounded Phase 13 shared-helper anchors, while adjacent notifier evidence stays release-surface support rather than a fifth helper family.",
            "* keep the helper-local split explicit here too: `libfs` stays mapped through `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`; `devres` stays mapped through the current slice, survey, planner, checker, helper, and manifest-backed replay packet; `landlock/ruleset` stays mapped through its survey, helper starter, manifest-backed replay, and checker; and `landlock/syscalls` stays mapped through its governance, slice, survey, survey-gap breadcrumb, checker, and helper starter without collapsing those helper-local packets into one generic Phase 13 summary.",
            "* `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` keep adjacent notifier evidence explicit from the docs root without promoting it into a fifth helper family, while `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and `scripts/zigux/check-phase13-notifier-priority-signal.py` stay repo-reality gaps on current `master`.",
            "* `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the returned file explicit as current repo evidence while leaving those route names recorded as repo-reality gaps instead of promoting them into a shipped shared build handle.",
            "* `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py` keep the current docs-root Phase 13 reminder packet aligned without widening it into helper-local replay or closure claims.",
            PHASE14_HEADING,
            "placeholder phase14",
            "",
        )
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase13_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        if collect_missing_markers(root):
            raise AssertionError("baseline Phase 13 docs-root fixture should pass")
        if not section_order_ok(root):
            raise AssertionError("baseline Phase 13 docs-root fixture should keep phase order")
        case_count += 1

        for marker in (
            REQUIRED_MARKERS[0],
            REQUIRED_MARKERS[1],
            REQUIRED_MARKERS[2],
            REQUIRED_MARKERS[3],
            REQUIRED_MARKERS[4],
            REQUIRED_MARKERS[7],
        ):
            _write(root / README_PATH, _sample_readme().replace(marker, "", 1))
            missing = collect_missing_markers(root)
            if missing != [marker]:
                raise AssertionError(f"unexpected missing markers for {marker!r}: {missing}")
            _write(root / README_PATH, _sample_readme())
            case_count += 1

        swapped = _sample_readme().replace(
            f"{PHASE12_HEADING}\nplaceholder phase12\n{PHASE13_HEADING}",
            f"{PHASE13_HEADING}\nplaceholder phase12\n{PHASE12_HEADING}",
            1,
        )
        _write(root / README_PATH, swapped)
        if section_order_ok(root):
            raise AssertionError("section order should fail when Phase 12 and Phase 13 are swapped")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE13_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE13_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 docs-root Phase 13 reminder packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Phase 13 docs-root fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: missing marker: {item}")
        return 1

    if not section_order_ok(args.root):
        print("ERROR: Phase 13 notes packet is not ordered between Phase 12 and Phase 14.")
        return 1

    print("LANE01_DOCS_ROOT_PHASE13_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE13_NOTES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_DOCS_ROOT_PHASE13_NOTES_SECTION_ORDER=Phase12->Phase13->Phase14")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
