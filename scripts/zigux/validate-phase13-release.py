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
        "Shared contributor edit loop: reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first",
    ],
    "Documentation/zigux/phase12-phase13-release-handoff.md": [
        "- Phase 13 destination companions: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`",
        "- Phase 13 stays the next release-facing packet only as a contributor-facing and reminder-surface transition.",
    ],
    "Documentation/zigux/phase13-release-packet-index.md": [
        "This note is the compact PMO packet index for the active Phase 13 shared-helper release packet.",
        "- `scripts/zigux/check-phase13-roadmap-traceability.py`",
        "- `scripts/zigux/validate-phase13-release.py`",
        "No shared Phase 13 build handle is returned on current `master`. Keep `make -C zigux phase13-validate`, `make -C zigux phase13`, and `zigux/tests/phase13_build.zig` explicit as repo-reality gaps rather than shared packet evidence.",
        "- `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    ],
    "Documentation/zigux/phase13-release-coordination-matrix.md": [
        "This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.",
        "release-packet index companion: `Documentation/zigux/phase13-release-packet-index.md`",
        "shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.",
    ],
    "Documentation/zigux/phase13-release-notes-survey.md": [
        "This note keeps the shared Phase 13 release summary honest against the live current-`master` packet.",
        "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:",
        "`Documentation/zigux/phase13-release-packet-index.md`",
        "`scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "`Documentation/zigux/phase13-devres-iounmap-planner.md`",
        "`Documentation/zigux/phase13-devres-iomap-planner.md`",
        "`Documentation/zigux/phase13-devres-scatterlist-planner.md`",
        "`scripts/zigux/check-phase13-devres-iounmap-planner.py`",
        "`scripts/zigux/check-phase13-devres-iomap-planner.py`",
        "`scripts/zigux/check-phase13-devres-scatterlist-planner.py`",
        "`zigux/tests/phase13_devres_iounmap_planner.zig`",
        "`zigux/tests/phase13_devres_iounmap_planner_manifest.json`",
        "`zigux/tests/phase13_devres_iomap_planner.zig`",
        "`zigux/tests/phase13_devres_iomap_planner_manifest.json`",
        "`zigux/tests/phase13_devres_scatterlist.zig`",
        "`zigux/tests/phase13_devres_scatterlist_build.zig`",
        "`zigux/tests/phase13_devres_scatterlist_planner_manifest.json`",
        "Fresh direct readback now shows the broader reminder packet is no longer split across the shared reminder surfaces.",
        "Current `master` now also materializes the direct `landlock/syscalls` replay pair through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`.",
        "Current `master` now materializes `zigux/helpers/notifier_chain_view.zig` and `include/zigux/notifier_abi.h` beside `Documentation/zigux/phase13-notifier-list-survey.md`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py` remains the direct notifier companion gap.",
        "Keep `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as the remaining direct repo-reality gap instead of promoting the helper-local packet into a closed shared build handle.",
        "Current `master` also now materializes `scripts/zigux/validate-phase13-release.py`, so keep that shared release-discipline validator explicit beside the shipped shared-summary guard, the stable contributor-facing handle, and the compact packet index while the remaining same-lane follow-through stays narrowed to still-missing direct companions or any future broader reminder drift.",
        "## Exact Checks For This Bounded Step",
        "Those checks confirm the shared-summary surfaces, the tests-root reminder packet, and the release-discipline packet only. They do not turn `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, or `zigux/tests/phase13_build.zig` into shipped Phase 13 route evidence.",
    ],
    "Documentation/zigux/phase13-roadmap-traceability.md": [
        "This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.",
        "- stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface",
        "Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, older direct devres companions, and the still-missing notifier priority-signal companion.",
    ],
    "Documentation/zigux/phase13-notifier-summary-gap.md": [
        "Public current-`master` readback now materializes these adjacent notifier or list surfaces:",
        "- `zigux/helpers/notifier_chain_view.zig`",
        "- `include/zigux/notifier_abi.h`",
        "That closes the older survey-local missing-checker gap, the older release-validator omission inside this adjacent packet, and the older stale gap wording that kept treating the shipped notifier-chain helper and notifier header as absent.",
        "that `zigux/helpers/notifier_chain_view.zig` and `include/zigux/notifier_abi.h` are now part of the shipped adjacent packet",
        "while the missing Phase 13 build-route names and priority-signal checker stay in the repo-reality-gap bucket.",
    ],
    "scripts/zigux/README.md": [
        "- Phase 13 flow - the current scripts-root shared-helper reminder should keep the stable contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, keep the shared-summary and tests-root alignment guards plus the shipped release-discipline validator explicit, and keep the live `libfs`, `devres`, `landlock`, and adjacent notifier packet split truthful without promoting the still-missing Phase 13 Makefile routes into the entrypoint",
        "`scripts/zigux/check-phase13-shared-summary-surfaces.py`, `scripts/zigux/check-phase13-tests-readme-alignment.py`, and `scripts/zigux/validate-phase13-release.py` keep the shared-summary, tests-root alignment, and release-discipline packet explicit from the scripts root without pretending a broader validator-first or convenience-route replay has returned",
        "`Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` keep adjacent notifier evidence explicit from the scripts root without promoting it into a fifth helper family, while `scripts/zigux/check-phase13-notifier-priority-signal.py` stays a repo-reality gap",
    ],
    "zigux/tests/README.md": [
        "Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
        "Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.",
        "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    ],
    "scripts/zigux/check-phase13-roadmap-traceability.py": [
        "\"\"\"Guard the shipped Phase 13 roadmap-traceability note.\"\"\"",
        "print(\"PHASE13_ROADMAP_TRACEABILITY=pass\")",
    ],
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase13-release-notes-survey.md": [
        "- `scripts/zigux/validate-phase13-release.py`",
        "while the still-missing `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and `scripts/zigux/check-phase13-notifier-priority-signal.py` remain separate repo-reality gaps rather than release-facing proof.",
        "the missing notifier-chain helper and notifier header recorded beside the shipped adjacent notifier evidence",
        "the missing validator-first helpers, adjacent notifier-chain helper, adjacent notifier header, and shared build route surfaces stay explicit as repo-reality gaps",
        "- `Documentation/zigux/phase13-landlock-syscalls-survey.md`",
        "- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    ],
    "Documentation/zigux/phase13-notifier-summary-gap.md": [
        "and keep `include/zigux/notifier_abi.h` plus `scripts/zigux/check-phase13-notifier-priority-signal.py` recorded as repo-reality gaps.",
        "while `include/zigux/notifier_abi.h` and the missing Phase 13 build-route names stay in the repo-reality-gap bucket.",
        "- `include/zigux/notifier_abi.h`\n- `zigux/tests/phase13_build.zig`",
    ],
    "scripts/zigux/README.md": [
        "Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`",
        "while `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and `scripts/zigux/check-phase13-notifier-priority-signal.py` stay repo-reality gaps",
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
