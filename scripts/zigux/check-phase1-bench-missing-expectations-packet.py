#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
PHASE1_CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
EXPECTATIONS_REL = Path("zigux/tests/fixtures/phase1_bench_expectations.json")

REQUIRED_FILES = (
    BENCH_CHECKER_REL,
    PHASE1_CLOSURE_VALIDATOR_REL,
    WORKFLOW_REL,
)

BENCH_MARKERS = (
    'EXPECTATIONS = ROOT / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"',
    'return ("missing_expectations_file", path)',
    'if kind == "missing_expectations_file":',
    'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
    'print(f"EXPECTATIONS_PATH={payload}")',
)

CLOSURE_MARKERS = (
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "`PHASE1_CURRENT_GAP_PACKET=",
)

WORKFLOW_MARKERS = (
    "- name: Self-test current Phase 1 bench checker",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
)


def repo_root(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    if (root / EXPECTATIONS_REL).exists():
        failures.append(f"unexpected_expectations_file:{EXPECTATIONS_REL.as_posix()}")

    bench_text = load_text(root, BENCH_CHECKER_REL)
    for marker in BENCH_MARKERS:
        failures.extend(require_exact_occurrence(bench_text, BENCH_CHECKER_REL.as_posix(), marker))

    closure_text = load_text(root, PHASE1_CLOSURE_VALIDATOR_REL)
    for marker in CLOSURE_MARKERS:
        failures.extend(
            require_exact_occurrence(
                closure_text,
                PHASE1_CLOSURE_VALIDATOR_REL.as_posix(),
                marker,
            )
        )

    workflow_text = load_text(root, WORKFLOW_REL)
    for marker in WORKFLOW_MARKERS:
        failures.extend(require_exact_occurrence(workflow_text, WORKFLOW_REL.as_posix(), marker))

    return failures


def write_sample_root(destination: Path) -> None:
    write_text(
        destination / BENCH_CHECKER_REL,
        "\n".join(
            (
                '#!/usr/bin/env python3',
                'from pathlib import Path',
                'ROOT = Path(__file__).resolve().parents[2]',
                'EXPECTATIONS = ROOT / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"',
                "",
                "def load_runtime_expectations(path: Path):",
                '    return ("missing_expectations_file", path)',
                "",
                "def main() -> int:",
                "    kind, payload = load_runtime_expectations(EXPECTATIONS)",
                '    if kind == "missing_expectations_file":',
                '        print("PHASE1_BENCH_CHECK=fail")',
                '        print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
                '        print(f"EXPECTATIONS_PATH={payload}")',
                "        return 1",
                "    return 0",
                "",
            )
        ),
    )
    write_text(
        destination / PHASE1_CLOSURE_VALIDATOR_REL,
        "\n".join(
            (
                '#!/usr/bin/env python3',
                'EXPECTED_CLOSURE_MARKERS = {',
                '    "gap_packet": "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,'
                'scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,'
                'zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,'
                'zigux/tests/fixtures/phase1_helpers_c_harness.c`",',
                "}",
                "",
            )
        ),
    )
    write_text(
        destination / WORKFLOW_REL,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Phase 1 bench checker",
                "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
                "",
            )
        ),
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-bench-missing-expectations-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        assert collect_failures(root) == []
        case_count += 1

        write_text(root / BENCH_CHECKER_REL, load_text(root, BENCH_CHECKER_REL).replace('print(f"EXPECTATIONS_PATH={payload}")\n', "", 1))
        failures = collect_failures(root)
        assert any("EXPECTATIONS_PATH" in failure for failure in failures), failures
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-missing-expectations-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        write_text(root / WORKFLOW_REL, load_text(root, WORKFLOW_REL).replace("run: python3 scripts/zigux/check-phase1-bench.py --self-test\n", "", 1))
        failures = collect_failures(root)
        assert any("check-phase1-bench.py --self-test" in failure for failure in failures), failures
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-missing-expectations-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        write_text(root / PHASE1_CLOSURE_VALIDATOR_REL, load_text(root, PHASE1_CLOSURE_VALIDATOR_REL).replace("zigux/tests/fixtures/phase1_bench_expectations.json,", "", 1))
        failures = collect_failures(root)
        assert any("phase1_bench_expectations.json" in failure for failure in failures), failures
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-missing-expectations-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        write_text(root / EXPECTATIONS_REL, "{}\n")
        failures = collect_failures(root)
        assert failures == [f"unexpected_expectations_file:{EXPECTATIONS_REL.as_posix()}"], failures
        case_count += 1

    print("PHASE1_BENCH_MISSING_EXPECTATIONS_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_MISSING_EXPECTATIONS_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 1 bench missing-expectations packet stays explicit."
    )
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument(
        "--write-sample-root",
        help="Write a minimal current-like tree for local packet validation.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BENCH_MISSING_EXPECTATIONS_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BENCH_MISSING_EXPECTATIONS_PACKET=pass")
    print(f"PHASE1_BENCH_MISSING_EXPECTATIONS_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BENCH_MISSING_EXPECTATIONS_PACKET_BENCH_MARKER_COUNT={len(BENCH_MARKERS)}")
    print(f"PHASE1_BENCH_MISSING_EXPECTATIONS_PACKET_CLOSURE_MARKER_COUNT={len(CLOSURE_MARKERS)}")
    print(f"PHASE1_BENCH_MISSING_EXPECTATIONS_PACKET_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
