#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
SECTION_HEADING = "## Purpose"
NEXT_HEADING = "## Inputs Reviewed"
EXPECTED_LINES = (
    "This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.",
    "## Bootstrap Status Note",
    "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.",
    "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.",
    "Positioning:",
    "- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.",
    "- `Zigux` is the product repo.",
    "- Future ZAR work should only be prioritized if it directly reduces Zigux product risk, proves a future Zigux phase, or hardens Zigux validation, build, ABI, or driver delivery.",
    "This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.",
)


def extract_purpose_packet(root: Path) -> tuple[str, ...]:
    roadmap_lines = (root / ROADMAP_PATH).read_text(encoding="utf-8").splitlines()

    try:
        start = roadmap_lines.index(SECTION_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {SECTION_HEADING}") from exc

    try:
        end = roadmap_lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {NEXT_HEADING}") from exc

    return tuple(line for line in roadmap_lines[start + 1 : end] if line.strip())


def check_purpose_packet(root: Path) -> list[str]:
    try:
        packet = extract_purpose_packet(root)
    except AssertionError as exc:
        return [str(exc)]

    if packet != EXPECTED_LINES:
        return [
            "purpose packet mismatch",
            f"expected:{EXPECTED_LINES!r}",
            f"actual:{packet!r}",
        ]

    return []


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Purpose

This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.

## Bootstrap Status Note

This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.

For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.

Positioning:
- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.
- `Zigux` is the product repo.
- Future ZAR work should only be prioritized if it directly reduces Zigux product risk, proves a future Zigux phase, or hardens Zigux validation, build, ABI, or driver delivery.

This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.

## Inputs Reviewed

The roadmap is based on all bundle artifacts in `zigux_bundle_v2.zip`:
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_purpose_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        errors = check_purpose_packet(root)
        if errors:
            raise AssertionError(
                f"baseline Lane 01 roadmap Purpose fixture should pass: {errors}"
            )
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{SECTION_HEADING}\n\n", "", 1))
        errors = check_purpose_packet(root)
        if errors != [f"missing heading: {SECTION_HEADING}"]:
            raise AssertionError(f"unexpected purpose-heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{NEXT_HEADING}\n\n", "", 1))
        errors = check_purpose_packet(root)
        if errors != [f"missing heading: {NEXT_HEADING}"]:
            raise AssertionError(f"unexpected inputs-heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.\n",
                "",
                1,
            ),
        )
        errors = check_purpose_packet(root)
        if not errors or errors[0] != "purpose packet mismatch":
            raise AssertionError(f"expected missing-status mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.\n"
                "- `Zigux` is the product repo.\n",
                "- `Zigux` is the product repo.\n"
                "- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.\n",
                1,
            ),
        )
        errors = check_purpose_packet(root)
        if not errors or errors[0] != "purpose packet mismatch":
            raise AssertionError(f"expected positioning reorder mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "Positioning:\n",
                "Positioning:\n- synthetic expansion promise\n",
                1,
            ),
        )
        errors = check_purpose_packet(root)
        if not errors or errors[0] != "purpose packet mismatch":
            raise AssertionError(f"expected extra-line mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PURPOSE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PURPOSE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Purpose packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Lane 01 roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_purpose_packet(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PURPOSE=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PURPOSE_REQUIRED_LINE_COUNT={len(EXPECTED_LINES)}")
    print("LANE01_BOOTSTRAP_ROADMAP_PURPOSE_SECTION_ORDER=Purpose->InputsReviewed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
