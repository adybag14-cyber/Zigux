#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")
REQUIRED_FILES = (
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("Documentation/zigux/freeze-map.md"),
    Path("Documentation/zigux/phase15-freeze-map-governance.md"),
    Path("scripts/zigux/check-lane01-bootstrap-charter-alignment.py"),
)
ACTIVE_PRODUCT_SURFACE_LINES = (
    "- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.",
    "- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.",
    "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
)


def _find_section_order(readme: str) -> str:
    rules_index = readme.find("\nRules\n")
    active_index = readme.find("\nActive product surfaces\n")
    start_here_index = readme.find("\nStart here\n")
    if rules_index == -1:
        raise ValueError("missing heading: Rules")
    if active_index == -1:
        raise ValueError("missing heading: Active product surfaces")
    if start_here_index == -1:
        raise ValueError("missing heading: Start here")
    if not (rules_index < active_index < start_here_index):
        raise ValueError("unexpected section order for README handoff packet")
    return "Rules->ActiveProductSurfaces->StartHere"


def collect_failures(root: Path) -> list[str]:
    readme_path = root / README_PATH
    readme = readme_path.read_text(encoding="utf-8")

    failures: list[str] = []
    try:
        section_order = _find_section_order(readme)
    except ValueError as exc:
        failures.append(f"section:{exc}")
        section_order = None

    if section_order is not None:
        active_heading = "\nActive product surfaces\n"
        active_start = readme.find(active_heading)
        start_here = readme.find("\nStart here\n")
        active_section = readme[active_start + len(active_heading) : start_here]
        for line in ACTIVE_PRODUCT_SURFACE_LINES:
            if line not in active_section:
                failures.append(f"marker:{line}")
        bullet_count = sum(
            1 for line in active_section.splitlines() if line.startswith("- ")
        )
        if bullet_count != len(ACTIVE_PRODUCT_SURFACE_LINES):
            failures.append(f"bullet-count:{bullet_count}")

    for path in REQUIRED_FILES:
        if not (root / path).is_file():
            failures.append(f"missing-file:{path.as_posix()}")

    return failures


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


def _write_required_files(root: Path) -> None:
    for path in REQUIRED_FILES:
        _write(root / path, "placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_active_product_surfaces_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())
        _write_required_files(root)

        if collect_failures(root):
            raise AssertionError("baseline active-product-surfaces fixture should pass")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                ACTIVE_PRODUCT_SURFACE_LINES[1] + "\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [f"marker:{ACTIVE_PRODUCT_SURFACE_LINES[1]}", "bullet-count:4"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for missing review-checklist line: {failures}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace("Active product surfaces\n", "Current product surfaces\n", 1),
        )
        failures = collect_failures(root)
        expected = ["section:missing heading: Active product surfaces"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for heading rename: {failures}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "Rules\n- Keep product planning and bootstrap artifacts here first.\n\nActive product surfaces\n",
                "Active product surfaces\n- Keep product planning and bootstrap artifacts here first.\n\nRules\n",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = ["section:unexpected section order for README handoff packet"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for section order case: {failures}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        (root / REQUIRED_FILES[2]).unlink()
        failures = collect_failures(root)
        expected = [f"missing-file:{REQUIRED_FILES[2].as_posix()}"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for missing freeze-map file: {failures}")
        _write_required_files(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                ACTIVE_PRODUCT_SURFACE_LINES[4] + "\n",
                ACTIVE_PRODUCT_SURFACE_LINES[4] + "\n" + ACTIVE_PRODUCT_SURFACE_LINES[4] + "\n",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = ["bullet-count:6"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for duplicate bullet case: {failures}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 bootstrap README active-product-surfaces packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the bootstrap README packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    readme = (args.root / README_PATH).read_text(encoding="utf-8")
    active_heading = "\nActive product surfaces\n"
    active_start = readme.find(active_heading)
    start_here = readme.find("\nStart here\n")
    active_section = readme[active_start + len(active_heading) : start_here]
    bullet_count = sum(1 for line in active_section.splitlines() if line.startswith("- "))

    print("LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES=pass")
    print(f"LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_BULLET_COUNT={bullet_count}")
    print(
        "LANE01_BOOTSTRAP_ACTIVE_PRODUCT_SURFACES_SECTION_ORDER="
        + _find_section_order(readme)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
