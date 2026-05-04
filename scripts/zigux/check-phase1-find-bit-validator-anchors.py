#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

DEFAULT_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase1.py"
DEFAULT_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase1-closure.py"
DEFAULT_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase1-closure.md"
DEFAULT_BENCH_CHECKER = ROOT / "scripts" / "zigux" / "check-phase1-bench.py"
DEFAULT_WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
DEFAULT_MAKEFILE = ROOT / "zigux" / "Makefile"
DEFAULT_SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
DEFAULT_DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
DEFAULT_FIND_BIT_SOURCE = ROOT / "tools" / "lib" / "find_bit.zig"
DEFAULT_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"

FIND_BIT_BENCH_KEYS = (
    "PHASE1_FIND_BIT_BENCH_KEYS=PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM,"
    "PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM,PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM,"
    "PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM,PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM,"
    "PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM"
)
FIND_BIT_BENCH_ITERATIONS = (
    "PHASE1_FIND_BIT_BENCH_ITERATIONS=PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS,"
    "PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS,PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS,"
    "PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS"
)
BENCH_SELF_TEST_COUNT = "print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=19')"

REQUIRED_VALIDATOR_SNIPPETS = {
    "closure_small_bitmap_review": (
        '"PHASE1_FIND_BIT_SMALL_BITMAP_UNIT_REVIEW=find_bit single-word set zero and shared-bit '
        'scans keep Linux small-bitmap semantics aligned by masking out-of-range tail bits while '
        'preserving inclusive in-range matches inside one word"'
    ),
    "closure_low_level_review": (
        '"PHASE1_FIND_BIT_LOW_LEVEL_UNIT_REVIEW=find_bit low-level underscore entry points '
        'preserve same-word inclusive starts and tail-clamped set, shared-bit, and zero-bit '
        'scan behavior across the same caller-selected bit windows as the public helpers"'
    ),
    "closure_tail_start_review": (
        '"PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit '
        'scans keep the last in-range bit reachable from an inclusive start while later starts '
        'still return nbits instead of leaking the out-of-range tail"'
    ),
    "closure_zero_sized_review": (
        '"PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW=find_bit zero-length set zero and shared-bit '
        'scans return 0 even when backing words are populated so declared nbits stays '
        'authoritative over caller storage"'
    ),
    "closure_tail_word_boundary_review": (
        '"PHASE1_FIND_BIT_TAIL_WORD_BOUNDARY_UNIT_REVIEW=find_bit tail-clamped set zero and '
        'shared-bit scans keep the first in-range tail-word match reachable when the search '
        'starts exactly at the tail-word boundary instead of rereading an earlier full-word result"'
    ),
    "manifest_tail_start_anchor_marker": (
        '"tail_start_unit_test_anchor": '
        '\'tools/lib/find_bit.zig:test "tail scans keep the last in-range bit reachable from an inclusive start"\''
    ),
    "manifest_tail_start_contract_marker": (
        '"tail_start_unit_test_contract": '
        '"Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned '
        'when the inclusive start lands on the last in-range bit, while later starts still return '
        'nbits instead of leaking the out-of-range tail.",'
    ),
    "manifest_zero_sized_anchor_marker": (
        '"zero_sized_unit_test_anchor": '
        '\'tools/lib/find_bit.zig:test "zero-sized scans ignore populated backing words"\''
    ),
    "manifest_zero_sized_contract_marker": (
        '"zero_sized_unit_test_contract": '
        '"Direct Zig unit coverage keeps zero-length set, zero, and shared-bit scans aligned by '
        'returning 0 even when backing words are populated, so declared nbits stays '
        'authoritative over caller storage.",'
    ),
    "manifest_tail_word_boundary_anchor_marker": (
        '"tail_word_boundary_unit_test_anchor": '
        '\'tools/lib/find_bit.zig:test "tail scans honor an exact tail-word boundary start"\''
    ),
    "manifest_tail_word_boundary_contract_marker": (
        '"tail_word_boundary_unit_test_contract": '
        '"Direct Zig unit coverage keeps set, zero, and shared-bit tail scans aligned when the '
        'search starts exactly at the first tail-word bit index, so the first in-range tail '
        'match remains reachable without rereading an earlier full-word result.",'
    ),
}

REQUIRED_CLOSURE_VALIDATOR_SNIPPETS = {
    "bench_self_test_count_marker": f'"{BENCH_SELF_TEST_COUNT}",',
    "bench_self_test_expect_failure": f'expect_failure(root, "bench_checker:{BENCH_SELF_TEST_COUNT}")',
}

REQUIRED_CLOSURE_DOC_SNIPPETS = {
    "find_bit_bench_keys_marker": f"`{FIND_BIT_BENCH_KEYS}`",
    "find_bit_bench_iterations_marker": f"`{FIND_BIT_BENCH_ITERATIONS}`",
    "find_bit_small_bitmap_review_marker": (
        "PHASE1_FIND_BIT_SMALL_BITMAP_UNIT_REVIEW=find_bit single-word set zero and shared-bit scans keep Linux "
        "small-bitmap semantics aligned by masking out-of-range tail bits while preserving inclusive in-range "
        "matches inside one word"
    ),
    "find_bit_low_level_review_marker": (
        "PHASE1_FIND_BIT_LOW_LEVEL_UNIT_REVIEW=find_bit low-level underscore entry points preserve same-word "
        "inclusive starts and tail-clamped set, shared-bit, and zero-bit scan behavior across the same "
        "caller-selected bit windows as the public helpers"
    ),
}

REQUIRED_BENCH_CHECKER_SNIPPETS = {
    "bench_self_test_count_marker": BENCH_SELF_TEST_COUNT,
}

REQUIRED_WORKFLOW_LINES = {
    "self_test_step": "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test",
    "live_step": "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py",
}

REQUIRED_MAKEFILE_LINES = {
    "self_test_step": "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test",
    "live_step": "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py",
}

REQUIRED_SCRIPTS_README_LINES = {
    "helper_listing": "- `check-phase1-find-bit-validator-anchors.py`",
}

REQUIRED_SCRIPTS_README_SNIPPETS = {
    "self_test_command": (
        "`check-phase1-find-bit-validator-anchors.py --self-test` and "
        "`check-phase1-find-bit-validator-anchors.py`"
    ),
    "flow_note": "matching `phase1_helper_manifest.json` tail-start and zero-sized anchor checks",
    "tail_word_boundary_note": "the paired tail-word-boundary anchor review",
}

REQUIRED_DOCS_README_LINES = {
    "current_closure_records_heading": "Current closure records",
    "phase1_closure_listing": "- `Documentation/zigux/phase1-closure.md`",
}

REQUIRED_FIND_BIT_SOURCE_SNIPPETS = {
    "small_bitmap_anchor": 'test "single-word scans keep linux small-bitmap semantics" {',
    "low_level_anchor": 'test "find low-level underscore entry points preserve same-word and tail-clamped scan semantics" {',
}

REQUIRED_MANIFEST_FIELDS = {
    "small_bitmap_unit_test_anchor": 'tools/lib/find_bit.zig:test "single-word scans keep linux small-bitmap semantics"',
    "small_bitmap_unit_test_contract": "Direct Zig unit coverage keeps single-word set, zero, and shared-bit scans aligned with Linux small-bitmap semantics by masking out-of-range tail bits while preserving inclusive in-range matches inside one word.",
    "low_level_unit_test_anchor": 'tools/lib/find_bit.zig:test "find low-level underscore entry points preserve same-word and tail-clamped scan semantics"',
    "low_level_unit_test_contract": "Direct Zig unit coverage keeps _find_first_bit(), _find_first_and_bit(), _find_first_zero_bit(), _find_next_bit(), _find_next_and_bit(), and _find_next_zero_bit() aligned with the public scan helpers across same-word inclusive starts and tail-clamped caller-selected bit windows.",
    "tail_start_unit_test_anchor": 'tools/lib/find_bit.zig:test "tail scans keep the last in-range bit reachable from an inclusive start"',
    "tail_start_unit_test_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit, while later starts still return nbits instead of leaking the out-of-range tail.",
    "tail_word_boundary_unit_test_anchor": 'tools/lib/find_bit.zig:test "tail scans honor an exact tail-word boundary start"',
    "tail_word_boundary_unit_test_contract": "Direct Zig unit coverage keeps set, zero, and shared-bit tail scans aligned when the search starts exactly at the first tail-word bit index, so the first in-range tail match remains reachable without rereading an earlier full-word result.",
    "zero_sized_unit_test_anchor": 'tools/lib/find_bit.zig:test "zero-sized scans ignore populated backing words"',
    "zero_sized_unit_test_contract": "Direct Zig unit coverage keeps zero-length set, zero, and shared-bit scans aligned by returning 0 even when backing words are populated, so declared nbits stays authoritative over caller storage.",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_required_files(required_files: dict[str, Path]) -> list[str]:
    missing: list[str] = []
    for rel, path in required_files.items():
        if not path.exists():
            missing.append(f"missing_file:{rel}")
    return missing


def validate_exact_lines(prefix: str, text: str, lines: dict[str, str]) -> list[str]:
    missing: list[str] = []
    normalized = [line.strip() for line in text.splitlines()]
    for label, line in lines.items():
        count = sum(1 for actual in normalized if actual == line)
        if count != 1:
            missing.append(f"{prefix}:{label}:expected=1:actual={count}")
    return missing


def validate_snippet_counts(prefix: str, text: str, snippets: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for label, snippet in snippets.items():
        count = text.count(snippet)
        if count != 1:
            missing.append(f"{prefix}:{label}:expected=1:actual={count}")
    return missing


def validate_manifest(prefix: str, text: str) -> list[str]:
    missing: list[str] = []
    manifest = json.loads(text)
    review = manifest.get("helper_review_notes", {}).get("tools/lib/find_bit.zig", {})
    for key, value in REQUIRED_MANIFEST_FIELDS.items():
        if review.get(key) != value:
            missing.append(f"{prefix}:{key}")
    return missing


def collect_missing(
    validator_text: str,
    closure_validator_text: str,
    closure_doc_text: str,
    bench_checker_text: str,
    workflow_text: str,
    makefile_text: str,
    scripts_readme_text: str,
    docs_readme_text: str,
    find_bit_source_text: str,
    manifest_text: str,
) -> list[str]:
    return [
        *validate_snippet_counts("phase1_validator_find_bit", validator_text, REQUIRED_VALIDATOR_SNIPPETS),
        *validate_snippet_counts(
            "phase1_closure_validator_find_bit",
            closure_validator_text,
            REQUIRED_CLOSURE_VALIDATOR_SNIPPETS,
        ),
        *validate_snippet_counts(
            "phase1_closure_doc_find_bit",
            closure_doc_text,
            REQUIRED_CLOSURE_DOC_SNIPPETS,
        ),
        *validate_snippet_counts(
            "phase1_bench_checker_find_bit",
            bench_checker_text,
            REQUIRED_BENCH_CHECKER_SNIPPETS,
        ),
        *validate_exact_lines(
            "phase1_validator_find_bit_workflow",
            workflow_text,
            REQUIRED_WORKFLOW_LINES,
        ),
        *validate_exact_lines(
            "phase1_validator_find_bit_makefile",
            makefile_text,
            REQUIRED_MAKEFILE_LINES,
        ),
        *validate_exact_lines(
            "phase1_validator_find_bit_scripts_readme",
            scripts_readme_text,
            REQUIRED_SCRIPTS_README_LINES,
        ),
        *validate_snippet_counts(
            "phase1_validator_find_bit_scripts_readme",
            scripts_readme_text,
            REQUIRED_SCRIPTS_README_SNIPPETS,
        ),
        *validate_exact_lines(
            "phase1_validator_find_bit_docs_readme",
            docs_readme_text,
            REQUIRED_DOCS_README_LINES,
        ),
        *validate_snippet_counts(
            "phase1_find_bit_source",
            find_bit_source_text,
            REQUIRED_FIND_BIT_SOURCE_SNIPPETS,
        ),
        *validate_manifest(
            "phase1_find_bit_manifest",
            manifest_text,
        ),
    ]


def run_check(
    validator_path: Path,
    closure_validator_path: Path,
    closure_doc_path: Path,
    bench_checker_path: Path,
    workflow_path: Path,
    makefile_path: Path,
    scripts_readme_path: Path,
    docs_readme_path: Path,
    find_bit_source_path: Path,
    manifest_path: Path,
) -> int:
    required_files = {
        "scripts/zigux/validate-phase1.py": validator_path,
        "scripts/zigux/validate-phase1-closure.py": closure_validator_path,
        "Documentation/zigux/phase1-closure.md": closure_doc_path,
        "scripts/zigux/check-phase1-bench.py": bench_checker_path,
        ".github/workflows/zigux-bootstrap.yml": workflow_path,
        "zigux/Makefile": makefile_path,
        "scripts/zigux/README.md": scripts_readme_path,
        "Documentation/zigux/README.md": docs_readme_path,
        "tools/lib/find_bit.zig": find_bit_source_path,
        "zigux/tests/fixtures/phase1_helper_manifest.json": manifest_path,
    }
    missing_files = validate_required_files(required_files)
    if missing_files:
        print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_CHECK=fail")
        print("MISSING_PHASE1_FIND_BIT_VALIDATOR_ANCHORS_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_FIND_BIT_VALIDATOR_ANCHORS_END")
        return 1

    missing = collect_missing(
        read_text(validator_path),
        read_text(closure_validator_path),
        read_text(closure_doc_path),
        read_text(bench_checker_path),
        read_text(workflow_path),
        read_text(makefile_path),
        read_text(scripts_readme_path),
        read_text(docs_readme_path),
        read_text(find_bit_source_path),
        read_text(manifest_path),
    )
    if missing:
        print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_CHECK=fail")
        print("MISSING_PHASE1_FIND_BIT_VALIDATOR_ANCHORS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_FIND_BIT_VALIDATOR_ANCHORS_END")
        return 1

    print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_CHECK=pass")
    print(
        "PHASE1_FIND_BIT_VALIDATOR_ANCHOR_COUNT="
        f"{len(REQUIRED_VALIDATOR_SNIPPETS) + len(REQUIRED_CLOSURE_VALIDATOR_SNIPPETS) + len(REQUIRED_CLOSURE_DOC_SNIPPETS) + len(REQUIRED_BENCH_CHECKER_SNIPPETS) + len(REQUIRED_WORKFLOW_LINES) + len(REQUIRED_MAKEFILE_LINES) + len(REQUIRED_SCRIPTS_README_LINES) + len(REQUIRED_SCRIPTS_README_SNIPPETS) + len(REQUIRED_DOCS_README_LINES) + len(REQUIRED_FIND_BIT_SOURCE_SNIPPETS) + len(REQUIRED_MANIFEST_FIELDS)}"
    )
    print(f"PHASE1_FIND_BIT_VALIDATOR_PATH={validator_path}")
    print(f"PHASE1_FIND_BIT_CLOSURE_VALIDATOR_PATH={closure_validator_path}")
    print(f"PHASE1_FIND_BIT_CLOSURE_DOC_PATH={closure_doc_path}")
    print(f"PHASE1_FIND_BIT_BENCH_CHECKER_PATH={bench_checker_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_WORKFLOW_PATH={workflow_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_MAKEFILE_PATH={makefile_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_SCRIPTS_README_PATH={scripts_readme_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_DOCS_README_PATH={docs_readme_path}")
    print(f"PHASE1_FIND_BIT_SOURCE_PATH={find_bit_source_path}")
    print(f"PHASE1_FIND_BIT_MANIFEST_PATH={manifest_path}")
    return 0


def expect_missing(label: str, expected: str, **texts: str) -> None:
    missing = collect_missing(
        texts["validator_text"],
        texts["closure_validator_text"],
        texts["closure_doc_text"],
        texts["bench_checker_text"],
        texts["workflow_text"],
        texts["makefile_text"],
        texts["scripts_readme_text"],
        texts["docs_readme_text"],
        texts["find_bit_source_text"],
        texts["manifest_text"],
    )
    if expected not in missing:
        raise SystemExit(
            f"phase1-find-bit-validator-self-test:{label}:expected={expected!r}:actual={missing!r}"
        )


def expect_run_check_failure(paths: dict[str, Path], expected: str) -> None:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = run_check(
            paths["validator"],
            paths["closure_validator"],
            paths["closure_doc"],
            paths["bench_checker"],
            paths["workflow"],
            paths["makefile"],
            paths["scripts_readme"],
            paths["docs_readme"],
            paths["find_bit_source"],
            paths["manifest"],
        )
    output = buffer.getvalue()
    if result == 0:
        raise SystemExit(
            f"phase1-find-bit-validator-self-test:expected_failure:{expected}"
        )
    if expected not in output:
        raise SystemExit(
            "phase1-find-bit-validator-self-test:missing_expected_output:"
            f"expected={expected!r}:actual={output!r}"
        )


def run_self_test() -> int:
    validator_text = "\n".join(REQUIRED_VALIDATOR_SNIPPETS.values()) + "\n"
    closure_validator_text = "\n".join(REQUIRED_CLOSURE_VALIDATOR_SNIPPETS.values()) + "\n"
    closure_doc_text = "\n".join(REQUIRED_CLOSURE_DOC_SNIPPETS.values()) + "\n"
    bench_checker_text = "\n".join(REQUIRED_BENCH_CHECKER_SNIPPETS.values()) + "\n"
    workflow_text = "\n".join(REQUIRED_WORKFLOW_LINES.values()) + "\n"
    makefile_text = "\n".join(REQUIRED_MAKEFILE_LINES.values()) + "\n"
    scripts_readme_text = (
        "\n".join(REQUIRED_SCRIPTS_README_LINES.values())
        + "\n"
        + "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS.values())
        + "\n"
    )
    docs_readme_text = "\n".join(REQUIRED_DOCS_README_LINES.values()) + "\n"
    find_bit_source_text = "\n".join(REQUIRED_FIND_BIT_SOURCE_SNIPPETS.values()) + "\n"
    manifest_text = json.dumps(
        {
            "helper_review_notes": {
                "tools/lib/find_bit.zig": dict(REQUIRED_MANIFEST_FIELDS),
            }
        },
        indent=2,
    ) + "\n"

    baseline_missing = collect_missing(
        validator_text,
        closure_validator_text,
        closure_doc_text,
        bench_checker_text,
        workflow_text,
        makefile_text,
        scripts_readme_text,
        docs_readme_text,
        find_bit_source_text,
        manifest_text,
    )
    if baseline_missing:
        raise SystemExit(
            "phase1-find-bit-validator-self-test:baseline_failed:" + ",".join(baseline_missing)
        )

    total_cases = 1

    for label, snippet in REQUIRED_VALIDATOR_SNIPPETS.items():
        expect_missing(
            label,
            f"phase1_validator_find_bit:{label}:expected=1:actual=0",
            validator_text=validator_text.replace(snippet, "", 1),
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_validator_find_bit:{label}:expected=1:actual=2",
            validator_text=validator_text + snippet + "\n",
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label, snippet in REQUIRED_CLOSURE_VALIDATOR_SNIPPETS.items():
        expect_missing(
            label,
            f"phase1_closure_validator_find_bit:{label}:expected=1:actual=0",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text.replace(snippet, "", 1),
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_closure_validator_find_bit:{label}:expected=1:actual=2",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text + snippet + "\n",
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label, snippet in REQUIRED_CLOSURE_DOC_SNIPPETS.items():
        expect_missing(
            label,
            f"phase1_closure_doc_find_bit:{label}:expected=1:actual=0",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text.replace(snippet, "", 1),
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_closure_doc_find_bit:{label}:expected=1:actual=2",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text + snippet + "\n",
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label, snippet in REQUIRED_BENCH_CHECKER_SNIPPETS.items():
        expect_missing(
            label,
            f"phase1_bench_checker_find_bit:{label}:expected=1:actual=0",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text.replace(snippet, "", 1),
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_bench_checker_find_bit:{label}:expected=1:actual=2",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text + snippet + "\n",
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label, line in REQUIRED_WORKFLOW_LINES.items():
        missing_lines = [raw for raw in workflow_text.splitlines() if raw.strip() != line]
        expect_missing(
            label,
            f"phase1_validator_find_bit_workflow:{label}:expected=1:actual=0",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text="\n".join(missing_lines) + "\n",
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_validator_find_bit_workflow:{label}:expected=1:actual=2",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text + line + "\n",
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label, line in REQUIRED_MAKEFILE_LINES.items():
        missing_lines = [raw for raw in makefile_text.splitlines() if raw.strip() != line]
        expect_missing(
            label,
            f"phase1_validator_find_bit_makefile:{label}:expected=1:actual=0",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text="\n".join(missing_lines) + "\n",
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_validator_find_bit_makefile:{label}:expected=1:actual=2",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text + line + "\n",
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label, line in REQUIRED_SCRIPTS_README_LINES.items():
        expect_missing(
            label,
            f"phase1_validator_find_bit_scripts_readme:{label}:expected=1:actual=0",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text.replace(line, "", 1),
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_validator_find_bit_scripts_readme:{label}:expected=1:actual=2",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text + line + "\n",
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label, snippet in REQUIRED_SCRIPTS_README_SNIPPETS.items():
        expect_missing(
            label,
            f"phase1_validator_find_bit_scripts_readme:{label}:expected=1:actual=0",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text.replace(snippet, "", 1),
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_validator_find_bit_scripts_readme:{label}:expected=1:actual=2",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text + snippet + "\n",
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label, line in REQUIRED_DOCS_README_LINES.items():
        expect_missing(
            label,
            f"phase1_validator_find_bit_docs_readme:{label}:expected=1:actual=0",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text.replace(line, "", 1),
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_validator_find_bit_docs_readme:{label}:expected=1:actual=2",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text + line + "\n",
            find_bit_source_text=find_bit_source_text,
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label, snippet in REQUIRED_FIND_BIT_SOURCE_SNIPPETS.items():
        expect_missing(
            label,
            f"phase1_find_bit_source:{label}:expected=1:actual=0",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text.replace(snippet, "", 1),
            manifest_text=manifest_text,
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            f"phase1_find_bit_source:{label}:expected=1:actual=2",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text + snippet + "\n",
            manifest_text=manifest_text,
        )
        total_cases += 1

    for label in REQUIRED_MANIFEST_FIELDS:
        manifest = json.loads(manifest_text)
        manifest["helper_review_notes"]["tools/lib/find_bit.zig"][label] = "drift"
        expect_missing(
            label,
            f"phase1_find_bit_manifest:{label}",
            validator_text=validator_text,
            closure_validator_text=closure_validator_text,
            closure_doc_text=closure_doc_text,
            bench_checker_text=bench_checker_text,
            workflow_text=workflow_text,
            makefile_text=makefile_text,
            scripts_readme_text=scripts_readme_text,
            docs_readme_text=docs_readme_text,
            find_bit_source_text=find_bit_source_text,
            manifest_text=json.dumps(manifest, indent=2) + "\n",
        )
        total_cases += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_validator_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        paths = {
            "validator": tmp_root / "validate-phase1.py",
            "closure_validator": tmp_root / "validate-phase1-closure.py",
            "closure_doc": tmp_root / "phase1-closure.md",
            "bench_checker": tmp_root / "check-phase1-bench.py",
            "workflow": tmp_root / "zigux-bootstrap.yml",
            "makefile": tmp_root / "Makefile",
            "scripts_readme": tmp_root / "README.md",
            "docs_readme": tmp_root / "docs-README.md",
            "find_bit_source": tmp_root / "find_bit.zig",
            "manifest": tmp_root / "phase1_helper_manifest.json",
        }
        paths["validator"].write_text(validator_text, encoding="utf-8")
        paths["closure_validator"].write_text(closure_validator_text, encoding="utf-8")
        paths["closure_doc"].write_text(closure_doc_text, encoding="utf-8")
        paths["bench_checker"].write_text(bench_checker_text, encoding="utf-8")
        paths["workflow"].write_text(workflow_text, encoding="utf-8")
        paths["makefile"].write_text(makefile_text, encoding="utf-8")
        paths["scripts_readme"].write_text(scripts_readme_text, encoding="utf-8")
        paths["docs_readme"].write_text(docs_readme_text, encoding="utf-8")
        paths["find_bit_source"].write_text(find_bit_source_text, encoding="utf-8")
        paths["manifest"].write_text(manifest_text, encoding="utf-8")
        if (
            run_check(
                paths["validator"],
                paths["closure_validator"],
                paths["closure_doc"],
                paths["bench_checker"],
                paths["workflow"],
                paths["makefile"],
                paths["scripts_readme"],
                paths["docs_readme"],
                paths["find_bit_source"],
                paths["manifest"],
            )
            != 0
        ):
            raise SystemExit("phase1-find-bit-validator-self-test:file_check_failed")
        total_cases += 1

        missing_file_cases = [
            ("validator", "missing_file:scripts/zigux/validate-phase1.py"),
            ("closure_validator", "missing_file:scripts/zigux/validate-phase1-closure.py"),
            ("closure_doc", "missing_file:Documentation/zigux/phase1-closure.md"),
            ("bench_checker", "missing_file:scripts/zigux/check-phase1-bench.py"),
            ("workflow", "missing_file:.github/workflows/zigux-bootstrap.yml"),
            ("makefile", "missing_file:zigux/Makefile"),
            ("scripts_readme", "missing_file:scripts/zigux/README.md"),
            ("docs_readme", "missing_file:Documentation/zigux/README.md"),
            ("find_bit_source", "missing_file:tools/lib/find_bit.zig"),
            ("manifest", "missing_file:zigux/tests/fixtures/phase1_helper_manifest.json"),
        ]
        for path_key, expected in missing_file_cases:
            baseline = paths[path_key].read_text(encoding="utf-8")
            paths[path_key].unlink()
            expect_run_check_failure(paths, expected)
            paths[path_key].write_text(baseline, encoding="utf-8")
            total_cases += 1

    print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed if the Phase 1 find_bit validators, manifest, helper source, Makefile route, or docs-root index "
            "stop naming the shipped small-bitmap, low-level underscore, tail-start, tail-word-boundary, zero-sized, "
            "or bench workload-size evidence packet."
        )
    )
    parser.add_argument("--validator", type=Path, default=DEFAULT_VALIDATOR)
    parser.add_argument("--closure-validator", type=Path, default=DEFAULT_CLOSURE_VALIDATOR)
    parser.add_argument("--closure-doc", type=Path, default=DEFAULT_CLOSURE_DOC)
    parser.add_argument("--bench-checker", type=Path, default=DEFAULT_BENCH_CHECKER)
    parser.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW)
    parser.add_argument("--makefile", type=Path, default=DEFAULT_MAKEFILE)
    parser.add_argument("--scripts-readme", type=Path, default=DEFAULT_SCRIPTS_README)
    parser.add_argument("--docs-readme", type=Path, default=DEFAULT_DOCS_README)
    parser.add_argument("--find-bit-source", type=Path, default=DEFAULT_FIND_BIT_SOURCE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(
        args.validator,
        args.closure_validator,
        args.closure_doc,
        args.bench_checker,
        args.workflow,
        args.makefile,
        args.scripts_readme,
        args.docs_readme,
        args.find_bit_source,
        args.manifest,
    )


if __name__ == "__main__":
    raise SystemExit(main())