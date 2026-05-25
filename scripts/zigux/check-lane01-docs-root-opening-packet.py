#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("Documentation/zigux/README.md")

HEADING_MARKER = "# Zigux Documentation This directory is the product documentation root for Zigux."
SCOPE_MARKER = (
    "Scope - product charter - review rules - freeze map - phase closure records "
    "- phase policy - future porting guides - validation and artifact-diff policy"
)
RULES_MARKER = (
    "Rules - keep product commitments here, not in ad hoc issue threads "
    "- keep deep-core freeze decisions explicit "
    "- require validation and rollback language for every new active port target "
    "- align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`"
)
CURRENT_CLOSURE_RECORDS_MARKER = (
    "Current closure records - `Documentation/zigux/phase1-closure.md` "
    "- `Documentation/zigux/phase2-closure.md`"
)

REQUIRED_MARKERS = (
    HEADING_MARKER,
    SCOPE_MARKER,
    RULES_MARKER,
    CURRENT_CLOSURE_RECORDS_MARKER,
)


def read_readme(root: Path) -> str:
    return (root / README_PATH).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    readme = read_readme(root)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in readme:
            failures.append(f"missing:{marker}")

    heading_index = readme.find(HEADING_MARKER)
    scope_index = readme.find(SCOPE_MARKER)
    rules_index = readme.find(RULES_MARKER)
    closure_index = readme.find(CURRENT_CLOSURE_RECORDS_MARKER)

    if (
        heading_index != -1
        and scope_index != -1
        and rules_index != -1
        and closure_index != -1
        and not (heading_index < scope_index < rules_index < closure_index)
    ):
        failures.append("order:heading/scope/rules/current-closure-records packet drifted")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return (
        "# Zigux Documentation This directory is the product documentation root for Zigux.\n"
        "Scope - product charter - review rules - freeze map - phase closure records "
        "- phase policy - future porting guides - validation and artifact-diff policy "
        "Rules - keep product commitments here, not in ad hoc issue threads "
        "- keep deep-core freeze decisions explicit "
        "- require validation and rollback language for every new active port target "
        "- align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` "
        "Current closure records - `Documentation/zigux/phase1-closure.md` "
        "- `Documentation/zigux/phase2-closure.md`\n"
    )


def write_sample_root(root: Path) -> None:
    _write(root / README_PATH, _sample_readme())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_docs_root_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        if collect_failures(root):
            raise AssertionError("baseline Lane 01 docs-root opening packet fixture should pass")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{HEADING_MARKER}\n", "", 1))
        failures = collect_failures(root)
        expected = [f"missing:{HEADING_MARKER}"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for heading case: {failures}")
        write_sample_root(root)
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{SCOPE_MARKER} ", "", 1))
        failures = collect_failures(root)
        expected = [f"missing:{SCOPE_MARKER}"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for scope case: {failures}")
        write_sample_root(root)
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{RULES_MARKER} ", "", 1))
        failures = collect_failures(root)
        expected = [f"missing:{RULES_MARKER}"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for rules case: {failures}")
        write_sample_root(root)
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(f"{CURRENT_CLOSURE_RECORDS_MARKER}\n", "", 1),
        )
        failures = collect_failures(root)
        expected = [f"missing:{CURRENT_CLOSURE_RECORDS_MARKER}"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for closure-records case: {failures}")
        write_sample_root(root)
        case_count += 1

        reordered = _sample_readme().replace(f"{CURRENT_CLOSURE_RECORDS_MARKER}\n", "", 1)
        reordered = reordered.replace(
            f"{RULES_MARKER} ",
            f"{CURRENT_CLOSURE_RECORDS_MARKER} {RULES_MARKER} ",
            1,
        )
        _write(root / README_PATH, reordered)
        failures = collect_failures(root)
        expected = ["order:heading/scope/rules/current-closure-records packet drifted"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for order case: {failures}")
        case_count += 1

    print("LANE01_DOCS_ROOT_OPENING_PACKET_SELF_TEST=pass")
    print(f"LANE01_DOCS_ROOT_OPENING_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 docs-root opening packet stays aligned."
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
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root for focused local validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"Wrote sample root to {args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"LANE01_DOCS_ROOT_OPENING_PACKET_FAILURE={failure}")
        return 1

    print("Lane 01 docs-root opening packet check passed.")
    print("LANE01_DOCS_ROOT_OPENING_PACKET=pass")
    print("LANE01_DOCS_ROOT_OPENING_PACKET_REQUIRED_MARKER_COUNT=4")
    print("LANE01_DOCS_ROOT_OPENING_PACKET_SECTION_ORDER=Heading->Scope->Rules->CurrentClosureRecords")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
