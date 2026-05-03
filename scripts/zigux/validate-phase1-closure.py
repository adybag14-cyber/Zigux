#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    override = os.environ.get("ZIGUX_PHASE1_ROOT")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2]


ROOT = repo_root()

REQUIRED_FILE_RELS = [
    " .github/workflows/zigux-bootstrap.yml".strip(),
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "zigux/tests/phase1_bench.zig",
]

REQUIRED_WORKFLOW_MARKERS = [
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "uses: actions/checkout@v6.0.2",
    "uses: actions/setup-python@v6.2.0",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "run: python3 scripts/zigux/check-phase1-parity.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe",
]

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_CLOSURE_SELF_TEST_GATE=python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "PHASE1_STRING_MEMPARSE_UNIT_REVIEW=string memparse preserves decimal, hexadecimal, suffix-bearing, and invalid inputs without changing the parsed value or rest pointer contract",
    "PHASE1_RBTREE_BENCH_KEYS=PHASE1_BENCH_RBTREE_CHECKSUM,PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM,PHASE1_BENCH_RBTREE_CACHED_CHECKSUM,PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM,PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
]

REQUIRED_BUILD_MARKERS = [
    '.root_source_file = b.path("phase1_bench.zig"),',
    'bench_root_module.addImport("find_bit", find_bit_module);',
    "const bench = b.addExecutable(.{",
    '.name = "phase1-bench",',
    "const run_bench = b.addRunArtifact(bench);",
    'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");',
]

REQUIRED_LEDGER_MARKERS = [
    "15. `docs(zigux): close bounded phase-1 helper tranche`",
    "16. `test(zigux): harden phase-1 closure gates`",
    "17. `ci(zigux): harden phase-1 closure workflow viability`",
    "18. `build(zigux): remove node-20-bound Zig action from phase-1 closure path`",
]

REQUIRED_BENCH_CHECKER_MARKERS = [
    "print('PHASE1_BENCH_SELF_TEST=pass')",
    "print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=18')",
    "print('DUPLICATE_PHASE1_BENCH_KEYS_START')",
    "print('MISSING_PHASE1_BENCH_KEYS_START')",
]

REQUIRED_PARITY_CHECKER_MARKERS = [
    "print('PHASE1_PARITY_SELF_TEST=pass')",
    "print('PHASE1_PARITY_SELF_TEST_CASE_COUNT=7')",
]

REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 2260000,
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 620000,
    "PHASE1_BENCH_BITMAP_COPY_CHECKSUM": 22040000,
    "PHASE1_BENCH_BITMAP_SCNPRINTF_CHECKSUM": 11760000,
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 15621472,
    "PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM": 17862764,
    "PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM": 8124000,
    "PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM": 2200000,
    "PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM": 1929133,
    "PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM": 1925492,
    "PHASE1_BENCH_STRING_CHECKSUM": 2500000,
    "PHASE1_BENCH_STRING_BOOL_TRIM_CHECKSUM": 500000,
    "PHASE1_BENCH_STRING_MEMCHR_CHECKSUM": 2400000,
    "PHASE1_BENCH_STRING_COMPARE_CHECKSUM": 360000,
    "PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM": 437855789,
    "PHASE1_BENCH_RBTREE_CHECKSUM": 1308000,
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 1188000,
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 196000,
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 3484000,
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 1484000,
}

REQUIRED_ITERATIONS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_COPY_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_SCNPRINTF_ITERATIONS": 12000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
}

STRING_MEMPARSE_CONTRACT = (
    "Direct Zig unit coverage keeps memparse aligned by preserving decimal, "
    "hexadecimal, suffix-bearing, and invalid inputs without changing the parsed "
    "value or rest pointer contract."
)


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def fail(items: list[str]) -> int:
    print("PHASE1_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE1_CLOSURE_MARKERS_START")
    for item in items:
        print(item)
    print("MISSING_PHASE1_CLOSURE_MARKERS_END")
    return 1


def validate_manifest(missing: list[str]) -> None:
    manifest = json.loads(read_text("zigux/tests/fixtures/phase1_helper_manifest.json"))
    notes = manifest.get("helper_review_notes", {})
    string_note = notes.get("tools/lib/string.zig", {})
    if string_note.get("memparse_unit_test_contract") != STRING_MEMPARSE_CONTRACT:
        missing.append("manifest:tools/lib/string.zig:memparse_unit_test_contract")


def validate_expectations(missing: list[str]) -> None:
    expectations = json.loads(read_text("zigux/tests/fixtures/phase1_bench_expectations.json"))
    if expectations.get("status") != "pass":
        missing.append("bench:status=pass")
    iterations = expectations.get("iterations", {})
    exact = expectations.get("exact_checksums", {})
    checksums = set(expectations.get("checksums", []))

    for key, expected in REQUIRED_ITERATIONS.items():
        if iterations.get(key) != expected:
            missing.append(f"bench:iterations.{key}={expected}")
    for key, expected in REQUIRED_EXACT_CHECKSUMS.items():
        if exact.get(key) != expected:
            missing.append(f"bench:exact_checksums.{key}={expected}")
        if key in checksums:
            missing.append(f"bench:remove_loose_exact_checksum:{key}")


def main() -> int:
    missing_files = [rel for rel in REQUIRED_FILE_RELS if not (ROOT / rel).exists()]
    if missing_files:
        return fail([f"file:{rel}" for rel in missing_files])

    missing: list[str] = []
    checks = [
        ("closure", "Documentation/zigux/phase1-closure.md", REQUIRED_CLOSURE_MARKERS),
        ("workflow", ".github/workflows/zigux-bootstrap.yml", REQUIRED_WORKFLOW_MARKERS),
        ("build", "zigux/tests/build.zig", REQUIRED_BUILD_MARKERS),
        ("ledger", "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", REQUIRED_LEDGER_MARKERS),
        ("bench_checker", "scripts/zigux/check-phase1-bench.py", REQUIRED_BENCH_CHECKER_MARKERS),
        ("parity_checker", "scripts/zigux/check-phase1-parity.py", REQUIRED_PARITY_CHECKER_MARKERS),
    ]
    for label, rel, markers in checks:
        text = read_text(rel)
        for marker in markers:
            if marker not in text:
                missing.append(f"{label}:{marker}")

    validate_manifest(missing)
    validate_expectations(missing)

    if missing:
        return fail(missing)

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILE_RELS)}")
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_BUILD_MARKERS) + len(REQUIRED_LEDGER_MARKERS) + len(REQUIRED_BENCH_CHECKER_MARKERS) + len(REQUIRED_PARITY_CHECKER_MARKERS)}"
    )
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-closure-") as tmp:
        root = Path(tmp)
        for rel in REQUIRED_FILE_RELS:
            if rel.endswith(".json"):
                continue
            write(root / rel, "// fixture\n")

        write(root / "Documentation/zigux/phase1-closure.md", "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
        write(root / ".github/workflows/zigux-bootstrap.yml", "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n")
        write(root / "zigux/tests/build.zig", "\n".join(REQUIRED_BUILD_MARKERS) + "\n")
        write(root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", "\n".join(REQUIRED_LEDGER_MARKERS) + "\n")
        write(root / "scripts/zigux/check-phase1-bench.py", "\n".join(REQUIRED_BENCH_CHECKER_MARKERS) + "\n")
        write(root / "scripts/zigux/check-phase1-parity.py", "\n".join(REQUIRED_PARITY_CHECKER_MARKERS) + "\n")
        write(
            root / "zigux/tests/fixtures/phase1_helper_manifest.json",
            json.dumps(
                {
                    "helper_review_notes": {
                        "tools/lib/string.zig": {
                            "memparse_unit_test_contract": STRING_MEMPARSE_CONTRACT,
                        }
                    }
                },
                indent=2,
            )
            + "\n",
        )
        write(
            root / "zigux/tests/fixtures/phase1_bench_expectations.json",
            json.dumps(
                {
                    "status": "pass",
                    "iterations": REQUIRED_ITERATIONS,
                    "exact_checksums": REQUIRED_EXACT_CHECKSUMS,
                    "checksums": [
                        "PHASE1_BENCH_HWEIGHT_CHECKSUM",
                        "PHASE1_BENCH_LIST_SORT_CHECKSUM",
                    ],
                },
                indent=2,
            )
            + "\n",
        )
        write(root / "zigux/tests/fixtures/phase1_helpers.json", "{}\n")

        env = dict(os.environ)
        env["ZIGUX_PHASE1_ROOT"] = str(root)
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, __file__], env)
        if code != 0:
            print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=fail")
            return 1

        write(
            root / "scripts/zigux/check-phase1-bench.py",
            "print('PHASE1_BENCH_SELF_TEST=pass')\nprint('PHASE1_BENCH_SELF_TEST_CASE_COUNT=16')\n",
        )
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, __file__], env)
        if code == 0:
            print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=fail")
            return 1

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=2")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())
