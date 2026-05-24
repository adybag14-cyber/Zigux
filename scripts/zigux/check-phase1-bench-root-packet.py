#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


TARGET_REL = Path("scripts/zigux/check-phase1-bench.py")
REQUIRED_MARKERS = {
    "default_root": "DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent",
    "expectations_rel": 'EXPECTATIONS_REL = Path("zigux/tests/fixtures/phase1_bench_expectations.json")',
    "bench_rel": 'PHASE1_BENCH_REL = Path("zigux/tests/phase1_bench.zig")',
    "repo_root_fn": "def repo_root(root: str | None) -> Path:",
    "expectations_path_fn": "def expectations_path(root: Path) -> Path:",
    "bench_source_path_fn": "def bench_source_path(root: Path) -> Path:",
    "argparse_root": 'parser.add_argument("--repo-root", "--root", dest="repo_root", help="Override the repository root used for validation.")',
    "root_assignment": "root = repo_root(args.repo_root)",
    "expectations_assignment": "expectations_file = expectations_path(root)",
    "bench_assignment": "phase1_bench = bench_source_path(root)",
    "load_rooted_expectations": "kind, payload = load_runtime_expectations(expectations_file)",
    "load_rooted_source": "kind, payload = load_runtime_bench_source(phase1_bench)",
    "bench_cwd": "cwd=str(root),",
    "pass_expectations_output": 'print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")',
    "pass_source_output": 'print(f"PHASE1_BENCH_SOURCE={phase1_bench}")',
    "selftest_root_override": 'assert_case(repo_root(str(root)) == root.resolve(), "repo root override")',
    "selftest_expectations_override": 'assert_case(kind == "pass", "expectations root override", (kind, payload))',
    "selftest_source_override": 'assert_case(kind == "pass", "bench source root override", (kind, payload))',
}


def target_path(root: Path) -> Path:
    return root / TARGET_REL


def validate_target(text: str) -> tuple[str, object]:
    missing = [label for label, marker in REQUIRED_MARKERS.items() if marker not in text]
    if missing:
        return ("missing_markers", missing)
    return ("pass", len(REQUIRED_MARKERS))


def load_target(root: Path) -> tuple[str, object]:
    path = target_path(root)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_target_file", path)
    return validate_target(text)


def write_sample_root(root: Path, *, omit_marker: str | None = None) -> Path:
    path = target_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [marker for key, marker in REQUIRED_MARKERS.items() if key != omit_marker]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def assert_case(condition: bool, name: str, payload: object = None) -> None:
    if not condition:
        raise AssertionError((name, payload))


def run_self_test() -> None:
    case_count = 0

    kind, payload = validate_target("\n".join(REQUIRED_MARKERS.values()) + "\n")
    assert_case(kind == "pass", "direct validation pass", (kind, payload))
    assert_case(payload == len(REQUIRED_MARKERS), "marker count", payload)
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-root-packet-") as tmpdir:
        root = Path(tmpdir)

        kind, payload = load_target(root)
        assert_case(kind == "missing_target_file", "missing target file", (kind, payload))
        assert_case(payload == target_path(root), "missing target path", payload)
        case_count += 1

        write_sample_root(root)
        kind, payload = load_target(root)
        assert_case(kind == "pass", "sample root pass", (kind, payload))
        assert_case(payload == len(REQUIRED_MARKERS), "sample root marker count", payload)
        case_count += 1

        write_sample_root(root, omit_marker="bench_cwd")
        kind, payload = load_target(root)
        assert_case(kind == "missing_markers", "missing bench cwd marker", (kind, payload))
        assert_case(payload == ["bench_cwd"], "missing bench cwd payload", payload)
        case_count += 1

        write_sample_root(root, omit_marker="selftest_root_override")
        kind, payload = load_target(root)
        assert_case(kind == "missing_markers", "missing selftest root marker", (kind, payload))
        assert_case(payload == ["selftest_root_override"], "missing selftest root payload", payload)
        case_count += 1

    print("PHASE1_BENCH_ROOT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_ROOT_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the current rooted Phase 1 bench contract in scripts/zigux/check-phase1-bench.py."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to inspect.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root at the provided path and exit.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run local checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"PHASE1_BENCH_ROOT_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    root = args.root.resolve()
    kind, payload = load_target(root)
    if kind == "missing_target_file":
        print("PHASE1_BENCH_ROOT_PACKET=fail")
        print(f"PHASE1_BENCH_ROOT_PACKET_REASON={kind}")
        print(f"PHASE1_BENCH_ROOT_PACKET_TARGET={payload}")
        return 1
    if kind != "pass":
        print("PHASE1_BENCH_ROOT_PACKET=fail")
        print(f"PHASE1_BENCH_ROOT_PACKET_REASON={kind}")
        print(",".join(payload))
        return 1

    print("PHASE1_BENCH_ROOT_PACKET=pass")
    print("PHASE1_BENCH_ROOT_PACKET_REQUIRED_FILE_COUNT=1")
    print(f"PHASE1_BENCH_ROOT_PACKET_REQUIRED_MARKER_COUNT={payload}")
    print(f"PHASE1_BENCH_ROOT_PACKET_TARGET={target_path(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
