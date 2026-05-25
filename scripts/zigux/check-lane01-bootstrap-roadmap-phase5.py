#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE4_HEADING = "## Phase 4: Differential Validation and Rollback"
PHASE5_HEADING = "## Phase 5: Samples and Reference Patterns"
PHASE6_HEADING = "## Phase 6: Greenfield Leaf Helpers"

REQUIRED_LINES = (
    "Primary product goal:",
    "- make approved Zigux idioms reviewable and repeatable",
    "Primary Linux anchors:",
    "- `samples/kfifo/bytestream-example.c`",
    "- `samples/kobject/kobject-example.c`",
    "- `samples/kprobes/kretprobe_example.c`",
    "- `samples/trace_events/trace-events-sample.c`",
    "Required Zigux features:",
    "- side-by-side sample ports",
    "- ownership and lifetime examples",
    "- tracing examples",
    "- review checklist and contributor guide",
    "Recommended Zigux destinations:",
    "- `samples/zigux/`",
    "- `Documentation/zigux/`",
)


def _extract_phase5_section(roadmap: str) -> tuple[str, int, int, int]:
    try:
        phase4_index = roadmap.index(PHASE4_HEADING)
        phase5_index = roadmap.index(PHASE5_HEADING)
        phase6_index = roadmap.index(PHASE6_HEADING)
    except ValueError as exc:
        raise AssertionError(f"missing section heading: {exc}") from exc

    if not phase4_index < phase5_index < phase6_index:
        raise AssertionError("Phase 4, Phase 5, and Phase 6 headings are out of order")

    return roadmap[phase5_index:phase6_index], phase4_index, phase5_index, phase6_index


def check_phase5(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    missing: list[str] = []

    try:
        phase5_section, _, _, _ = _extract_phase5_section(roadmap)
    except AssertionError as exc:
        return [str(exc)]

    for line in REQUIRED_LINES:
        if line not in phase5_section:
            missing.append(line)

    return missing


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    required_body = "\n".join(REQUIRED_LINES)
    return (
        "# ZAR to Zigux Product Roadmap\n\n"
        f"{PHASE4_HEADING}\n\n"
        "Primary product goal:\n"
        "- make every future Zigux port measurable and reversible\n\n"
        f"{PHASE5_HEADING}\n\n"
        f"{required_body}\n\n"
        f"{PHASE6_HEADING}\n\n"
        "Primary product goal:\n"
        "- allow low-risk new helper code in Zigux without taking runtime-core risk\n"
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase5_") as tmp_dir:
        root = Path(tmp_dir)
        roadmap_path = root / ROADMAP_PATH
        _write(roadmap_path, _sample_roadmap())

        if check_phase5(root):
            raise AssertionError("baseline Phase 5 roadmap fixture should pass")
        case_count += 1

        for missing_line in (
            "- `samples/kfifo/bytestream-example.c`",
            "- review checklist and contributor guide",
            "- `Documentation/zigux/`",
        ):
            _write(roadmap_path, _sample_roadmap().replace(f"{missing_line}\n", "", 1))
            missing = check_phase5(root)
            if missing != [missing_line]:
                raise AssertionError(f"unexpected missing markers for {missing_line}: {missing}")
            case_count += 1

        _write(roadmap_path, _sample_roadmap().replace(PHASE5_HEADING, "## Phase Five", 1))
        missing = check_phase5(root)
        if missing != ["missing section heading: substring not found"]:
            raise AssertionError(f"unexpected missing markers for missing Phase 5 heading: {missing}")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                f"{PHASE4_HEADING}\n\nPrimary product goal:\n- make every future Zigux port measurable and reversible\n\n",
                "",
                1,
            ),
        )
        missing = check_phase5(root)
        if missing != ["missing section heading: substring not found"]:
            raise AssertionError(f"unexpected missing markers for missing Phase 4 heading: {missing}")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                f"{PHASE6_HEADING}\n\nPrimary product goal:\n- allow low-risk new helper code in Zigux without taking runtime-core risk\n",
                "",
                1,
            ),
        )
        missing = check_phase5(root)
        if missing != ["missing section heading: substring not found"]:
            raise AssertionError(f"unexpected missing markers for missing Phase 6 heading: {missing}")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                f"{PHASE4_HEADING}\n\nPrimary product goal:\n- make every future Zigux port measurable and reversible\n\n"
                f"{PHASE5_HEADING}",
                f"{PHASE5_HEADING}\n\nPrimary product goal:\n- make approved Zigux idioms reviewable and repeatable\n\n"
                f"{PHASE4_HEADING}",
                1,
            ),
        )
        missing = check_phase5(root)
        if missing != ["Phase 4, Phase 5, and Phase 6 headings are out of order"]:
            raise AssertionError(f"unexpected missing markers for heading order case: {missing}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE5_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE5_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 roadmap Phase 5 packet stays aligned."
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
        help="exercise the checker against synthetic Phase 5 roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = check_phase5(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE5=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE5_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())