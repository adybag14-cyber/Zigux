#!/usr/bin/env python3
"""Guard the Lane 01 roadmap First Commit and Push Sequence packet."""

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

PREV_HEADING = "## Risk Register That Must Drive Prioritization"
SECTION_HEADING = "## First Commit and Push Sequence for Zigux"
NEXT_HEADING = "## Recommended Validation Gates"

EXPECTED_SECTION_LINES = (
    "This is the recommended near-term commit train after this roadmap lands.",
    "### Bootstrap commits",
    "1. `docs(zigux-alpha): establish roadmap and folder charter`",
    "- add `zigux-alpha/README.md`",
    "- add this roadmap",
    "2. `docs(Documentation/zigux): add program charter and freeze map`",
    "- create `Documentation/zigux/README.md`",
    "- create `Documentation/zigux/review-checklist.md`",
    "- create `Documentation/zigux/freeze-map.md`",
    "3. `build(scripts/zigux): add toolchain pinning and version checks`",
    "- create `scripts/zigux/`",
    "- add Zig toolchain version policy",
    "- add deterministic version-check helper",
    "4. `test(zigux/tests): add differential harness scaffolding`",
    "- create `zigux/tests/`",
    "- add bitmap and atomic parity harness scaffolds",
    "- add artifact-diff scaffolds for host-side tools",
    "### Phase 1 commits",
    "5. `feat(tools/lib): add bitmap.zig host helper port`",
    "6. `feat(tools/lib): add find_bit.zig host helper port`",
    "7. `feat(tools/lib): add string.zig host helper port`",
    "8. `feat(tools/lib): add rbtree.zig host helper port`",
    "9. `test(tools/lib): add golden-output parity gates for alpha helper ports`",
    "### Phase 2 commits",
    "10. `feat(scripts/zigux): add fixdep dual implementation`",
    "11. `feat(scripts/zigux): add genksyms dual implementation`",
    "12. `feat(scripts/zigux): add kconfig bridge scaffolding`",
    "13. `ci(zigux): add cross-arch build and artifact diff matrix`",
    "### Phase 3 and 4 commits",
    "14. `feat(zigux): add ABI, bindings, and export substrate skeleton`",
    "15. `test(zigux/tests): add atomic64 and runtime bitmap differential gates`",
    "16. `docs(Documentation/zigux): add unsafe policy and interop rules`",
    "### Phase 5 commits",
    "17. `feat(samples/zigux): add reference samples for fifo, kobject, kretprobe, and trace events`",
    "18. `docs(Documentation/zigux): add sample-backed review guide`",
    "Do not schedule Phase 10+ commits until the earlier gates are actually green.",
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
        raise AssertionError("invalid heading order before commit-sequence section")

    if end <= start + 1:
        raise AssertionError("commit-sequence section is empty")

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

## Risk Register That Must Drive Prioritization

The highest-risk items from the bundle are the ones that must shape scope:
- mirror-tree sprawl

## First Commit and Push Sequence for Zigux

{section}

## Recommended Validation Gates

Every approved Zigux slice should declare and satisfy these gates.
"""


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"lane01-roadmap-commit-sequence-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_roadmap_commit_sequence_") as tmp_dir:
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
                "3. `build(scripts/zigux): add toolchain pinning and version checks`\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_section_line:3. `build(scripts/zigux): add toolchain pinning and version checks`"
            ],
            "missing_bootstrap_commit",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace(
                "### Phase 2 commits\n10. `feat(scripts/zigux): add fixdep dual implementation`\n",
                "10. `feat(scripts/zigux): add fixdep dual implementation`\n### Phase 2 commits\n",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "misordered_section_line:### Phase 2 commits:found_at=25:expected_at=24",
                "misordered_section_line:10. `feat(scripts/zigux): add fixdep dual implementation`:found_at=24:expected_at=25",
            ],
            "misordered_phase_sections",
        )
        _write(path, _sample_roadmap())
        case_count += 1

        _write(
            path,
            _read(path).replace(
                "Do not schedule Phase 10+ commits until the earlier gates are actually green.\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "missing_section_line:Do not schedule Phase 10+ commits until the earlier gates are actually green."
            ],
            "missing_closeout_rule",
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

    print("LANE01_BOOTSTRAP_ROADMAP_COMMIT_SEQUENCE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_COMMIT_SEQUENCE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 01 First Commit and Push Sequence roadmap packet aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = validate(args.root)
    if problems:
        print("LANE01_BOOTSTRAP_ROADMAP_COMMIT_SEQUENCE=fail")
        print("LANE01_BOOTSTRAP_ROADMAP_COMMIT_SEQUENCE_ISSUES_START")
        for problem in problems:
            print(problem)
        print("LANE01_BOOTSTRAP_ROADMAP_COMMIT_SEQUENCE_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_COMMIT_SEQUENCE=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_COMMIT_SEQUENCE_REQUIRED_LINE_COUNT={len(EXPECTED_SECTION_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
