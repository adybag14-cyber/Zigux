#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
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
    ".github/workflows/zigux-bootstrap.yml",
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

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_CLOSURE_SELF_TEST_GATE=python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "PHASE1_STRING_MEMPARSE_UNIT_REVIEW=string memparse preserves decimal, hexadecimal, suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B forms without changing the parsed value or rest pointer contract",
    "PHASE1_RBTREE_POSTORDER_SAFE_REBALANCE_UNIT_REVIEW=rbtree iteratePostorderSafe stays aligned across erase-driven rebalancing so the walk still reaches each remaining node exactly once after the current node is removed",
    "PHASE1_RBTREE_BENCH_KEYS=PHASE1_BENCH_RBTREE_CHECKSUM,PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM,PHASE1_BENCH_RBTREE_CACHED_CHECKSUM,PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM,PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
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

REQUIRED_BUILD_MARKERS = [
    '.root_source_file = b.path("phase1_bench.zig"),',
    'bench_root_module.addImport("find_bit", find_bit_module);',
    'const bench = b.addExecutable(.{',
    '.name = "phase1-bench",',
    'const run_bench = b.addRunArtifact(bench);',
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
    "print('bitmap.scnprintf_empty_len')",
    "print('bitmap.scnprintf_empty_bytes')",
    "print('bitmap.scnprintf_trunc_len')",
    "print('bitmap.scnprintf_trunc')",
    "print('PHASE1_PARITY_SELF_TEST=pass')",
    "print('PHASE1_PARITY_SELF_TEST_CASE_COUNT=7')",
]

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
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 1488000,
}

REQUIRED_MANIFEST_FIELDS = {
    "tools/lib/bitmap.zig": {
        "allocator_alias_unit_test_contract": "Direct Zig unit coverage keeps bitmap_alloc(), bitmap_zalloc(), and bitmap_free() aligned with bitmapAlloc(), bitmapZalloc(), and bitmapFree() for partial-word sizing, zero-filled allocation, and optional-handle reset semantics.",
    },
    "tools/lib/find_bit.zig": {
        "tail_word_boundary_unit_test_contract": "Direct Zig unit coverage keeps set, zero, and shared-bit tail scans aligned when the search starts exactly at the first tail-word bit index, so the first in-range tail match remains reachable without rereading an earlier full-word result.",
    },
    "tools/lib/rbtree.zig": {
        "cached_find_add_unit_test_contract": "Direct Zig unit coverage keeps findAddCached() aligned so equal-key probes return the original resident node, distinct inserts still link into the cached tree, and RootCached continues to expose the same leftmost node as the underlying tree root.",
        "postorder_safe_rebalance_unit_test_contract": "Direct Zig unit coverage keeps iteratePostorderSafe() aligned across erase-driven rebalancing so the walk still reaches each remaining node exactly once after the current node is removed.",
    },
    "tools/lib/string.zig": {
        "strscpy_unit_test_contract": "Direct Zig unit coverage keeps strscpy aligned with bounded kernel copy semantics for exact-fit, truncation, embedded-NUL, and zero-sized destination cases.",
        "sysfs_unit_test_contract": "Direct Zig unit coverage keeps sysfsStreq() and sysfs_streq() aligned by treating a single trailing newline as equivalent to C-string termination while still rejecting non-terminal newline and content mismatches.",
        "memparse_unit_test_contract": "Direct Zig unit coverage keeps memparse aligned by preserving decimal, hexadecimal, suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B forms without changing the parsed value or rest pointer contract.",
    },
}

RBTREE_UNEXPECTED_ALIAS_MARKERS = ["pub fn rb_first(", "pub fn rb_next_match(", "pub fn rb_erase("]


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def fail(items: list[str]) -> int:
    print("PHASE1_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE1_CLOSURE_MARKERS_START")
    for item in items:
        print(item)
    print("MISSING_PHASE1_CLOSURE_MARKERS_END")
    return 1


def check_contains(label: str, rel: str, markers: list[str], missing: list[str]) -> None:
    text = read_text(rel)
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate_manifest(missing: list[str]) -> None:
    manifest = json.loads(read_text("zigux/tests/fixtures/phase1_helper_manifest.json"))
    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        missing.append("manifest:status=closed")
    if manifest.get("helper_count") != 13:
        missing.append("manifest:helper_count=13")
    review = manifest.get("helper_review_notes", {})
    for helper, fields in REQUIRED_MANIFEST_FIELDS.items():
        actual = review.get(helper, {})
        for key, value in fields.items():
            if actual.get(key) != value:
                missing.append(f"manifest:{helper}:{key}")


def validate_expectations(missing: list[str]) -> None:
    expectations = json.loads(read_text("zigux/tests/fixtures/phase1_bench_expectations.json"))
    if expectations.get("status") != "pass":
        missing.append("bench:status=pass")
    iterations = expectations.get("iterations", {})
    exact = expectations.get("exact_checksums", {})
    checksums = set(expectations.get("checksums", []))
    for key, value in REQUIRED_ITERATIONS.items():
        if iterations.get(key) != value:
            missing.append(f"bench:iterations.{key}={value}")
    for key, value in REQUIRED_EXACT_CHECKSUMS.items():
        if exact.get(key) != value:
            missing.append(f"bench:exact_checksums.{key}={value}")
        if key in checksums:
            missing.append(f"bench:remove_loose_exact_checksum:{key}")


def validate_rbtree_alias_gap(missing: list[str]) -> None:
    source = read_text("tools/lib/rbtree.zig")
    for marker in RBTREE_UNEXPECTED_ALIAS_MARKERS:
        if marker in source:
            missing.append(f"rbtree_source:unexpected_alias:{marker}")


def main() -> int:
    missing_files = [rel for rel in REQUIRED_FILE_RELS if not (ROOT / rel).exists()]
    if missing_files:
        return fail([f"file:{rel}" for rel in missing_files])
    missing: list[str] = []
    check_contains("closure", "Documentation/zigux/phase1-closure.md", REQUIRED_CLOSURE_MARKERS, missing)
    check_contains("workflow", ".github/workflows/zigux-bootstrap.yml", REQUIRED_WORKFLOW_MARKERS, missing)
    check_contains("build", "zigux/tests/build.zig", REQUIRED_BUILD_MARKERS, missing)
    check_contains("ledger", "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", REQUIRED_LEDGER_MARKERS, missing)
    check_contains("bench_checker", "scripts/zigux/check-phase1-bench.py", REQUIRED_BENCH_CHECKER_MARKERS, missing)
    check_contains("parity_checker", "scripts/zigux/check-phase1-parity.py", REQUIRED_PARITY_CHECKER_MARKERS, missing)
    validate_manifest(missing)
    validate_expectations(missing)
    validate_rbtree_alias_gap(missing)
    if missing:
        return fail(missing)
    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILE_RELS)}")
    marker_count = sum(len(group) for group in [
        REQUIRED_CLOSURE_MARKERS,
        REQUIRED_WORKFLOW_MARKERS,
        REQUIRED_BUILD_MARKERS,
        REQUIRED_LEDGER_MARKERS,
        REQUIRED_BENCH_CHECKER_MARKERS,
        REQUIRED_PARITY_CHECKER_MARKERS,
    ])
    print(f"PHASE1_CLOSURE_REQUIRED_MARKER_COUNT={marker_count}")
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_manifest() -> dict[str, object]:
    review = {helper: dict(fields) for helper, fields in REQUIRED_MANIFEST_FIELDS.items()}
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helper_review_notes": review,
    }


def fixture_expectations() -> dict[str, object]:
    return {
        "status": "pass",
        "iterations": REQUIRED_ITERATIONS,
        "exact_checksums": REQUIRED_EXACT_CHECKSUMS,
        "checksums": ["PHASE1_BENCH_HWEIGHT_CHECKSUM", "PHASE1_BENCH_LIST_SORT_CHECKSUM"],
    }


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(root / "scripts/zigux/validate-phase1-closure.py")], cwd=root, capture_output=True, text=True, check=False)


def expect_failure(root: Path, expected: str) -> None:
    result = run_validator(root)
    if result.returncode == 0 or expected not in result.stdout:
        raise SystemExit(f"phase1-self-test:expected_failure:{expected}:actual:{result.stdout or result.stderr}")


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
        write(root / "scripts/zigux/artifact_diff.py", "# fixture\n")
        write(root / "scripts/zigux/install-zig.py", "# fixture\n")
        write(root / "zigux/tests/phase1_bench.zig", "// fixture\n")
        write(root / "zigux/tests/fixtures/phase1_helpers.json", "{}\n")
        write(root / "zigux/tests/fixtures/phase1_helpers_c_harness.c", "/* fixture */\n")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(fixture_expectations(), indent=2) + "\n")
        write(root / "tools/lib/rbtree.zig", "pub fn first() void {}\n")
        env = dict(os.environ)
        env["ZIGUX_PHASE1_ROOT"] = str(root)
        script_path = root / "scripts/zigux/validate-phase1-closure.py"
        script_path.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
        ok = subprocess.run([sys.executable, str(script_path)], cwd=root, env=env, capture_output=True, text=True, check=False)
        if ok.returncode != 0:
            raise SystemExit(f"phase1-self-test:baseline:{ok.stdout or ok.stderr}")

        write(root / "scripts/zigux/check-phase1-bench.py", "print('PHASE1_BENCH_SELF_TEST=pass')\n")
        expect_failure(root, "bench_checker:print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=18')")
        write(root / "scripts/zigux/check-phase1-bench.py", "\n".join(REQUIRED_BENCH_CHECKER_MARKERS) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/string.zig"]["memparse_unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/string.zig:memparse_unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["postorder_safe_rebalance_unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/rbtree.zig:postorder_safe_rebalance_unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        expectations = fixture_expectations()
        expectations["exact_checksums"]["PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM"] = 1
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(expectations, indent=2) + "\n")
        expect_failure(root, "bench:exact_checksums.PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM=437855789")
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(fixture_expectations(), indent=2) + "\n")

        expectations = fixture_expectations()
        expectations["iterations"]["PHASE1_BENCH_RBTREE_ITERATIONS"] = 1
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(expectations, indent=2) + "\n")
        expect_failure(root, "bench:iterations.PHASE1_BENCH_RBTREE_ITERATIONS=4000")
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(fixture_expectations(), indent=2) + "\n")

        write(root / "tools/lib/rbtree.zig", "pub fn rb_first() void {}\n")
        expect_failure(root, "rbtree_source:unexpected_alias:pub fn rb_first(")

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=7")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())
