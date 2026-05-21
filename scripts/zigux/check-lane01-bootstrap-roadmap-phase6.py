#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE5_HEADING = "## Phase 5: Samples and Reference Patterns"
PHASE6_HEADING = "## Phase 6: Greenfield Leaf Helpers"
PHASE7_HEADING = "## Phase 7: In-Kernel Leaf Libraries"

REQUIRED_LINES = (
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


def _extract_phase6_section(roadmap: str) -> tuple[str, int, int, int]:
    try:
        phase5_index = roadmap.index(PHASE5_HEADING)
        phase6_index = roadmap.index(PHASE6_HEADING)
        phase7_index = roadmap.index(PHASE7_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing section heading: {exc}") from exc

    if not phase5_index < phase6_index < phase7_index:
        raise AssertionError("Phase 5, Phase 6, and Phase 7 headings are out of order")

    return roadmap[phase6_index:phase7_index], phase5_index, phase6_index, phase7_index


def check_phase6(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    missing: list[str] = []

    try:
        phase6_section, _, _, _ = _extract_phase6_section(roadmap)
    except AssertionError as exc:
        return [str(exc)]

    for line in REQUIRED_LINES:
        if line not in phase6_section:
            missing.append(line)

    return missing


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    required_body = "\n".join(REQUIRED_LINES)
    return (
        "# ZAR to Zigux Product Roadmap\n\n"
        f"{PHASE5_HEADING}\n\n"
        "Primary product goal:\n"
        "- make approved Zigux idioms reviewable and repeatable\n\n"
        f"{PHASE6_HEADING}\n\n"
        f"{required_body}\n\n"
        f"{PHASE7_HEADING}\n\n"
        "Primary product goal:\n"
        "- bring the first reusable runtime helper families into the product path\n"
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase6_") as tmp_dir:
        root = Path(tmp_dir)
        roadmap_path = root / ROADMAP_PATH
        _write(roadmap_path, _sample_roadmap())

        if check_phase6(root):
            raise AssertionError("baseline Phase 6 roadmap fixture should pass")
        case_count += 1

        for missing_line in (
            "- `lib/base64.c`",
            "- perf gates for math-sensitive helpers",
            "- `lib/hexdump.zig`",
        ):
            _write(roadmap_path, _sample_roadmap().replace(f"{missing_line}\n", "", 1))
            missing = check_phase6(root)
            if missing != [missing_line]:
                raise AssertionError(f"unexpected missing markers for {missing_line}: {missing}")
            case_count += 1

        _write(roadmap_path, _sample_roadmap().replace(PHASE6_HEADING, "## Phase Six", 1))
        missing = check_phase6(root)
        if missing != ["missing section heading: substring not found"]:
            raise AssertionError(f"unexpected missing markers for missing Phase 6 heading: {missing}")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                f"{PHASE5_HEADING}\n\nPrimary product goal:\n- make approved Zigux idioms reviewable and repeatable\n\n",
                "",
                1,
            ),
        )
        missing = check_phase6(root)
        if missing != ["missing section heading: substring not found"]:
            raise AssertionError(f"unexpected missing markers for missing Phase 5 heading: {missing}")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                f"{PHASE7_HEADING}\n\nPrimary product goal:\n- bring the first reusable runtime helper families into the product path\n",
                "",
                1,
            ),
        )
        missing = check_phase6(root)
        if missing != ["missing section heading: substring not found"]:
            raise AssertionError(f"unexpected missing markers for missing Phase 7 heading: {missing}")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                f"{PHASE5_HEADING}\n\nPrimary product goal:\n- make approved Zigux idioms reviewable and repeatable\n\n"
                f"{PHASE6_HEADING}",
                f"{PHASE6_HEADING}\n\nPrimary product goal:\n- allow low-risk new helper code in Zigux without taking runtime-core risk\n\n"
                f"{PHASE5_HEADING}",
                1,
            ),
        )
        missing = check_phase6(root)
        if missing != ["Phase 5, Phase 6, and Phase 7 headings are out of order"]:
            raise AssertionError(f"unexpected missing markers for heading order case: {missing}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE6_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE6_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 roadmap Phase 6 packet stays aligned."
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

    missing = check_phase6(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE6=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE6_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
