#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SECTION_HEADING = "## How ZAR Should Feed Zigux"
PREVIOUS_HEADING = "## Non-Negotiable Product Rules"
NEXT_HEADING = "## zigux-alpha Scope"

REQUIRED_LINES = (
    "ZAR should not try to become Zigux.",
    "ZAR should instead feed Zigux in these ways:",
    "| ZAR capability or work type | Use for Zigux | How to transfer it | Zigux phase impact |",
    "| --- | --- | --- | --- |",
    "| parity gates and drift checks | High | Rebuild as Linux-facing differential gates inside `zigux/tests/` and `scripts/zigux/` | 2-4 |",
    "| build reproducibility discipline | High | Transfer the release-gate mindset, not the exact scripts | 2-4 |",
    "| ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3 |",
    "| bare-metal i386 platform and SMP research | Medium | Use as concurrency-validation research input only | 4, 9, 14 |",
    "| virtio, E1000, RTL8139 proof methodology | Medium | Reuse the validation mindset and probe culture, not the current ZAR code shape | 9-12 |",
    "| storage and filesystem probe methodology | Medium | Reuse for `fs/libfs`, `lib/devres`, and driver validation scaffolding | 4, 13 |",
    "| shell, TTY, tool-service runtime | Low | Product value is indirect; use only where it informs repo-hosted tooling or validation UX | 4-8 |",
    "| workspace/package/trust runtime | Low | Mostly ZAR-specific; keep out of near-term Zigux product scope | research only |",
    "| VFS overlay experiments | Medium | Use only as design lessons for bounded helper layers, not as a direct port target | 13-15 |",
    "| driver lifecycle proofs | High | Use to shape lab matrices, teardown checks, and failure-mode expectations | 10-12 |",
    "The rule is simple:",
    "- If a ZAR slice reduces Zigux product risk, keep it.",
    "- If it only expands ZAR’s own experimental surface, do not let it consume Zigux product bandwidth.",
)


def extract_section(text: str, heading: str, next_heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        raise ValueError(f"missing heading: {heading}")
    end = text.find(next_heading, start)
    if end == -1:
        raise ValueError(f"missing next heading: {next_heading}")
    return text[start:end]


def ensure_section_order(text: str) -> None:
    previous_index = text.find(PREVIOUS_HEADING)
    current_index = text.find(SECTION_HEADING)
    next_index = text.find(NEXT_HEADING)
    if previous_index == -1 or current_index == -1 or next_index == -1:
        raise ValueError("missing required section boundary heading")
    if not previous_index < current_index < next_index:
        raise ValueError("roadmap section order drifted")


def collect_errors(root: Path) -> list[str]:
    roadmap_path = root / ROADMAP_PATH
    text = roadmap_path.read_text(encoding="utf-8")

    errors: list[str] = []
    try:
        ensure_section_order(text)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    section = extract_section(text, SECTION_HEADING, NEXT_HEADING)
    for line in REQUIRED_LINES:
        if line not in section:
            errors.append(f"missing line: {line}")
    return errors


def write_sample_root(root: Path) -> None:
    (root / ROADMAP_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / ROADMAP_PATH).write_text(_sample_roadmap(), encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Non-Negotiable Product Rules

1. No flag-day rewrite.

## How ZAR Should Feed Zigux

ZAR should not try to become Zigux.

ZAR should instead feed Zigux in these ways:

| ZAR capability or work type | Use for Zigux | How to transfer it | Zigux phase impact |
| --- | --- | --- | --- |
| parity gates and drift checks | High | Rebuild as Linux-facing differential gates inside `zigux/tests/` and `scripts/zigux/` | 2-4 |
| build reproducibility discipline | High | Transfer the release-gate mindset, not the exact scripts | 2-4 |
| ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3 |
| bare-metal i386 platform and SMP research | Medium | Use as concurrency-validation research input only | 4, 9, 14 |
| virtio, E1000, RTL8139 proof methodology | Medium | Reuse the validation mindset and probe culture, not the current ZAR code shape | 9-12 |
| storage and filesystem probe methodology | Medium | Reuse for `fs/libfs`, `lib/devres`, and driver validation scaffolding | 4, 13 |
| shell, TTY, tool-service runtime | Low | Product value is indirect; use only where it informs repo-hosted tooling or validation UX | 4-8 |
| workspace/package/trust runtime | Low | Mostly ZAR-specific; keep out of near-term Zigux product scope | research only |
| VFS overlay experiments | Medium | Use only as design lessons for bounded helper layers, not as a direct port target | 13-15 |
| driver lifecycle proofs | High | Use to shape lab matrices, teardown checks, and failure-mode expectations | 10-12 |

The rule is simple:
- If a ZAR slice reduces Zigux product risk, keep it.
- If it only expands ZAR’s own experimental surface, do not let it consume Zigux product bandwidth.

## zigux-alpha Scope

`zigux-alpha/` is the staging area for:
- roadmap and phase sequencing
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane01_zar_feed_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        if collect_errors(root):
            raise AssertionError("baseline sample root should pass")
        case_count += 1

        roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")

        for needle in (
            "ZAR should not try to become Zigux.\n",
            "| ZAR capability or work type | Use for Zigux | How to transfer it | Zigux phase impact |\n",
            "| driver lifecycle proofs | High | Use to shape lab matrices, teardown checks, and failure-mode expectations | 10-12 |\n",
            "- If it only expands ZAR’s own experimental surface, do not let it consume Zigux product bandwidth.\n",
        ):
            (root / ROADMAP_PATH).write_text(roadmap.replace(needle, "", 1), encoding="utf-8")
            errors = collect_errors(root)
            if len(errors) != 1 or needle.strip() not in errors[0]:
                raise AssertionError(f"expected one missing-line error for {needle!r}, got {errors}")
            (root / ROADMAP_PATH).writeText = None
            (root / ROADMAP_PATH).write_text(roadmap, encoding="utf-8")
            case_count += 1

        (root / ROADMAP_PATH).write_text(
            roadmap.replace(NEXT_HEADING, "## zigux alpha Scope", 1),
            encoding="utf-8",
        )
        errors = collect_errors(root)
        if errors != ["missing required section boundary heading"]:
            raise AssertionError(f"expected next-heading boundary failure, got {errors}")
        (root / ROADMAP_PATH).write_text(roadmap, encoding="utf-8")
        case_count += 1

        broken_order = roadmap.replace(
            f"{PREVIOUS_HEADING}\n\n1. No flag-day rewrite.\n\n{SECTION_HEADING}",
            f"{SECTION_HEADING}\n\n{PREVIOUS_HEADING}\n\n1. No flag-day rewrite.",
            1,
        )
        (root / ROADMAP_PATH).write_text(broken_order, encoding="utf-8")
        errors = collect_errors(root)
        if errors != ["roadmap section order drifted"]:
            raise AssertionError(f"expected section-order failure, got {errors}")
        case_count += 1

        (root / ROADMAP_PATH).write_text(
            roadmap.replace(
                "| workspace/package/trust runtime | Low | Mostly ZAR-specific; keep out of near-term Zigux product scope | research only |\n",
                "| workspace/package/trust runtime | Medium | Mostly ZAR-specific; keep out of near-term Zigux product scope | research only |\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = collect_errors(root)
        expected = "missing line: | workspace/package/trust runtime | Low | Mostly ZAR-specific; keep out of near-term Zigux product scope | research only |"
        if errors != [expected]:
            raise AssertionError(f"expected exact-row failure, got {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 roadmap How ZAR Should Feed Zigux packet."
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
        help="run synthetic self-tests for the checker",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root for focused validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    errors = collect_errors(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print("LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED_SECTION_ORDER=NonNegotiableProductRules->HowZARShouldFeedZigux->ziguxAlphaScope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
