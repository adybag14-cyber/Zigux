#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

APPROVER_MATRIX_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-approver-matrix.md"
)

REQUIRED_MATRIX_MARKERS = (
    "`PHASE15_STATUS=architecture_council_approver_matrix_landed`",
    "`PHASE15_LANE_KEY=P15-L17`",
    "`PHASE15_SLICE=required-approver-and-rollback-owner-matrix`",
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "`kernel/sched/core.c`",
    "`Architecture Council + PMO / Release Management`",
    "`blocked_no_bounded_scheduler_seam`",
    "`mm/page_alloc.c`",
    "`Architecture Council + Validation and Perf Team`",
    "`blocked_no_bounded_allocator_seam`",
    "`kernel/rcu/tree.c`",
    "`Architecture Council + ABI and Runtime Team`",
    "`blocked_phase14_followup_still_wider_than_allowed_rcu_seam`",
    "`net/core/skbuff.c`",
    "`Architecture Council + Shared Subsystems Pod`",
    "`blocked_packet_lifetime_boundary_still_too_wide`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_failures(root: Path) -> list[str]:
    if not (root / APPROVER_MATRIX_PATH).exists():
        return [f"missing_file:{APPROVER_MATRIX_PATH}"]

    matrix = _read(root / APPROVER_MATRIX_PATH)
    failures: list[str] = []
    for marker in REQUIRED_MATRIX_MARKERS:
        if marker not in matrix:
            failures.append(f"approver_matrix:missing:{marker}")
    return failures


def _sample_matrix() -> str:
    return """# Phase 15 Architecture Council Approver Matrix

- `PHASE15_STATUS=architecture_council_approver_matrix_landed`
- `PHASE15_LANE_KEY=P15-L17`
- `PHASE15_SLICE=required-approver-and-rollback-owner-matrix`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`

### `kernel/sched/core.c`
- `Architecture Council + PMO / Release Management`
- `blocked_no_bounded_scheduler_seam`

### `mm/page_alloc.c`
- `Architecture Council + Validation and Perf Team`
- `blocked_no_bounded_allocator_seam`

### `kernel/rcu/tree.c`
- `Architecture Council + ABI and Runtime Team`
- `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`

### `net/core/skbuff.c`
- `Architecture Council + Shared Subsystems Pod`
- `blocked_packet_lifetime_boundary_still_too_wide`
"""


def _seed(root: Path) -> None:
    _write(root / APPROVER_MATRIX_PATH, _sample_matrix())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_approver_matrix_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_anchor = root / "missing_anchor"
        _seed(missing_anchor)
        _write(
            missing_anchor / APPROVER_MATRIX_PATH,
            _sample_matrix().replace("### `net/core/skbuff.c`\n", "", 1),
        )
        failures = collect_failures(missing_anchor)
        expected = ["approver_matrix:missing:`net/core/skbuff.c`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-anchor failure: {failures}")

        missing_file = root / "missing_file"
        _seed(missing_file)
        (missing_file / APPROVER_MATRIX_PATH).unlink()
        failures = collect_failures(missing_file)
        expected = [
            "missing_file:Documentation/zigux/phase15-architecture-council-approver-matrix.md"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-file failure: {failures}")

    print("PHASE15_APPROVER_MATRIX_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 Architecture Council approver matrix stays aligned with the current governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE15_APPROVER_MATRIX=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
