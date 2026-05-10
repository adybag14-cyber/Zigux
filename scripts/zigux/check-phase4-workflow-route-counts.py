#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_MAKEFILE_LINES = [
    "$(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test",
    "$(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py",
]

REQUIRED_WORKFLOW_COUNTS = {
    "run: make -C zigux phase4-validate": 1,
    "run: python3 scripts/zigux/validate-phase4.py --self-test": 1,
    "run: python3 scripts/zigux/validate-phase4.py": 1,
    "run: zig build test --build-file zigux/tests/phase4_build.zig": 1,
}

FORBIDDEN_WORKFLOW_LINES = [
    "run: python3 scripts/zigux/artifact_diff.py --self-test",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "run: python3 scripts/zigux/check-phase4-gate-evidence.py",
]

EXPECTED_SELF_TEST_CASES = [
    "makefile_line_missing",
    "makefile_line_duplicate",
    "workflow_make_route_missing",
    "workflow_make_route_duplicate",
    "workflow_direct_validator_missing",
    "workflow_phase4_test_missing",
    "workflow_forbidden_direct_helper_route",
]


def _normalize_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()]


def _count_text(haystack: str, needle: str) -> int:
    return sum(1 for line in _normalize_lines(haystack) if line == needle)


def _require_exact_count(problems: list[str], haystack: str, needle: str, expected: int, label: str) -> None:
    actual = _count_text(haystack, needle)
    if actual != expected:
        problems.append(f"{label}:{needle}:{actual}:{expected}")


def _require_absent(problems: list[str], haystack: str, needle: str, label: str) -> None:
    actual = _count_text(haystack, needle)
    if actual != 0:
        problems.append(f"{label}:{needle}:{actual}:0")


def check_makefile(makefile_text: str) -> list[str]:
    problems: list[str] = []
    for line in EXPECTED_MAKEFILE_LINES:
        _require_exact_count(problems, makefile_text, line, 1, "makefile")
    return problems


def check_workflow(workflow_text: str) -> list[str]:
    problems: list[str] = []
    for line, expected in REQUIRED_WORKFLOW_COUNTS.items():
        _require_exact_count(problems, workflow_text, line, expected, "workflow")
    for line in FORBIDDEN_WORKFLOW_LINES:
        _require_absent(problems, workflow_text, line, "workflow_forbidden")
    return problems


def run_live_check(root: Path) -> list[str]:
    makefile_text = (root / "zigux/Makefile").read_text(encoding="utf-8")
    workflow_text = (root / ".github/workflows/zigux-bootstrap.yml").read_text(encoding="utf-8")
    return [
        *check_makefile(makefile_text),
        *check_workflow(workflow_text),
    ]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_fixture_tree(root: Path) -> None:
    _write(
        root / "zigux/Makefile",
        "\n".join(
            [
                "phase4-validate:",
                *[f"\t{line}" for line in EXPECTED_MAKEFILE_LINES],
                "",
            ]
        ),
    )
    _write(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Validate Phase 4 diff gates",
                "        run: make -C zigux phase4-validate",
                "      - name: Self-test Phase 4 validator directly",
                "        run: python3 scripts/zigux/validate-phase4.py --self-test",
                "      - name: Validate Phase 4 diff packet directly",
                "        run: python3 scripts/zigux/validate-phase4.py",
                "      - name: Run Phase 4 diff tests directly",
                "        run: zig build test --build-file zigux/tests/phase4_build.zig",
                "",
            ]
        ),
    )


def expect_problems(label: str, callback, expected_problem_prefix: str) -> None:
    problems = callback()
    if not problems:
        raise AssertionError(f"expected problems for self-test case {label}")
    if not any(problem.startswith(expected_problem_prefix) for problem in problems):
        raise AssertionError(
            f"expected {expected_problem_prefix!r} in self-test case {label}, got {problems}"
        )


def run_self_test() -> None:
    covered_cases: list[str] = []
    with tempfile.TemporaryDirectory(prefix="phase4_workflow_route_counts_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        if run_live_check(root):
            raise AssertionError(f"expected clean fixture tree, got {run_live_check(root)}")

        makefile_path = root / "zigux/Makefile"
        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"

        makefile_path.write_text("phase4-validate:\n", encoding="utf-8")
        expect_problems("makefile_line_missing", lambda: run_live_check(root), "makefile:")
        covered_cases.append("makefile_line_missing")
        build_fixture_tree(root)

        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8")
            + f"\t{EXPECTED_MAKEFILE_LINES[0]}\n",
            encoding="utf-8",
        )
        expect_problems("makefile_line_duplicate", lambda: run_live_check(root), "makefile:")
        covered_cases.append("makefile_line_duplicate")
        build_fixture_tree(root)

        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "        run: make -C zigux phase4-validate\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_problems(
            "workflow_make_route_missing",
            lambda: run_live_check(root),
            "workflow:run: make -C zigux phase4-validate:",
        )
        covered_cases.append("workflow_make_route_missing")
        build_fixture_tree(root)

        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8")
            + "      - name: Duplicate Phase 4 diff gates\n        run: make -C zigux phase4-validate\n",
            encoding="utf-8",
        )
        expect_problems(
            "workflow_make_route_duplicate",
            lambda: run_live_check(root),
            "workflow:run: make -C zigux phase4-validate:",
        )
        covered_cases.append("workflow_make_route_duplicate")
        build_fixture_tree(root)

        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/validate-phase4.py\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_problems(
            "workflow_direct_validator_missing",
            lambda: run_live_check(root),
            "workflow:run: python3 scripts/zigux/validate-phase4.py:",
        )
        covered_cases.append("workflow_direct_validator_missing")
        build_fixture_tree(root)

        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "        run: zig build test --build-file zigux/tests/phase4_build.zig\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_problems(
            "workflow_phase4_test_missing",
            lambda: run_live_check(root),
            "workflow:run: zig build test --build-file zigux/tests/phase4_build.zig:",
        )
        covered_cases.append("workflow_phase4_test_missing")
        build_fixture_tree(root)

        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8")
            + "      - name: Forbidden direct helper replay\n        run: python3 scripts/zigux/check-artifact-diff-contract.py\n",
            encoding="utf-8",
        )
        expect_problems(
            "workflow_forbidden_direct_helper_route",
            lambda: run_live_check(root),
            "workflow_forbidden:run: python3 scripts/zigux/check-artifact-diff-contract.py:",
        )
        covered_cases.append("workflow_forbidden_direct_helper_route")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"workflow-route self-test catalog drifted: expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )
    print("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass")
    print(f"PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}")
    print("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES=" + ",".join(EXPECTED_SELF_TEST_CASES))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 4 artifact-diff CI route stays aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    problems = run_live_check(ROOT)
    if problems:
        print("PHASE4_WORKFLOW_ROUTE_COUNTS=fail")
        print("PHASE4_WORKFLOW_ROUTE_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE4_WORKFLOW_ROUTE_PROBLEMS_END")
        return 1

    print("PHASE4_WORKFLOW_ROUTE_COUNTS=pass")
    print(f"PHASE4_WORKFLOW_REQUIRED_MARKER_COUNT={len(EXPECTED_MAKEFILE_LINES) + len(REQUIRED_WORKFLOW_COUNTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
