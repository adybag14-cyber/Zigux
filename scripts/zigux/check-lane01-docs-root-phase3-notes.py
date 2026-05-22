#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_ROOT_README = Path("Documentation/zigux/README.md")

PHASE3_MARKERS = (
    "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-errptr-xarray-slice.md` - `Documentation/zigux/phase3-xarray-slot-slice.md` - `Documentation/zigux/phase3-policy-slice.md`",
    "`scripts/zigux/check-phase3-dev-t-starter-packet.py`",
    "`scripts/zigux/validate-phase3.py`",
    "`zigux/helpers/xarray_slot_view.zig`",
    "`zigux/tests/phase3_low_level_wrappers_build.zig` keep the bounded Phase 3 docs-root packet explicit through the returned starter, helper, validator-support, shared-reminder, export/UAPI, header-family, manifest, catalog, low-level-wrapper, and layout-replay surfaces instead of leaving the docs root narrower than the current-tree packet or widening it into broader shared replay claims.",
    "* the current docs-root Phase 3 reminder packet should stay parked on `Documentation/zigux/phase3-abi-slice.md`",
    "* current `master` directly serves the focused `err_ptr` / `xarray` helper packet through `zigux/helpers/err_ptr.zig`",
    "* current `master` also directly serves `Documentation/zigux/phase3-validator-support-surface.md`",
    "* current `master` directly serves the starter export shim, the version-only and `dev_t` starter UAPI companions",
    "* current `master` also directly serves the helper-local policy packet through `Documentation/zigux/phase3-policy-slice.md`",
    "* `python3 scripts/zigux/validate-phase3.py`, `python3 scripts/zigux/validate-phase3-validator-support-surface.py`",
)

SECTION_SEQUENCE = (
    "Phase 2 notes -",
    "Phase 3 notes -",
    "Phase 5 notes -",
)


def collect_missing_markers(root: Path) -> list[str]:
    readme = (root / DOCS_ROOT_README).read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in PHASE3_MARKERS:
        if marker not in readme:
            missing.append(marker)
    return missing


def phase3_heading_count(root: Path) -> int:
    readme = (root / DOCS_ROOT_README).read_text(encoding="utf-8")
    return readme.count("Phase 3 notes -")


def section_order_ok(root: Path) -> bool:
    readme = (root / DOCS_ROOT_README).read_text(encoding="utf-8")
    positions: list[int] = []
    for marker in SECTION_SEQUENCE:
        pos = readme.find(marker)
        if pos == -1:
            return False
        positions.append(pos)
    return positions == sorted(positions)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_root_readme() -> str:
    return """# Zigux Documentation This directory is the product documentation root for Zigux.
Phase 2 notes - current packet anchor
Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-errptr-xarray-slice.md` - `Documentation/zigux/phase3-xarray-slot-slice.md` - `Documentation/zigux/phase3-policy-slice.md`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `scripts/zigux/validate-phase3.py`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig` keep the bounded Phase 3 docs-root packet explicit through the returned starter, helper, validator-support, shared-reminder, export/UAPI, header-family, manifest, catalog, low-level-wrapper, and layout-replay surfaces instead of leaving the docs root narrower than the current-tree packet or widening it into broader shared replay claims.
* the current docs-root Phase 3 reminder packet should stay parked on `Documentation/zigux/phase3-abi-slice.md`
* current `master` directly serves the focused `err_ptr` / `xarray` helper packet through `zigux/helpers/err_ptr.zig`
* current `master` also directly serves `Documentation/zigux/phase3-validator-support-surface.md`
* current `master` directly serves the starter export shim, the version-only and `dev_t` starter UAPI companions
* current `master` also directly serves the helper-local policy packet through `Documentation/zigux/phase3-policy-slice.md`
* `python3 scripts/zigux/validate-phase3.py`, `python3 scripts/zigux/validate-phase3-validator-support-surface.py`
Phase 5 notes - current packet anchor
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase3_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_ROOT_README, _sample_docs_root_readme())

        if collect_missing_markers(root):
            raise AssertionError("baseline docs-root Phase 3 fixture should pass")
        if not section_order_ok(root):
            raise AssertionError("baseline docs-root Phase 3 section order should pass")
        if phase3_heading_count(root) != 1:
            raise AssertionError("baseline docs-root Phase 3 heading count should be one")
        case_count += 1

        for marker in (
            PHASE3_MARKERS[0],
            PHASE3_MARKERS[4],
            PHASE3_MARKERS[6],
            PHASE3_MARKERS[7],
            PHASE3_MARKERS[8],
            PHASE3_MARKERS[10],
        ):
            _write(root / DOCS_ROOT_README, _sample_docs_root_readme().replace(marker, "", 1))
            missing = collect_missing_markers(root)
            if missing != [marker]:
                raise AssertionError(f"unexpected missing markers for case {marker!r}: {missing}")
            _write(root / DOCS_ROOT_README, _sample_docs_root_readme())
            case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_docs_root_readme().replace(
                "Phase 2 notes - current packet anchor\nPhase 3 notes -",
                "Phase 3 notes -\nPhase 2 notes - current packet anchor",
                1,
            ),
        )
        if section_order_ok(root):
            raise AssertionError("out-of-order Phase 3 packet should fail section-order validation")
        _write(root / DOCS_ROOT_README, _sample_docs_root_readme())
        case_count += 1

        _write(root / DOCS_ROOT_README, _sample_docs_root_readme() + "Phase 3 notes - duplicate\n")
        if phase3_heading_count(root) != 2:
            raise AssertionError("duplicate Phase 3 heading should be counted")
        case_count += 1

    print("LANE01_DOCS_ROOT_PHASE3_NOTES_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_PHASE3_NOTES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 docs-root Phase 3 reminder packet remains aligned."
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
        help="exercise the checker against synthetic docs-root Phase 3 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for marker in missing:
            print(f"LANE01_DOCS_ROOT_PHASE3_NOTES_MISSING={marker}")
        return 1

    count = phase3_heading_count(args.root)
    if count != 1:
        print(f"LANE01_DOCS_ROOT_PHASE3_NOTES_HEADING_COUNT={count}")
        return 1

    if not section_order_ok(args.root):
        print("LANE01_DOCS_ROOT_PHASE3_NOTES_SECTION_ORDER=fail")
        return 1

    print("LANE01_DOCS_ROOT_PHASE3_NOTES=pass")
    print(f"LANE01_DOCS_ROOT_PHASE3_NOTES_REQUIRED_MARKER_COUNT={len(PHASE3_MARKERS)}")
    print(f"LANE01_DOCS_ROOT_PHASE3_NOTES_HEADING_COUNT={count}")
    print(f"LANE01_DOCS_ROOT_PHASE3_NOTES_SECTION_COUNT={len(SECTION_SEQUENCE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
