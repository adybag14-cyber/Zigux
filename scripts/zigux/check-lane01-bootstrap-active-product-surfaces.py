#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")
SECTION_HEADING = "Active product surfaces"
PREVIOUS_HEADING = "Rules"
NEXT_HEADING = "Start here"
EXPECTED_LINES = (
    "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.",
    "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.",
    "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
)
EXPECTED_LINKED_PATHS = (
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("Documentation/zigux/freeze-map.md"),
    Path("Documentation/zigux/phase15-freeze-map-governance.md"),
    Path("scripts/zigux/check-lane01-bootstrap-charter-alignment.py"),
)


def _read_readme_lines(root: Path) -> list[str]:
    return (root / README_PATH).read_text(encoding="utf-8").splitlines()


def _find_heading(lines: list[str], heading: str, start: int = 0) -> int:
    try:
        return lines.index(heading, start)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {heading}") from exc


def extract_active_product_surfaces(root: Path) -> tuple[str, ...]:
    readme_lines = _read_readme_lines(root)
    start = _find_heading(readme_lines, SECTION_HEADING)
    end = _find_heading(readme_lines, NEXT_HEADING, start + 1)
    return tuple(line for line in readme_lines[start + 1 : end] if line.strip())


def check_active_product_surfaces(root: Path) -> list[str]:
    errors: list[str] = []

    try:
        readme_lines = _read_readme_lines(root)
    except FileNotFoundError:
        return [f"missing file: {README_PATH.as_posix()}"]

    try:
        rules_index = _find_heading(readme_lines, PREVIOUS_HEADING)
        surfaces_first_index = _find_heading(readme_lines, SECTION_HEADING)
        start_here_first_index = _find_heading(readme_lines, NEXT_HEADING)
        surfaces_index = _find_heading(readme_lines, SECTION_HEADING, rules_index + 1)
        start_here_index = _find_heading(readme_lines, NEXT_HEADING, surfaces_index + 1)
    except AssertionError as exc:
        return [str(exc)]

    if not (rules_index < surfaces_first_index < start_here_first_index):
        errors.append("section order mismatch: Rules->ActiveProductSurfaces->StartHere")

    packet = tuple(line for line in readme_lines[surfaces_index + 1 : start_here_index] if line.strip())
    if packet != EXPECTED_LINES:
        errors.extend(
            (
                "active-product-surfaces packet mismatch",
                f"expected:{EXPECTED_LINES!r}",
                f"actual:{packet!r}",
            )
        )

    for linked_path in EXPECTED_LINKED_PATHS:
        if not (root / linked_path).exists():
            errors.append(f"missing linked path: {linked_path.as_posix()}")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

Rules
- Keep product planning and bootstrap artifacts here first.

Active product surfaces
- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.
- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.
- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.
- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.

Start here
- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)
"""


def _write_sample_root(root: Path) -> None:
    _write(root / README_PATH, _sample_readme())
    for linked_path in EXPECTED_LINKED_PATHS:
        _write(root / linked_path, "# placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_active_surfaces_") as tmp_dir:
        root = Path(tmp_dir)
        _write_sample_root(root)

        errors = check_active_product_surfaces(root)
        if errors:
            raise AssertionError(f"baseline Lane 01 active product surfaces fixture should pass: {errors}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Active product surfaces\n", "", 1))
        errors = check_active_product_surfaces(root)
        if errors != ["missing heading: Active product surfaces"]:
            raise AssertionError(f"unexpected heading error: {errors}")
        _write_sample_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.\n",
                "",
                1,
            ),
        )
        errors = check_active_product_surfaces(root)
        if not errors or errors[0] != "active-product-surfaces packet mismatch":
            raise AssertionError(f"expected missing-checker mismatch, got: {errors}")
        _write_sample_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "Rules\n- Keep product planning and bootstrap artifacts here first.\n\nActive product surfaces\n",
                "Rules\n- Keep product planning and bootstrap artifacts here first.\n\nStart here\n- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)\n\nActive product surfaces\n",
                1,
            ),
        )
        errors = check_active_product_surfaces(root)
        if "section order mismatch: Rules->ActiveProductSurfaces->StartHere" not in errors:
            raise AssertionError(f"expected section-order mismatch, got: {errors}")
        _write_sample_root(root)
        case_count += 1

        (root / EXPECTED_LINKED_PATHS[2]).unlink()
        errors = check_active_product_surfaces(root)
        if f"missing linked path: {EXPECTED_LINKED_PATHS[2].as_posix()}" not in errors:
            raise AssertionError(f"expected missing linked path error, got: {errors}")
        _write_sample_root(root)
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Start here\n", "Next steps\n", 1))
        errors = check_active_product_surfaces(root)
        if errors != ["missing heading: Start here"]:
            raise AssertionError(f"unexpected next-heading error: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 Active product surfaces packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Lane 01 README fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_active_product_surfaces(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Lane 01 bootstrap Active product surfaces check passed.")
    print(f"LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_BULLET_COUNT={len(EXPECTED_LINES)}")
    print("LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SECTION_ORDER=Rules->ActiveProductSurfaces->StartHere")
    print(f"LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_LINKED_PATH_COUNT={len(EXPECTED_LINKED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
