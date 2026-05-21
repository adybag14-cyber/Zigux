#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
SURVEY_GATE_PATH = "zigux/tests/runtime_trace_events_survey.zig"

PREVIOUS_STEP = "      - name: Run Phase 8 tooling tests"
NEXT_STEP = "      - name: Self-test current Phase 7 shared-control gap checker"
WORKFLOW_STEPS = (
    "      - name: Self-test current Phase 9 review-checklist boundaries checker",
    "      - name: Check current Phase 9 review-checklist boundaries packet",
    "      - name: Self-test current Phase 9 freeze-map study-boundaries checker",
    "      - name: Check current Phase 9 freeze-map study-boundaries packet",
    "      - name: Self-test current Phase 9 trace-events runtime packet checker",
    "      - name: Check current Phase 9 trace-events runtime packet",
    "      - name: Self-test current Phase 9 trace-events summary-preservation checker",
    "      - name: Check current Phase 9 trace-events summary-preservation packet",
    "      - name: Run current Phase 9 trace-events runtime sample tests",
    "      - name: Run current Phase 9 unregistered gate companion tests",
    "      - name: Run current Phase 9 exit rollback guard companion tests",
    "      - name: Run current Phase 9 registration reentry companion tests",
    "      - name: Run current Phase 9 trace-events survey witness",
)

REQUIRED_MARKERS = {
    SEQUENCING_PATH: [
        "### 1. Trace-events remains the direct shipped runtime sample family",
        "`samples/zigux/runtime_trace_events.zig`",
        "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
        "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
        "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
        "the trace-events runtime packet is still the shipped direct current-`master` proof for selftest-hook and lifecycle-parity reviewability",
    ],
    MODULE_SLICE_PATH: [
        "The paired family-local survey packet through `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` now keeps that pilot-module story directly reviewable under `zigux/tests/runtime_*` again without pretending the wider loader-backed family returned.",
        "which reruns `zig test samples/zigux/runtime_trace_events.zig`, `zig test samples/zigux/runtime_trace_events_unregistered_gate.zig`, `zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, and `zig test zigux/tests/runtime_trace_events_survey.zig` without turning the workflow into dedicated family-local loader parity proof.",
        "The adjacent shared build shard in `zigux/tests/phase9_build.zig` now names `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, `phase9-runtime-trace-events-loader-substrate-drift-tests`, aggregate `phase9-runtime-loader-shared-tests`, and the broader `phase9-first-loadable-runtime-module-parity-survey-tests` route, but those loader-backed and shared-control rerun routes remain neighboring shared-owner evidence instead of expanding this module slice into returned family-local runtime-loader parity.",
    ],
    SAMPLES_README_PATH: [
        "The surviving direct runtime-module sample packet in this directory is still centered on `samples/zigux/runtime_trace_events.zig`.",
        "Keep `samples/zigux/runtime_trace_events.zig` explicit as the direct runtime sample, including the rejected re-selftest rollback proof that keeps both selftest-complete and exited summaries stable when `runSelftest()` is retried out of lifecycle order.",
        "Keep `samples/zigux/runtime_trace_events_unregistered_gate.zig` explicit as the unregistered function-thread fail-closed companion for the same direct runtime packet.",
        "Keep `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` explicit as the failed-exit rollback companion for the selftest-ready proof plus both the initialized no-direct-activity and initialized direct-activity lifecycle proofs in the same packet.",
        "Keep `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the reusable registration-reentry companion, including the initialized direct-activity clean-exit proof without selftest.",
    ],
    SURVEY_GATE_PATH: [
        'test "phase9 trace-events survey packet matches the narrow current-master pilot-module story" {',
        'try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test");',
        'try expectContains(survey_note, "adjacent shared loader-handoff build shard in `zigux/tests/phase9_build.zig`");',
    ],
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SEQUENCING_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line == marker)


def replace_line(text: str, old: str, new: str) -> str:
    return "\n".join(new if line == old else line for line in text.splitlines()) + "\n"


def duplicate_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"missing line: {marker}")


def render_workflow_fixture() -> str:
    lines = ["name: zigux-bootstrap", PREVIOUS_STEP, *WORKFLOW_STEPS, NEXT_STEP]
    return "\n".join(lines) + "\n"


def seed_fixture_tree(base: Path) -> None:
    write_text(base / WORKFLOW_PATH, render_workflow_fixture())
    for rel_path, markers in REQUIRED_MARKERS.items():
        prefix = "# fixture\n\n" if rel_path.endswith(".md") else ""
        write_text(base / rel_path, prefix + "\n".join(markers) + "\n")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = [WORKFLOW_PATH, *REQUIRED_MARKERS]
    for rel_path in required_paths:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    workflow = read_text(root, WORKFLOW_PATH)
    for marker in [PREVIOUS_STEP, *WORKFLOW_STEPS, NEXT_STEP]:
        count = count_exact_line(workflow, marker)
        if count == 0:
            failures.append(f"missing_workflow_step:{marker.strip()}")
        elif count != 1:
            failures.append(f"duplicate_workflow_step:{marker.strip()}:count={count}")

    if not any(failure.startswith(("missing_workflow_step:", "duplicate_workflow_step:")) for failure in failures):
        positions = []
        for marker in [PREVIOUS_STEP, *WORKFLOW_STEPS, NEXT_STEP]:
            positions.append(workflow.index(marker))
        if positions != sorted(positions):
            failures.append("workflow_step_order_invalid")

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    return failures


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-bootstrap-trace-events-cluster-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        seed_fixture_tree(base)
        workflow = read_text(base, WORKFLOW_PATH).replace(WORKFLOW_STEPS[4] + "\n", "", 1)
        write_text(base / WORKFLOW_PATH, workflow)
        expect_failure(base, f"missing_workflow_step:{WORKFLOW_STEPS[4].strip()}")

        seed_fixture_tree(base)
        workflow = duplicate_line(read_text(base, WORKFLOW_PATH), WORKFLOW_STEPS[8])
        write_text(base / WORKFLOW_PATH, workflow)
        expect_failure(base, f"duplicate_workflow_step:{WORKFLOW_STEPS[8].strip()}:count=2")

        seed_fixture_tree(base)
        workflow = read_text(base, WORKFLOW_PATH)
        workflow = replace_line(workflow, WORKFLOW_STEPS[8], "__TEMP__")
        workflow = replace_line(workflow, WORKFLOW_STEPS[9], WORKFLOW_STEPS[8])
        workflow = replace_line(workflow, "__TEMP__", WORKFLOW_STEPS[9])
        write_text(base / WORKFLOW_PATH, workflow)
        expect_failure(base, "workflow_step_order_invalid")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                text = read_text(base, rel_path).replace(marker, "", 1)
                write_text(base / rel_path, text)
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in [WORKFLOW_PATH, *REQUIRED_MARKERS]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER_SELF_TEST=pass")
    print(f"PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER_WORKFLOW_STEP_COUNT={len(WORKFLOW_STEPS)}")
    print(f"PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER_REQUIRED_FILE_COUNT={len(REQUIRED_MARKERS) + 1}")
    print(
        "PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 9 bootstrap trace-events cluster stays "
            "in order between the Phase 8 tooling tail and the next shared-control "
            "checker handoff, while the current reminder packet stays aligned."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing fixture tree for current-like replay",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        seed_fixture_tree(args.write_sample_root)
        print(f"PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = validate(args.root)
    if failures:
        print("PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER=fail")
        for failure in failures:
            print(f"PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER_ERROR={failure}")
        return 1

    print("PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER=pass")
    print(f"PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER_WORKFLOW_STEP_COUNT={len(WORKFLOW_STEPS)}")
    print(f"PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER_REQUIRED_FILE_COUNT={len(REQUIRED_MARKERS) + 1}")
    print(
        "PHASE9_BOOTSTRAP_TRACE_EVENTS_CLUSTER_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
