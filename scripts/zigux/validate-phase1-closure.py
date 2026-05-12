#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
VALIDATE_PHASE1_REL = Path("scripts/zigux/validate-phase1.py")

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-installer-companion-checks.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/phase1_helpers.zig",
]

WORKFLOW_MARKERS = [
    "uses: actions/checkout@v6.0.2",
    "uses: actions/setup-python@v6.2.0",
    "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}-{2}', github.workflow, github.ref, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
    "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
    "run: python3 scripts/zigux/validate-phase1.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: zig build test --build-file zigux/tests/build.zig",
    "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe",
]

DOCS_ROOT_MARKERS = [
    "Phase 1 notes - `Documentation/zigux/phase1-closure.md` - `scripts/zigux/README.md` - `scripts/zigux/install-zig.py` - `scripts/zigux/check-phase1-installer-review-surfaces.py` - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
]

TESTS_README_MARKERS = [
    "keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`",
    "`scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`",
]

LEDGER_MARKERS = [
    "`docs(zigux): close bounded phase-1 helper tranche`",
    "`test(zigux): harden phase-1 closure gates`",
    "`ci(zigux): harden phase-1 closure workflow viability`",
    "`build(zigux): remove node-20-bound Zig action from phase-1 closure path`",
]

MAKEFILE_MARKERS = [
    "phase1-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-companion-checks.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py",
    "phase1-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig",
    "phase1-bench:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig",
    "phase1: phase1-validate phase1-test phase1-bench",
]

BUILD_MARKERS = [
    '.root_source_file = b.path("phase1_helpers.zig")',
    '.name = "phase1-helper-tests"',
    'b.step("test", "Run Phase 1 helper tests")',
    '.root_source_file = b.path("phase1_bench.zig")',
    '.name = "phase1-bench"',
    'b.step("bench", "Run Phase 1 helper benchmark smoke")',
]

CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py",
    "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
    "PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary",
    "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it",
    "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
    "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
    "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
    "PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW=helper-local raw bitmap_copy alias proof stays explicit through the direct bitmap test anchor so copy and bitmap_copy preserve unmasked source words instead of silently adopting tail-clearing semantics",
    "PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW=helper-local bitmap zero-bit no-op proof stays explicit through the direct bitmap test anchor so zero-bit windows keep mutating helpers, boolean queries, and the rendered empty-window path from touching caller-visible storage or writing hidden bytes",
    "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
    "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior keep direct review anchors without implying a broader shared iterator or cached-root fixture packet than current master ships",
    "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, signed inputs keep trailing-rest splits aligned with unsigned parsing, signed overflow saturates instead of trapping, and suffixes are still consumed after saturation",
    "PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors, committed C-string replacement bytes, and parity fixture keys",
    "PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior",
    "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start",
    "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_OWNER=the shared Phase 1 replay now consumes the committed inclusive_boundary_* fixture fields directly, while the direct helper-local inclusive-boundary test remains a review-visible same-word anchor for that path",
    "PHASE1_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_REVIEW=helper-local tail-word inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans in the final partial tail word keep the last in-range bit reachable from an inclusive start",
    "PHASE1_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_OWNER=the shared Phase 1 replay still only consumes the committed inclusive_boundary_* head-word fields directly, so the direct helper-local tail-word inclusive-boundary test remains the owning review-visible anchor for the final partial-word boundary path",
    "PHASE1_FIND_BIT_ZERO_WINDOW_REVIEW=helper-local zero-bit-window proof stays explicit through the direct find_bit test anchor so first-scan entrypoints return the empty-window boundary without reading bitmap words",
    "PHASE1_FIND_BIT_PAST_NBITS_REVIEW=helper-local past-nbits short-circuit proof stays explicit through the direct find_bit test anchor so next scans starting at or beyond nbits return the boundary without reading bitmap words outside the caller-visible window",
    "PHASE1_FIND_BIT_UNDERSCORE_ALIAS_REVIEW=helper-local underscore alias proof stays explicit through the direct find_bit test anchor so the Linux-style underscore entry points remain behaviorally locked to the primary Zig helpers",
    "PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, and tail_and_clamped_next stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits",
    "PHASE1_FIND_BIT_BENCH_REVIEW=the shared Phase 1 benchmark packet keeps the exact next-bit and edge-loop iteration and checksum contract explicit so the steady-state and edge-case find_bit smoke paths remain live and review-visible",
    "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring",
]

EXPECTED_BENCH = {
    "status": "pass",
    "iterations": {
        "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
        "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
        "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
        "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
        "PHASE1_BENCH_STRING_ITERATIONS": 40000,
        "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
        "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
        "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
    },
    "checksums": [
        "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
        "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
        "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
        "PHASE1_BENCH_STRING_CHECKSUM",
        "PHASE1_BENCH_HWEIGHT_CHECKSUM",
        "PHASE1_BENCH_LIST_SORT_CHECKSUM",
        "PHASE1_BENCH_RBTREE_CHECKSUM",
    ],
    "exact_checksums": {
        "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 2260000,
        "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 620000,
        "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 15621472,
        "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 23340000,
        "PHASE1_BENCH_STRING_CHECKSUM": 320000,
        "PHASE1_BENCH_RBTREE_CHECKSUM": 3380000,
    },
}

EXPECTED_FIND_BIT_MANIFEST = {
    "helper_test_anchors": [
        'test "single-word next scans honor start masks"',
        'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        'test "zero-bit windows return without reading bitmap words"',
        'test "zero-sized scans ignore populated backing words"',
        'test "next scans past nbits return without reading bitmap words"',
        'test "tail-word next set scans skip earlier in-range matches before clamping"',
        'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
        'test "low-level underscore aliases mirror the primary find helpers"',
        'test "Linux-style aliases mirror the primary find helpers"',
    ],
    "same_word_start_masks": 'test "single-word next scans honor start masks"',
    "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail.",
    "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
    "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
    "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
    "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers"',
    "tail_word_skip_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    "tail_clamp_fixture_keys": [
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_clamped_last",
        "tail_clamped_empty_last",
    ],
    "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, underscore-alias, and Linux-style alias behavior review-visible on current master",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: str) -> Any:
    return json.loads(load_text(root, relative_path))


def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def require_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")
    return missing


def collect_bench_markers(bench: Any) -> list[str]:
    missing: list[str] = []
    if not isinstance(bench, dict):
        return ["bench:json_object"]
    if bench.get("status") != EXPECTED_BENCH["status"]:
        missing.append("bench:status")
    if bench.get("iterations") != EXPECTED_BENCH["iterations"]:
        missing.append("bench:iterations")
    if bench.get("checksums") != EXPECTED_BENCH["checksums"]:
        missing.append("bench:checksums")
    if bench.get("exact_checksums") != EXPECTED_BENCH["exact_checksums"]:
        missing.append("bench:exact_checksums")
    return missing


def run_phase1_validator(root: Path) -> list[str]:
    validator = root / VALIDATE_PHASE1_REL
    result = subprocess.run(
        [sys.executable, str(validator), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    detail = (result.stdout + result.stderr).strip()
    return [f"phase1_validator_failed:{detail}"]


def collect_find_bit_manifest_markers(manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return ["find_bit_manifest:json_object"]
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["find_bit_manifest:review_anchors"]
    find_bit_anchors = review_anchors.get("tools/lib/find_bit.zig")
    if not isinstance(find_bit_anchors, dict):
        return ["find_bit_manifest:tools/lib/find_bit.zig"]

    missing: list[str] = []
    for key, expected in EXPECTED_FIND_BIT_MANIFEST.items():
        if find_bit_anchors.get(key) != expected:
            missing.append(f"find_bit_manifest:{key}")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    workflow = load_text(root, ".github/workflows/zigux-bootstrap.yml")
    docs_root = load_text(root, "Documentation/zigux/README.md")
    tests_readme = load_text(root, "zigux/tests/README.md")
    review_checklist = load_text(root, "Documentation/zigux/review-checklist.md")
    closure = load_text(root, "Documentation/zigux/phase1-closure.md")
    ledger = load_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
    makefile = load_text(root, "zigux/Makefile")
    build_zig = load_text(root, "zigux/tests/build.zig")
    bench = load_json(root, "zigux/tests/fixtures/phase1_bench_expectations.json")
    manifest = load_json(root, "zigux/tests/fixtures/phase1_helper_manifest.json")

    missing: list[str] = []
    missing.extend(run_phase1_validator(root))
    missing.extend(require_markers(workflow, "workflow", WORKFLOW_MARKERS))
    if "mlugg/setup-zig@" in workflow:
        missing.append("workflow:unexpected mlugg/setup-zig@ reference")
    missing.extend(require_markers(docs_root, "docs_root", DOCS_ROOT_MARKERS))
    missing.extend(require_markers(tests_readme, "tests_readme", TESTS_README_MARKERS))
    missing.extend(require_markers(review_checklist, "review_checklist", REVIEW_CHECKLIST_MARKERS))
    missing.extend(require_markers(closure, "closure", CLOSURE_MARKERS))
    missing.extend(require_markers(ledger, "ledger", LEDGER_MARKERS))
    missing.extend(require_markers(makefile, "makefile", MAKEFILE_MARKERS))
    missing.extend(require_markers(build_zig, "build", BUILD_MARKERS))
    missing.extend(collect_bench_markers(bench))
    missing.extend(collect_find_bit_manifest_markers(manifest))
    return missing


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "{}\n" if relative_path.endswith(".json") else "// fixture\n")

    write_text(root, ".github/workflows/zigux-bootstrap.yml", "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root, "Documentation/zigux/README.md", "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(root, "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root, "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root, "Documentation/zigux/phase1-closure.md", "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", "\n".join(LEDGER_MARKERS) + "\n")
    write_text(root, "zigux/Makefile", "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root, "zigux/tests/build.zig", "\n".join(BUILD_MARKERS) + "\n")
    write_text(root, "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(EXPECTED_BENCH, indent=2) + "\n")
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps({"review_anchors": {"tools/lib/find_bit.zig": EXPECTED_FIND_BIT_MANIFEST}}, indent=2) + "\n",
    )
    write_text(root, "scripts/zigux/validate-phase1.py", "import sys\nif __name__ == '__main__':\n    print('PHASE1_VALIDATION=pass')\n    raise SystemExit(0)\n")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmp:
        root = Path(tmp)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        (root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md").unlink()
        assert "Documentation/zigux/phase1-host-helper-lane-sequencing.md" in collect_missing_files(root)
        case_count += 1
        make_fixture_root(root)

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        workflow_path.write_text(workflow_path.read_text(encoding="utf-8").replace(WORKFLOW_MARKERS[0], "", 1), encoding="utf-8")
        assert any(item.startswith("workflow:") for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[0], "", 1), encoding="utf-8")
        assert any(item.startswith("closure:") for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[19], "", 1), encoding="utf-8")
        assert any(item == f"closure:{CLOSURE_MARKERS[19]}" for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_word_inclusive_boundary_anchor"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "find_bit_manifest:tail_word_inclusive_boundary_anchor" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        bench_path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(bench_path.read_text(encoding="utf-8"))
        bench["exact_checksums"]["PHASE1_BENCH_RBTREE_CHECKSUM"] = 1
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "bench:exact_checksums" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        phase1_validator = root / VALIDATE_PHASE1_REL
        phase1_validator.write_text("import sys\nif __name__ == '__main__':\n    print('PHASE1_VALIDATION=fail')\n    raise SystemExit(1)\n", encoding="utf-8")
        assert any(item.startswith("phase1_validator_failed:") for item in collect_missing_markers(root))
        case_count += 1

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 1 closure packet.")
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_CLOSURE_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_CLOSURE_MARKERS_END")
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(WORKFLOW_MARKERS) + len(DOCS_ROOT_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(CLOSURE_MARKERS) + len(LEDGER_MARKERS) + len(MAKEFILE_MARKERS) + len(BUILD_MARKERS) + len(EXPECTED_FIND_BIT_MANIFEST)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
