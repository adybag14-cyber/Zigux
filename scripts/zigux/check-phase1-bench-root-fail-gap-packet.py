#!/usr/bin/env python3
"""Guard the current Lane 16 root/fail-output gap around check-phase1-bench.py."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    BENCH_CHECKER_REL,
    CLOSURE_VALIDATOR_REL,
    WORKFLOW_REL,
)

REQUIRED_BENCH_MARKERS = {
    "fixed_root_binding": 'ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent',
    "fixed_expectations_path": 'EXPECTATIONS = ROOT / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"',
    "fixed_source_path": 'PHASE1_BENCH = ROOT / "zigux" / "tests" / "phase1_bench.zig"',
    "zig_arg": 'parser.add_argument("--zig", help="Path to Zig executable")',
    "self_test_arg": 'parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without invoking Zig.")',
    "missing_expectations_reason": 'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
    "missing_expectations_path": 'print(f"EXPECTATIONS_PATH={payload}")',
    "json_error_branch": 'if kind == "expectations_json_error":',
    "json_error_detail": 'print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
    "json_error_line": 'print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
    "json_error_column": 'print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
    "bench_command_exit": 'print(f"BENCH_COMMAND_EXIT={result.returncode}")',
}

FORBIDDEN_BENCH_MARKERS = {
    "root_arg": 'parser.add_argument("--root", help="override the repository root for validation")',
    "repo_root_helper": "def repo_root(",
    "root_path_join": "repo_root(args.root)",
    "rooted_expectations": 'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")',
    "rooted_reason_json": 'print("PHASE1_BENCH_CHECK_REASON=expectations_json_error")',
    "rooted_reason_bench_exit": 'print("PHASE1_BENCH_CHECK_REASON=bench_command_exit")',
}

REQUIRED_CLOSURE_MARKERS = {
    "run_checker_root": '[sys.executable, str(root / script_rel), "--root", str(root)]',
    "bench_checker_rel": '(BENCH_CHECKER_REL, "phase1-bench")',
}

REQUIRED_WORKFLOW_MARKERS = {
    "bench_self_test_name": "- name: Self-test current Phase 1 bench checker",
    "bench_self_test_run": "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "closure_check_name": "- name: Check current Phase 1 closure packet",
    "closure_check_run": "run: python3 scripts/zigux/validate-phase1-closure.py",
}

FORBIDDEN_WORKFLOW_MARKERS = {
    "direct_bench_run": "run: python3 scripts/zigux/check-phase1-bench.py\n",
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{marker}"]


def require_absent(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 0 else [f"{label}:forbidden_marker:actual_count={count}:{marker}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    bench_text = load_text(root, BENCH_CHECKER_REL)
    for label, marker in REQUIRED_BENCH_MARKERS.items():
        failures.extend(require_exact_occurrence(bench_text, f"{BENCH_CHECKER_REL.as_posix()}:{label}", marker))
    for label, marker in FORBIDDEN_BENCH_MARKERS.items():
        failures.extend(require_absent(bench_text, f"{BENCH_CHECKER_REL.as_posix()}:{label}", marker))

    closure_text = load_text(root, CLOSURE_VALIDATOR_REL)
    for label, marker in REQUIRED_CLOSURE_MARKERS.items():
        failures.extend(require_exact_occurrence(closure_text, f"{CLOSURE_VALIDATOR_REL.as_posix()}:{label}", marker))

    workflow_text = load_text(root, WORKFLOW_REL)
    for label, marker in REQUIRED_WORKFLOW_MARKERS.items():
        failures.extend(require_exact_occurrence(workflow_text, f"{WORKFLOW_REL.as_posix()}:{label}", marker))
    for label, marker in FORBIDDEN_WORKFLOW_MARKERS.items():
        failures.extend(require_absent(workflow_text, f"{WORKFLOW_REL.as_posix()}:{label}", marker))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    write_text(
        root / BENCH_CHECKER_REL,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "HERE = Path(__file__).resolve()",
                'ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent',
                'EXPECTATIONS = ROOT / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"',
                'PHASE1_BENCH = ROOT / "zigux" / "tests" / "phase1_bench.zig"',
                'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
                'print(f"EXPECTATIONS_PATH={payload}")',
                'if kind == "expectations_json_error":',
                '    print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
                '    print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
                '    print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
                'print(f"BENCH_COMMAND_EXIT={result.returncode}")',
                'parser.add_argument("--zig", help="Path to Zig executable")',
                'parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without invoking Zig.")',
                "",
            ]
        ),
    )
    write_text(
        root / CLOSURE_VALIDATOR_REL,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                'BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")',
                'DELEGATED_CHECKERS = ((BENCH_CHECKER_REL, "phase1-bench"),)',
                'cmd = [sys.executable, str(root / script_rel), "--root", str(root)]',
                "",
            ]
        ),
    )
    write_text(
        root / WORKFLOW_REL,
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Phase 1 bench checker",
                "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
                "      - name: Check current Phase 1 closure packet",
                "        run: python3 scripts/zigux/validate-phase1-closure.py",
                "",
            ]
        ),
    )


def mutate_remove(root: Path, rel: Path, marker: str) -> None:
    path = root / rel
    path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")


def mutate_append(root: Path, rel: Path, marker: str) -> None:
    path = root / rel
    path.write_text(path.read_text(encoding="utf-8") + marker, encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_json_branch", lambda root: mutate_remove(root, BENCH_CHECKER_REL, 'if kind == "expectations_json_error":\n')),
        ("missing_command_exit", lambda root: mutate_remove(root, BENCH_CHECKER_REL, 'print(f"BENCH_COMMAND_EXIT={result.returncode}")\n')),
        ("bench_gains_root_arg", lambda root: mutate_append(root, BENCH_CHECKER_REL, 'parser.add_argument("--root", help="override the repository root for validation")\n')),
        ("bench_gains_structured_json_reason", lambda root: mutate_append(root, BENCH_CHECKER_REL, 'print("PHASE1_BENCH_CHECK_REASON=expectations_json_error")\n')),
        ("bench_gains_structured_exit_reason", lambda root: mutate_append(root, BENCH_CHECKER_REL, 'print("PHASE1_BENCH_CHECK_REASON=bench_command_exit")\n')),
        ("bench_gains_expectations_footer", lambda root: mutate_append(root, BENCH_CHECKER_REL, 'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")\n')),
        ("closure_drops_root_delegation", lambda root: mutate_remove(root, CLOSURE_VALIDATOR_REL, '[sys.executable, str(root / script_rel), "--root", str(root)]')),
        ("workflow_drops_bench_selftest", lambda root: mutate_remove(root, WORKFLOW_REL, "      - name: Self-test current Phase 1 bench checker\n")),
        ("workflow_gains_direct_bench_run", lambda root: mutate_append(root, WORKFLOW_REL, "        run: python3 scripts/zigux/check-phase1-bench.py\n")),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-root-gap-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-bench-root-gap-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-bench-root-gap-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BENCH_ROOT_FAIL_GAP_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_ROOT_FAIL_GAP_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def write_sample_root(target: Path) -> None:
    make_fixture_tree(target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument("--write-sample-root", help="write a sample current-gap tree to this directory")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BENCH_ROOT_FAIL_GAP_PACKET=pass")
    print(f"PHASE1_BENCH_ROOT_FAIL_GAP_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BENCH_ROOT_FAIL_GAP_PACKET_BENCH_MARKER_COUNT={len(REQUIRED_BENCH_MARKERS)}")
    print(f"PHASE1_BENCH_ROOT_FAIL_GAP_PACKET_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    print(f"PHASE1_BENCH_ROOT_FAIL_GAP_PACKET_WORKFLOW_MARKER_COUNT={len(REQUIRED_WORKFLOW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
