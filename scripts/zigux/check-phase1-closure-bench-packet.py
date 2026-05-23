#!/usr/bin/env python3
"""Guard the live Phase 1 closure-side bench packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    BENCH_CHECKER_REL,
    CLOSURE_VALIDATOR_REL,
)

EXPECTED_CLOSURE_MARKERS = {
    "find_bit_bench_guard": (
        "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes "
        "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 "
        "and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM "
        "when the broader expectations packet returns`"
    ),
    "rbtree_bench_guard": (
        "`PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes "
        "PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, "
        "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM, "
        "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the "
        "broader expectations packet returns`"
    ),
}

EXPECTED_BENCH_MARKERS = {
    "find_next_iterations": '"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,',
    "find_edge_iterations": '"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,',
    "rbtree_iterations": '"PHASE1_BENCH_RBTREE_ITERATIONS": 4000,',
    "find_next_checksum": '"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",',
    "find_edge_checksum": '"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",',
    "rbtree_checksum": '"PHASE1_BENCH_RBTREE_CHECKSUM",',
    "rbtree_postorder_safe_checksum": '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",',
    "rbtree_find_add_checksum": '"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",',
    "rbtree_duplicate_checksum": '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",',
    "rbtree_cached_checksum": '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
}

EXPECTED_VALIDATOR_MARKERS = {
    "bench_checker_path": 'BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")',
    "find_bit_marker_key": '"find_bit_bench_guard": "`PHASE1_FIND_BIT_BENCH_GUARD=',
    "bench_delegate": '(BENCH_CHECKER_REL, "phase1-bench"),',
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


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

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for label, marker in EXPECTED_CLOSURE_MARKERS.items():
        failures.extend(
            require_exact_occurrence(
                closure_text,
                f"{PHASE1_CLOSURE_REL.as_posix()}:{label}",
                marker,
            )
        )

    bench_text = load_text(root, BENCH_CHECKER_REL)
    for label, marker in EXPECTED_BENCH_MARKERS.items():
        failures.extend(
            require_exact_occurrence(
                bench_text,
                f"{BENCH_CHECKER_REL.as_posix()}:{label}",
                marker,
            )
        )

    validator_text = load_text(root, CLOSURE_VALIDATOR_REL)
    for label, marker in EXPECTED_VALIDATOR_MARKERS.items():
        failures.extend(
            require_exact_occurrence(
                validator_text,
                f"{CLOSURE_VALIDATOR_REL.as_posix()}:{label}",
                marker,
            )
        )

    return failures


def make_fixture_tree(root: Path) -> None:
    write_text(
        root / PHASE1_CLOSURE_REL,
        "# Phase 1 Closure\n\n"
        + "\n".join(EXPECTED_CLOSURE_MARKERS.values())
        + "\n",
    )
    write_text(
        root / BENCH_CHECKER_REL,
        "#!/usr/bin/env python3\n"
        + "\n".join(EXPECTED_BENCH_MARKERS.values())
        + "\n",
    )
    write_text(
        root / CLOSURE_VALIDATOR_REL,
        "#!/usr/bin/env python3\n"
        + "\n".join(EXPECTED_VALIDATOR_MARKERS.values())
        + "\n",
    )


def mutate_remove_closure_marker(root: Path, key: str) -> None:
    path = root / PHASE1_CLOSURE_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(EXPECTED_CLOSURE_MARKERS[key] + "\n", "", 1), encoding="utf-8")


def mutate_replace_closure_marker(root: Path, key: str, replacement: str) -> None:
    path = root / PHASE1_CLOSURE_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(EXPECTED_CLOSURE_MARKERS[key], replacement, 1), encoding="utf-8")


def mutate_remove_bench_marker(root: Path, key: str) -> None:
    path = root / BENCH_CHECKER_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(EXPECTED_BENCH_MARKERS[key] + "\n", "", 1), encoding="utf-8")


def mutate_remove_validator_marker(root: Path, key: str) -> None:
    path = root / CLOSURE_VALIDATOR_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(EXPECTED_VALIDATOR_MARKERS[key] + "\n", "", 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_find_bit_closure_marker", lambda root: mutate_remove_closure_marker(root, "find_bit_bench_guard")),
        ("missing_rbtree_closure_marker", lambda root: mutate_remove_closure_marker(root, "rbtree_bench_guard")),
        (
            "drifted_rbtree_closure_marker",
            lambda root: mutate_replace_closure_marker(
                root,
                "rbtree_bench_guard",
                "`PHASE1_RBTREE_BENCH_GUARD=drifted rbtree bench marker`",
            ),
        ),
        ("missing_find_edge_checksum_marker", lambda root: mutate_remove_bench_marker(root, "find_edge_checksum")),
        ("missing_rbtree_cached_checksum_marker", lambda root: mutate_remove_bench_marker(root, "rbtree_cached_checksum")),
        ("missing_validator_delegate", lambda root: mutate_remove_validator_marker(root, "bench_delegate")),
        ("missing_validator_marker_key", lambda root: mutate_remove_validator_marker(root, "find_bit_marker_key")),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-bench-packet-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-bench-packet-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-bench-packet-self-test:{name}:expected_failure")
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
    print(f"PHASE1_CLOSURE_BENCH_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_CLOSURE_BENCH_PACKET_CLOSURE_MARKER_COUNT={len(EXPECTED_CLOSURE_MARKERS)}")
    print(f"PHASE1_CLOSURE_BENCH_PACKET_BENCH_MARKER_COUNT={len(EXPECTED_BENCH_MARKERS)}")
    print(f"PHASE1_CLOSURE_BENCH_PACKET_VALIDATOR_MARKER_COUNT={len(EXPECTED_VALIDATOR_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
