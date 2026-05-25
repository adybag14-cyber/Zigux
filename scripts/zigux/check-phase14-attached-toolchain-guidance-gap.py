#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=attached_toolchain_guidance_gap

Fail-closed checker for the current Phase 14 attached-toolchain guidance split.

This guard stays inside the Phase 14 shared-reminder lane. It validates that the
current reminder packet keeps the attached Zig toolchain explicit as a bounded
fallback while the readable Makefile exposes `phase14-validate` only and leaves
the broader `phase14-*` wrapper family as historical packet-local vocabulary.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=attached_toolchain_guidance_gap"

ATTACHED_GUIDANCE_PATH = Path("Documentation/zigux/phase14-attached-toolchain-guidance-gap.md")
SMOKE_SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
PRODUCTIZATION_GAP_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")
SHARED_SMOKE_GAP_PATH = Path("Documentation/zigux/phase14-shared-smoke-current-master-gap.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")

ATTACHED_GUIDANCE_MARKERS = [
    "- lane: `P14-L10`",
    "- status: `current-master reminder truthfulness follow-through`",
    "attached Zig bundle used by this lane still behaves like a usable bounded-check fallback rather than a stale archival assumption",
    "`phase14-validate`",
    "manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides remain optional packet-local escape hatches rather than the primary current rerun path",
    "the scripts-root Phase 14 summary still owns the smallest same-lane reminder repair because it undercounts the returned skbuff stay-in-C guard",
]

SMOKE_SURVEY_MARKERS = [
    "* `PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
    "the current readable route layer still stops at `make -C zigux phase14-validate`",
    "Keep those older wrapper names recorded only as historical packet vocabulary until the same exact readback mode restores the missing broader Phase 14 Makefile routes on current `master`.",
]

RELEASE_BOUNDARY_MARKERS = [
    "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
    "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
    "Keep the attached-toolchain boundary here as historical packet-local vocabulary too, without restating the older `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-*` wrapper triplet as current fallback guidance while the readable Makefile still omits those broader targets.",
]

PRODUCTIZATION_GAP_MARKERS = [
    "The higher-value same-lane task is reminder-surface truthfulness:",
    "the directly readable shared smoke manifest",
    "the readable non-owner Makefile body with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
]

SHARED_SMOKE_GAP_MARKERS = [
    "the returned `phase14-validate` gate",
    "the returned route checker",
    "the returned tests-root reminder checker",
    "the aligned manifest posture",
    "the continued absence of the broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers on current `master`",
]

SCRIPTS_README_MARKERS = [
    "## Phase 14",
    "the current scripts-root shared smoke packet stays reviewable",
    "the readable `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)` chain in `zigux/Makefile`",
    "without implying that manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides are the default current rerun path",
]

MAKEFILE_PRESENT_MARKERS = [
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
    "phase12-smoke:",
    "phase14-validate:",
]

MAKEFILE_ABSENT_MARKERS = [
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
]


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden_marker:{rel.as_posix()}:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    required = [
        ATTACHED_GUIDANCE_PATH,
        SMOKE_SURVEY_PATH,
        RELEASE_BOUNDARY_PATH,
        PRODUCTIZATION_GAP_PATH,
        SHARED_SMOKE_GAP_PATH,
        SCRIPTS_README_PATH,
        MAKEFILE_PATH,
    ]
    for rel in required:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    require_markers(errors, ATTACHED_GUIDANCE_PATH, read_text(root, ATTACHED_GUIDANCE_PATH), ATTACHED_GUIDANCE_MARKERS)
    require_markers(errors, SMOKE_SURVEY_PATH, read_text(root, SMOKE_SURVEY_PATH), SMOKE_SURVEY_MARKERS)
    require_markers(errors, RELEASE_BOUNDARY_PATH, read_text(root, RELEASE_BOUNDARY_PATH), RELEASE_BOUNDARY_MARKERS)
    require_markers(errors, PRODUCTIZATION_GAP_PATH, read_text(root, PRODUCTIZATION_GAP_PATH), PRODUCTIZATION_GAP_MARKERS)
    require_markers(errors, SHARED_SMOKE_GAP_PATH, read_text(root, SHARED_SMOKE_GAP_PATH), SHARED_SMOKE_GAP_MARKERS)
    require_markers(errors, SCRIPTS_README_PATH, read_text(root, SCRIPTS_README_PATH), SCRIPTS_README_MARKERS)

    makefile = read_text(root, MAKEFILE_PATH)
    require_markers(errors, MAKEFILE_PATH, makefile, MAKEFILE_PRESENT_MARKERS)
    require_absent(errors, MAKEFILE_PATH, makefile, MAKEFILE_ABSENT_MARKERS)

    return errors


def fixture_attached_guidance() -> str:
    return "\n".join(["# Phase 14 Attached Toolchain Guidance Gap", "## Scope", *ATTACHED_GUIDANCE_MARKERS, ""])


def fixture_smoke_survey() -> str:
    return "\n".join(["# Phase 14 End-to-End Smoke Survey", *SMOKE_SURVEY_MARKERS, ""])


def fixture_release_boundary() -> str:
    return "\n".join(["# Phase 14 Release Boundary Survey", *RELEASE_BOUNDARY_MARKERS, ""])


def fixture_productization_gap() -> str:
    return "\n".join(["# Phase 14 Productization Gap Survey", *PRODUCTIZATION_GAP_MARKERS, ""])


def fixture_shared_smoke_gap() -> str:
    return "\n".join(["# Phase 14 Shared Smoke Current-Master Gap", *SHARED_SMOKE_GAP_MARKERS, ""])


def fixture_scripts_readme() -> str:
    return "\n".join(["# scripts/zigux", *SCRIPTS_README_MARKERS, ""])


def fixture_makefile() -> str:
    return "\n".join(MAKEFILE_PRESENT_MARKERS) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, ATTACHED_GUIDANCE_PATH, fixture_attached_guidance())
    write_text(root, SMOKE_SURVEY_PATH, fixture_smoke_survey())
    write_text(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
    write_text(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
    write_text(root, SHARED_SMOKE_GAP_PATH, fixture_shared_smoke_gap())
    write_text(root, SCRIPTS_README_PATH, fixture_scripts_readme())
    write_text(root, MAKEFILE_PATH, fixture_makefile())


def remove_marker(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    write_text(root, rel, updated)


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-attached-guidance-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write_fixture_tree(base)
        remove_marker(base, ATTACHED_GUIDANCE_PATH, ATTACHED_GUIDANCE_MARKERS[2])
        if not any(ATTACHED_GUIDANCE_MARKERS[2] in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_SELF_TEST=fail")
            print("expected attached-guidance drift to fail")
            return 1

        write_fixture_tree(base)
        remove_marker(base, RELEASE_BOUNDARY_PATH, RELEASE_BOUNDARY_MARKERS[2])
        if not any(RELEASE_BOUNDARY_MARKERS[2] in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_SELF_TEST=fail")
            print("expected release-boundary archival drift to fail")
            return 1

        write_fixture_tree(base)
        remove_marker(base, SCRIPTS_README_PATH, SCRIPTS_README_MARKERS[2])
        if not any(SCRIPTS_README_MARKERS[2] in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_SELF_TEST=fail")
            print("expected scripts-readme guidance drift to fail")
            return 1

        write_fixture_tree(base)
        write_text(base, MAKEFILE_PATH, fixture_makefile() + "phase14-smoke:\n")
        if not any("phase14-smoke:" in error for error in check(base)):
            print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_SELF_TEST=fail")
            print("expected stale phase14 make route to fail")
            return 1

        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_SELF_TEST=pass")
        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP=fail")
        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_ISSUES_END")
        return 1

    print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP=pass")
    print("PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_REQUIRED_FILE_COUNT=7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
