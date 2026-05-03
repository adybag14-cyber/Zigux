#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
if len(SELF_PATH.parents) >= 3:
    ROOT = SELF_PATH.parents[2]
else:
    ROOT = SELF_PATH.parent

DEFAULT_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase1.py"
DEFAULT_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase1-closure.py"
DEFAULT_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase1-closure.md"
DEFAULT_BENCH_CHECKER = ROOT / "scripts" / "zigux" / "check-phase1-bench.py"
DEFAULT_WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
DEFAULT_MAKEFILE = ROOT / "zigux" / "Makefile"
DEFAULT_SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
DEFAULT_DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"

FIND_BIT_BENCH_KEYS = (
    "PHASE1_FIND_BIT_BENCH_KEYS=PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM,"
    "PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM,PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM,"
    "PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM,PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM,"
    "PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM"
)
BENCH_SELF_TEST_COUNT = "print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=18')"

REQUIRED_VALIDATOR_SNIPPETS = {
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
    "bench_self_test_expect_failure": (
        f'expect_failure(root, "bench_checker:{BENCH_SELF_TEST_COUNT}")'
    ),
}

REQUIRED_CLOSURE_DOC_SNIPPETS = {
    "find_bit_bench_keys_marker": f"`{FIND_BIT_BENCH_KEYS}`",
}

REQUIRED_BENCH_CHECKER_SNIPPETS = {
    "bench_self_test_count_marker": BENCH_SELF_TEST_COUNT,
}

REQUIRED_WORKFLOW_SNIPPETS = {
    "self_test_step": "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test",
    "live_step": "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py",
}

REQUIRED_MAKEFILE_SNIPPETS = {
    "self_test_step": "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test",
    "live_step": "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py",
}

REQUIRED_SCRIPTS_README_SNIPPETS = {
    "helper_listing": "- `check-phase1-find-bit-validator-anchors.py`",
    "self_test_command": (
        "`check-phase1-find-bit-validator-anchors.py --self-test` and "
        "`check-phase1-find-bit-validator-anchors.py`"
    ),
    "flow_note": (
        "matching `phase1_helper_manifest.json` tail-start and zero-sized anchor checks"
    ),
}

REQUIRED_DOCS_README_SNIPPETS = {
    "current_closure_records_heading": "Current closure records",
    "phase1_closure_listing": "- `Documentation/zigux/phase1-closure.md`",
}


def validate_text(prefix: str, source: str, required_snippets: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for label, snippet in required_snippets.items():
        if snippet not in source:
            missing.append(f"{prefix}:{label}")
    return missing


def validate_exact_lines(prefix: str, source: str, required_lines: dict[str, str]) -> list[str]:
    missing: list[str] = []
    lines = [line.strip() for line in source.splitlines()]
    for label, required_line in required_lines.items():
        actual_count = sum(1 for line in lines if line == required_line)
        if actual_count != 1:
            missing.append(f"{prefix}:{label}:expected=1:actual={actual_count}")
    return missing


def run_check(
    validator_path: Path,
    closure_validator_path: Path,
    closure_doc_path: Path,
    bench_checker_path: Path,
    workflow_path: Path,
    makefile_path: Path,
    scripts_readme_path: Path,
    docs_readme_path: Path,
) -> int:
    validator_source = validator_path.read_text(encoding="utf-8")
    closure_validator_source = closure_validator_path.read_text(encoding="utf-8")
    closure_doc_source = closure_doc_path.read_text(encoding="utf-8")
    bench_checker_source = bench_checker_path.read_text(encoding="utf-8")
    workflow_source = workflow_path.read_text(encoding="utf-8")
    makefile_source = makefile_path.read_text(encoding="utf-8")
    scripts_readme_source = scripts_readme_path.read_text(encoding="utf-8")
    docs_readme_source = docs_readme_path.read_text(encoding="utf-8")

    missing = [
        *validate_text("phase1_validator_find_bit", validator_source, REQUIRED_VALIDATOR_SNIPPETS),
        *validate_text(
            "phase1_closure_validator_find_bit",
            closure_validator_source,
            REQUIRED_CLOSURE_VALIDATOR_SNIPPETS,
        ),
        *validate_text(
            "phase1_closure_doc_find_bit",
            closure_doc_source,
            REQUIRED_CLOSURE_DOC_SNIPPETS,
        ),
        *validate_text(
            "phase1_bench_checker_find_bit",
            bench_checker_source,
            REQUIRED_BENCH_CHECKER_SNIPPETS,
        ),
        *validate_exact_lines("phase1_validator_find_bit_workflow", workflow_source, REQUIRED_WORKFLOW_SNIPPETS),
        *validate_exact_lines("phase1_validator_find_bit_makefile", makefile_source, REQUIRED_MAKEFILE_SNIPPETS),
        *validate_text("phase1_validator_find_bit_scripts_readme", scripts_readme_source, REQUIRED_SCRIPTS_README_SNIPPETS),
        *validate_text("phase1_validator_find_bit_docs_readme", docs_readme_source, REQUIRED_DOCS_README_SNIPPETS),
    ]
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
        f"{len(REQUIRED_VALIDATOR_SNIPPETS) + len(REQUIRED_CLOSURE_VALIDATOR_SNIPPETS) + len(REQUIRED_CLOSURE_DOC_SNIPPETS) + len(REQUIRED_BENCH_CHECKER_SNIPPETS) + len(REQUIRED_WORKFLOW_SNIPPETS) + len(REQUIRED_MAKEFILE_SNIPPETS) + len(REQUIRED_SCRIPTS_README_SNIPPETS) + len(REQUIRED_DOCS_README_SNIPPETS)}"
    )
    print(f"PHASE1_FIND_BIT_VALIDATOR_PATH={validator_path}")
    print(f"PHASE1_FIND_BIT_CLOSURE_VALIDATOR_PATH={closure_validator_path}")
    print(f"PHASE1_FIND_BIT_CLOSURE_DOC_PATH={closure_doc_path}")
    print(f"PHASE1_FIND_BIT_BENCH_CHECKER_PATH={bench_checker_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_WORKFLOW_PATH={workflow_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_MAKEFILE_PATH={makefile_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_SCRIPTS_README_PATH={scripts_readme_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_DOCS_README_PATH={docs_readme_path}")
    return 0


def expect_missing(
    label: str,
    validator_text: str,
    closure_validator_text: str,
    closure_doc_text: str,
    bench_checker_text: str,
    workflow_text: str,
    makefile_text: str,
    scripts_readme_text: str,
    docs_readme_text: str,
    expected: str,
) -> None:
    missing = [
        *validate_text("phase1_validator_find_bit", validator_text, REQUIRED_VALIDATOR_SNIPPETS),
        *validate_text(
            "phase1_closure_validator_find_bit",
            closure_validator_text,
            REQUIRED_CLOSURE_VALIDATOR_SNIPPETS,
        ),
        *validate_text(
            "phase1_closure_doc_find_bit",
            closure_doc_text,
            REQUIRED_CLOSURE_DOC_SNIPPETS,
        ),
        *validate_text(
            "phase1_bench_checker_find_bit",
            bench_checker_text,
            REQUIRED_BENCH_CHECKER_SNIPPETS,
        ),
        *validate_exact_lines("phase1_validator_find_bit_workflow", workflow_text, REQUIRED_WORKFLOW_SNIPPETS),
        *validate_exact_lines("phase1_validator_find_bit_makefile", makefile_text, REQUIRED_MAKEFILE_SNIPPETS),
        *validate_text(
            "phase1_validator_find_bit_scripts_readme",
            scripts_readme_text,
            REQUIRED_SCRIPTS_README_SNIPPETS,
        ),
        *validate_text(
            "phase1_validator_find_bit_docs_readme",
            docs_readme_text,
            REQUIRED_DOCS_README_SNIPPETS,
        ),
    ]
    if expected not in missing:
        raise SystemExit(
            f"phase1-find-bit-validator-self-test:{label}:expected={expected!r}:actual={missing!r}"
        )


def run_self_test() -> int:
    validator_baseline = "\n".join(REQUIRED_VALIDATOR_SNIPPETS.values()) + "\n"
    closure_validator_baseline = "\n".join(REQUIRED_CLOSURE_VALIDATOR_SNIPPETS.values()) + "\n"
    closure_doc_baseline = "\n".join(REQUIRED_CLOSURE_DOC_SNIPPETS.values()) + "\n"
    bench_checker_baseline = "\n".join(REQUIRED_BENCH_CHECKER_SNIPPETS.values()) + "\n"
    workflow_baseline = "\n".join(REQUIRED_WORKFLOW_SNIPPETS.values()) + "\n"
    makefile_baseline = "\n".join(REQUIRED_MAKEFILE_SNIPPETS.values()) + "\n"
    scripts_readme_baseline = "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS.values()) + "\n"
    docs_readme_baseline = "\n".join(REQUIRED_DOCS_README_SNIPPETS.values()) + "\n"

    baseline_missing = [
        *validate_text("phase1_validator_find_bit", validator_baseline, REQUIRED_VALIDATOR_SNIPPETS),
        *validate_text(
            "phase1_closure_validator_find_bit",
            closure_validator_baseline,
            REQUIRED_CLOSURE_VALIDATOR_SNIPPETS,
        ),
        *validate_text(
            "phase1_closure_doc_find_bit",
            closure_doc_baseline,
            REQUIRED_CLOSURE_DOC_SNIPPETS,
        ),
        *validate_text(
            "phase1_bench_checker_find_bit",
            bench_checker_baseline,
            REQUIRED_BENCH_CHECKER_SNIPPETS,
        ),
        *validate_exact_lines("phase1_validator_find_bit_workflow", workflow_baseline, REQUIRED_WORKFLOW_SNIPPETS),
        *validate_exact_lines("phase1_validator_find_bit_makefile", makefile_baseline, REQUIRED_MAKEFILE_SNIPPETS),
        *validate_text(
            "phase1_validator_find_bit_scripts_readme",
            scripts_readme_baseline,
            REQUIRED_SCRIPTS_README_SNIPPETS,
        ),
        *validate_text(
            "phase1_validator_find_bit_docs_readme",
            docs_readme_baseline,
            REQUIRED_DOCS_README_SNIPPETS,
        ),
    ]
    if baseline_missing:
        raise SystemExit(
            "phase1-find-bit-validator-self-test:baseline_failed:"
            + ",".join(baseline_missing)
        )

    total_cases = 1

    for label, snippet in REQUIRED_VALIDATOR_SNIPPETS.items():
        expect_missing(
            label,
            validator_baseline.replace(snippet, "", 1),
            closure_validator_baseline,
            closure_doc_baseline,
            bench_checker_baseline,
            workflow_baseline,
            makefile_baseline,
            scripts_readme_baseline,
            docs_readme_baseline,
            f"phase1_validator_find_bit:{label}",
        )
        total_cases += 1

    for label, snippet in REQUIRED_CLOSURE_VALIDATOR_SNIPPETS.items():
        expect_missing(
            label,
            validator_baseline,
            closure_validator_baseline.replace(snippet, "", 1),
            closure_doc_baseline,
            bench_checker_baseline,
            workflow_baseline,
            makefile_baseline,
            scripts_readme_baseline,
            docs_readme_baseline,
            f"phase1_closure_validator_find_bit:{label}",
        )
        total_cases += 1

    for label, snippet in REQUIRED_CLOSURE_DOC_SNIPPETS.items():
        expect_missing(
            label,
            validator_baseline,
            closure_validator_baseline,
            closure_doc_baseline.replace(snippet, "", 1),
            bench_checker_baseline,
            workflow_baseline,
            makefile_baseline,
            scripts_readme_baseline,
            docs_readme_baseline,
            f"phase1_closure_doc_find_bit:{label}",
        )
        total_cases += 1

    for label, snippet in REQUIRED_BENCH_CHECKER_SNIPPETS.items():
        expect_missing(
            label,
            validator_baseline,
            closure_validator_baseline,
            closure_doc_baseline,
            bench_checker_baseline.replace(snippet, "", 1),
            workflow_baseline,
            makefile_baseline,
            scripts_readme_baseline,
            docs_readme_baseline,
            f"phase1_bench_checker_find_bit:{label}",
        )
        total_cases += 1

    for label, snippet in REQUIRED_WORKFLOW_SNIPPETS.items():
        mutated_workflow_lines = [
            line for line in workflow_baseline.splitlines() if line.strip() != snippet
        ]
        expect_missing(
            label,
            validator_baseline,
            closure_validator_baseline,
            closure_doc_baseline,
            bench_checker_baseline,
            "\n".join(mutated_workflow_lines) + "\n",
            makefile_baseline,
            scripts_readme_baseline,
            docs_readme_baseline,
            f"phase1_validator_find_bit_workflow:{label}:expected=1:actual=0",
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            validator_baseline,
            closure_validator_baseline,
            closure_doc_baseline,
            bench_checker_baseline,
            workflow_baseline + snippet + "\n",
            makefile_baseline,
            scripts_readme_baseline,
            docs_readme_baseline,
            f"phase1_validator_find_bit_workflow:{label}:expected=1:actual=2",
        )
        total_cases += 1

    for label, snippet in REQUIRED_MAKEFILE_SNIPPETS.items():
        mutated_makefile_lines = [
            line for line in makefile_baseline.splitlines() if line.strip() != snippet
        ]
        expect_missing(
            label,
            validator_baseline,
            closure_validator_baseline,
            closure_doc_baseline,
            bench_checker_baseline,
            workflow_baseline,
            "\n".join(mutated_makefile_lines) + "\n",
            scripts_readme_baseline,
            docs_readme_baseline,
            f"phase1_validator_find_bit_makefile:{label}:expected=1:actual=0",
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            validator_baseline,
            closure_validator_baseline,
            closure_doc_baseline,
            bench_checker_baseline,
            workflow_baseline,
            makefile_baseline + snippet + "\n",
            scripts_readme_baseline,
            docs_readme_baseline,
            f"phase1_validator_find_bit_makefile:{label}:expected=1:actual=2",
        )
        total_cases += 1

    for label, snippet in REQUIRED_SCRIPTS_README_SNIPPETS.items():
        expect_missing(
            label,
            validator_baseline,
            closure_validator_baseline,
            closure_doc_baseline,
            bench_checker_baseline,
            workflow_baseline,
            makefile_baseline,
            scripts_readme_baseline.replace(snippet, "", 1),
            docs_readme_baseline,
            f"phase1_validator_find_bit_scripts_readme:{label}",
        )
        total_cases += 1

    for label, snippet in REQUIRED_DOCS_README_SNIPPETS.items():
        expect_missing(
            label,
            validator_baseline,
            closure_validator_baseline,
            closure_doc_baseline,
            bench_checker_baseline,
            workflow_baseline,
            makefile_baseline,
            scripts_readme_baseline,
            docs_readme_baseline.replace(snippet, "", 1),
            f"phase1_validator_find_bit_docs_readme:{label}",
        )
        total_cases += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_validator_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        temp_validator = tmp_root / "validate-phase1.py"
        temp_closure_validator = tmp_root / "validate-phase1-closure.py"
        temp_closure_doc = tmp_root / "phase1-closure.md"
        temp_bench_checker = tmp_root / "check-phase1-bench.py"
        temp_workflow = tmp_root / "zigux-bootstrap.yml"
        temp_makefile = tmp_root / "Makefile"
        temp_scripts_readme = tmp_root / "README.md"
        temp_docs_readme = tmp_root / "docs-README.md"
        temp_validator.write_text(validator_baseline, encoding="utf-8")
        temp_closure_validator.write_text(closure_validator_baseline, encoding="utf-8")
        temp_closure_doc.write_text(closure_doc_baseline, encoding="utf-8")
        temp_bench_checker.write_text(bench_checker_baseline, encoding="utf-8")
        temp_workflow.write_text(workflow_baseline, encoding="utf-8")
        temp_makefile.write_text(makefile_baseline, encoding="utf-8")
        temp_scripts_readme.write_text(scripts_readme_baseline, encoding="utf-8")
        temp_docs_readme.write_text(docs_readme_baseline, encoding="utf-8")
        if (
            run_check(
                temp_validator,
                temp_closure_validator,
                temp_closure_doc,
                temp_bench_checker,
                temp_workflow,
                temp_makefile,
                temp_scripts_readme,
                temp_docs_readme,
            )
            != 0
        ):
            raise SystemExit("phase1-find-bit-validator-self-test:file_check_failed")
        total_cases += 1

    print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed if the Phase 1 find_bit validators, Makefile route, or docs-root index stop naming the shipped "
            "tail-start, tail-word-boundary, zero-sized, or six-key bench evidence packet."
        )
    )
    parser.add_argument(
        "--validator",
        type=Path,
        default=DEFAULT_VALIDATOR,
        help="Path to the validate-phase1.py source to inspect.",
    )
    parser.add_argument(
        "--closure-validator",
        type=Path,
        default=DEFAULT_CLOSURE_VALIDATOR,
        help="Path to the validate-phase1-closure.py source to inspect.",
    )
    parser.add_argument(
        "--closure-doc",
        type=Path,
        default=DEFAULT_CLOSURE_DOC,
        help="Path to the phase1-closure.md document to inspect.",
    )
    parser.add_argument(
        "--bench-checker",
        type=Path,
        default=DEFAULT_BENCH_CHECKER,
        help="Path to the check-phase1-bench.py source to inspect.",
    )
    parser.add_argument(
        "--workflow",
        type=Path,
        default=DEFAULT_WORKFLOW,
        help="Path to the bootstrap workflow to inspect.",
    )
    parser.add_argument(
        "--makefile",
        type=Path,
        default=DEFAULT_MAKEFILE,
        help="Path to the Zigux Makefile to inspect.",
    )
    parser.add_argument(
        "--scripts-readme",
        type=Path,
        default=DEFAULT_SCRIPTS_README,
        help="Path to the scripts/zigux README to inspect.",
    )
    parser.add_argument(
        "--docs-readme",
        type=Path,
        default=DEFAULT_DOCS_README,
        help="Path to the Documentation/zigux README to inspect.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test.")
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
    )


if __name__ == "__main__":
    raise SystemExit(main())
