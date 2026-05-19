#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")
ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
LEDGER_PATH = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

README_MARKERS = (
    "`zigux-alpha` is the Zigux bootstrap workspace.",
    "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.",
    "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "`Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
    "[Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
    "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
)

ROADMAP_MARKERS = (
    "## Bootstrap Status Note",
    "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.",
    "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.",
    "starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.",
)

LEDGER_MARKERS = (
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    "## Scope Note",
    "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
    "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
)


def collect_missing_markers(root: Path) -> list[str]:
    readme = (root / README_PATH).read_text(encoding="utf-8")
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    ledger = (root / LEDGER_PATH).read_text(encoding="utf-8")

    missing: list[str] = []
    for marker in README_MARKERS:
        if marker not in readme:
            missing.append(f"readme:{marker}")
    for marker in ROADMAP_MARKERS:
        if marker not in roadmap:
            missing.append(f"roadmap:{marker}")
    for marker in LEDGER_MARKERS:
        if marker not in ledger:
            missing.append(f"ledger:{marker}")
    return missing


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

Rules
- Keep product planning and bootstrap artifacts here first.
- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.
- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.

Active product surfaces
- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.
- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.

Start here
- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)
- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)
"""


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Purpose

This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.

## Bootstrap Status Note

This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.

For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.

This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.
"""


def _sample_ledger() -> str:
    return """# Zigux Alpha Bootstrap Commit Ledger

25. `docs(zigux): reopen and close broadened Phase 2 tranche`

## Scope Note

- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.
- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_charter_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())
        _write(root / ROADMAP_PATH, _sample_roadmap())
        _write(root / LEDGER_PATH, _sample_ledger())

        if collect_missing_markers(root):
            raise AssertionError("baseline Lane 01 charter fixture should pass")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = [
            "readme:Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane."
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for README rule case: {missing}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = [
            "readme:The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth."
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for README ledger-scope case: {missing}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = [
            "readme:`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet."
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for README guard case: {missing}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = [
            "readme:[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)"
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for README link case: {missing}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("## Bootstrap Status Note\n\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap:## Bootstrap Status Note"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for roadmap heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = [
            "roadmap:confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`."
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for roadmap status note case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / LEDGER_PATH, _sample_ledger().replace("## Scope Note\n\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["ledger:## Scope Note"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for ledger heading case: {missing}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = [
            "ledger:Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands."
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for ledger follow-through case: {missing}")
        case_count += 1

    print("LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 zigux-alpha charter packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the zigux-alpha charter files",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Lane 01 charter fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    print("Lane 01 bootstrap charter alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())