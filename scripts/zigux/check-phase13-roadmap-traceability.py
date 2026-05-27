#!/usr/bin/env python3
"""Guard the shipped Phase 13 roadmap-traceability note."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


ROADMAP_NOTE = "Documentation/zigux/phase13-roadmap-traceability.md"

REQUIRED_MARKERS = [
    "This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.",
    "Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche bounded to four Linux anchors:",
    "- stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
    "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface",
    "`Documentation/zigux/phase13-devres-iomap-planner.md`",
    "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`",
    "direct replay and direct reviewability companions through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, older direct devres companions, and missing notifier-chain companion.",
    "- `zigux/helpers/notifier_chain_view.zig`",
]

FORBIDDEN_MARKERS = [
    "keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` framed as repo-reality gaps until current `master` materializes them again.",
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
        source_text = source_note.read_text(encoding="utf-8")
        write_text(tempdir, ROADMAP_NOTE, source_text)
        assert collect_issues(tempdir) == []
        checks_run += 1

        note_path = tempdir / ROADMAP_NOTE
        note_path.write_text(
            source_text.replace(
                "direct replay and direct reviewability companions through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
                "direct reviewability companions through `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:direct replay and direct reviewability companions through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`"
            in issues
        )
        checks_run += 1

        write_text(
            tempdir,
            ROADMAP_NOTE,
            source_text.replace(
                "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
                "`zigux/tests/phase13_landlock_syscalls_manifest_missing.json`",
            ),
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:`zigux/tests/phase13_landlock_syscalls_manifest.json`"
            in issues
        )
        checks_run += 1

        write_text(
            tempdir,
            ROADMAP_NOTE,
            source_text.replace(
                "Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, older direct devres companions, and missing notifier-chain companion.",
                "Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, still-missing direct Landlock syscall companions, older direct devres companions, and missing notifier-chain companion.",
                1,
            ),
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-roadmap-traceability.md:Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, older direct devres companions, and missing notifier-chain companion."
            in issues
        )
        checks_run += 1

        write_text(tempdir, ROADMAP_NOTE, source_text + FORBIDDEN_MARKERS[0] + "\n")
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-roadmap-traceability.md:" + FORBIDDEN_MARKERS[0]
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
    print(f"PHASE13_ROADMAP_TRACEABILITY_FORBIDDEN_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
