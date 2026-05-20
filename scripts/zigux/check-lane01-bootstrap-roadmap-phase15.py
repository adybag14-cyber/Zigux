#!/usr/bin/env python3
"""LANE01_BOOTSTRAP_ROADMAP_PHASE15_CHECK=full_parity_blockers_and_long_term_governance

Fail-closed checker for the Lane 01 roadmap Phase 15 packet.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

MARKER = (
    "LANE01_BOOTSTRAP_ROADMAP_PHASE15_CHECK="
    "full_parity_blockers_and_long_term_governance"
)
ROADMAP_PATH = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"

PHASE14_HEADING = "## Phase 14: Core-Adjacent Bounded Internals"
PHASE15_HEADING = "## Phase 15: Full-Parity Blockers and Long-Term Governance"
FREEZE_MAP_HEADING = "## Freeze Map for Near- and Mid-Term Planning"

EXPECTED_GOAL = "- govern the final mixed-language steady state honestly"
EXPECTED_ANCHORS = [
    "- `kernel/sched/core.c`",
    "- `mm/page_alloc.c`",
    "- `kernel/rcu/tree.c`",
    "- `net/core/skbuff.c`",
]
EXPECTED_FEATURES = [
    "- freeze map",
    "- Architecture Council review process",
    "- parity scorecard",
    "- policy for code that remains in C indefinitely",
]
EXPECTED_DISCIPLINE_LINE = "This phase is about discipline, not bravado."
UNEXPECTED_DESTINATION_LABEL = "Recommended Zigux destinations:"
EXPECTED_REQUIRED_LINE_COUNT = 14


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_section(lines: list[str], heading: str) -> list[str] | None:
    start = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index
            break
    if start is None:
        return None

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return lines[start:end]


def extract_bullets(section: list[str], label: str) -> list[str]:
    bullets: list[str] = []
    in_block = False
    for line in section:
        stripped = line.strip()
        if stripped == label:
            in_block = True
            continue
        if not in_block:
            continue
        if stripped.startswith("- "):
            bullets.append(stripped)
            continue
        if bullets:
            break
    return bullets


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    roadmap = root / ROADMAP_PATH
    if not roadmap.is_file():
        return [f"missing file: {ROADMAP_PATH}"]

    checker_source = source_text if source_text is not None else read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")

    roadmap_text = read_text(roadmap)
    lines = roadmap_text.splitlines()
    section = extract_section(lines, PHASE15_HEADING)
    if section is None:
        return errors + [f"missing heading: {PHASE15_HEADING}"]

    section_text = "\n".join(section)
    phase14_index = roadmap_text.find(PHASE14_HEADING)
    phase15_index = roadmap_text.find(PHASE15_HEADING)
    freeze_map_index = roadmap_text.find(FREEZE_MAP_HEADING)
    if -1 in (phase14_index, phase15_index, freeze_map_index):
        errors.append("phase15 order anchors missing")
    elif not (phase14_index < phase15_index < freeze_map_index):
        errors.append("roadmap phase order drifted around Phase 15")

    if EXPECTED_GOAL not in section:
        errors.append("phase15:goal_drift")

    anchors = extract_bullets(section, "Primary Linux anchors:")
    if anchors != EXPECTED_ANCHORS:
        errors.append(f"phase15:anchor_drift:{anchors}")

    features = extract_bullets(section, "Required Zigux features:")
    if features != EXPECTED_FEATURES:
        errors.append(f"phase15:feature_drift:{features}")

    if EXPECTED_DISCIPLINE_LINE not in section:
        errors.append("phase15:discipline_line_drift")

    if UNEXPECTED_DESTINATION_LABEL in section_text:
        errors.append("phase15:unexpected_destinations_block")

    required_line_count = (
        1
        + 1
        + 1
        + 1
        + len(EXPECTED_ANCHORS)
        + 1
        + len(EXPECTED_FEATURES)
        + 1
    )
    if required_line_count != EXPECTED_REQUIRED_LINE_COUNT:
        errors.append(f"phase15:required_line_formula_drift:{required_line_count}")

    if PHASE15_HEADING not in section_text:
        errors.append("phase15:section_heading_missing_after_extract")

    return errors


def good_roadmap_text() -> str:
    return "\n".join(
        [
            "# ZAR to Zigux Product Roadmap",
            "",
            PHASE14_HEADING,
            "",
            "placeholder",
            "",
            PHASE15_HEADING,
            "",
            "Primary product goal:",
            EXPECTED_GOAL,
            "",
            "Primary Linux anchors:",
            *EXPECTED_ANCHORS,
            "",
            "Required Zigux features:",
            *EXPECTED_FEATURES,
            "",
            EXPECTED_DISCIPLINE_LINE,
            "",
            FREEZE_MAP_HEADING,
            "",
            "placeholder",
            "",
        ]
    )


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}: expected {expected}, got {actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane01_bootstrap_phase15_") as temp_dir:
        root = Path(temp_dir)
        roadmap = root / ROADMAP_PATH

        write_text(roadmap, good_roadmap_text())
        assert_only(check(root, MARKER), [], "baseline")
        case_count += 1

        write_text(roadmap, good_roadmap_text().replace(PHASE15_HEADING, "## Phase 15: Drifted", 1))
        assert_only(check(root, MARKER), [f"missing heading: {PHASE15_HEADING}"], "heading")
        case_count += 1

        write_text(roadmap, good_roadmap_text().replace(EXPECTED_GOAL, "- chase parity claims early", 1))
        assert_only(check(root, MARKER), ["phase15:goal_drift"], "goal")
        case_count += 1

        write_text(roadmap, good_roadmap_text().replace(EXPECTED_ANCHORS[-1], "- `net/core/dev.c`", 1))
        assert_only(
            check(root, MARKER),
            [f"phase15:anchor_drift:{EXPECTED_ANCHORS[:-1] + ['- `net/core/dev.c`']}"],
            "anchors",
        )
        case_count += 1

        write_text(
            roadmap,
            good_roadmap_text().replace(
                EXPECTED_FEATURES[-1], "- direct parity approval for frozen C areas", 1
            ),
        )
        assert_only(
            check(root, MARKER),
            [
                "phase15:feature_drift:"
                f"{EXPECTED_FEATURES[:-1] + ['- direct parity approval for frozen C areas']}"
            ],
            "features",
        )
        case_count += 1

        write_text(
            roadmap,
            good_roadmap_text().replace(
                EXPECTED_DISCIPLINE_LINE,
                "This phase is about velocity, not discipline.",
                1,
            ),
        )
        assert_only(check(root, MARKER), ["phase15:discipline_line_drift"], "discipline")
        case_count += 1

        write_text(
            roadmap,
            good_roadmap_text().replace(
                EXPECTED_DISCIPLINE_LINE,
                "Recommended Zigux destinations:\n- `kernel/*.zig`\n\n" + EXPECTED_DISCIPLINE_LINE,
                1,
            ),
        )
        assert_only(
            check(root, MARKER),
            ["phase15:unexpected_destinations_block"],
            "destinations",
        )
        case_count += 1

        swapped = good_roadmap_text().replace(PHASE15_HEADING, "__TEMP_PHASE15__", 1)
        swapped = swapped.replace(FREEZE_MAP_HEADING, PHASE15_HEADING, 1)
        swapped = swapped.replace("__TEMP_PHASE15__", FREEZE_MAP_HEADING, 1)
        write_text(roadmap, swapped)
        assert_only(
            check(root, MARKER),
            [
                "roadmap phase order drifted around Phase 15",
                "phase15:goal_drift",
                "phase15:anchor_drift:[]",
                "phase15:feature_drift:[]",
                "phase15:discipline_line_drift",
            ],
            "order",
        )
        case_count += 1

        write_text(roadmap, good_roadmap_text())
        assert_only(check(root, "missing"), ["checker marker missing from checker source"], "marker")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE15_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE15_SELF_TEST_CASES={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail-closed checker for the Lane 01 roadmap Phase 15 packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=repo_root(),
        help="Repository root containing zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests instead of checking a repo root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        for error in errors:
            print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE15_ERROR={error}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE15=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE15_REQUIRED_LINE_COUNT={EXPECTED_REQUIRED_LINE_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
