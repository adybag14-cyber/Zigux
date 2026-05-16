#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/review-checklist.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
MAKEFILE_PATH = "zigux/Makefile"

PHASE9_SHARED_PACKET_MARKER = "if the change touches the shared Phase 9 runtime-loader packet"
PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"
PHASE2_BOUNDARY_MARKER = "remain Phase 2 config-surface bridge references"
PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references rather than runtime-pilot evidence"
MAKEFILE_PHASE9_TEST_MARKER = "phase9-test:"
MAKEFILE_SELFTEST_MARKER = "$(PYTHON) scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test"
MAKEFILE_ROUTE_MARKER = """\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-review-checklist-phase-boundaries.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-build-only-surface.py"""

CHECKLIST_REQUIRED_MARKERS = [
    PHASE9_SHARED_PACKET_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    PHASE2_BOUNDARY_MARKER,
    PHASE3_BOUNDARY_MARKER,
]

MAKEFILE_REQUIRED_MARKERS = [
    MAKEFILE_PHASE9_TEST_MARKER,
    MAKEFILE_SELFTEST_MARKER,
    MAKEFILE_ROUTE_MARKER,
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    checklist_path = root / REVIEW_CHECKLIST_PATH
    makefile_path = root / MAKEFILE_PATH
    if not checklist_path.exists():
        failures.append(f"missing_file:{REVIEW_CHECKLIST_PATH}")
    if not makefile_path.exists():
        failures.append(f"missing_file:{MAKEFILE_PATH}")
    if failures:
        return failures

    checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    for marker in CHECKLIST_REQUIRED_MARKERS:
        if marker not in checklist:
            failures.append(f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")

    makefile = read_text(root, MAKEFILE_PATH)
    for marker in MAKEFILE_REQUIRED_MARKERS:
        if marker not in makefile:
            failures.append(f"missing_marker:{MAKEFILE_PATH}:{marker}")

    return failures


def build_fixture_text() -> str:
    return f"""# Zigux Review Checklist

- {PHASE9_SHARED_PACKET_MARKER}
- the shared Phase 9 reminder should also keep the older cross-phase non-owner boundaries explicit:
  {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} {PHASE2_BOUNDARY_MARKER}, while
  {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} {PHASE3_BOUNDARY_MARKER}.
"""


def build_makefile_fixture_text() -> str:
    return f"""phase9-test:
\tcd $(ZIGUX_ROOT) && {MAKEFILE_SELFTEST_MARKER}
\tcd $(ZIGUX_ROOT) && {MAKEFILE_ROUTE_MARKER}
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-build-only-surface.py
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-review-checklist-boundaries-"))
    try:
        fixture_path = base / REVIEW_CHECKLIST_PATH
        makefile_path = base / MAKEFILE_PATH
        write_text(fixture_path, build_fixture_text())
        write_text(makefile_path, build_makefile_fixture_text())
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in CHECKLIST_REQUIRED_MARKERS:
            write_text(fixture_path, build_fixture_text().replace(marker, "", 1))
            write_text(makefile_path, build_makefile_fixture_text())
            expect_failure(base, f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")
            write_text(fixture_path, build_fixture_text())

        for marker in MAKEFILE_REQUIRED_MARKERS:
            write_text(fixture_path, build_fixture_text())
            write_text(makefile_path, build_makefile_fixture_text().replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{MAKEFILE_PATH}:{marker}")
            write_text(makefile_path, build_makefile_fixture_text())

        shutil.rmtree(base / "Documentation", ignore_errors=True)
        expect_failure(base, f"missing_file:{REVIEW_CHECKLIST_PATH}")
        write_text(fixture_path, build_fixture_text())
        write_text(makefile_path, build_makefile_fixture_text())

        shutil.rmtree(base / "zigux", ignore_errors=True)
        expect_failure(base, f"missing_file:{MAKEFILE_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 9 review checklist keeps the older Phase 2 and Phase 3 non-owner boundaries explicit and that the Phase 9 make route reruns that checker."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_ERROR={failure}")
        return 1

    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_CHECKLIST_MARKER_COUNT={len(CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_MAKEFILE_MARKER_COUNT={len(MAKEFILE_REQUIRED_MARKERS)}")
    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
