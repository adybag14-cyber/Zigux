#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
if SELF_PATH.parent.name == "zigux" and SELF_PATH.parent.parent.name == "scripts":
    ROOT = SELF_PATH.parents[2]
else:
    ROOT = SELF_PATH.parent

REQUIRED_FILE_RELS = [
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("Documentation/zigux/phase1-closure.md"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helper_manifest.json"),
    Path("zigux/tests/fixtures/phase1_helpers.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
    Path("zigux/tests/phase1_bench.zig"),
]

PHASE1_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_CLOSURE_SELF_TEST_GATE=python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "PHASE1_FIND_BIT_ALIAS_UNIT_REVIEW=find_bit underscore alias entry points preserve the same set, shared-bit, and zero-bit scan semantics as the camelCase helpers across the same caller-selected bit windows and tail clamps",
    "PHASE1_BITMAP_ALIAS_UNIT_REVIEW=bitmap underscore alias entry points preserve the same caller-selected window semantics as the camelCase helpers for weight bitwise range and formatting operations",
    "PHASE1_STRING_SUFFIX_UNIT_REVIEW=string strEndsWith, str_ends_with, and strends keep kernel-style suffix checks aligned for exact, empty-suffix, shorter-input, and case-sensitive comparisons",
    "PHASE1_FIND_BIT_BENCH_REVIEW=find_bit benchmark smoke pins deterministic next-bit, whole-family, tail-window, same-word, zero-bit, and shared-bit scan checksums plus the live loop counts so helper-local scan regressions cannot hide behind a generic positive checksum or a silently shrunk workload",
    "PHASE1_FIND_BIT_BENCH_KEYS=PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM,PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM,PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM,PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM",
    "PHASE1_FIND_BIT_BENCH_ITERATIONS=PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS,PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS,PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS,PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS",
]

REQUIRED_WORKFLOW_MARKERS = [
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "uses: actions/checkout@v6.0.2",
    "uses: actions/setup-python@v6.2.0",
    "python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
    "run: zig version",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
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
    "const run_bench = b.addRunArtifact(bench);",
    'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");',
    "bench_step.dependOn(&run_bench.step);",
]

REQUIRED_LEDGER_MARKERS = [
    "15. `docs(zigux): close bounded phase-1 helper tranche`",
    "- `Documentation/zigux/phase1-closure.md`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "- `zigux/tests/phase1_bench.zig`",
    "16. `test(zigux): harden phase-1 closure gates`",
    "- `scripts/zigux/check-phase1-bench.py`",
    "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
]

REQUIRED_BENCH_CHECKER_MARKERS = [
    "print('PHASE1_BENCH_SELF_TEST=pass')",
    "print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=11')",
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
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS": 20000,
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
    "PHASE1_BENCH_RBTREE_CHECKSUM": 1308000,
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 1188000,
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 196000,
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 3484000,
}

REQUIRED_REVIEW_FIELDS = {
    "tools/lib/bitmap.zig": [
        "fixture",
        "unit_test_anchor",
        "alias_unit_test_anchor",
    ],
    "tools/lib/find_bit.zig": [
        "fixture",
        "unit_test_anchor",
        "set_unit_test_anchor",
        "and_unit_test_anchor",
        "mask_unit_test_anchor",
        "boundary_unit_test_anchor",
        "alias_unit_test_anchor",
    ],
    "tools/lib/rbtree.zig": [
        "fixture",
        "unit_test_anchor",
        "search_unit_test_anchor",
    ],
    "tools/lib/string.zig": [
        "fixture",
        "unit_test_anchor",
        "suffix_unit_test_anchor",
    ],
}


def has_conflict_marker(text: str) -> str | None:
    for marker in ("<<<<<<<", "=======", ">>>>>>>"):
        if marker in text:
            return marker
    return None


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "zigux" / "validate-phase1-closure.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase1-self-test:{label}:unexpected_pass")
    if expected_marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "none"
        raise SystemExit(
            f"phase1-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, indent=2) + "\n")


def build_manifest() -> dict[str, object]:
    review_notes: dict[str, dict[str, str]] = {}
    for rel_path, fields in REQUIRED_REVIEW_FIELDS.items():
        entry = {"fixture": "zigux/tests/fixtures/phase1_helpers.json"}
        for field in fields:
            if field == "fixture":
                continue
            entry[field] = f"{rel_path}:{field}"
        review_notes[rel_path] = entry
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": PHASE1_HELPERS,
        "helper_review_notes": review_notes,
    }


def build_expectations() -> dict[str, object]:
    return {
        "status": "pass",
        "iterations": {
            **REQUIRED_ITERATIONS,
            "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
        },
        "exact_checksums": REQUIRED_EXACT_CHECKSUMS,
        "checksums": [
            "PHASE1_BENCH_HWEIGHT_CHECKSUM",
            "PHASE1_BENCH_LIST_SORT_CHECKSUM",
        ],
    }


def create_fixture_root(root: Path) -> None:
    closure_body = "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n"
    workflow_body = "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n"
    build_body = "\n".join(REQUIRED_BUILD_MARKERS) + "\n"
    ledger_body = "\n".join(REQUIRED_LEDGER_MARKERS) + "\n"
    bench_checker_body = "\n".join(REQUIRED_BENCH_CHECKER_MARKERS) + "\n"
    parity_checker_body = "\n".join(REQUIRED_PARITY_CHECKER_MARKERS) + "\n"

    write_text(root / "Documentation" / "zigux" / "phase1-closure.md", closure_body)
    write_text(root / ".github" / "workflows" / "zigux-bootstrap.yml", workflow_body)
    write_text(root / "zigux" / "tests" / "build.zig", build_body)
    write_text(root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md", ledger_body)
    write_text(root / "scripts" / "zigux" / "check-phase1-bench.py", bench_checker_body)
    write_text(root / "scripts" / "zigux" / "check-phase1-parity.py", parity_checker_body)
    write_text(root / "scripts" / "zigux" / "artifact_diff.py", "# fixture\n")
    write_text(root / "scripts" / "zigux" / "install-zig.py", "# fixture\n")
    write_text(root / "zigux" / "tests" / "phase1_bench.zig", "// fixture\n")
    write_text(root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json", "{}\n")
    write_text(root / "zigux" / "tests" / "fixtures" / "phase1_helpers_c_harness.c", "/* fixture */\n")
    write_json(root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json", build_manifest())
    write_json(root / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json", build_expectations())
    shutil.copyfile(Path(__file__), root / "scripts" / "zigux" / "validate-phase1-closure.py")

    for helper in PHASE1_HELPERS:
        write_text(root / helper, "// helper fixture\n")


def check_text_markers(label: str, text: str, markers: list[str], missing: list[str]) -> None:
    conflict = has_conflict_marker(text)
    if conflict is not None:
        missing.append(f"{label}_conflict:{conflict}")
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate_manifest(root: Path, manifest: dict[str, object], missing: list[str]) -> None:
    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        missing.append("manifest:status=closed")
    if manifest.get("helper_count") != 13:
        missing.append("manifest:helper_count=13")

    helpers = manifest.get("helpers")
    if helpers != PHASE1_HELPERS:
        missing.append("manifest:helpers")
    else:
        for rel_path in helpers:
            if not (root / rel_path).exists():
                missing.append(f"manifest_file:{rel_path}")

    review_notes = manifest.get("helper_review_notes")
    if not isinstance(review_notes, dict):
        missing.append("manifest:helper_review_notes")
        return

    for rel_path, fields in REQUIRED_REVIEW_FIELDS.items():
        entry = review_notes.get(rel_path)
        if not isinstance(entry, dict):
            missing.append(f"manifest:{rel_path}")
            continue
        if entry.get("fixture") != "zigux/tests/fixtures/phase1_helpers.json":
            missing.append(f"manifest:{rel_path}.fixture")
        for field in fields:
            if not entry.get(field):
                missing.append(f"manifest:{rel_path}.{field}")


def validate_expectations(expectations: dict[str, object], missing: list[str]) -> None:
    if expectations.get("status") != "pass":
        missing.append("bench:status=pass")

    iterations = expectations.get("iterations")
    exact = expectations.get("exact_checksums")
    checksums = expectations.get("checksums")
    if not isinstance(iterations, dict):
        missing.append("bench:iterations")
        return
    if not isinstance(exact, dict):
        missing.append("bench:exact_checksums")
        return
    if not isinstance(checksums, list):
        missing.append("bench:checksums")
        return

    for key, expected in REQUIRED_ITERATIONS.items():
        if iterations.get(key) != expected:
            missing.append(f"bench:iterations.{key}={expected}")
    for key, expected in REQUIRED_EXACT_CHECKSUMS.items():
        if exact.get(key) != expected:
            missing.append(f"bench:exact_checksums.{key}={expected}")
        if key in checksums:
            missing.append(f"bench:remove_loose_exact_checksum:{key}")


def validate_tree(root: Path) -> tuple[int, list[str]]:
    required_files = [root / rel for rel in REQUIRED_FILE_RELS]
    missing_files = [str(path.relative_to(root)) for path in required_files if not path.exists()]
    if missing_files:
        return 1, [f"file:{item}" for item in missing_files]

    closure = (root / "Documentation" / "zigux" / "phase1-closure.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    build = (root / "zigux" / "tests" / "build.zig").read_text(encoding="utf-8")
    ledger = (root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md").read_text(encoding="utf-8")
    bench_checker = (root / "scripts" / "zigux" / "check-phase1-bench.py").read_text(encoding="utf-8")
    parity_checker = (root / "scripts" / "zigux" / "check-phase1-parity.py").read_text(encoding="utf-8")
    manifest = json.loads((root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json").read_text(encoding="utf-8"))
    expectations = json.loads((root / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json").read_text(encoding="utf-8"))

    missing: list[str] = []
    check_text_markers("closure", closure, REQUIRED_CLOSURE_MARKERS, missing)
    check_text_markers("workflow", workflow, REQUIRED_WORKFLOW_MARKERS, missing)
    check_text_markers("build", build, REQUIRED_BUILD_MARKERS, missing)
    check_text_markers("ledger", ledger, REQUIRED_LEDGER_MARKERS, missing)
    check_text_markers("bench_checker", bench_checker, REQUIRED_BENCH_CHECKER_MARKERS, missing)
    check_text_markers("parity_checker", parity_checker, REQUIRED_PARITY_CHECKER_MARKERS, missing)
    validate_manifest(root, manifest, missing)
    validate_expectations(expectations, missing)
    return (1 if missing else 0), missing


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        create_fixture_root(tmp_root)

        code, missing = validate_tree(tmp_root)
        if code != 0:
            raise SystemExit(f"phase1-self-test:baseline_failed:{','.join(missing)}")

        closure_path = tmp_root / "Documentation" / "zigux" / "phase1-closure.md"
        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        build_path = tmp_root / "zigux" / "tests" / "build.zig"
        ledger_path = tmp_root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md"
        bench_checker_path = tmp_root / "scripts" / "zigux" / "check-phase1-bench.py"
        parity_checker_path = tmp_root / "scripts" / "zigux" / "check-phase1-parity.py"
        manifest_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"
        expectations_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"

        original = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(original.replace("PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py", "", 1), encoding="utf-8")
        expect_missing_marker("closure_gate", tmp_root, "closure:PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py")
        closure_path.write_text(original, encoding="utf-8")

        original = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(original.replace("uses: actions/checkout@v6.0.2", "uses: actions/checkout@v5", 1), encoding="utf-8")
        expect_missing_marker("workflow_checkout", tmp_root, "workflow:uses: actions/checkout@v6.0.2")
        workflow_path.write_text(original, encoding="utf-8")

        original = build_path.read_text(encoding="utf-8")
        build_path.write_text(original.replace("const run_bench = b.addRunArtifact(bench);", "", 1), encoding="utf-8")
        expect_missing_marker("build_run_bench", tmp_root, "build:const run_bench = b.addRunArtifact(bench);")
        build_path.write_text(original, encoding="utf-8")

        original = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(original.replace("16. `test(zigux): harden phase-1 closure gates`", "", 1), encoding="utf-8")
        expect_missing_marker("ledger_commit_16", tmp_root, "ledger:16. `test(zigux): harden phase-1 closure gates`")
        ledger_path.write_text(original, encoding="utf-8")

        original = bench_checker_path.read_text(encoding="utf-8")
        bench_checker_path.write_text(original.replace("print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=11')", "", 1), encoding="utf-8")
        expect_missing_marker("bench_case_count", tmp_root, "bench_checker:print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=11')")
        bench_checker_path.write_text(original, encoding="utf-8")

        original = parity_checker_path.read_text(encoding="utf-8")
        parity_checker_path.write_text(original.replace("print('PHASE1_PARITY_SELF_TEST_CASE_COUNT=7')", "", 1), encoding="utf-8")
        expect_missing_marker("parity_case_count", tmp_root, "parity_checker:print('PHASE1_PARITY_SELF_TEST_CASE_COUNT=7')")
        parity_checker_path.write_text(original, encoding="utf-8")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["helper_count"] = 12
        write_json(manifest_path, manifest)
        expect_missing_marker("manifest_helper_count", tmp_root, "manifest:helper_count=13")

        manifest = build_manifest()
        manifest["helper_review_notes"]["tools/lib/find_bit.zig"]["alias_unit_test_anchor"] = ""
        write_json(manifest_path, manifest)
        expect_missing_marker("manifest_find_bit_alias_anchor", tmp_root, "manifest:tools/lib/find_bit.zig.alias_unit_test_anchor")

        expectations = build_expectations()
        expectations["iterations"]["PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS"] = 1
        write_json(expectations_path, expectations)
        expect_missing_marker("bench_iteration", tmp_root, "bench:iterations.PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS=20000")

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=8")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())

    code, missing = validate_tree(ROOT)
    if code != 0:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_MARKERS_START")
        for marker in missing:
            print(marker)
        print("MISSING_PHASE1_CLOSURE_MARKERS_END")
        raise SystemExit(1)

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILE_RELS)}")
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_BUILD_MARKERS) + len(REQUIRED_LEDGER_MARKERS) + len(REQUIRED_BENCH_CHECKER_MARKERS) + len(REQUIRED_PARITY_CHECKER_MARKERS)}"
    )