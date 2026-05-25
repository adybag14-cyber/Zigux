#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")
DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
CHARTER_GUARD_PATH = Path("scripts/zigux/check-lane01-bootstrap-charter-alignment.py")

RULES_HEADING = "Rules"
SECTION_HEADING = "Active product surfaces"
NEXT_HEADING = "Start here"
DOCS_ROOT_IDENTITY_MARKER = "product documentation root for Zigux"

EXPECTED_LINES = (
    "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.",
    "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.",
    "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
)

REQUIRED_LINKED_PATHS = (
    DOCS_ROOT_PATH,
    REVIEW_CHECKLIST_PATH,
    FREEZE_MAP_PATH,
    FREEZE_GOVERNANCE_PATH,
    CHARTER_GUARD_PATH,
)


def _read_lines(root: Path) -> list[str]:
    return (root / README_PATH).read_text(encoding="utf-8").splitlines()


def extract_active_product_surfaces(root: Path) -> tuple[str, ...]:
    readme_lines = _read_lines(root)

    try:
        rules_index = readme_lines.index(RULES_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {RULES_HEADING}") from exc

    try:
        start = readme_lines.index(SECTION_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {SECTION_HEADING}") from exc

    try:
        end = readme_lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {NEXT_HEADING}") from exc

    if not rules_index < start < end:
        raise AssertionError(
            f"section-order mismatch: expected {RULES_HEADING}->{SECTION_HEADING}->{NEXT_HEADING}"
        )

    return tuple(line for line in readme_lines[start + 1 : end] if line.strip())


def check_active_product_surfaces(root: Path) -> list[str]:
    errors: list[str] = []

    try:
        packet = extract_active_product_surfaces(root)
    except AssertionError as exc:
        return [str(exc)]

    if packet != EXPECTED_LINES:
        errors.extend(
            [
                "active-product-surfaces packet mismatch",
                f"expected:{EXPECTED_LINES!r}",
                f"actual:{packet!r}",
            ]
        )

    for required_path in REQUIRED_LINKED_PATHS:
        candidate = root / required_path
        if not candidate.is_file():
            errors.append(f"missing linked route: {required_path.as_posix()}")

    docs_root = root / DOCS_ROOT_PATH
    if docs_root.is_file():
        docs_root_text = docs_root.read_text(encoding="utf-8")
        if DOCS_ROOT_IDENTITY_MARKER not in docs_root_text:
            errors.append(
                "docs-root identity mismatch: missing `product documentation root for Zigux` marker"
            )

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


def _sample_docs_root() -> str:
    return "# Zigux Documentation This directory is the product documentation root for Zigux.\n"


def _write_current_like_root(root: Path) -> None:
    _write(root / README_PATH, _sample_readme())
    _write(root / DOCS_ROOT_PATH, _sample_docs_root())
    for relative_path in (
        REVIEW_CHECKLIST_PATH,
        FREEZE_MAP_PATH,
        FREEZE_GOVERNANCE_PATH,
        CHARTER_GUARD_PATH,
    ):
        _write(root / relative_path, "# placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_active_surfaces_") as tmp_dir:
        root = Path(tmp_dir)
        _write_current_like_root(root)

        errors = check_active_product_surfaces(root)
        if errors:
            raise AssertionError(f"baseline Lane 01 active product surfaces fixture should pass: {errors}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Rules\n", "Guidance\n", 1))
        errors = check_active_product_surfaces(root)
        if errors != ["missing heading: Rules"]:
            raise AssertionError(f"unexpected rules-heading error: {errors}")
        _write_current_like_root(root)
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
            raise AssertionError(f"expected packet mismatch for reordered bullets, got: {errors}")
        _write_current_like_root(root)
        case_count += 1

        (root / FREEZE_GOVERNANCE_PATH).unlink()
        errors = check_active_product_surfaces(root)
        if errors != [f"missing linked route: {FREEZE_GOVERNANCE_PATH.as_posix()}"]:
            raise AssertionError(f"unexpected linked-route error: {errors}")
        _write_current_like_root(root)
        case_count += 1

        _write(root / DOCS_ROOT_PATH, "# Zigux Documentation\n")
        errors = check_active_product_surfaces(root)
        expected = [
            "docs-root identity mismatch: missing `product documentation root for Zigux` marker"
        ]
        if errors != expected:
            raise AssertionError(f"unexpected docs-root identity error: {errors}")
        _write_current_like_root(root)
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

    print("LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES=pass")
    print(f"LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_BULLET_COUNT={len(EXPECTED_LINES)}")
    print("LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SECTION_ORDER=Rules->ActiveProductSurfaces->StartHere")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
