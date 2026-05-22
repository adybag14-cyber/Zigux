#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")

START_HERE_HEADING = "Start here"
ACTIVE_SURFACES_HEADING = "Active product surfaces"
EXPECTED_LINKS = (
    "- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)",
    "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
    "- [Live Product Docs](../Documentation/zigux/README.md)",
    "- [Review Checklist](../Documentation/zigux/review-checklist.md)",
    "- [Freeze Map](../Documentation/zigux/freeze-map.md)",
    "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
)


def _extract_start_here_lines(readme: str) -> list[str]:
    lines = readme.splitlines()
    try:
        start_index = lines.index(START_HERE_HEADING)
    except ValueError as exc:
        raise AssertionError("missing `Start here` heading") from exc

    section: list[str] = []
    for line in lines[start_index + 1 :]:
        if not line.strip():
            if section:
                break
            continue
        if not line.startswith("- "):
            break
        section.append(line)
    return section


def check_start_here_links(root: Path) -> tuple[int, int]:
    readme = (root / README_PATH).read_text(encoding="utf-8")
    lines = readme.splitlines()
    section = _extract_start_here_lines(readme)

    if section != list(EXPECTED_LINKS):
        raise AssertionError("Start here links drifted from the expected six-link packet")

    if len(section) != len(set(section)):
        raise AssertionError("Start here links must stay unique")

    try:
        active_index = lines.index(ACTIVE_SURFACES_HEADING)
        start_index = lines.index(START_HERE_HEADING)
    except ValueError as exc:
        raise AssertionError("missing Lane 01 README section heading") from exc

    if start_index <= active_index:
        raise AssertionError("`Start here` must stay after `Active product surfaces`")

    return len(section), start_index - active_index


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

Active product surfaces
- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
- `Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.
- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.
- `Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.
- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.

Start here
- [ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)
- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)
- [Live Product Docs](../Documentation/zigux/README.md)
- [Review Checklist](../Documentation/zigux/review-checklist.md)
- [Freeze Map](../Documentation/zigux/freeze-map.md)
- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_start_here_") as tmp_dir:
        root = Path(tmp_dir)
        readme_path = root / README_PATH
        _write(readme_path, _sample_readme())

        count, section_distance = check_start_here_links(root)
        if count != 6 or section_distance <= 0:
            raise AssertionError("baseline Lane 01 Start here fixture should pass")
        case_count += 1

        _write(
            readme_path,
            _sample_readme().replace(
                "- [Live Product Docs](../Documentation/zigux/README.md)\n",
                "",
                1,
            ),
        )
        try:
            check_start_here_links(root)
        except AssertionError as exc:
            if "expected six-link packet" not in str(exc):
                raise
        else:
            raise AssertionError("missing Start here link should fail")
        case_count += 1

        _write(
            readme_path,
            _sample_readme().replace(
                "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)\n",
                "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)\n"
                "- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)\n",
                1,
            ),
        )
        try:
            check_start_here_links(root)
        except AssertionError as exc:
            if "expected six-link packet" not in str(exc):
                raise
        else:
            raise AssertionError("duplicate Start here link should fail")
        case_count += 1

        _write(
            readme_path,
            _sample_readme().replace(
                "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)\n"
                "- [Live Product Docs](../Documentation/zigux/README.md)\n",
                "- [Live Product Docs](../Documentation/zigux/README.md)\n"
                "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)\n",
                1,
            ),
        )
        try:
            check_start_here_links(root)
        except AssertionError as exc:
            if "expected six-link packet" not in str(exc):
                raise
        else:
            raise AssertionError("reordered Start here links should fail")
        case_count += 1

        _write(
            readme_path,
            _sample_readme().replace(
                "- [Freeze Map](../Documentation/zigux/freeze-map.md)\n",
                "- [Product Freeze Map](../Documentation/zigux/freeze-map.md)\n",
                1,
            ),
        )
        try:
            check_start_here_links(root)
        except AssertionError as exc:
            if "expected six-link packet" not in str(exc):
                raise
        else:
            raise AssertionError("stale replacement link should fail")
        case_count += 1

        _write(readme_path, _sample_readme().replace("Start here\n", "", 1))
        try:
            check_start_here_links(root)
        except AssertionError as exc:
            if "missing `Start here` heading" not in str(exc):
                raise
        else:
            raise AssertionError("missing Start here heading should fail")
        case_count += 1

    print("LANE01_BOOTSTRAP_START_HERE_LINKS_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_START_HERE_LINKS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 bootstrap README Start here links stay aligned."
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
        help="exercise the checker against synthetic README fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    count, section_distance = check_start_here_links(args.root)
    print("Lane 01 bootstrap Start here link check passed.")
    print(f"LANE01_BOOTSTRAP_START_HERE_LINK_COUNT={count}")
    print(f"LANE01_BOOTSTRAP_START_HERE_SECTION_DISTANCE={section_distance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
