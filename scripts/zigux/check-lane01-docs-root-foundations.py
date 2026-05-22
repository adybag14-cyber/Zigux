#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("Documentation/zigux/README.md")
TITLE_LINE = "# Zigux Documentation"
IDENTITY_LINE = "This directory is the product documentation root for Zigux."
SCOPE_LINE = (
    "Scope - product charter - review rules - freeze map - phase closure records - "
    "phase policy - future porting guides - validation and artifact-diff policy"
)
RULES_LINE = (
    "Rules - keep product commitments here, not in ad hoc issue threads - keep deep-core "
    "freeze decisions explicit - require validation and rollback language for every new "
    "active port target - align all new product docs with "
    "`zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`"
)
SECTION_HEADING = "Current closure records"
NEXT_SECTION_HEADING = "Phase 1 notes"
PHASE2_SECTION_HEADING = "Phase 2 notes"
REQUIRED_LINES = (
    "- `Documentation/zigux/phase1-closure.md`",
    "- `Documentation/zigux/phase2-closure.md`",
)


def extract_current_closure_section(readme_text: str) -> str:
    start = readme_text.find(SECTION_HEADING)
    if start == -1:
        raise ValueError(f"missing heading: {SECTION_HEADING}")

    phase1_start = readme_text.find(NEXT_SECTION_HEADING)
    if phase1_start == -1:
        raise ValueError(f"missing heading: {NEXT_SECTION_HEADING}")
    if phase1_start <= start:
        raise ValueError("Current closure records section must come before Phase 1 notes")

    end = readme_text.find(NEXT_SECTION_HEADING, start)
    if end == -1:
        raise ValueError(f"missing heading: {NEXT_SECTION_HEADING}")

    return readme_text[start:end]


def verify_current_closure_records(root: Path) -> None:
    readme_text = (root / README_PATH).read_text(encoding="utf-8")
    for marker in (TITLE_LINE, IDENTITY_LINE, SCOPE_LINE, RULES_LINE):
        if marker not in readme_text:
            raise ValueError(f"missing marker: {marker}")

    section = extract_current_closure_section(readme_text)

    missing = [line for line in REQUIRED_LINES if line not in section]
    if missing:
        raise ValueError("missing required line(s): " + ", ".join(missing))

    phase1_start = readme_text.find(NEXT_SECTION_HEADING)
    phase2_start = readme_text.find(PHASE2_SECTION_HEADING)
    if phase2_start == -1:
        raise ValueError(f"missing heading: {PHASE2_SECTION_HEADING}")
    if phase2_start <= phase1_start:
        raise ValueError("Phase 1 notes must come before Phase 2 notes")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# Zigux Documentation
This directory is the product documentation root for Zigux.

Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy
Rules - keep product commitments here, not in ad hoc issue threads - keep deep-core freeze decisions explicit - require validation and rollback language for every new active port target - align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`

Current closure records
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`

Phase 1 notes
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`

Phase 2 notes
- `Documentation/zigux/phase2-closure.md`
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_current_closure_") as tmp_dir:
        root = Path(tmp_dir)
        readme_path = root / README_PATH

        _write(readme_path, _sample_readme())
        verify_current_closure_records(root)
        case_count += 1

        _write(readme_path, _sample_readme().replace("# Zigux Documentation\n", "", 1))
        try:
            verify_current_closure_records(root)
        except ValueError as exc:
            expected = f"missing marker: {TITLE_LINE}"
            if str(exc) != expected:
                raise AssertionError(f"unexpected title-marker error: {exc}") from exc
        else:
            raise AssertionError("missing title line should fail")
        case_count += 1

        _write(readme_path, _sample_readme().replace(f"{IDENTITY_LINE}\n", "", 1))
        try:
            verify_current_closure_records(root)
        except ValueError as exc:
            expected = f"missing marker: {IDENTITY_LINE}"
            if str(exc) != expected:
                raise AssertionError(f"unexpected identity-marker error: {exc}") from exc
        else:
            raise AssertionError("missing identity line should fail")
        case_count += 1

        _write(readme_path, _sample_readme().replace(f"{SCOPE_LINE}\n", "", 1))
        try:
            verify_current_closure_records(root)
        except ValueError as exc:
            expected = f"missing marker: {SCOPE_LINE}"
            if str(exc) != expected:
                raise AssertionError(f"unexpected scope-marker error: {exc}") from exc
        else:
            raise AssertionError("missing scope line should fail")
        case_count += 1

        _write(readme_path, _sample_readme().replace(f"{RULES_LINE}\n", "", 1))
        try:
            verify_current_closure_records(root)
        except ValueError as exc:
            expected = f"missing marker: {RULES_LINE}"
            if str(exc) != expected:
                raise AssertionError(f"unexpected rules-marker error: {exc}") from exc
        else:
            raise AssertionError("missing rules line should fail")
        case_count += 1

        _write(readme_path, _sample_readme().replace("Current closure records\n", "", 1))
        try:
            verify_current_closure_records(root)
        except ValueError as exc:
            if str(exc) != f"missing heading: {SECTION_HEADING}":
                raise AssertionError(f"unexpected missing-heading error: {exc}") from exc
        else:
            raise AssertionError("missing current closure records heading should fail")
        case_count += 1

        _write(
            readme_path,
            _sample_readme().replace("- `Documentation/zigux/phase1-closure.md`\n", "", 1),
        )
        try:
            verify_current_closure_records(root)
        except ValueError as exc:
            expected = "missing required line(s): - `Documentation/zigux/phase1-closure.md`"
            if str(exc) != expected:
                raise AssertionError(f"unexpected phase1-line error: {exc}") from exc
        else:
            raise AssertionError("missing phase1 closure line should fail")
        case_count += 1

        _write(
            readme_path,
            _sample_readme().replace("- `Documentation/zigux/phase2-closure.md`\n", "", 1),
        )
        try:
            verify_current_closure_records(root)
        except ValueError as exc:
            expected = "missing required line(s): - `Documentation/zigux/phase2-closure.md`"
            if str(exc) != expected:
                raise AssertionError(f"unexpected phase2-line error: {exc}") from exc
        else:
            raise AssertionError("missing phase2 closure line should fail")
        case_count += 1

        reordered = """# Zigux Documentation
This directory is the product documentation root for Zigux.

Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy
Rules - keep product commitments here, not in ad hoc issue threads - keep deep-core freeze decisions explicit - require validation and rollback language for every new active port target - align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`

Phase 1 notes
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`

Current closure records
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`
"""
        _write(readme_path, reordered)
        try:
            verify_current_closure_records(root)
        except ValueError as exc:
            expected = "Current closure records section must come before Phase 1 notes"
            if str(exc) != expected:
                raise AssertionError(f"unexpected section-order error: {exc}") from exc
        else:
            raise AssertionError("reordered sections should fail")
        case_count += 1

        reordered_phase_sections = """# Zigux Documentation
This directory is the product documentation root for Zigux.

Scope - product charter - review rules - freeze map - phase closure records - phase policy - future porting guides - validation and artifact-diff policy
Rules - keep product commitments here, not in ad hoc issue threads - keep deep-core freeze decisions explicit - require validation and rollback language for every new active port target - align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`

Current closure records
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`

Phase 2 notes
- `Documentation/zigux/phase2-closure.md`

Phase 1 notes
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
"""
        _write(readme_path, reordered_phase_sections)
        try:
            verify_current_closure_records(root)
        except ValueError as exc:
            expected = "Phase 1 notes must come before Phase 2 notes"
            if str(exc) != expected:
                raise AssertionError(f"unexpected phase-section-order error: {exc}") from exc
        else:
            raise AssertionError("phase section reorder should fail")
        case_count += 1

    print("LANE01_DOCS_ROOT_FOUNDATIONS_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_FOUNDATIONS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 docs-root foundations packet remains intact."
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
        help="exercise the checker against synthetic Documentation/zigux/README.md fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    verify_current_closure_records(args.root)
    print("LANE01_DOCS_ROOT_FOUNDATIONS=pass")
    print(f"LANE01_DOCS_ROOT_FOUNDATIONS_CLOSURE_RECORD_COUNT={len(REQUIRED_LINES)}")
    print("LANE01_DOCS_ROOT_FOUNDATIONS_SECTION_ORDER=CurrentClosureRecords->Phase1Notes->Phase2Notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
