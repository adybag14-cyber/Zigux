#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_ROOT_README = Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = (
    "# Zigux Documentation",
    "This directory is the product documentation root for Zigux.",
    "Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy",
    "Rules - keep product commitments here, not in ad hoc issue threads",
    "align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`",
    "Current closure records - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/phase2-closure.md`",
    "Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "Phase 2 notes - `Documentation/zigux/phase2-closure.md`",
)

ORDER_MARKERS = (
    "Current closure records",
    "Phase 1 notes",
    "Phase 2 notes",
)


def collect_failures(root: Path) -> list[str]:
    text = (root / DOCS_ROOT_README).read_text(encoding="utf-8")

    failures: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing:{marker}")

    if text.count("# Zigux Documentation") != 1:
        failures.append("count:# Zigux Documentation")
    if text.count("Current closure records") != 1:
        failures.append("count:Current closure records")

    positions = [text.find(marker) for marker in ORDER_MARKERS]
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        failures.append("order:Current closure records -> Phase 1 notes -> Phase 2 notes")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# Zigux Documentation
This directory is the product documentation root for Zigux.
Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy
Rules - keep product commitments here, not in ad hoc issue threads - keep deep-core freeze decisions explicit - require validation and rollback language for every new active port target - align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
Current closure records - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/phase2-closure.md`
Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
Phase 2 notes - `Documentation/zigux/phase2-closure.md`
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_docs_root_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_ROOT_README, _sample_readme())

        if collect_failures(root):
            raise AssertionError("baseline docs-root fixture should pass")
        case_count += 1

        _write(root / DOCS_ROOT_README, _sample_readme().replace("# Zigux Documentation\n", "", 1))
        failures = collect_failures(root)
        expected = ["missing:# Zigux Documentation", "count:# Zigux Documentation"]
        if failures != expected:
            raise AssertionError(f"unexpected heading failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected scope failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`",
                "align all new product docs with the roadmap",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected roadmap-alignment failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "Current closure records - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/phase2-closure.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:Current closure records - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/phase2-closure.md`",
            "count:Current closure records",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected closure-record failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing:Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected phase1 failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            _sample_readme().replace(
                "Phase 2 notes - `Documentation/zigux/phase2-closure.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = ["missing:Phase 2 notes - `Documentation/zigux/phase2-closure.md`"]
        if failures != expected:
            raise AssertionError(f"unexpected phase2 failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(
            root / DOCS_ROOT_README,
            """# Zigux Documentation
This directory is the product documentation root for Zigux.
Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy
Rules - keep product commitments here, not in ad hoc issue threads - keep deep-core freeze decisions explicit - require validation and rollback language for every new active port target - align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
Current closure records - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/phase2-closure.md`
Phase 2 notes - `Documentation/zigux/phase2-closure.md`
""",
        )
        failures = collect_failures(root)
        expected = ["order:Current closure records -> Phase 1 notes -> Phase 2 notes"]
        if failures != expected:
            raise AssertionError(f"unexpected ordering failures: {failures}")
        _write(root / DOCS_ROOT_README, _sample_readme())
        case_count += 1

        _write(root / DOCS_ROOT_README, _sample_readme() + "# Zigux Documentation\n")
        failures = collect_failures(root)
        expected = ["count:# Zigux Documentation"]
        if failures != expected:
            raise AssertionError(f"unexpected duplicate-heading failures: {failures}")
        case_count += 1

    print("LANE01_DOCS_ROOT_FOUNDATIONS_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_FOUNDATIONS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the live Zigux docs root keeps its foundational Lane 01 packet."
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
        help="exercise the checker against synthetic docs-root fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("LANE01_DOCS_ROOT_FOUNDATIONS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
