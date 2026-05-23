#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
PREVIOUS_HEADING = "## Phase 5: Samples and Reference Patterns"
SECTION_HEADING = "## Phase 6: Greenfield Leaf Helpers"
NEXT_HEADING = "## Phase 7: In-Kernel Leaf Libraries"

EXPECTED_LINES = (
    "Primary product goal:",
    "- allow low-risk new helper code in Zigux without taking runtime-core risk",
    "Primary Linux anchors:",
    "- `lib/base64.c`",
    "- `lib/bsearch.c`",
    "- `lib/checksum.c`",
    "- `lib/hexdump.c`",
    "Required Zigux features:",
    "- leaf helper portability",
    "- clear API parity",
    "- perf gates for math-sensitive helpers",
    "Recommended Zigux destinations:",
    "- `lib/base64.zig`",
    "- `lib/bsearch.zig`",
    "- `lib/checksum.zig`",
    "- `lib/hexdump.zig`",
)


def roadmap_lines(root: Path) -> list[str]:
    return (root / ROADMAP_PATH).read_text(encoding="utf-8").splitlines()


def find_heading(lines: list[str], heading: str) -> int:
    try:
        return lines.index(heading)
    except ValueError as exc:
        raise AssertionError(f"missing heading: {heading}") from exc


def extract_phase6_packet(root: Path) -> tuple[str, ...]:
    lines = roadmap_lines(root)
    start = find_heading(lines, SECTION_HEADING)
    end = find_heading(lines, NEXT_HEADING)
    if start >= end:
        raise AssertionError("broken heading order: Phase6->Phase7")
    return tuple(line for line in lines[start + 1 : end] if line.strip())


def check_phase6(root: Path) -> list[str]:
    try:
        lines = roadmap_lines(root)
        prev_index = find_heading(lines, PREVIOUS_HEADING)
        phase6_index = find_heading(lines, SECTION_HEADING)
        next_index = find_heading(lines, NEXT_HEADING)
    except AssertionError as exc:
        return [str(exc)]

    if not (prev_index < phase6_index < next_index):
        return [
            "broken heading order",
            f"expected:{PREVIOUS_HEADING}->{SECTION_HEADING}->{NEXT_HEADING}",
            f"actual_indexes:{prev_index},{phase6_index},{next_index}",
        ]

    try:
        packet = extract_phase6_packet(root)
    except AssertionError as exc:
        return [str(exc)]

    if packet != EXPECTED_LINES:
        return [
            "phase6 packet mismatch",
            f"expected:{EXPECTED_LINES!r}",
            f"actual:{packet!r}",
        ]

    return []


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Phase 5: Samples and Reference Patterns

Primary product goal:
- make approved Zigux idioms reviewable and repeatable

## Phase 6: Greenfield Leaf Helpers

Primary product goal:
- allow low-risk new helper code in Zigux without taking runtime-core risk

Primary Linux anchors:
- `lib/base64.c`
- `lib/bsearch.c`
- `lib/checksum.c`
- `lib/hexdump.c`

Required Zigux features:
- leaf helper portability
- clear API parity
- perf gates for math-sensitive helpers

Recommended Zigux destinations:
- `lib/base64.zig`
- `lib/bsearch.zig`
- `lib/checksum.zig`
- `lib/hexdump.zig`

## Phase 7: In-Kernel Leaf Libraries

Primary product goal:
- bring the first reusable runtime helper families into the product path
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase6_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        errors = check_phase6(root)
        if errors:
            raise AssertionError(f"baseline Phase 6 fixture should pass: {errors}")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(SECTION_HEADING + "\n\n", "", 1))
        errors = check_phase6(root)
        if errors != [f"missing heading: {SECTION_HEADING}"]:
            raise AssertionError(f"unexpected missing Phase 6 heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(NEXT_HEADING + "\n\n", "", 1))
        errors = check_phase6(root)
        if errors != [f"missing heading: {NEXT_HEADING}"]:
            raise AssertionError(f"unexpected missing Phase 7 heading error: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- `lib/hexdump.c`\n", "", 1),
        )
        errors = check_phase6(root)
        if not errors or errors[0] != "phase6 packet mismatch":
            raise AssertionError(f"expected missing-anchor mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- clear API parity\n", "- exact API parity\n", 1),
        )
        errors = check_phase6(root)
        if not errors or errors[0] != "phase6 packet mismatch":
            raise AssertionError(f"expected feature drift mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- `lib/checksum.zig`\n", "", 1),
        )
        errors = check_phase6(root)
        if not errors or errors[0] != "phase6 packet mismatch":
            raise AssertionError(f"expected missing-destination mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "## Phase 5: Samples and Reference Patterns\n\nPrimary product goal:\n- make approved Zigux idioms reviewable and repeatable\n\n"
                "## Phase 6: Greenfield Leaf Helpers\n\n",
                "## Phase 6: Greenfield Leaf Helpers\n\n"
                "## Phase 5: Samples and Reference Patterns\n\nPrimary product goal:\n- make approved Zigux idioms reviewable and repeatable\n\n",
                1,
            ),
        )
        errors = check_phase6(root)
        if not errors or errors[0] != "broken heading order":
            raise AssertionError(f"expected heading-order mismatch, got: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "- perf gates for math-sensitive helpers\n",
                "- perf gates for math-sensitive helpers\n- narrow scope discipline\n",
                1,
            ),
        )
        errors = check_phase6(root)
        if not errors or errors[0] != "phase6 packet mismatch":
            raise AssertionError(f"expected widened-packet mismatch, got: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE6_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE6_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 6 packet remains aligned."
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
        help="exercise the checker against synthetic Phase 6 roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_phase6(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE6=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE6_REQUIRED_LINE_COUNT={len(EXPECTED_LINES)}")
    print("LANE01_BOOTSTRAP_ROADMAP_PHASE6_SECTION_ORDER=Phase5->Phase6->Phase7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
