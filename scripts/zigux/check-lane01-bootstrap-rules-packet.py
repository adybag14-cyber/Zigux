#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")
SECTION_HEADING = "Rules"
NEXT_HEADING = "Active product surfaces"
EXPECTED_LINES = (
    "- Keep product planning and bootstrap artifacts here first.",
    "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.",
    "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.",
    "- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.",
    "- Treat ZAR as the research and proving repo and Zigux as the product repo.",
    "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.",
)


def _heading_indexes(lines: list[str], heading: str) -> list[int]:
    return [index for index, line in enumerate(lines) if line == heading]


def extract_rules_packet(root: Path) -> tuple[str, ...]:
    readme_lines = (root / README_PATH).read_text(encoding="utf-8").splitlines()

    rule_indexes = _heading_indexes(readme_lines, SECTION_HEADING)
    if not rule_indexes:
        raise AssertionError(f"missing heading: {SECTION_HEADING}")
    if len(rule_indexes) != 1:
        raise AssertionError(f"duplicate heading: {SECTION_HEADING}")
    start = rule_indexes[0]

    next_indexes = [index for index in _heading_indexes(readme_lines, NEXT_HEADING) if index > start]
    if not next_indexes:
        raise AssertionError(f"missing heading: {NEXT_HEADING}")
    if len(next_indexes) != 1:
        raise AssertionError(f"duplicate heading: {NEXT_HEADING}")
    end = next_indexes[0]

    return tuple(line for line in readme_lines[start + 1 : end] if line.strip())


def check_rules_packet(root: Path) -> list[str]:
    try:
        packet = extract_rules_packet(root)
    except AssertionError as exc:
        return [str(exc)]

    if packet != EXPECTED_LINES:
        return [
            "rules packet mismatch",
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
- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.
- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.
- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.
- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.
- Treat ZAR as the research and proving repo and Zigux as the product repo.
- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.

Active product surfaces
- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_rules_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        errors = check_rules_packet(root)
        if errors:
            raise AssertionError(f"baseline Lane 01 rules fixture should pass: {errors}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Rules\n", "", 1))
        errors = check_rules_packet(root)
        if errors != ["missing heading: Rules"]:
            raise AssertionError(f"unexpected missing-rules error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Active product surfaces\n", "Start here\n", 1))
        errors = check_rules_packet(root)
        if errors != ["missing heading: Active product surfaces"]:
            raise AssertionError(f"unexpected missing-next-heading error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Rules\n", "Rules\nRules\n", 1))
        errors = check_rules_packet(root)
        if errors != ["duplicate heading: Rules"]:
            raise AssertionError(f"unexpected duplicate-rules error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "Active product surfaces\n",
                "Active product surfaces\nActive product surfaces\n",
                1,
            ),
        )
        errors = check_rules_packet(root)
        if errors != ["duplicate heading: Active product surfaces"]:
            raise AssertionError(f"unexpected duplicate-next-heading error: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.\n",
                "",
                1,
            ),
        )
        errors = check_rules_packet(root)
        if not errors or errors[0] != "rules packet mismatch":
            raise AssertionError(f"expected missing-rule mismatch, got: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- Treat ZAR as the research and proving repo and Zigux as the product repo.\n"
                "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.\n",
                "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.\n"
                "- Treat ZAR as the research and proving repo and Zigux as the product repo.\n",
                1,
            ),
        )
        errors = check_rules_packet(root)
        if not errors or errors[0] != "rules packet mismatch":
            raise AssertionError(f"expected reorder mismatch, got: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.\n",
                "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.\n"
                "- Keep validation notes local to issue threads.\n",
                1,
            ),
        )
        errors = check_rules_packet(root)
        if not errors or errors[0] != "rules packet mismatch":
            raise AssertionError(f"expected extra-rule mismatch, got: {errors}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.",
                "- Move actual product code into the final Zigux root immediately.",
                1,
            ),
        )
        errors = check_rules_packet(root)
        if not errors or errors[0] != "rules packet mismatch":
            raise AssertionError(f"expected wording mismatch, got: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_RULES_PACKET_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_RULES_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 bootstrap README Rules packet remains aligned."
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

    errors = check_rules_packet(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Lane 01 bootstrap Rules packet check passed.")
    print(f"LANE01_BOOTSTRAP_RULE_COUNT={len(EXPECTED_LINES)}")
    print("LANE01_BOOTSTRAP_RULES_PACKET_SECTION_ORDER=Rules->ActiveProductSurfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())