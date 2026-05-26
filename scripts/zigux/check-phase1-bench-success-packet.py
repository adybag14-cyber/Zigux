#!/usr/bin/env python3
"""Guard the current Phase 1 bench success packet against footer and workflow drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_BENCH_MARKERS = {
    "success_status": 'print("PHASE1_BENCH_CHECK=pass")',
    "success_expectations": 'print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")',
    "success_source": 'print(f"PHASE1_BENCH_SOURCE={phase1_bench}")',
    "success_zig": 'print(f"PHASE1_BENCH_ZIG={zig}")',
    "self_test_status": 'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
    "self_test_case_count": 'print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
}

REJECTED_BENCH_MARKERS = {
    "stale_expectation_count": "PHASE1_BENCH_EXPECTATION_COUNT",
}

REQUIRED_WORKFLOW_MARKERS = {
    "self_test_step_name": "- name: Self-test current Phase 1 bench checker",
    "self_test_command": "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def collect_exact_count_failures(text: str, markers: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for label, marker in markers.items():
        count = text.count(marker)
        if count != 1:
            failures.append(f"{label}:expected=1:actual={count}")
    return failures


def collect_rejected_marker_failures(text: str, markers: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for label, marker in markers.items():
        count = text.count(marker)
        if count != 0:
            failures.append(f"{label}:expected=0:actual={count}")
    return failures


def validate_packet(bench_text: str, workflow_text: str) -> tuple[str, object]:
    bench_failures = collect_exact_count_failures(bench_text, REQUIRED_BENCH_MARKERS)
    if bench_failures:
        return ("invalid_bench_marker_counts", bench_failures)

    rejected_failures = collect_rejected_marker_failures(bench_text, REJECTED_BENCH_MARKERS)
    if rejected_failures:
        return ("stale_bench_markers_present", rejected_failures)

    workflow_failures = collect_exact_count_failures(workflow_text, REQUIRED_WORKFLOW_MARKERS)
    if workflow_failures:
        return ("invalid_workflow_marker_counts", workflow_failures)

    return ("pass", None)


def load_text(root: Path, relative_path: Path) -> tuple[str, object]:
    path = root / relative_path
    try:
        return ("pass", path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ("missing_file", path)


def load_packet(root: Path) -> tuple[str, object]:
    bench_kind, bench_payload = load_text(root, BENCH_CHECKER_REL)
    if bench_kind != "pass":
        return (bench_kind, bench_payload)

    workflow_kind, workflow_payload = load_text(root, WORKFLOW_REL)
    if workflow_kind != "pass":
        return (workflow_kind, workflow_payload)

    assert isinstance(bench_payload, str)
    assert isinstance(workflow_payload, str)
    return validate_packet(bench_payload, workflow_payload)


def build_sample_bench(
    omit_label: str | None = None,
    duplicate_label: str | None = None,
    include_rejected_label: str | None = None,
) -> str:
    lines = list(REQUIRED_BENCH_MARKERS.values())

    if omit_label is not None:
        marker = REQUIRED_BENCH_MARKERS[omit_label]
        lines = [line for line in lines if line != marker]

    if duplicate_label is not None:
        marker = REQUIRED_BENCH_MARKERS[duplicate_label]
        for idx, line in enumerate(lines):
            if line == marker:
                lines.insert(idx + 1, line)
                break

    if include_rejected_label is not None:
        lines.append(REJECTED_BENCH_MARKERS[include_rejected_label])

    return "\n".join(lines) + "\n"


def build_sample_workflow(
    omit_label: str | None = None,
    duplicate_label: str | None = None,
) -> str:
    lines = list(REQUIRED_WORKFLOW_MARKERS.values())

    if omit_label is not None:
        marker = REQUIRED_WORKFLOW_MARKERS[omit_label]
        lines = [line for line in lines if line != marker]

    if duplicate_label is not None:
        marker = REQUIRED_WORKFLOW_MARKERS[duplicate_label]
        for idx, line in enumerate(lines):
            if line == marker:
                lines.insert(idx + 1, line)
                break

    return "\n".join(lines) + "\n"


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> None:
    case_count = 0

    kind, payload = validate_packet(build_sample_bench(), build_sample_workflow())
    assert kind == "pass", (kind, payload)
    case_count += 1

    for label in REQUIRED_BENCH_MARKERS:
        kind, payload = validate_packet(
            build_sample_bench(omit_label=label),
            build_sample_workflow(),
        )
        assert kind == "invalid_bench_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=0"], (label, payload)
        case_count += 1

    for label in REQUIRED_BENCH_MARKERS:
        kind, payload = validate_packet(
            build_sample_bench(duplicate_label=label),
            build_sample_workflow(),
        )
        assert kind == "invalid_bench_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=2"], (label, payload)
        case_count += 1

    for label in REJECTED_BENCH_MARKERS:
        kind, payload = validate_packet(
            build_sample_bench(include_rejected_label=label),
            build_sample_workflow(),
        )
        assert kind == "stale_bench_markers_present", (label, kind, payload)
        assert payload == [f"{label}:expected=0:actual=1"], (label, payload)
        case_count += 1

    for label in REQUIRED_WORKFLOW_MARKERS:
        kind, payload = validate_packet(
            build_sample_bench(),
            build_sample_workflow(omit_label=label),
        )
        assert kind == "invalid_workflow_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=0"], (label, payload)
        case_count += 1

    for label in REQUIRED_WORKFLOW_MARKERS:
        kind, payload = validate_packet(
            build_sample_bench(),
            build_sample_workflow(duplicate_label=label),
        )
        assert kind == "invalid_workflow_marker_counts", (label, kind, payload)
        assert payload == [f"{label}:expected=1:actual=2"], (label, payload)
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-success-packet-") as tmp:
        root = Path(tmp)

        kind, payload = load_packet(root)
        assert kind == "missing_file", (kind, payload)
        assert payload == root / BENCH_CHECKER_REL
        case_count += 1

        write_file(root, BENCH_CHECKER_REL, build_sample_bench())
        kind, payload = load_packet(root)
        assert kind == "missing_file", (kind, payload)
        assert payload == root / WORKFLOW_REL
        case_count += 1

        write_file(root, WORKFLOW_REL, build_sample_workflow())
        kind, payload = load_packet(root)
        assert kind == "pass", (kind, payload)
        case_count += 1

    print("PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run self-test cases")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    kind, payload = load_packet(repo_root(args.root))
    if kind != "pass":
        if isinstance(payload, list):
            for failure in payload:
                print(failure)
        else:
            print(f"{kind}:{payload}")
        return 1

    print("PHASE1_BENCH_SUCCESS_PACKET=pass")
    print(f"PHASE1_BENCH_SUCCESS_PACKET_CHECKER={BENCH_CHECKER_REL.as_posix()}")
    print(f"PHASE1_BENCH_SUCCESS_PACKET_WORKFLOW={WORKFLOW_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
