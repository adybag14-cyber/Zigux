#!/usr/bin/env python3
"""Guard the current Lane 17 Phase 1 workflow-viability packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
ROUTE_SUMMARY_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BUILD_REL = Path("zigux/tests/build.zig")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
    CLOSURE_REL,
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    SHARED_REMINDER_REL,
    CLOSURE_VALIDATOR_REL,
    ROUTE_SUMMARY_REL,
    BUILD_REL,
    SMOKE_REL,
    MANIFEST_REL,
)

PHASE1_CHAIN = (
    ("Self-test current Phase 1 shared reminder checker", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("Check current Phase 1 shared reminder packet", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
    ("Self-test current Phase 1 closure validator", "python3 scripts/zigux/validate-phase1-closure.py --self-test"),
    ("Check current Phase 1 closure packet", "python3 scripts/zigux/validate-phase1-closure.py"),
    ("Self-test current Phase 3 interop packet", "python3 scripts/zigux/validate_phase3_selftest.py"),
)

PHASE3_TO_PHASE4_CHAIN = (
    ("Run current Phase 3 low-level wrapper replay", "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"),
    ("Run current Phase 3 shared tests-root packet", "zig build phase3-test --build-file zigux/tests/build.zig"),
    ("Run current Phase 3 ABI dump replay", "zig build phase3-dump --build-file zigux/tests/build.zig"),
    ("Run current Phase 1 shared tests-root smoke", "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"),
    ("Self-test current Phase 4 repo-reality warning checker", "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test"),
)

REQUIRED_CLOSURE_SNIPPETS = (
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "The current bootstrap workflow also replays the adjacent Phase 1 route-summary guard beside that same live reminder packet.",
)

REQUIRED_DOCS_SNIPPETS = (
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/check-phase1-bench.py",
)

REQUIRED_SCRIPTS_SNIPPETS = (
    "python3 scripts/zigux/validate-phase1-closure.py",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

REQUIRED_TESTS_SNIPPETS = (
    "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
)

REQUIRED_CHECKLIST_SNIPPETS = (
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

FORBIDDEN_WORKFLOW_SNIPPETS = (
    "python3 scripts/zigux/validate-phase1.py",
    "python3 scripts/zigux/check-phase1-parity.py",
    "zig build test --build-file zigux/tests/build.zig",
    "zig build bench --build-file zigux/tests/build.zig",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
    "make -C zigux phase1",
)


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for current in text.splitlines() if current == line)


def require_once(text: str, label: str, line: str) -> list[str]:
    count = count_exact_line(text, line)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_contains(text: str, label: str, needle: str) -> list[str]:
    return [] if needle in text else [f"{label}:missing:{needle}"]


def require_step(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures: list[str] = []
    failures.extend(require_once(workflow_text, f"workflow_step:{step_name}", f"      - name: {step_name}"))
    failures.extend(require_once(workflow_text, f"workflow_run:{step_name}", f"        run: {run_command}"))
    return failures


def workflow_step_names(workflow_text: str) -> list[str]:
    names: list[str] = []
    prefix = "      - name: "
    for line in workflow_text.splitlines():
        if line.startswith(prefix):
            names.append(line[len(prefix) :])
    return names


def require_adjacent_chain(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    names = workflow_step_names(workflow_text)
    chain = list(step_names)
    max_start = len(names) - len(chain) + 1
    for index in range(max_start):
        if names[index : index + len(chain)] == chain:
            return []
    return [f"workflow_adjacent_chain:missing:{'->'.join(step_names)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILE_RELS:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    closure_text = load_text(root, CLOSURE_REL)
    docs_text = load_text(root, DOCS_README_REL)
    checklist_text = load_text(root, REVIEW_CHECKLIST_REL)
    scripts_text = load_text(root, SCRIPTS_README_REL)
    tests_text = load_text(root, TESTS_README_REL)

    for step_name, run_command in PHASE1_CHAIN + PHASE3_TO_PHASE4_CHAIN:
        failures.extend(require_step(workflow_text, step_name, run_command))

    failures.extend(require_adjacent_chain(workflow_text, tuple(step_name for step_name, _ in PHASE1_CHAIN)))
    failures.extend(require_adjacent_chain(workflow_text, tuple(step_name for step_name, _ in PHASE3_TO_PHASE4_CHAIN)))

    for snippet in REQUIRED_CLOSURE_SNIPPETS:
        failures.extend(require_contains(closure_text, "phase1-closure", snippet))
    for snippet in REQUIRED_DOCS_SNIPPETS:
        failures.extend(require_contains(docs_text, "docs-readme", snippet))
    for snippet in REQUIRED_SCRIPTS_SNIPPETS:
        failures.extend(require_contains(scripts_text, "scripts-readme", snippet))
    for snippet in REQUIRED_TESTS_SNIPPETS:
        failures.extend(require_contains(tests_text, "tests-readme", snippet))
    for snippet in REQUIRED_CHECKLIST_SNIPPETS:
        failures.extend(require_contains(checklist_text, "review-checklist", snippet))

    for forbidden in FORBIDDEN_WORKFLOW_SNIPPETS:
        if forbidden in workflow_text:
            failures.append(f"workflow_forbidden:{forbidden}:unexpected_present")

    return failures


def build_workflow_text() -> str:
    lines = ["name: zigux-bootstrap", "", "jobs:", "  bootstrap:", "    runs-on: ubuntu-latest", "    steps:", ""]
    for step_name, run_command in PHASE1_CHAIN + PHASE3_TO_PHASE4_CHAIN:
        lines.append(f"      - name: {step_name}")
        lines.append(f"        run: {run_command}")
        lines.append("")
    return "\n".join(lines)


def build_closure_text() -> str:
    return "\n".join(
        (
            "# Phase 1 Closure",
            "",
            "The current bootstrap workflow also replays the adjacent Phase 1 route-summary guard beside that same live reminder packet.",
            "",
            "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
            "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
            "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
            "",
        )
    )


def build_sample_root(root: Path) -> None:
    write_file(root, WORKFLOW_REL, build_workflow_text())
    write_file(root, CLOSURE_REL, build_closure_text())
    write_file(root, DOCS_README_REL, "scripts/zigux/validate-phase1-closure.py\nscripts/zigux/check-phase1-shared-reminder-packet.py\nscripts/zigux/check-phase1-bench.py\n")
    write_file(root, REVIEW_CHECKLIST_REL, "scripts/zigux/validate-phase1-closure.py\nscripts/zigux/check-phase1-shared-reminder-packet.py\nzig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n")
    write_file(root, SCRIPTS_README_REL, "python3 scripts/zigux/validate-phase1-closure.py\npython3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\nzig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n")
    write_file(root, TESTS_README_REL, "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`\nscripts/zigux/validate-phase1-closure.py\nscripts/zigux/check-phase1-shared-reminder-packet.py\n")
    for relative_path in REQUIRED_FILE_RELS[6:]:
        if not (root / relative_path).exists():
            write_file(root, relative_path, "# placeholder\n")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    build_sample_root(root)


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample text: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-") as tmpdir:
        root = Path(tmpdir)

        build_sample_root(root)
        if collect_failures(root):
            print("self-test:unexpected_failures")
            return 1
        case_count += 1

        sample_root = root / "written-sample-root"
        write_sample_root(sample_root)
        if collect_failures(sample_root):
            print("self-test:write_sample_root_output_failed")
            return 1
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            rewrite_once(
                workflow_text,
                "      - name: Self-test current Phase 1 closure validator\n        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
            ),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if not any(failure.startswith("workflow_adjacent_chain:missing:") for failure in failures):
            print("self-test:expected_phase1_chain_failure")
            return 1
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow_text
            + "      - name: Run current Phase 1 shared tests-root smoke\n"
            + "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if "workflow_step:Run current Phase 1 shared tests-root smoke:expected=1:actual=2" not in failures:
            print("self-test:duplicate_smoke_step_not_detected")
            return 1
        case_count += 1

        build_sample_root(root)
        closure_path = root / CLOSURE_REL
        closure_text = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(
            rewrite_once(
                closure_text,
                "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`\n",
            ),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if not any(failure.startswith("phase1-closure:missing:`PHASE1_ROUTE_SUMMARY_GUARD=") for failure in failures):
            print("self-test:missing_route_summary_guard_not_detected")
            return 1
        case_count += 1

        build_sample_root(root)
        docs_path = root / DOCS_README_REL
        docs_text = docs_path.read_text(encoding="utf-8")
        docs_path.write_text(
            rewrite_once(docs_text, "scripts/zigux/check-phase1-bench.py\n"),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if not any(failure.startswith("docs-readme:missing:scripts/zigux/check-phase1-bench.py") for failure in failures):
            print("self-test:missing_docs_bench_anchor_not_detected")
            return 1
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow_text + "      - name: Historical route\n        run: make -C zigux phase1\n",
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if "workflow_forbidden:make -C zigux phase1:unexpected_present" not in failures:
            print("self-test:forbidden_historical_route_not_detected")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="write a current-like sample repository root and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"phase1-workflow-viability:sample-root-written:{args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_VIABILITY=pass")
    print("PHASE1_WORKFLOW_VIABILITY_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
