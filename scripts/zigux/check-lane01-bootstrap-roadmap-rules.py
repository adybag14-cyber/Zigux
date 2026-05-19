#!/usr/bin/env python3
"""Guard the Lane 01 roadmap Non-Negotiable Product Rules packet."""

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

PREV_HEADING = "## Licensing and Reuse Policy"
SECTION_HEADING = "## Non-Negotiable Product Rules"
NEXT_HEADING = "## How ZAR Should Feed Zigux"

EXPECTED_SECTION_LINES = (
    "These rules are consistent across the bundle and should govern every Zigux commit series.",
    "1. No flag-day rewrite.",
    "- Zigux grows through mixed-language coexistence.",
    "- C remains in place until each bounded area proves parity and maintainability.",
    "2. No mirror-tree sprawl.",
    "- Do not build a fake parallel kernel under a generic Zigux namespace.",
    "- `zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.",
    "3. Co-locate product code with Linux ownership.",
    "- Host-side helper ports belong beside current files such as `tools/lib/*.zig`.",
    "- Runtime helper ports belong beside current files such as `lib/*.zig`.",
    "- Driver pilots belong in current subsystem trees such as `drivers/virtio/*.zig`.",
    "4. Keep the Zigux support root small.",
    "- The support root exists for boundary code, not for duplicating Linux subsystems.",
    "- The intended long-term support root is:",
    "  - `zigux/kernel/`",
    "  - `zigux/helpers/`",
    "  - `zigux/bindings/`",
    "  - `zigux/uapi/`",
    "  - `zigux/tests/`",
    "  - `zigux/unsafe/`",
    "5. Port leaf helpers before shared runtime helpers.",
    "- Port shared runtime helpers before drivers.",
    "- Port simple drivers before high-throughput queueing and DMA-heavy drivers.",
    "6. Validation is mandatory before expansion.",
    "- Every approved target needs parity tests.",
    "- Every sensitive path needs a perf threshold.",
    "- Every migration needs a rollback owner.",
    "7. Wrapper-first or dual-implementation is the default where semantics are risky.",
    "- Build tooling",
    "- ABI/export surfaces",
    "- allocators",
    "- atomics and barriers",
    "- MMIO",
    "- virtio rings",
    "- DMA-sensitive drivers",
    "- tracing and queueing infrastructure",
    "8. Deep-core freeze is real.",
    "- Do not move these into active delivery before the roadmap says so:",
    "  - `kernel/sched/core.c`",
    "  - `mm/page_alloc.c`",
    "  - `kernel/rcu/tree.c`",
    "  - `net/core/skbuff.c`",
    "- Treat `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` as boundary-study targets first, not rewrite targets.",
    "9. Human review remains mandatory.",
    "- Follow Linux process expectations.",
    "- Use AI-assisted work only as a human-reviewed aid, not as an autonomous authority.",
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
        raise AssertionError("invalid heading order before rules section")

    if end <= start + 1:
        raise AssertionError("rules section is empty")

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

## Licensing and Reuse Policy

For Zigux product work, licensing is not the blocker.

## Non-Negotiable Product Rules

{section}

## How ZAR Should Feed Zigux

ZAR should not try to become Zigux.
"""


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(
            f"lane01-roadmap-rules-self-test:{label}:got={got}:want={want}"
        )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_roadmap_rules_") as tmp_dir:
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
                "- `zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_section_line:- `zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports."
            ],
            "missing_rule_detail",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace(
                "1. No flag-day rewrite.\n- Zigux grows through mixed-language coexistence.\n",
                "- Zigux grows through mixed-language coexistence.\n1. No flag-day rewrite.\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "misordered_section_line:1. No flag-day rewrite.:found_at=3:expected_at=2",
                "misordered_section_line:- Zigux grows through mixed-language coexistence.:found_at=2:expected_at=3",
            ],
            "misordered_rule_heading",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(path, _read(path).replace("  - `zigux/tests/`\n", "", 1))
        _assert_only(
            validate(root),
            ["missing_section_line:  - `zigux/tests/`"],
            "missing_support_root_entry",
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

    print("LANE01_BOOTSTRAP_ROADMAP_RULES_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_RULES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 01 roadmap Non-Negotiable Product Rules packet aligned."
    )
    parser.add_argument(
        "--self-test", action="store_true", help="Run isolated fixture coverage."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = validate(args.root)
    if problems:
        print("LANE01_BOOTSTRAP_ROADMAP_RULES=fail")
        print("LANE01_BOOTSTRAP_ROADMAP_RULES_ISSUES_START")
        for problem in problems:
            print(problem)
        print("LANE01_BOOTSTRAP_ROADMAP_RULES_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_RULES=pass")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_RULES_REQUIRED_LINE_COUNT="
        f"{len(EXPECTED_SECTION_LINES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
