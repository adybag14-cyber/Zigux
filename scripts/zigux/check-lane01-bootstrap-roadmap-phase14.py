#!/usr/bin/env python3
"""LANE01_BOOTSTRAP_ROADMAP_PHASE14_CHECK=core_adjacent_bounded_internals

Fail-closed checker for the Lane 01 roadmap Phase 14 packet.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

MARKER = "LANE01_BOOTSTRAP_ROADMAP_PHASE14_CHECK=core_adjacent_bounded_internals"
ROADMAP_PATH = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"

PHASE12_HEADING = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers"
PHASE13_HEADING = "## Phase 13: Shared Subsystem Helpers"
PHASE14_HEADING = "## Phase 14: Core-Adjacent Bounded Internals"
PHASE15_HEADING = "## Phase 15: Full-Parity Blockers and Long-Term Governance"

EXPECTED_GOAL = "- study or wrap critical shared infrastructure without claiming premature parity"
EXPECTED_ANCHORS = [
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "- `net/core/skbuff.c`",
    "- `kernel/rcu/tree.c`",
]
EXPECTED_FEATURES = [
    "- boundary maps",
    "- concurrency audits",
    "- explicit stay-in-C decisions where warranted",
    "- wrapper-first or study-only posture",
]
EXPECTED_DESTINATIONS = [
    "- `kernel/workqueue_bridge.zig`",
    "- `kernel/trace/ring_buffer.zig` only if years of evidence justify it",
    "- `net/core/skbuff_bridge.zig`",
    "- `kernel/rcu/tree_bridge.zig`",
]
EXPECTED_REQUIRED_LINE_COUNT = 18


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
    section = extract_section(lines, PHASE14_HEADING)
    if section is None:
        return errors + [f"missing heading: {PHASE14_HEADING}"]

    section_text = "\n".join(section)
    phase12_index = roadmap_text.find(PHASE12_HEADING)
    phase13_index = roadmap_text.find(PHASE13_HEADING)
    phase14_index = roadmap_text.find(PHASE14_HEADING)
    phase15_index = roadmap_text.find(PHASE15_HEADING)
    if -1 in (phase12_index, phase13_index, phase14_index, phase15_index):
        errors.append("phase order anchors missing")
    elif not (phase12_index < phase13_index < phase14_index < phase15_index):
        errors.append("roadmap phase order drifted around Phases 12-15")

    if EXPECTED_GOAL not in section:
        errors.append("phase14:goal_drift")

    anchors = extract_bullets(section, "Primary Linux anchors:")
    if anchors != EXPECTED_ANCHORS:
        errors.append(f"phase14:anchor_drift:{anchors}")

    features = extract_bullets(section, "Required Zigux features:")
    if features != EXPECTED_FEATURES:
        errors.append(f"phase14:feature_drift:{features}")

    destinations = extract_bullets(section, "Recommended Zigux destinations:")
    if destinations != EXPECTED_DESTINATIONS:
        errors.append(f"phase14:destination_drift:{destinations}")

    required_line_count = (
        1
        + 1
        + 1
        + 1
        + len(EXPECTED_ANCHORS)
        + 1
        + len(EXPECTED_FEATURES)
        + 1
        + len(EXPECTED_DESTINATIONS)
    )
    if required_line_count != EXPECTED_REQUIRED_LINE_COUNT:
        errors.append(f"phase14:required_line_formula_drift:{required_line_count}")

    if PHASE14_HEADING not in section_text:
        errors.append("phase14:section_heading_missing_after_extract")

    return errors


def good_roadmap_text() -> str:
    return "\n".join(
        [
            "# ZAR to Zigux Product Roadmap",
            "",
            PHASE12_HEADING,
            "",
            "placeholder",
            "",
            PHASE13_HEADING,
            "",
            "placeholder",
            "",
            PHASE14_HEADING,
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
            "Recommended Zigux destinations:",
            *EXPECTED_DESTINATIONS,
            "",
            PHASE15_HEADING,
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
    with tempfile.TemporaryDirectory(prefix="lane01_bootstrap_phase14_") as temp_dir:
        root = Path(temp_dir)
        roadmap = root / ROADMAP_PATH

        write_text(roadmap, good_roadmap_text())
        assert_only(check(root, MARKER), [], "baseline")
        case_count += 1

        write_text(roadmap, good_roadmap_text().replace(PHASE14_HEADING, "## Phase 14: Drifted", 1))
        assert_only(check(root, MARKER), [f"missing heading: {PHASE14_HEADING}"], "heading")
        case_count += 1

        write_text(roadmap, good_roadmap_text().replace(EXPECTED_ANCHORS[-1], "- `kernel/rcu/tasks.c`", 1))
        assert_only(
            check(root, MARKER),
            [f"phase14:anchor_drift:{EXPECTED_ANCHORS[:-1] + ['- `kernel/rcu/tasks.c`']}"],
            "anchors",
        )
        case_count += 1

        write_text(
            roadmap,
            good_roadmap_text().replace(
                EXPECTED_FEATURES[-1], "- direct parity claims for frozen internals", 1
            ),
        )
        assert_only(
            check(root, MARKER),
            [
                "phase14:feature_drift:"
                f"{EXPECTED_FEATURES[:-1] + ['- direct parity claims for frozen internals']}"
            ],
            "features",
        )
        case_count += 1

        write_text(roadmap, good_roadmap_text().replace(EXPECTED_DESTINATIONS[1], "- `kernel/trace/*.zig`", 1))
        assert_only(
            check(root, MARKER),
            [f"phase14:destination_drift:{[EXPECTED_DESTINATIONS[0], '- `kernel/trace/*.zig`', *EXPECTED_DESTINATIONS[2:]]}"],
            "destinations",
        )
        case_count += 1

        swapped = good_roadmap_text().replace(PHASE13_HEADING, "__TEMP_PHASE13__", 1)
        swapped = swapped.replace(PHASE14_HEADING, PHASE13_HEADING, 1)
        swapped = swapped.replace("__TEMP_PHASE13__", PHASE14_HEADING, 1)
        write_text(roadmap, swapped)
        assert_only(
            check(root, MARKER),
            [
                "roadmap phase order drifted around Phases 12-15",
                "phase14:goal_drift",
                "phase14:anchor_drift:[]",
                "phase14:feature_drift:[]",
                "phase14:destination_drift:[]",
            ],
            "order",
        )
        case_count += 1

        write_text(roadmap, good_roadmap_text())
        assert_only(check(root, "missing"), ["checker marker missing from checker source"], "marker")
        case_count += 1

        roadmap.unlink()
        assert_only(check(root, MARKER), [f"missing file: {ROADMAP_PATH}"], "missing_file")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE14_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE14_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=repo_root())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE14=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE14_REQUIRED_LINE_COUNT={EXPECTED_REQUIRED_LINE_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
