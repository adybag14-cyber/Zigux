#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")
SECTION_HEADING = "Active product surfaces"
NEXT_HEADING = "Start here"
EXPECTED_LINES = (
    "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.",
    "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.",
)


def extract_active_product_surfaces(root: Path) -> tuple[str, ...]:
    readme_lines = (root / README_PATH).read_text(encoding="utf-8").splitlines()

    try:
        start = readme_lines.index(SECTION_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {SECTION_HEADING}") from exc

    try:
        end = readme_lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {NEXT_HEADING}") from exc

    packet = tuple(
        line
        for line in readme_lines[start + 1 : end]
        if line.strip()
    )
    return packet


def check_active_product_surfaces(root: Path) -> list[str]:
    try:
        packet = extract_active_product_surfaces(root)
    except AssertionError as exc:
        return [str(exc)]

    if packet != EXPECTED_LINES:
        return [
            "active-product-surfaces packet mismatch",
            f"expected:{EXPECTED_LINES!r}",
            f"actual:{packet!r}",
        ]

    return []


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

Start here
- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_active_surfaces_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        errors = check_active_product_surfaces(root)
        if errors:
            raise AssertionError(f"baseline Lane 01 active product surfaces fixture should pass: {errors}")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace("Active product surfaces\n", "", 1),
        )
        errors = check_active_product_surfaces(root)
        if errors != ["missing heading: Active product surfaces"]:
            raise AssertionError(f"unexpected heading error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.\n",
                "",
                1,
            ),
        )
        errors = check_active_product_surfaces(root)
        if not errors or errors[0] != "active-product-surfaces packet mismatch":
            raise AssertionError(f"expected missing-item mismatch, got: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.\n"
                "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.\n",
                "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.\n"
                "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.\n",
                1,
            ),
        )
        errors = check_active_product_surfaces(root)
        if not errors or errors[0] != "active-product-surfaces packet mismatch":
            raise AssertionError(f"expected reorder mismatch, got: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.\n",
                "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.\n"
                "- `Documentation/zigux/phase2-closure.md` is the live closure summary for the broadened Phase 2 tranche.\n",
                1,
            ),
        )
        errors = check_active_product_surfaces(root)
        if not errors or errors[0] != "active-product-surfaces packet mismatch":
            raise AssertionError(f"expected extra-item mismatch, got: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace("Start here\n", "Next steps\n", 1),
        )
        errors = check_active_product_surfaces(root)
        if errors != ["missing heading: Start here"]:
            raise AssertionError(f"unexpected next-heading error: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 Active product surfaces packet remains aligned."
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
    print(f"LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACE_COUNT={len(EXPECTED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
