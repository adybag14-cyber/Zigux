#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
ROADMAP_REL = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SECTION_HEADING = "## Phase 13: Shared Subsystem Helpers"
PREVIOUS_HEADING = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers"
NEXT_HEADING = "## Phase 14: Core-Adjacent Bounded Internals"

EXPECTED_SECTION_LINES = (
    "Primary product goal:",
    "- port bounded helper layers shared across multiple runtime consumers",
    "Primary Linux anchors:",
    "- `fs/libfs.c`",
    "- `lib/devres.c`",
    "- `security/landlock/ruleset.c`",
    "- `security/landlock/syscalls.c`",
    "Required Zigux features:",
    "- filesystem helper wrappers",
    "- resource lifetime helpers",
    "- bounded security helper pilots",
    "Recommended Zigux destinations:",
    "- `fs/libfs.zig`",
    "- `lib/devres.zig`",
    "- `security/landlock/*.zig`",
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
        start = lines.index(SECTION_HEADING)
    except ValueError as exc:
        raise AssertionError("missing Phase 13 heading") from exc

    try:
        end = lines.index(NEXT_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError("missing Phase 14 heading") from exc

    if end <= start + 1:
        raise AssertionError("phase13 section is empty")

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

    content = _read(roadmap)
    heading_positions = []
    missing_heading = False
    for heading, error in (
        (PREVIOUS_HEADING, "missing Phase 12 heading"),
        (SECTION_HEADING, "missing Phase 13 heading"),
        (NEXT_HEADING, "missing Phase 14 heading"),
    ):
        position = content.find(heading)
        if position == -1:
            problems.append(error)
            missing_heading = True
        heading_positions.append(position)

    if not missing_heading and heading_positions != sorted(heading_positions):
        problems.append("order:Phase12->Phase13->Phase14")

    return problems


def _sample_roadmap() -> str:
    section = "\n".join(EXPECTED_SECTION_LINES)
    return f"""# ZAR to Zigux Product Roadmap

{PREVIOUS_HEADING}

Primary product goal:
- take on high-value, high-risk drivers only after earlier proof

{SECTION_HEADING}

{section}

{NEXT_HEADING}

Primary product goal:
- study or wrap critical shared infrastructure without claiming premature parity
"""


def write_sample_root(root: Path) -> None:
    _write(root / ROADMAP_REL, _sample_roadmap())


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"lane01-roadmap-phase13-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_roadmap_phase13_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace(f"{SECTION_HEADING}\n\n", "", 1))
        _assert_only(validate(root), ["missing Phase 13 heading"], "missing_section_heading")
        write_sample_root(root)
        case_count += 1

        path = root / ROADMAP_REL
        _write(
            path,
            _read(path).replace(
                "- port bounded helper layers shared across multiple runtime consumers\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_section_line:- port bounded helper layers shared across multiple runtime consumers"
            ],
            "missing_goal_line",
        )
        write_sample_root(root)
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace("- `security/landlock/syscalls.c`\n", "", 1))
        _assert_only(
            validate(root),
            ["missing_section_line:- `security/landlock/syscalls.c`"],
            "missing_anchor",
        )
        write_sample_root(root)
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace("- bounded security helper pilots\n", "", 1))
        _assert_only(
            validate(root),
            ["missing_section_line:- bounded security helper pilots"],
            "missing_feature",
        )
        write_sample_root(root)
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace("- `security/landlock/*.zig`\n", "", 1))
        _assert_only(
            validate(root),
            ["missing_section_line:- `security/landlock/*.zig`"],
            "missing_destination",
        )
        write_sample_root(root)
        case_count += 1

        path = root / ROADMAP_REL
        _write(
            path,
            _read(path).replace(
                "- `fs/libfs.c`\n- `lib/devres.c`\n",
                "- `lib/devres.c`\n- `fs/libfs.c`\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "misordered_section_line:- `fs/libfs.c`:found_at=5:expected_at=4",
                "misordered_section_line:- `lib/devres.c`:found_at=4:expected_at=5",
            ],
            "misordered_anchors",
        )
        write_sample_root(root)
        case_count += 1

        path = root / ROADMAP_REL
        _write(path, _read(path).replace(f"{NEXT_HEADING}\n\n", "", 1))
        _assert_only(validate(root), ["missing Phase 14 heading"], "missing_next_heading")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE13_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE13_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 01 roadmap Phase 13 packet aligned with the bootstrap charter."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root for focused local validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"Wrote sample root to {args.write_sample_root}")
        return 0

    problems = validate(args.root)
    if problems:
        print("LANE01_BOOTSTRAP_ROADMAP_PHASE13=fail")
        print("LANE01_BOOTSTRAP_ROADMAP_PHASE13_ISSUES_START")
        for problem in problems:
            print(problem)
        print("LANE01_BOOTSTRAP_ROADMAP_PHASE13_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE13=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE13_REQUIRED_LINE_COUNT={len(EXPECTED_SECTION_LINES)}")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_PHASE13_SECTION_ORDER="
        f"{PREVIOUS_HEADING.removeprefix('## ').replace(' ', '')}->"
        f"{SECTION_HEADING.removeprefix('## ').replace(' ', '')}->"
        f"{NEXT_HEADING.removeprefix('## ').replace(' ', '')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
