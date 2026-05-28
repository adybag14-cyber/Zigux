#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
SECTION_HEADER = "## Next Step"

REQUIRED_SECTION_MARKERS = (
    "Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
    "If the kconfig bridge lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step that preserves the live split between request-plan overrides, the non-empty sentinel packet, and helper-local explicit-override coverage, then add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again on current `master`.",
    "If the `genksyms` lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step around the still-missing CRC-side evidence recorded in the survey rather than widening this shared note again.",
    "request-plan overrides",
    "non-empty sentinel packet",
    "helper-local explicit-override coverage",
    "`conf.c` / `confdata.c` provenance anchor",
    "current `master`",
    "still-missing CRC-side evidence",
    "survey",
    "widening this shared note again",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_next_step(text: str) -> str:
    header_marker = SECTION_HEADER + "\n"
    if header_marker not in text:
        raise SystemExit(
            f"required note section missing: {PHASE2_CLOSURE_REL}: {SECTION_HEADER}"
        )
    return text.split(header_marker, 1)[1]


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    next_step_text = extract_next_step(closure_text)
    issues: list[tuple[str, str]] = []

    header_count = count_exact_lines(closure_text, SECTION_HEADER)
    if header_count != 1:
        issues.append(("EXACT_HEADER_COUNT", f"{header_count}::{SECTION_HEADER}"))

    for marker in REQUIRED_SECTION_MARKERS:
        if marker not in next_step_text:
            issues.append(("MISSING_SECTION_MARKER", marker))

    if next_step_text.count("If the ") != 2:
        issues.append(("EXACT_BRANCH_COUNT", f"{next_step_text.count('If the ')}::If the "))

    if next_step_text.count("shared reminder surface drifts again") != 1:
        issues.append(
            (
                "EXACT_PARKED_GUIDANCE_COUNT",
                f"{next_step_text.count('shared reminder surface drifts again')}::shared reminder surface drifts again",
            )
        )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_NEXT_SAFE_STEP=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root / PHASE2_CLOSURE_REL,
        """# Phase 2 Closure

## Next Step

Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again. If the kconfig bridge lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step that preserves the live split between request-plan overrides, the non-empty sentinel packet, and helper-local explicit-override coverage, then add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again on current `master`. If the `genksyms` lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step around the still-missing CRC-side evidence recorded in the survey rather than widening this shared note again.
""",
    )


def write_sample_root(root: Path) -> int:
    build_sample_root(root)
    print(f"PHASE2_NEXT_SAFE_STEP_SAMPLE_ROOT={root}")
    return 0


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_next_safe_step_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        write_text(
            closure_path,
            read_text(closure_path).replace("shared reminder surface drifts again", "shared drift returns", 1),
        )
        assert (
            "MISSING_SECTION_MARKER",
            "Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        write_text(
            closure_path,
            read_text(closure_path).replace("non-empty sentinel packet", "sentinel packet", 1),
        )
        assert ("MISSING_SECTION_MARKER", "non-empty sentinel packet") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        write_text(
            closure_path,
            read_text(closure_path).replace("If the `genksyms` lane", "When the `genksyms` lane", 1),
        )
        assert ("EXACT_BRANCH_COUNT", "1::If the ") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        write_text(
            closure_path,
            read_text(closure_path).replace("## Next Step\n", "## Next Step\n## Next Step\n", 1),
        )
        assert ("EXACT_HEADER_COUNT", f"2::{SECTION_HEADER}") in collect_issues(root)
        checks_run += 1

    print("PHASE2_NEXT_SAFE_STEP_SELF_TEST=pass")
    print(f"PHASE2_NEXT_SAFE_STEP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure note next-step guidance aligned."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in self-test")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root.resolve())

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_NEXT_SAFE_STEP=pass")
    print(f"PHASE2_NEXT_SAFE_STEP_MARKER_COUNT={len(REQUIRED_SECTION_MARKERS)}")
    print("PHASE2_NEXT_SAFE_STEP_BRANCH_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
