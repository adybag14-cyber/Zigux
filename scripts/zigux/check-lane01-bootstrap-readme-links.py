#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")

REQUIRED_MARKERS = (
    "`zigux-alpha` is the Zigux bootstrap workspace.",
    "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.",
    "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "`Documentation/zigux/review-checklist.md` is the reviewer-facing gate for active Zigux product work.",
    "`Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "`Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.",
    "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
    "[ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)",
    "[Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
    "[Live Product Docs](../Documentation/zigux/README.md)",
    "[Review Checklist](../Documentation/zigux/review-checklist.md)",
    "[Freeze Map](../Documentation/zigux/freeze-map.md)",
    "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
)

REQUIRED_PATHS = (
    Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"),
    Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("Documentation/zigux/freeze-map.md"),
    Path("Documentation/zigux/phase15-freeze-map-governance.md"),
    Path("scripts/zigux/check-lane01-bootstrap-charter-alignment.py"),
)


def collect_failures(root: Path) -> list[str]:
    readme = (root / README_PATH).read_text(encoding="utf-8")
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in readme:
            failures.append(f"readme:{marker}")

    for path in REQUIRED_PATHS:
        if not (root / path).exists():
            failures.append(f"missing_path:{path.as_posix()}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def _sample_readme() -> str:
    return """# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

Rules
- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.
- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.

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


def _populate_sample_root(root: Path) -> None:
    _write(root / README_PATH, _sample_readme())
    for path in REQUIRED_PATHS:
        _touch(root / path)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_readme_links_") as tmp_dir:
        root = Path(tmp_dir)
        _populate_sample_root(root)

        if collect_failures(root):
            raise AssertionError("baseline Lane 01 bootstrap README fixture should pass")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace("[Review Checklist](../Documentation/zigux/review-checklist.md)\n", "", 1),
        )
        failures = collect_failures(root)
        expected = ["readme:[Review Checklist](../Documentation/zigux/review-checklist.md)"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for review-checklist link case: {failures}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "`Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "readme:`Documentation/zigux/phase15-freeze-map-governance.md` is the governance companion that records the current Phase 15 review and blocker posture behind that freeze map."
        ]
        if failures != expected:
            raise AssertionError(
                f"unexpected failures for governance companion surface case: {failures}"
            )
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        (root / "Documentation/zigux/review-checklist.md").unlink()
        failures = collect_failures(root)
        expected = ["missing_path:Documentation/zigux/review-checklist.md"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for review-checklist path case: {failures}")
        _touch(root / "Documentation/zigux/review-checklist.md")
        case_count += 1

        (root / "scripts/zigux/check-lane01-bootstrap-charter-alignment.py").unlink()
        failures = collect_failures(root)
        expected = ["missing_path:scripts/zigux/check-lane01-bootstrap-charter-alignment.py"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for checker path case: {failures}")
        _touch(root / "scripts/zigux/check-lane01-bootstrap-charter-alignment.py")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "readme:The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected failures for ledger-scope marker case: {failures}")
        case_count += 1

    print("LANE01_BOOTSTRAP_README_LINKS_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_README_LINKS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 bootstrap README keeps its live handoff links and linked file routes intact."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the zigux-alpha README packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Lane 01 bootstrap README fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for item in failures:
            print(f"ERROR: {item}")
        return 1

    print("Lane 01 bootstrap README links check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
