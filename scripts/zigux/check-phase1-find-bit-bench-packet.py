#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

EXPECTED_ITERATIONS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
}

EXPECTED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 15621472,
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 12820000,
}

REQUIRED_FILES = [
    "scripts/zigux/check-phase1-find-bit-bench-packet.py",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/phase1_bench.zig",
]

REQUIRED_MARKERS = {
    "zigux/tests/phase1_bench.zig": [
        "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
        "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
        "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    ],
}


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel)
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}:missing={marker}")

    expectations = json.loads(read_text(root, "zigux/tests/fixtures/phase1_bench_expectations.json"))
    iterations = expectations.get("iterations")
    exact_checksums = expectations.get("exact_checksums")

    if not isinstance(iterations, dict):
        missing.append("zigux/tests/fixtures/phase1_bench_expectations.json:iterations=dict")
    else:
        for key, expected in EXPECTED_ITERATIONS.items():
            if iterations.get(key) != expected:
                missing.append(f"zigux/tests/fixtures/phase1_bench_expectations.json:iteration={key}:{expected}")

    if not isinstance(exact_checksums, dict):
        missing.append("zigux/tests/fixtures/phase1_bench_expectations.json:exact_checksums=dict")
    else:
        for key, expected in EXPECTED_EXACT_CHECKSUMS.items():
            if exact_checksums.get(key) != expected:
                missing.append(f"zigux/tests/fixtures/phase1_bench_expectations.json:exact_checksum={key}:{expected}")

    return missing


def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")

    for rel, markers in REQUIRED_MARKERS.items():
        (root / rel).write_text("\n".join(markers) + "\n", encoding="utf-8")

    expectations = {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_EXACT_CHECKSUMS),
        "exact_checksums": dict(EXPECTED_EXACT_CHECKSUMS),
    }
    (root / "zigux/tests/fixtures/phase1_bench_expectations.json").write_text(
        json.dumps(expectations, indent=2) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_bench_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []

        bench = root / "zigux/tests/phase1_bench.zig"
        bench.write_text("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS\n", encoding="utf-8")
        assert any("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM" in item for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        expectations_path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        expectations = json.loads(expectations_path.read_text(encoding="utf-8"))
        expectations["iterations"]["PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS"] = 1
        expectations_path.write_text(json.dumps(expectations, indent=2) + "\n", encoding="utf-8")
        assert any("iteration=PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS:20000" in item for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        (root / "scripts/zigux/check-phase1-find-bit-bench-packet.py").unlink()
        assert collect_missing_files(root) == ["scripts/zigux/check-phase1-find-bit-bench-packet.py"]
        case_count += 1

    print("PHASE1_FIND_BIT_BENCH_PACKET_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_BENCH_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 find_bit bench packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_FIND_BIT_BENCH_PACKET=fail")
        print("MISSING_PHASE1_FIND_BIT_BENCH_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_FIND_BIT_BENCH_PACKET_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_FIND_BIT_BENCH_PACKET=fail")
        print("MISSING_PHASE1_FIND_BIT_BENCH_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_FIND_BIT_BENCH_PACKET_MARKERS_END")
        return 1

    print("PHASE1_FIND_BIT_BENCH_PACKET=pass")
    print(f"PHASE1_FIND_BIT_BENCH_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_FIND_BIT_BENCH_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values()) + len(EXPECTED_ITERATIONS) + len(EXPECTED_EXACT_CHECKSUMS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
