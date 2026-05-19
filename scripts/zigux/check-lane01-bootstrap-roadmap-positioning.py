#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
ROADMAP_REL = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"

POSITIONING_MARKERS = (
    "Positioning:",
    "- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.",
    "- `Zigux` is the product repo.",
    "- Future ZAR work should only be prioritized if it directly reduces Zigux product risk, proves a future Zigux phase, or hardens Zigux validation, build, ABI, or driver delivery.",
    "This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.",
)

ORDERED_MARKERS = (
    "## Purpose",
    "Positioning:",
    "## Inputs Reviewed",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    roadmap = root / ROADMAP_REL
    if not roadmap.exists():
        return [f"missing_file:{ROADMAP_REL}"]

    text = _read(roadmap)
    for marker in POSITIONING_MARKERS:
        if marker not in text:
            issues.append(f"roadmap:missing:{marker}")

    last_index = -1
    for marker in ORDERED_MARKERS:
        index = text.find(marker)
        if index == -1:
            issues.append(f"roadmap:missing_order_marker:{marker}")
            continue
        if index < last_index:
            issues.append(f"roadmap:out_of_order:{marker}")
        last_index = index

    return issues


def _seed(root: Path) -> None:
    _write(
        root / ROADMAP_REL,
        """# ZAR to Zigux Product Roadmap

## Purpose

This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.

Positioning:
- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.
- `Zigux` is the product repo.
- Future ZAR work should only be prioritized if it directly reduces Zigux product risk, proves a future Zigux phase, or hardens Zigux validation, build, ABI, or driver delivery.

This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.

## Inputs Reviewed
""",
    )


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"lane01-roadmap-positioning-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_roadmap_positioning_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace("Positioning:\n", "", 1))
        _assert_only(
            validate(root),
            [
                "roadmap:missing:Positioning:",
                "roadmap:missing_order_marker:Positioning:",
            ],
            "missing_positioning_heading",
        )
        _seed(root)
        case_count += 1

        path = root / ROADMAP_REL
        _write(
            path,
            _read(path).replace(
                "- `Zigux` is the product repo.\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["roadmap:missing:- `Zigux` is the product repo."],
            "missing_zigux_repo_marker",
        )
        _seed(root)
        case_count += 1

        path = root / ROADMAP_REL
        _write(
            path,
            _read(path).replace(
                "This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "roadmap:missing:This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved."
            ],
            "missing_execution_sentence",
        )
        _seed(root)
        case_count += 1

        path = root / ROADMAP_REL
        _write(
            path,
            _read(path).replace(
                "Positioning:\n- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.\n- `Zigux` is the product repo.\n- Future ZAR work should only be prioritized if it directly reduces Zigux product risk, proves a future Zigux phase, or hardens Zigux validation, build, ABI, or driver delivery.\n\nThis roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.\n\n## Inputs Reviewed\n",
                "## Inputs Reviewed\nPositioning:\n- `ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.\n- `Zigux` is the product repo.\n- Future ZAR work should only be prioritized if it directly reduces Zigux product risk, proves a future Zigux phase, or hardens Zigux validation, build, ABI, or driver delivery.\n\nThis roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["roadmap:out_of_order:## Inputs Reviewed"],
            "inputs_reviewed_before_positioning",
        )
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_POSITIONING_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_POSITIONING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 01 roadmap positioning packet aligned with the bootstrap charter."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("LANE01_BOOTSTRAP_ROADMAP_POSITIONING=fail")
        print("LANE01_BOOTSTRAP_ROADMAP_POSITIONING_ISSUES_START")
        for issue in issues:
            print(issue)
        print("LANE01_BOOTSTRAP_ROADMAP_POSITIONING_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_POSITIONING=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_POSITIONING_REQUIRED_MARKER_COUNT={len(POSITIONING_MARKERS) + len(ORDERED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
