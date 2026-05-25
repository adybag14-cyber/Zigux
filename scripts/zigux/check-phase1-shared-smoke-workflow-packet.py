#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
    Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    Path("scripts/zigux/check-phase4-tests-readme-packet.py"),
    Path("zigux/tests/build.zig"),
)

REQUIRED_STEPS = (
    ("Self-test current Phase 1 closure validator", "python3 scripts/zigux/validate-phase1-closure.py --self-test"),
    ("Check current Phase 1 closure packet", "python3 scripts/zigux/validate-phase1-closure.py"),
    ("Self-test current Phase 3 interop packet", "python3 scripts/zigux/validate_phase3_selftest.py"),
    ("Check current Phase 3 interop packet", "python3 scripts/zigux/run-phase3-checks.py"),
    (
        "Self-test current Phase 3 low-level wrapper survey validator",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    ),
    (
        "Check current Phase 3 low-level wrapper survey packet",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    ),
    (
        "Run current Phase 3 low-level wrapper replay",
        "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    ("Run current Phase 3 shared tests-root packet", "zig build phase3-test --build-file zigux/tests/build.zig"),
    ("Run current Phase 3 ABI dump replay", "zig build phase3-dump --build-file zigux/tests/build.zig"),
    (
        "Run current Phase 1 shared tests-root smoke",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    (
        "Self-test current Phase 4 repo-reality warning checker",
        "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
    ),
    (
        "Check current Phase 4 repo-reality warning packet",
        "python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    ),
    (
        "Self-test current Phase 4 reversible-delivery pin checker",
        "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
    ),
    (
        "Check current Phase 4 reversible-delivery pin packet",
        "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py",
    ),
    (
        "Self-test current Phase 4 tests README checker",
        "python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test",
    ),
    (
        "Check current Phase 4 tests README packet",
        "python3 scripts/zigux/check-phase4-tests-readme-packet.py",
    ),
)

REQUIRED_STEP_NAMES = tuple(name for name, _ in REQUIRED_STEPS)
REQUIRED_ADJACENCY = (
    "Run current Phase 3 ABI dump replay",
    "Run current Phase 1 shared tests-root smoke",
    "Self-test current Phase 4 repo-reality warning checker",
)

SAMPLE_WORKFLOW = """name: zigux-bootstrap

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 1 closure validator
        run: python3 scripts/zigux/validate-phase1-closure.py --self-test
      - name: Check current Phase 1 closure packet
        run: python3 scripts/zigux/validate-phase1-closure.py
      - name: Self-test current Phase 3 interop packet
        run: python3 scripts/zigux/validate_phase3_selftest.py
      - name: Check current Phase 3 interop packet
        run: python3 scripts/zigux/run-phase3-checks.py
      - name: Self-test current Phase 3 low-level wrapper survey validator
        run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test
      - name: Check current Phase 3 low-level wrapper survey packet
        run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py
      - name: Run current Phase 3 low-level wrapper replay
        run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig
      - name: Run current Phase 3 shared tests-root packet
        run: zig build phase3-test --build-file zigux/tests/build.zig
      - name: Run current Phase 3 ABI dump replay
        run: zig build phase3-dump --build-file zigux/tests/build.zig
      - name: Run current Phase 1 shared tests-root smoke
        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
      - name: Self-test current Phase 4 repo-reality warning checker
        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test
      - name: Check current Phase 4 repo-reality warning packet
        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py
      - name: Self-test current Phase 4 reversible-delivery pin checker
        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test
      - name: Check current Phase 4 reversible-delivery pin packet
        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py
      - name: Self-test current Phase 4 tests README checker
        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test
      - name: Check current Phase 4 tests README packet
        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py
"""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _parse_workflow_steps(text: str) -> list[tuple[str, str]]:
    steps: list[tuple[str, str]] = []
    pending_name: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- name: "):
            pending_name = line[len("- name: ") :].strip()
            continue
        if pending_name is not None and line.startswith("run: "):
            steps.append((pending_name, line[len("run: ") :].strip()))
            pending_name = None
    return steps


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILE_RELS:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel.as_posix()}")
    if issues:
        return issues

    workflow_steps = _parse_workflow_steps(_read(root / WORKFLOW_REL))
    step_names = [name for name, _ in workflow_steps]
    step_runs = {name: run for name, run in workflow_steps}

    for name, run in REQUIRED_STEPS:
        if name not in step_names:
            issues.append(f"workflow:missing_step:{name}")
            continue
        actual_run = step_runs[name]
        if actual_run != run:
            issues.append(f"workflow:run_mismatch:{name}:expected={run}:actual={actual_run}")

    if issues:
        return issues

    positions = {name: step_names.index(name) for name in REQUIRED_STEP_NAMES}
    for earlier, later in zip(REQUIRED_STEP_NAMES, REQUIRED_STEP_NAMES[1:]):
        if positions[earlier] >= positions[later]:
            issues.append(f"workflow:order_violation:{earlier}->{later}")

    first, second, third = REQUIRED_ADJACENCY
    if not (
        positions[first] + 1 == positions[second]
        and positions[second] + 1 == positions[third]
    ):
        issues.append(f"workflow:adjacency_violation:{first}->{second}->{third}")

    return issues


def _seed(root: Path) -> None:
    _write(root / WORKFLOW_REL, SAMPLE_WORKFLOW)
    for rel in REQUIRED_FILE_RELS[1:]:
        _write(root / rel, "# packet placeholder\n")


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase1-shared-smoke-workflow-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_shared_smoke_workflow_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        workflow_path = root / WORKFLOW_REL
        _write(
            workflow_path,
            _read(workflow_path).replace(
                "      - name: Run current Phase 1 shared tests-root smoke\n"
                "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["workflow:missing_step:Run current Phase 1 shared tests-root smoke"],
            "missing_smoke_step",
        )
        _seed(root)
        case_count += 1

        _write(
            workflow_path,
            _read(workflow_path).replace(
                "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
                "python3 scripts/zigux/check-phase4-repo-reality-warning.py",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "workflow:run_mismatch:Self-test current Phase 4 repo-reality warning checker:"
                "expected=python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test:"
                "actual=python3 scripts/zigux/check-phase4-repo-reality-warning.py"
            ],
            "repo_reality_selftest_run",
        )
        _seed(root)
        case_count += 1

        text = _read(workflow_path)
        smoke_block = (
            "      - name: Run current Phase 1 shared tests-root smoke\n"
            "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n"
        )
        repo_block = (
            "      - name: Self-test current Phase 4 repo-reality warning checker\n"
            "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test\n"
        )
        _write(workflow_path, text.replace(smoke_block + repo_block, repo_block + smoke_block, 1))
        _assert_only(
            validate(root),
            [
                "workflow:order_violation:Run current Phase 1 shared tests-root smoke->Self-test current Phase 4 repo-reality warning checker",
                "workflow:adjacency_violation:Run current Phase 3 ABI dump replay->Run current Phase 1 shared tests-root smoke->Self-test current Phase 4 repo-reality warning checker",
            ],
            "smoke_repo_reality_order",
        )
        _seed(root)
        case_count += 1

        (root / "scripts/zigux/check-phase4-tests-readme-packet.py").unlink()
        _assert_only(
            validate(root),
            ["missing_file:scripts/zigux/check-phase4-tests-readme-packet.py"],
            "missing_phase4_readme_checker",
        )
        case_count += 1

    print("PHASE1_SHARED_SMOKE_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_SMOKE_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the current bootstrap workflow drifts around the Phase 1 shared-smoke handoff."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree to the given directory.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        _seed(args.write_sample_root.resolve())
        return 0

    root = args.root.resolve()
    issues = validate(root)
    if issues:
        for issue in issues:
            print(f"PHASE1_SHARED_SMOKE_WORKFLOW_PACKET_ISSUE={issue}")
        return 1

    print("PHASE1_SHARED_SMOKE_WORKFLOW_PACKET=pass")
    print(f"PHASE1_SHARED_SMOKE_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILE_RELS)}")
    print(f"PHASE1_SHARED_SMOKE_WORKFLOW_PACKET_REQUIRED_STEP_COUNT={len(REQUIRED_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
