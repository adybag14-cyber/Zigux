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
    "## Release-Planning Continuation",
    "- Practical rule:",
)

LINKED_PATHS = (
    README_PATH,
    ROADMAP_PATH,
    LEDGER_PATH,
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("Documentation/zigux/freeze-map.md"),
    Path("Documentation/zigux/phase15-freeze-map-governance.md"),
)

README_SECTION_ORDER = ("Rules", "Active product surfaces", "Start here")
ROADMAP_SECTION_ORDER = ("## Purpose", "## Bootstrap Status Note", "## Inputs Reviewed")
LEDGER_SECTION_ORDER = (
    "## Commit Train",
    "## Scope Note",
    "## Release-Planning Continuation",
)


def _read(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def collect_missing_markers(root: Path) -> list[str]:
    readme = _read(root, README_PATH)
    roadmap = _read(root, ROADMAP_PATH)
    ledger = _read(root, LEDGER_PATH)

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


def collect_missing_linked_paths(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in LINKED_PATHS:
        if not (root / rel).exists():
            missing.append(str(rel))
    return missing


def _section_order_error(text: str, expected: tuple[str, ...], label: str) -> str | None:
    indexes: list[int] = []
    for marker in expected:
        try:
            indexes.append(text.index(marker))
        except ValueError:
            return f"{label} missing section marker: {marker}"

    if indexes != sorted(indexes):
        return f"{label} section order mismatch: {' -> '.join(expected)}"
    return None


def collect_order_errors(root: Path) -> list[str]:
    errors: list[str] = []

    readme_error = _section_order_error(_read(root, README_PATH), README_SECTION_ORDER, "readme")
    if readme_error is not None:
        errors.append(readme_error)

    roadmap_error = _section_order_error(
        _read(root, ROADMAP_PATH),
        ROADMAP_SECTION_ORDER,
        "roadmap",
    )
    if roadmap_error is not None:
        errors.append(roadmap_error)

    ledger_error = _section_order_error(
        _read(root, LEDGER_PATH),
        LEDGER_SECTION_ORDER,
        "ledger",
    )
    if ledger_error is not None:
        errors.append(ledger_error)

    return errors


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
- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)
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

## Inputs Reviewed

The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`.
"""


def _sample_ledger() -> str:
    return """# Zigux Alpha Bootstrap Commit Ledger

## Commit Train

25. `docs(zigux): reopen and close broadened Phase 2 tranche`

## Scope Note

- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.
- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.

## Release-Planning Continuation

- Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.
- Practical rule:
"""


def _write_linked_paths(root: Path) -> None:
    _write(root / README_PATH, _sample_readme())
    _write(root / ROADMAP_PATH, _sample_roadmap())
    _write(root / LEDGER_PATH, _sample_ledger())
    _write(root / Path("Documentation/zigux/README.md"), "# docs-root\n")
    _write(root / Path("Documentation/zigux/review-checklist.md"), "# review checklist\n")
    _write(root / Path("Documentation/zigux/freeze-map.md"), "# freeze map\n")
    _write(
        root / Path("Documentation/zigux/phase15-freeze-map-governance.md"),
        "# freeze governance\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_charter_") as tmp_dir:
        root = Path(tmp_dir)
        _write_linked_paths(root)

        if collect_missing_markers(root):
            raise AssertionError("baseline Lane 01 charter fixture should pass marker checks")
        if collect_missing_linked_paths(root):
            raise AssertionError("baseline Lane 01 charter fixture should pass linked-path checks")
        if collect_order_errors(root):
            raise AssertionError("baseline Lane 01 charter fixture should pass order checks")
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
            raise AssertionError(f"unexpected README marker error: {missing}")
        _write(root / README_PATH, _sample_readme())
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
            raise AssertionError(f"unexpected roadmap marker error: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("## Release-Planning Continuation\n\n", "", 1),
        )
        missing = collect_missing_markers(root)
        expected = ["ledger:## Release-Planning Continuation"]
        if missing != expected:
            raise AssertionError(f"unexpected ledger marker error: {missing}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        (root / Path("Documentation/zigux/freeze-map.md")).unlink()
        missing_paths = collect_missing_linked_paths(root)
        expected_paths = ["Documentation/zigux/freeze-map.md"]
        if missing_paths != expected_paths:
            raise AssertionError(f"unexpected linked-path error: {missing_paths}")
        _write(root / Path("Documentation/zigux/freeze-map.md"), "# freeze map\n")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "Rules\n"
                "- Keep product planning and bootstrap artifacts here first.\n"
                "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.\n"
                "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.\n\n"
                "Active product surfaces\n"
                "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.\n"
                "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.\n"
                "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.\n\n",
                "Active product surfaces\n"
                "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.\n"
                "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.\n"
                "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.\n\n"
                "Rules\n"
                "- Keep product planning and bootstrap artifacts here first.\n"
                "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.\n"
                "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.\n\n",
                1,
            ),
        )
        order_errors = collect_order_errors(root)
        expected_order = [
            "readme section order mismatch: Rules -> Active product surfaces -> Start here"
        ]
        if order_errors != expected_order:
            raise AssertionError(f"unexpected README order error: {order_errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "## Purpose\n\n"
                "This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.\n\n"
                "## Bootstrap Status Note\n\n"
                "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.\n\n"
                "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.\n\n"
                "This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.\n\n"
                "## Inputs Reviewed\n\n",
                "## Bootstrap Status Note\n\n"
                "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.\n\n"
                "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.\n\n"
                "This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.\n\n"
                "## Purpose\n\n"
                "This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.\n\n"
                "## Inputs Reviewed\n\n",
                1,
            ),
        )
        order_errors = collect_order_errors(root)
        expected_order = [
            "roadmap section order mismatch: ## Purpose -> ## Bootstrap Status Note -> ## Inputs Reviewed"
        ]
        if order_errors != expected_order:
            raise AssertionError(f"unexpected roadmap order error: {order_errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "## Scope Note\n\n"
                "- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.\n"
                "- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.\n\n"
                "## Release-Planning Continuation\n\n",
                "## Release-Planning Continuation\n\n"
                "## Scope Note\n\n"
                "- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.\n"
                "- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.\n\n",
                1,
            ),
        )
        order_errors = collect_order_errors(root)
        expected_order = [
            "ledger section order mismatch: ## Commit Train -> ## Scope Note -> ## Release-Planning Continuation"
        ]
        if order_errors != expected_order:
            raise AssertionError(f"unexpected ledger order error: {order_errors}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Start here\n", "", 1))
        order_errors = collect_order_errors(root)
        expected_order = ["readme missing section marker: Start here"]
        if order_errors != expected_order:
            raise AssertionError(f"unexpected README missing-section error: {order_errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("## Inputs Reviewed\n\n", "", 1),
        )
        order_errors = collect_order_errors(root)
        expected_order = ["roadmap missing section marker: ## Inputs Reviewed"]
        if order_errors != expected_order:
            raise AssertionError(f"unexpected roadmap missing-section error: {order_errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("- Practical rule:\n", "", 1),
        )
        missing = collect_missing_markers(root)
        expected = ["ledger:- Practical rule:"]
        if missing != expected:
            raise AssertionError(f"unexpected ledger practical-rule error: {missing}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        (root / ROADMAP_PATH).unlink()
        missing_paths = collect_missing_linked_paths(root)
        expected_paths = ["zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"]
        if missing_paths != expected_paths:
            raise AssertionError(f"unexpected roadmap linked-path error: {missing_paths}")
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

    errors = collect_missing_markers(args.root)
    errors.extend(f"missing linked path: {path}" for path in collect_missing_linked_paths(args.root))
    errors.extend(collect_order_errors(args.root))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Lane 01 bootstrap charter alignment check passed.")
    print(f"LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_LINKED_PATH_COUNT={len(LINKED_PATHS)}")
    print(
        "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_README_ORDER="
        + "->".join(README_SECTION_ORDER)
    )
    print(
        "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_ROADMAP_ORDER="
        + "->".join(ROADMAP_SECTION_ORDER)
    )
    print(
        "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_LEDGER_ORDER="
        + "->".join(LEDGER_SECTION_ORDER)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
