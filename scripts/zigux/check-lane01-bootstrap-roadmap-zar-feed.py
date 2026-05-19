#!/usr/bin/env python3
"""Guard the Lane 01 roadmap How ZAR Should Feed Zigux packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 2
    else Path.cwd()
)
ROADMAP_REL = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SECTION_HEADING = "## How ZAR Should Feed Zigux"
NEXT_HEADING = "## zigux-alpha Scope"
PREV_HEADING = "## Non-Negotiable Product Rules"

EXPECTED_SECTION_LINES = (
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
    "- If it only expands ZAR\u2019s own experimental surface, do not let it consume Zigux product bandwidth.",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_section(root: Path) -> list[str]:
    roadmap = root / ROADMAP_REL
    lines = roadmap.read_text(encoding="utf-8").splitlines()

    try:
        prev_index = lines.index(PREV_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing previous heading: {PREV_HEADING}") from exc

    try:
        start = lines.index(SECTION_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {SECTION_HEADING}") from exc

    try:
        end = lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError(f"missing next heading: {NEXT_HEADING}") from exc

    if prev_index >= start:
        raise AssertionError("invalid heading order before zar-feed section")

    if end <= start + 1:
        raise AssertionError("zar-feed section is empty")

    return [line for line in lines[start + 1 : end] if line]


def validate(root: Path) -> list[str]:
    roadmap = root / ROADMAP_REL
    if not roadmap.exists():
        return [f"missing_file:{ROADMAP_REL.as_posix()}"]

    try:
        actual_lines = read_section(root)
    except AssertionError as exc:
        return [str(exc)]

    problems: list[str] = []
    if actual_lines != list(EXPECTED_SECTION_LINES):
        expected_set = set(EXPECTED_SECTION_LINES)
        actual_set = set(actual_lines)

        for expected in EXPECTED_SECTION_LINES:
            if expected not in actual_set:
                problems.append(f"missing_section_line:{expected}")

        for actual in actual_lines:
            if actual not in expected_set:
                problems.append(f"unexpected_section_line:{actual}")

        if not problems:
            for index, expected in enumerate(EXPECTED_SECTION_LINES):
                actual_index = actual_lines.index(expected)
                if actual_index != index:
                    problems.append(
                        "misordered_section_line:"
                        f"{expected}:found_at={actual_index + 1}:expected_at={index + 1}"
                    )

    return problems


def _sample_roadmap() -> str:
    section = "\n".join(EXPECTED_SECTION_LINES)
    return f"""# ZAR to Zigux Product Roadmap

## Non-Negotiable Product Rules

These rules are consistent across the bundle and should govern every Zigux commit series.

## How ZAR Should Feed Zigux

{section}

## zigux-alpha Scope

`zigux-alpha/` is the staging area for:
- roadmap and phase sequencing
"""


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"lane01-roadmap-zar-feed-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_roadmap_zar_feed_") as tmp_dir:
        root = Path(tmp_dir)
        path = root / ROADMAP_REL

        _write(path, _sample_roadmap())
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        _write(path, _read(path).replace(f"{SECTION_HEADING}\n\n", "", 1))
        _assert_only(
            validate(root),
            [f"missing heading: {SECTION_HEADING}"],
            "missing_heading",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace(
                "| ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3 |\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_section_line:| ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3 |"
            ],
            "missing_table_row",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace(
                "| build reproducibility discipline | High | Transfer the release-gate mindset, not the exact scripts | 2-4 |\n"
                "| ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3 |\n",
                "| ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3 |\n"
                "| build reproducibility discipline | High | Transfer the release-gate mindset, not the exact scripts | 2-4 |\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "misordered_section_line:| build reproducibility discipline | High | Transfer the release-gate mindset, not the exact scripts | 2-4 |:found_at=7:expected_at=6",
                "misordered_section_line:| ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3 |:found_at=6:expected_at=7",
            ],
            "misordered_table_rows",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace(
                "- If it only expands ZAR\\u2019s own experimental surface, do not let it consume Zigux product bandwidth.\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_section_line:- If it only expands ZAR\\u2019s own experimental surface, do not let it consume Zigux product bandwidth."
            ],
            "missing_closing_rule",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(path, _read(path).replace(f"{NEXT_HEADING}\n\n", "", 1))
        _assert_only(
            validate(root),
            [f"missing next heading: {NEXT_HEADING}"],
            "missing_next_heading",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(path, _read(path).replace(f"{PREV_HEADING}\n\n", "", 1))
        _assert_only(
            validate(root),
            [f"missing previous heading: {PREV_HEADING}"],
            "missing_previous_heading",
        )
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 01 How ZAR Should Feed Zigux roadmap packet aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = validate(args.root)
    if problems:
        print("LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED=fail")
        print("LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED_ISSUES_START")
        for problem in problems:
            print(problem)
        print("LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_ZAR_FEED_REQUIRED_LINE_COUNT={len(EXPECTED_SECTION_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
