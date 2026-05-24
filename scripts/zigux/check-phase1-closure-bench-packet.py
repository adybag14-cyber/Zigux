#!/usr/bin/env python3
"""Guard the live Phase 1 closure-note bench packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    BENCH_CHECKER_REL,
    VALIDATOR_REL,
    WORKFLOW_REL,
)

EXPECTED_CLOSURE_MARKERS = {
    "find_bit_guard": (
        "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still "
        "hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and "
        "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires "
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM "
        "when the broader expectations packet returns`"
    ),
    "find_bit_anchor_guard": (
        "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 "
        "scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks "
        "inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and "
        "findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`"
    ),
    "rbtree_guard": (
        "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now "
        "hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks "
        "PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, "
        "PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, "
        "and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet "
        "returns`"
    ),
    "closure_validator": (
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`"
    ),
    "validator_state": (
        "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`"
    ),
}

EXPECTED_LANE_NOTE_MARKERS = {
    "shared_gap_summary": (
        "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now keeps "
        "scripts/zigux/check-phase1-bench.py explicit across Documentation/zigux/README.md, "
        "Documentation/zigux/review-checklist.md, zigux/tests/README.md, and "
        "scripts/zigux/README.md, while the older installer-backed, validator-first, "
        "bench-route, and replay names stay historical packet members until they reread "
        "cleanly on current master`"
    ),
    "active_packet": (
        "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,"
        "Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,"
        "zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,"
        "scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,"
        "scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`"
    ),
    "next_step": (
        "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording "
        "and shared-reminder checker packet parked unless a fresh reread finds drift across "
        "Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, "
        "scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, "
        "scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or "
        "scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller "
        "helper-specific next-safe-step markers below before reopening any shared reminder surface`"
    ),
}

EXPECTED_VALIDATOR_MARKERS = (
    'FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
    '(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors"),',
    '`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`',
)

EXPECTED_WORKFLOW_MARKERS = (
    "- name: Self-test current Phase 1 bench checker",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
)

FORBIDDEN_WORKFLOW_MARKERS = ("- name: Check current Phase 1 bench packet",)

EXPECTED_BENCH_MARKERS = (
    '"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,',
    '"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,',
    '"PHASE1_BENCH_RBTREE_ITERATIONS": 4000,',
    '"find_next_iterations_print": \'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\\\\n", .{iterations_find_bit});\',',
    '"find_edge_checksum_print": \'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\\\n", .{find_bit_edge_result.checksum});\',',
    '"rbtree_iterations_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\\\\n", .{iterations_rbtree});\',',
    '"rbtree_cached_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\\\n", .{rbtree_cached_result.checksum});\',',
    '("missing rbtree iteration", ok_output.replace("\\nPHASE1_BENCH_RBTREE_ITERATIONS=4000", ""), "missing_rbtree_iterations", ["PHASE1_BENCH_RBTREE_ITERATIONS"]),',
    '("rbtree iteration mismatch", ok_output.replace("PHASE1_BENCH_RBTREE_ITERATIONS=4000", "PHASE1_BENCH_RBTREE_ITERATIONS=4"), "rbtree_iteration_mismatch", ("PHASE1_BENCH_RBTREE_ITERATIONS", 4000, "4")),',
    '("missing_find_bit_exact_checksums", "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM", "3"),',
    '("missing_find_bit_exact_checksums", "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM", "4"),',
    '("expectations_checksums_rbtree_exact_required", "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM", "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM"),',
    '("expectations_checksums_rbtree_exact_required", "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"),',
)

EXPECTED_BENCH_CONTAINS = (
    '"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",',
    '"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",',
    '"PHASE1_BENCH_RBTREE_CHECKSUM",',
    '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",',
    '"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",',
    '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",',
    '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_present(text: str, label: str, needle: str) -> list[str]:
    return [] if needle in text else [f"{label}:missing:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for label, marker in EXPECTED_CLOSURE_MARKERS.items():
        failures.extend(
            require_exact_occurrence(
                closure_text,
                f"{PHASE1_CLOSURE_REL.as_posix()}:{label}",
                marker,
            )
        )

    lane_note_text = load_text(root, PHASE1_LANE_NOTE_REL)
    for label, marker in EXPECTED_LANE_NOTE_MARKERS.items():
        failures.extend(
            require_exact_occurrence(
                lane_note_text,
                f"{PHASE1_LANE_NOTE_REL.as_posix()}:{label}",
                marker,
            )
        )

    validator_text = load_text(root, VALIDATOR_REL)
    for marker in EXPECTED_VALIDATOR_MARKERS:
        failures.extend(
            require_exact_occurrence(
                validator_text,
                f"{VALIDATOR_REL.as_posix()}:required",
                marker,
            )
        )

    workflow_text = load_text(root, WORKFLOW_REL)
    for marker in EXPECTED_WORKFLOW_MARKERS:
        failures.extend(
            require_exact_occurrence(
                workflow_text,
                f"{WORKFLOW_REL.as_posix()}:required",
                marker,
            )
        )
    for marker in FORBIDDEN_WORKFLOW_MARKERS:
        count = workflow_text.count(marker)
        if count:
            failures.append(
                f"{WORKFLOW_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}"
            )

    bench_checker_text = load_text(root, BENCH_CHECKER_REL)
    for marker in EXPECTED_BENCH_MARKERS:
        failures.extend(
            require_exact_occurrence(
                bench_checker_text,
                f"{BENCH_CHECKER_REL.as_posix()}:required",
                marker,
            )
        )
    for marker in EXPECTED_BENCH_CONTAINS:
        failures.extend(
            require_present(
                bench_checker_text,
                f"{BENCH_CHECKER_REL.as_posix()}:required",
                marker,
            )
        )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(
        root / PHASE1_CLOSURE_REL,
        "# Phase 1 Closure\n\n" + "\n".join(EXPECTED_CLOSURE_MARKERS.values()) + "\n",
    )
    write_text(
        root / PHASE1_LANE_NOTE_REL,
        "# Phase 1 Host-Helper Lane Sequencing\n\n"
        + "\n".join(EXPECTED_LANE_NOTE_MARKERS.values())
        + "\n",
    )
    write_text(
        root / VALIDATOR_REL,
        "\n".join(EXPECTED_VALIDATOR_MARKERS) + "\n",
    )
    write_text(
        root / WORKFLOW_REL,
        "\n".join(EXPECTED_WORKFLOW_MARKERS) + "\n",
    )
    write_text(
        root / BENCH_CHECKER_REL,
        "\n".join(EXPECTED_BENCH_MARKERS + EXPECTED_BENCH_CONTAINS) + "\n",
    )


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        (
            "missing_find_bit_guard",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_CLOSURE_MARKERS["find_bit_guard"] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_find_bit_anchor_guard",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_CLOSURE_MARKERS["find_bit_anchor_guard"] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_rbtree_guard",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_CLOSURE_MARKERS["rbtree_guard"] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_closure_validator",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_CLOSURE_MARKERS["closure_validator"] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_validator_state",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_CLOSURE_MARKERS["validator_state"] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "stale_lane_note_next_step",
            lambda root: write_text(
                root / PHASE1_LANE_NOTE_REL,
                load_text(root, PHASE1_LANE_NOTE_REL).replace(
                    EXPECTED_LANE_NOTE_MARKERS["next_step"],
                    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=drifted`",
                    1,
                ),
            ),
        ),
        (
            "missing_validator_anchor_path",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(
                    EXPECTED_VALIDATOR_MARKERS[0] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_validator_anchor_delegate",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(
                    EXPECTED_VALIDATOR_MARKERS[1] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_validator_anchor_marker",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(
                    EXPECTED_VALIDATOR_MARKERS[2] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_workflow_selftest_line",
            lambda root: write_text(
                root / WORKFLOW_REL,
                load_text(root, WORKFLOW_REL).replace(
                    EXPECTED_WORKFLOW_MARKERS[1] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "forbidden_workflow_check_line",
            lambda root: write_text(
                root / WORKFLOW_REL,
                load_text(root, WORKFLOW_REL)
                + "- name: Check current Phase 1 bench packet\n"
                + "run: python3 scripts/zigux/check-phase1-bench.py\n",
            ),
        ),
        (
            "missing_bench_exact_marker",
            lambda root: write_text(
                root / BENCH_CHECKER_REL,
                load_text(root, BENCH_CHECKER_REL).replace(
                    EXPECTED_BENCH_MARKERS[8] + "\n",
                    "",
                    1,
                ),
            ),
        ),
        (
            "missing_bench_selftest_case",
            lambda root: write_text(
                root / BENCH_CHECKER_REL,
                load_text(root, BENCH_CHECKER_REL).replace(
                    EXPECTED_BENCH_MARKERS[12] + "\n",
                    "",
                    1,
                ),
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-bench-selftest-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-bench-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-bench-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_BENCH_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_BENCH_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
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

    print("PHASE1_CLOSURE_BENCH_PACKET=pass")
    print("PHASE1_CLOSURE_BENCH_PACKET_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
