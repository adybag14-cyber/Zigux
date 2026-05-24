#!/usr/bin/env python3
"""Guard the current Phase 1 closure workflow-to-smoke handoff packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    VALIDATOR_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    WORKFLOW_REL,
)

EXPECTED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    ),
    VALIDATOR_REL: (
        'TESTS_BUILD_REL = Path("zigux/tests/build.zig")',
        'PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")',
        '"shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",',
        'print("PHASE1_CLOSURE_VALIDATION=pass")',
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    ),
    TESTS_README_REL: (
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "Tests-root reviewer prompt:\n- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
    ),
    TESTS_BUILD_REL: (
        'const phase1_step = b.step(',
        '"phase1-host-tools-smoke",',
        '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests",',
        "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
    ),
    WORKFLOW_REL: (
        "- name: Self-test current Phase 1 closure validator",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "- name: Check current Phase 1 closure packet",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "- name: Run current Phase 1 shared tests-root smoke",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

FORBIDDEN_WORKFLOW_MARKERS = (
    "- name: Run current Phase 1 bench route",
    "run: zig build bench --build-file zigux/tests/build.zig",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_exact_line(text: str, label: str, needle: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line == needle)
    return [] if count == 1 else [f"{label}:expected_line_once:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    for relative_path, markers in EXPECTED_MARKERS.items():
        text = load_text(root, relative_path)
        if relative_path == WORKFLOW_REL:
            continue
        for marker in markers:
            failures.extend(
                require_exact_occurrence(
                    text,
                    f"{relative_path.as_posix()}:required",
                    marker,
                )
            )

    workflow_text = load_text(root, WORKFLOW_REL)
    for marker in EXPECTED_MARKERS[WORKFLOW_REL]:
        failures.extend(
            require_exact_line(
                workflow_text,
                f"{WORKFLOW_REL.as_posix()}:required",
                marker,
            )
        )
    for marker in FORBIDDEN_WORKFLOW_MARKERS:
        count = sum(1 for line in workflow_text.splitlines() if line == marker)
        if count:
            failures.append(
                f"{WORKFLOW_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}"
            )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    for relative_path, markers in EXPECTED_MARKERS.items():
        write_text(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        (
            "missing_closure_validator_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_MARKERS[PHASE1_CLOSURE_REL][0] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_shared_tests_route_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_MARKERS[PHASE1_CLOSURE_REL][1] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_validator_tests_build_rel",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(
                    EXPECTED_MARKERS[VALIDATOR_REL][0] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_validator_smoke_rel",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(
                    EXPECTED_MARKERS[VALIDATOR_REL][1] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_scripts_smoke_route",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL).replace(
                    EXPECTED_MARKERS[SCRIPTS_README_REL][0] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_tests_prompt",
            lambda root: write_text(
                root / TESTS_README_REL,
                load_text(root, TESTS_README_REL).replace(
                    EXPECTED_MARKERS[TESTS_README_REL][1] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_build_step_dependency",
            lambda root: write_text(
                root / TESTS_BUILD_REL,
                load_text(root, TESTS_BUILD_REL).replace(
                    EXPECTED_MARKERS[TESTS_BUILD_REL][3] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_workflow_closure_check",
            lambda root: write_text(
                root / WORKFLOW_REL,
                load_text(root, WORKFLOW_REL).replace(
                    EXPECTED_MARKERS[WORKFLOW_REL][2] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_workflow_smoke_run",
            lambda root: write_text(
                root / WORKFLOW_REL,
                load_text(root, WORKFLOW_REL).replace(
                    EXPECTED_MARKERS[WORKFLOW_REL][5] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "forbidden_workflow_bench_route",
            lambda root: write_text(
                root / WORKFLOW_REL,
                load_text(root, WORKFLOW_REL)
                + "- name: Run current Phase 1 bench route\n"
                + "run: zig build bench --build-file zigux/tests/build.zig\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-workflow-handoff-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-workflow-handoff-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-workflow-handoff-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_WORKFLOW_HANDOFF_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_WORKFLOW_HANDOFF_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_WORKFLOW_HANDOFF=pass")
    print("PHASE1_CLOSURE_WORKFLOW_HANDOFF_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
