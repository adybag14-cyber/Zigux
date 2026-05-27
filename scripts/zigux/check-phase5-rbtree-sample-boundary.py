#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

GUIDE_PATH = Path("Documentation/zigux/phase5-sample-review-guide.md")
LANE_SEQUENCING_PATH = Path("Documentation/zigux/phase5-sample-lane-sequencing.md")
SAMPLE_ROOT_PATH = Path("samples/zigux/README.md")
SCRIPTS_ROOT_PATH = Path("scripts/zigux/README.md")
TESTS_ROOT_PATH = Path("zigux/tests/README.md")

TRACKED_PATHS = (
    GUIDE_PATH,
    LANE_SEQUENCING_PATH,
    SAMPLE_ROOT_PATH,
    SCRIPTS_ROOT_PATH,
    TESTS_ROOT_PATH,
)

REQUIRED_TEXT = {
    GUIDE_PATH: (
        "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
        "Keep those helper-family reminders tied to their existing helper, closure, or later-phase packets instead of treating the sample root as proof they landed here.",
    ),
    LANE_SEQUENCING_PATH: (
        "there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`",
    ),
    SAMPLE_ROOT_PATH: (
        "* `*rbtree*`",
        "Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated string, cmdline, argv, rbtree, kasprintf, strarray, printf, vsprintf, or broad format samples have landed here.",
    ),
    SCRIPTS_ROOT_PATH: (
        "keep the no-extra-sample boundary explicit from the scripts root too: do not treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence, and do not treat standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 scripts-root packet.",
    ),
    TESTS_ROOT_PATH: (
        "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
    ),
}


def read_text(root: Path, rel_path: Path) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: Path, text: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def placeholder(rel_path: Path) -> str:
    return "\n".join(REQUIRED_TEXT[rel_path]) + "\n"


def seed(root: Path) -> None:
    for rel_path in TRACKED_PATHS:
        write_text(root, rel_path, placeholder(rel_path))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path, required_markers in REQUIRED_TEXT.items():
        text = read_text(root, rel_path)
        for marker in required_markers:
            if marker not in text:
                failures.append(f"{rel_path}:missing_text:{marker}")
    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="phase5_rbtree_boundary_") as tmpdir:
        root = Path(tmpdir)
        seed(root)
        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_guide_boundary"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH).replace(REQUIRED_TEXT[GUIDE_PATH][0], ""))
        expect_exact(
            "missing guide boundary",
            collect_failures(mutated),
            [f"{GUIDE_PATH}:missing_text:{REQUIRED_TEXT[GUIDE_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "missing_guide_scope"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH).replace(REQUIRED_TEXT[GUIDE_PATH][1], ""))
        expect_exact(
            "missing guide scope",
            collect_failures(mutated),
            [f"{GUIDE_PATH}:missing_text:{REQUIRED_TEXT[GUIDE_PATH][1]}"],
        )
        checks_run += 1

        mutated = root / "missing_lane_boundary"
        seed(mutated)
        write_text(mutated, LANE_SEQUENCING_PATH, placeholder(LANE_SEQUENCING_PATH).replace(REQUIRED_TEXT[LANE_SEQUENCING_PATH][0], ""))
        expect_exact(
            "missing lane boundary",
            collect_failures(mutated),
            [f"{LANE_SEQUENCING_PATH}:missing_text:{REQUIRED_TEXT[LANE_SEQUENCING_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "missing_sample_root_boundary"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder(SAMPLE_ROOT_PATH).replace(REQUIRED_TEXT[SAMPLE_ROOT_PATH][0], ""))
        expect_exact(
            "missing sample-root boundary",
            collect_failures(mutated),
            [f"{SAMPLE_ROOT_PATH}:missing_text:{REQUIRED_TEXT[SAMPLE_ROOT_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "missing_scripts_root_boundary"
        seed(mutated)
        write_text(mutated, SCRIPTS_ROOT_PATH, placeholder(SCRIPTS_ROOT_PATH).replace(REQUIRED_TEXT[SCRIPTS_ROOT_PATH][0], ""))
        expect_exact(
            "missing scripts-root boundary",
            collect_failures(mutated),
            [f"{SCRIPTS_ROOT_PATH}:missing_text:{REQUIRED_TEXT[SCRIPTS_ROOT_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "missing_tests_root_boundary"
        seed(mutated)
        write_text(mutated, TESTS_ROOT_PATH, placeholder(TESTS_ROOT_PATH).replace(REQUIRED_TEXT[TESTS_ROOT_PATH][0], ""))
        expect_exact(
            "missing tests-root boundary",
            collect_failures(mutated),
            [f"{TESTS_ROOT_PATH}:missing_text:{REQUIRED_TEXT[TESTS_ROOT_PATH][0]}"],
        )
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} self-test cases, ran {checks_run}")

    print("PHASE5_RBTREE_SAMPLE_BOUNDARY_SELF_TEST=pass")
    print(f"PHASE5_RBTREE_SAMPLE_BOUNDARY_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT.parent.parent.parent, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_RBTREE_SAMPLE_BOUNDARY=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE5_RBTREE_SAMPLE_BOUNDARY=pass")
    print(f"PHASE5_RBTREE_SAMPLE_BOUNDARY_PATH_COUNT={len(TRACKED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())