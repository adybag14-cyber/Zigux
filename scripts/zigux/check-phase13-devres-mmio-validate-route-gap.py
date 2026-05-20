#!/usr/bin/env python3
"""Guard the current Phase 13 devres MMIO validate-route gap note."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase13-devres-mmio-validate-route-gap.md")
README_PATH = Path("scripts/zigux/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")
TRACEABILITY_PATH = Path("Documentation/zigux/phase13-roadmap-traceability.md")
LANE_PATH = Path("Documentation/zigux/phase13-shared-helper-lane-sequencing.md")
SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
MMIO_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-mmio-packet.py")

REQUIRED_FILES = [
    NOTE_PATH,
    README_PATH,
    MAKEFILE_PATH,
    TRACEABILITY_PATH,
    LANE_PATH,
    SLICE_PATH,
    SURVEY_PATH,
    MMIO_CHECKER_PATH,
]

NOTE_MARKERS = [
    "# Phase 13 devres MMIO Validate-Route Gap",
    "`scripts/zigux/check-phase13-devres-mmio-packet.py`",
    "`zigux/Makefile` is present again on `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`.",
    "`scripts/zigux/validate-phase13-release.py`",
    "`scripts/zigux/check-phase13-devres-packet.py`",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
    "`zigux/tests/phase13_devres.zig`",
    "`zigux/tests/phase13_devres_reviewability.zig`",
    "`zigux/tests/phase13_devres_boundary_evidence.zig`",
    "`zigux/tests/phase13_devres_manifest.json`",
    "`zigux/tests/phase13_build.zig`",
]

README_MARKERS = [
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
    "current `master` still does not materialize `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, and `include/zigux/notifier_abi.h`, so treat those validator-first, build, helper, header, and notifier-route companions as repo-reality gaps rather than direct scripts-root evidence",
]

TRACEABILITY_MARKERS = [
    "the historically named `scripts/zigux/check-phase13-devres-mmio-packet.py`",
    "The `check-phase13-devres-mmio-packet.py` filename now persists as a historical handle, but on current `master` the checker fail-closes the narrower DMA-boundary, planner, and scatterlist packet rather than the older direct MMIO replay.",
    "- `make -C zigux phase13-validate`",
    "- `make -C zigux phase13`",
]

LANE_MARKERS = [
    "`scripts/zigux/check-phase13-devres-mmio-packet.py`",
    "do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence",
]

SLICE_MARKERS = [
    "`lib/devres.zig` and `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` now provide one pure helper-first `dmam_alloc_coherent()` planning surface, while the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker remain repo-reality gaps",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py` stays in the same repo-reality gaps bucket beside that broader direct helper packet",
]

SURVEY_MARKERS = [
    "current `master` still does not ship the broader direct helper packet that older Phase 13 lane memory described",
    "current `master` does not ship `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check-phase13-devres-packet-alignment.py`.",
]

MMIO_CHECKER_MARKERS = [
    "SURVEY_PATH = Path(\"Documentation/zigux/phase13-devres-survey.md\")",
    "PLANNER_NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md\")",
    "SCATTERLIST_SLICE_PATH = Path(\"Documentation/zigux/phase13-devres-scatterlist-slice.md\")",
    "PHASE13_DEVRES_MMIO_PACKET=pass",
]


def read_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"missing_file:{relpath.as_posix()}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: Path, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_missing(text: str, markers: list[str], label: str) -> list[str]:
    return [f"missing_marker:{label}:{marker}" for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relpath in REQUIRED_FILES:
        if not (root / relpath).exists():
            issues.append(f"missing_file:{relpath.as_posix()}")
    if issues:
        return issues

    issues.extend(collect_missing(read_text(root, NOTE_PATH), NOTE_MARKERS, NOTE_PATH.as_posix()))
    issues.extend(collect_missing(read_text(root, README_PATH), README_MARKERS, README_PATH.as_posix()))
    issues.extend(collect_missing(read_text(root, TRACEABILITY_PATH), TRACEABILITY_MARKERS, TRACEABILITY_PATH.as_posix()))
    issues.extend(collect_missing(read_text(root, LANE_PATH), LANE_MARKERS, LANE_PATH.as_posix()))
    issues.extend(collect_missing(read_text(root, SLICE_PATH), SLICE_MARKERS, SLICE_PATH.as_posix()))
    issues.extend(collect_missing(read_text(root, SURVEY_PATH), SURVEY_MARKERS, SURVEY_PATH.as_posix()))
    issues.extend(collect_missing(read_text(root, MMIO_CHECKER_PATH), MMIO_CHECKER_MARKERS, MMIO_CHECKER_PATH.as_posix()))

    makefile_text = read_text(root, MAKEFILE_PATH)
    if "phase13-validate" in makefile_text:
        issues.append("unexpected_route:zigux/Makefile:phase13-validate")
    if "\nphase13:" in makefile_text or ".PHONY: phase13" in makefile_text:
        issues.append("unexpected_route:zigux/Makefile:phase13")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP=fail")
    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    writes = {
        NOTE_PATH: "\n".join(NOTE_MARKERS) + "\n",
        README_PATH: "\n".join(README_MARKERS) + "\n",
        MAKEFILE_PATH: "PHONY += phase11-validate\n\nphase11-validate:\n\t@true\n",
        TRACEABILITY_PATH: "\n".join(TRACEABILITY_MARKERS) + "\n",
        LANE_PATH: "\n".join(LANE_MARKERS) + "\n",
        SLICE_PATH: "\n".join(SLICE_MARKERS) + "\n",
        SURVEY_PATH: "\n".join(SURVEY_MARKERS) + "\n",
        MMIO_CHECKER_PATH: "\n".join(MMIO_CHECKER_MARKERS) + "\n",
    }
    for relpath, content in writes.items():
        write_text(root, relpath, content)


def expect_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        raise AssertionError(f"{label}: got={issues!r} want={expected!r}")


def run_self_test() -> int:
    checks_run = 0
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-devres-mmio-validate-route-gap-"))
    try:
        populate_repo(tempdir)
        expect_only(collect_issues(tempdir), [], "baseline")
        checks_run += 1

        populate_repo(tempdir)
        (tempdir / NOTE_PATH).unlink()
        expect_only(
            collect_issues(tempdir),
            [f"missing_file:{NOTE_PATH.as_posix()}"],
            "missing_note",
        )
        checks_run += 1

        populate_repo(tempdir)
        write_text(
            tempdir,
            NOTE_PATH,
            "\n".join(marker for marker in NOTE_MARKERS if marker != "`scripts/zigux/check-phase13-devres-packet-alignment.py`") + "\n",
        )
        expect_only(
            collect_issues(tempdir),
            [f"missing_marker:{NOTE_PATH.as_posix()}:`scripts/zigux/check-phase13-devres-packet-alignment.py`"],
            "missing_note_marker",
        )
        checks_run += 1

        populate_repo(tempdir)
        write_text(
            tempdir,
            TRACEABILITY_PATH,
            "\n".join(marker for marker in TRACEABILITY_MARKERS if marker != "- `make -C zigux phase13-validate`") + "\n",
        )
        expect_only(
            collect_issues(tempdir),
            [f"missing_marker:{TRACEABILITY_PATH.as_posix()}:- `make -C zigux phase13-validate`"],
            "missing_traceability_gap_marker",
        )
        checks_run += 1

        populate_repo(tempdir)
        write_text(tempdir, MAKEFILE_PATH, "phase13-validate:\n\t@true\n")
        expect_only(
            collect_issues(tempdir),
            ["unexpected_route:zigux/Makefile:phase13-validate"],
            "unexpected_make_route",
        )
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP=pass")
    print(f"PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
