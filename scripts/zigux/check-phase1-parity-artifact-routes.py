#!/usr/bin/env python3

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
]

PARITY_SCRIPT_MARKERS = [
    'FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")',
    'HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")',
    'ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")',
]

VALIDATOR_MARKERS = [
    '    "scripts/zigux/artifact_diff.py",',
    '    "scripts/zigux/check-phase1-parity.py",',
    '    "zigux/tests/fixtures/phase1_helper_manifest.json",',
    '    "zigux/tests/fixtures/phase1_helpers_c_harness.c",',
    '    "zigux/tests/fixtures/phase1_helpers.json",',
]

SCRIPTS_README_MARKERS = [
    "Initial responsibilities - Zig toolchain policy checks - bootstrap validation - committed parity fixture generation and checking - future ABI/layout guards - artifact diff helpers for host-side tools",
    "- `check-phase1-parity.py` compares the bounded helper outputs against the committed Phase 1 fixture corpus so `bitmap`, `find_bit`, `string`, `rbtree`, and the rest of the closed helper set stay pinned to the current C behavior.",
]

MAKEFILE_MARKERS = [
    "phase1-test:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig",
]

WORKFLOW_MARKERS = [
    "- name: Self-test Phase 4 artifact-diff helper directly",
    "run: python3 scripts/zigux/artifact_diff.py --self-test",
    "- name: Check Phase 1 helper parity",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "- name: Check Phase 1 helper benchmark output",
    "run: python3 scripts/zigux/check-phase1-bench.py",
]

SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_required_file",
    "parity_script_marker_drift",
    "validator_marker_drift",
    "scripts_readme_marker_drift",
    "makefile_order_drift",
    "workflow_marker_drift",
    "workflow_order_drift",
]


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_count_markers(text: str, label: str, markers: list[str], *, lstrip: bool = False) -> list[str]:
    lines = [line.lstrip() if lstrip else line for line in text.splitlines()]
    issues: list[str] = []
    for marker in markers:
        count = lines.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_substring_markers(text: str, label: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_makefile_route_issues(root: Path) -> list[str]:
    makefile_lines = [line.lstrip() for line in read_text(root, "zigux/Makefile").splitlines()]
    try:
        parity_index = makefile_lines.index(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py"
        )
        zig_test_index = makefile_lines.index(
            "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig"
        )
    except ValueError:
        return []
    if parity_index > zig_test_index:
        return [
            "phase1_parity_artifact_makefile_order:check-phase1-parity.py must run before zig build test"
        ]
    return []


def collect_workflow_route_issues(root: Path) -> list[str]:
    workflow_lines = [line.lstrip() for line in read_text(root, ".github/workflows/zigux-bootstrap.yml").splitlines()]
    try:
        artifact_self_test_index = workflow_lines.index(
            "- name: Self-test Phase 4 artifact-diff helper directly"
        )
        parity_index = workflow_lines.index("- name: Check Phase 1 helper parity")
        bench_index = workflow_lines.index("- name: Check Phase 1 helper benchmark output")
    except ValueError:
        return []

    issues: list[str] = []
    if artifact_self_test_index > parity_index:
        issues.append(
            "phase1_parity_artifact_workflow_order:artifact_diff self-test must stay ahead of Phase 1 parity"
        )
    if parity_index > bench_index:
        issues.append(
            "phase1_parity_artifact_workflow_order:Phase 1 parity must stay ahead of the Phase 1 bench checker"
        )
    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(f"missing_file:{relative_path}" for relative_path in collect_missing_files(root))
    if issues:
        return issues

    issues.extend(
        collect_exact_count_markers(
            read_text(root, "scripts/zigux/check-phase1-parity.py"),
            "phase1_parity_artifact_parity_script",
            PARITY_SCRIPT_MARKERS,
        )
    )
    issues.extend(
        collect_exact_count_markers(
            read_text(root, "scripts/zigux/validate-phase1.py"),
            "phase1_parity_artifact_validator",
            VALIDATOR_MARKERS,
        )
    )
    issues.extend(
        collect_substring_markers(
            read_text(root, "scripts/zigux/README.md"),
            "phase1_parity_artifact_scripts_readme",
            SCRIPTS_README_MARKERS,
        )
    )
    issues.extend(
        collect_exact_count_markers(
            read_text(root, "zigux/Makefile"),
            "phase1_parity_artifact_makefile",
            MAKEFILE_MARKERS,
            lstrip=True,
        )
    )
    issues.extend(
        collect_exact_count_markers(
            read_text(root, ".github/workflows/zigux-bootstrap.yml"),
            "phase1_parity_artifact_workflow",
            WORKFLOW_MARKERS,
            lstrip=True,
        )
    )
    issues.extend(collect_makefile_route_issues(root))
    issues.extend(collect_workflow_route_issues(root))
    return issues


def write_fixture_file(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_fixture_file(root, relative_path, "placeholder\n")

    write_fixture_file(
        root,
        "scripts/zigux/check-phase1-parity.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                'FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")',
                'HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")',
                'ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")',
            ]
        )
        + "\n",
    )
    write_fixture_file(
        root,
        "scripts/zigux/validate-phase1.py",
        "\n".join(
            [
                "REQUIRED_FILES = [",
                '    "scripts/zigux/artifact_diff.py",',
                '    "scripts/zigux/check-phase1-parity.py",',
                '    "zigux/tests/fixtures/phase1_helper_manifest.json",',
                '    "zigux/tests/fixtures/phase1_helpers_c_harness.c",',
                '    "zigux/tests/fixtures/phase1_helpers.json",',
                "]",
            ]
        )
        + "\n",
    )
    write_fixture_file(
        root,
        "scripts/zigux/README.md",
        "\n".join(SCRIPTS_README_MARKERS) + "\n",
    )
    write_fixture_file(
        root,
        "zigux/Makefile",
        "\n".join(
            [
                "phase1-test:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig",
            ]
        )
        + "\n",
    )
    write_fixture_file(
        root,
        ".github/workflows/zigux-bootstrap.yml",
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test Phase 4 artifact-diff helper directly",
                "        run: python3 scripts/zigux/artifact_diff.py --self-test",
                "      - name: Check Phase 1 helper parity",
                "        run: python3 scripts/zigux/check-phase1-parity.py",
                "      - name: Check Phase 1 helper benchmark output",
                "        run: python3 scripts/zigux/check-phase1-bench.py",
            ]
        )
        + "\n",
    )


def run_self_test() -> None:
    if len(set(SELF_TEST_CASES)) != len(SELF_TEST_CASES):
        raise AssertionError(f"duplicate self-test cases: {SELF_TEST_CASES}")

    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_artifact_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)

        assert collect_missing_files(root) == []
        assert collect_issues(root) == []
        case_count += 1

        harness_path = root / "zigux/tests/fixtures/phase1_helpers_c_harness.c"
        harness_path.unlink()
        assert collect_issues(root) == ["missing_file:zigux/tests/fixtures/phase1_helpers_c_harness.c"]
        make_fixture_root(root)
        case_count += 1

        parity_script_path = root / "scripts/zigux/check-phase1-parity.py"
        original_parity_script = parity_script_path.read_text(encoding="utf-8")
        parity_script_path.write_text(
            original_parity_script.replace(
                'ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")',
                'ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff_drift.py")',
                1,
            ),
            encoding="utf-8",
        )
        assert (
            'phase1_parity_artifact_parity_script:ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py"):expected=1:actual=0'
            in collect_issues(root)
        )
        parity_script_path.write_text(original_parity_script, encoding="utf-8")
        case_count += 1

        validator_path = root / "scripts/zigux/validate-phase1.py"
        original_validator = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            original_validator.replace(
                '    "zigux/tests/fixtures/phase1_helpers.json",',
                '    "zigux/tests/fixtures/phase1_helpers_drift.json",',
                1,
            ),
            encoding="utf-8",
        )
        assert (
            'phase1_parity_artifact_validator:    "zigux/tests/fixtures/phase1_helpers.json",:expected=1:actual=0'
            in collect_issues(root)
        )
        validator_path.write_text(original_validator, encoding="utf-8")
        case_count += 1

        scripts_readme_path = root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace("artifact diff helpers", "artifact helper drift", 1),
            encoding="utf-8",
        )
        assert any(
            issue.startswith("phase1_parity_artifact_scripts_readme:")
            for issue in collect_issues(root)
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")
        case_count += 1

        makefile_path = root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            "\n".join(
                [
                    "phase1-test:",
                    "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        assert (
            "phase1_parity_artifact_makefile_order:check-phase1-parity.py must run before zig build test"
            in collect_issues(root)
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")
        case_count += 1

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Self-test Phase 4 artifact-diff helper directly\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "- name: Self-test Phase 4 artifact-diff helper directly:expected=1:actual=0"
            in "\n".join(collect_issues(root))
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")
        case_count += 1

        workflow_path.write_text(
            "\n".join(
                [
                    "jobs:",
                    "  bootstrap:",
                    "    steps:",
                    "      - name: Check Phase 1 helper benchmark output",
                    "        run: python3 scripts/zigux/check-phase1-bench.py",
                    "      - name: Check Phase 1 helper parity",
                    "        run: python3 scripts/zigux/check-phase1-parity.py",
                    "      - name: Self-test Phase 4 artifact-diff helper directly",
                    "        run: python3 scripts/zigux/artifact_diff.py --self-test",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        workflow_issues = collect_issues(root)
        assert (
            "phase1_parity_artifact_workflow_order:artifact_diff self-test must stay ahead of Phase 1 parity"
            in workflow_issues
        )
        assert (
            "phase1_parity_artifact_workflow_order:Phase 1 parity must stay ahead of the Phase 1 bench checker"
            in workflow_issues
        )
        case_count += 1

    if case_count != len(SELF_TEST_CASES):
        raise AssertionError(f"expected {len(SELF_TEST_CASES)} self-test cases, got {case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 1 parity-fixture and artifact-diff route surfaces."
    )
    parser.add_argument("--root", help="Repository root to inspect. Defaults to the current repository.")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("PHASE1_PARITY_ARTIFACT_ROUTE_SELF_TEST=pass")
        print(f"PHASE1_PARITY_ARTIFACT_ROUTE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
        print(
            "PHASE1_PARITY_ARTIFACT_ROUTE_SELF_TEST_CASES="
            + ",".join(SELF_TEST_CASES)
        )
        return 0

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_PARITY_ARTIFACT_ROUTES=fail")
        print(f"PHASE1_PARITY_ARTIFACT_ROUTE_ISSUE_COUNT={len(issues)}")
        for issue in issues:
            print(f"PHASE1_PARITY_ARTIFACT_ROUTE_ISSUE={issue}")
        return 1

    print("PHASE1_PARITY_ARTIFACT_ROUTES=pass")
    print("PHASE1_PARITY_ARTIFACT_ROUTE_ISSUE_COUNT=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
