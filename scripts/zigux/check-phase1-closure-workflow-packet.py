#!/usr/bin/env python3
"""Guard the closure-side Phase 1 workflow packet in zigux-bootstrap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
ROUTE_SUMMARY_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")

REQUIRED_FILES = (
    WORKFLOW_REL,
    ROUTE_SUMMARY_REL,
    BENCH_REL,
    SHARED_REMINDER_REL,
    CLOSURE_VALIDATOR_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
)

EXACT_ONCE_LINES = (
    "- name: Self-test current Phase 1 route summary checker",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "- name: Check current Phase 1 route summary packet",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "- name: Self-test current Phase 1 bench checker",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "- name: Self-test current Phase 1 shared reminder checker",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "- name: Check current Phase 1 shared reminder packet",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "- name: Self-test current Phase 1 closure validator",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "- name: Check current Phase 1 closure packet",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "- name: Run current Phase 1 shared tests-root smoke",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    "- name: Self-test current Phase 3 interop packet",
)

ORDERED_LINES = EXACT_ONCE_LINES

FORBIDDEN_LINES = (
    "- name: Self-test Phase 1 bench checker",
    "- name: Self-test Phase 1 shared reminder checker",
    "- name: Self-test Phase 1 closure validator",
    "- name: Check Phase 1 shared reminder packet",
    "- name: Check Phase 1 closure packet",
    "run: python3 scripts/zigux/validate-phase1.py --self-test",
    "run: python3 scripts/zigux/validate-phase1.py",
    "run: zig build phase1-bench --build-file zigux/tests/build.zig",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def count_exact_lines(text: str, marker: str) -> int:
    want = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def collect_failures(root: Path) -> list[str]:
    failures = [
        f"missing_file:{relative_path.as_posix()}"
        for relative_path in REQUIRED_FILES
        if not (root / relative_path).is_file()
    ]
    if failures:
        return failures

    workflow_text = (root / WORKFLOW_REL).read_text(encoding="utf-8")

    for marker in EXACT_ONCE_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count != 1:
            failures.append(f"missing_or_duplicate:{marker}:count={count}")

    for marker in FORBIDDEN_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count != 0:
            failures.append(f"forbidden_present:{marker}:count={count}")

    if failures:
        return failures

    stripped = [line.strip() for line in workflow_text.splitlines()]
    positions = [stripped.index(marker.strip()) for marker in ORDERED_LINES]
    if positions != sorted(positions):
        failures.append("phase1_closure_workflow_packet:order_drift")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    for relative_path in (
        ROUTE_SUMMARY_REL,
        BENCH_REL,
        SHARED_REMINDER_REL,
        CLOSURE_VALIDATOR_REL,
    ):
        write_text(root / relative_path, "#!/usr/bin/env python3\nprint('stub:ok')\n")

    write_text(root / TESTS_BUILD_REL, 'pub fn build(_: *std.Build) void {}\n')
    write_text(root / PHASE1_SMOKE_REL, 'test "phase1 host-tools smoke exercises live helper behavior" {}\n')

    write_text(
        root / WORKFLOW_REL,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Phase 1 route summary checker",
                "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
                "      - name: Check current Phase 1 route summary packet",
                "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
                "      - name: Self-test current Phase 1 bench checker",
                "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
                "      - name: Self-test current Phase 1 shared reminder checker",
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
                "      - name: Check current Phase 1 shared reminder packet",
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
                "      - name: Self-test current Phase 1 closure validator",
                "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
                "      - name: Check current Phase 1 closure packet",
                "        run: python3 scripts/zigux/validate-phase1-closure.py",
                "      - name: Run current Phase 1 shared tests-root smoke",
                "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
                "      - name: Self-test current Phase 3 interop packet",
                "        run: python3 scripts/zigux/validate_phase3_selftest.py",
            )
        )
        + "\n",
    )


def remove_line(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(marker)


def duplicate_line(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(marker)


def swap_lines(root: Path, first: str, second: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    first_idx = next(i for i, line in enumerate(lines) if line.strip() == first.strip())
    second_idx = next(i for i, line in enumerate(lines) if line.strip() == second.strip())
    lines[first_idx], lines[second_idx] = lines[second_idx], lines[first_idx]
    workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_line(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    workflow.write_text(workflow.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_workflow", lambda root: (root / WORKFLOW_REL).unlink()),
        (
            "missing_route_summary_selftest",
            lambda root: remove_line(root, "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test"),
        ),
        (
            "duplicate_shared_reminder_live",
            lambda root: duplicate_line(root, "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
        ),
        (
            "missing_closure_live",
            lambda root: remove_line(root, "run: python3 scripts/zigux/validate-phase1-closure.py"),
        ),
        (
            "missing_phase3_boundary",
            lambda root: remove_line(root, "- name: Self-test current Phase 3 interop packet"),
        ),
        (
            "bad_order",
            lambda root: swap_lines(
                root,
                "- name: Self-test current Phase 1 bench checker",
                "- name: Check current Phase 1 closure packet",
            ),
        ),
        (
            "forbidden_old_validate_phase1",
            lambda root: append_line(root, "        run: python3 scripts/zigux/validate-phase1.py"),
        ),
        (
            "forbidden_old_shared_reminder_label",
            lambda root: append_line(root, "      - name: Check Phase 1 shared reminder packet"),
        ),
        ("missing_smoke_file", lambda root: (root / PHASE1_SMOKE_REL).unlink()),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-workflow-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-workflow:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-workflow:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample repo root")
    args = parser.parse_args()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_CLOSURE_WORKFLOW_PACKET_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_WORKFLOW_PACKET=pass")
    print(f"PHASE1_CLOSURE_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_CLOSURE_WORKFLOW_PACKET_REQUIRED_LINE_COUNT={len(EXACT_ONCE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
