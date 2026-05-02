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
DEFAULT_WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
DEFAULT_SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"

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
    "manifest_tail_start_anchor_marker": '"tail_start_unit_test_anchor",',
    "manifest_tail_start_contract_marker": '"tail_start_unit_test_contract",',
    "manifest_zero_sized_anchor_marker": '"zero_sized_unit_test_anchor",',
    "manifest_zero_sized_contract_marker": '"zero_sized_unit_test_contract",',
    "manifest_tail_start_anchor_check": (
        'if find_bit_note.get("tail_start_unit_test_anchor") != '
        '\'tools/lib/find_bit.zig:test "tail scans keep the last in-range bit reachable from an inclusive start"\''
    ),
    "manifest_tail_start_contract_check": (
        'if find_bit_note.get("tail_start_unit_test_contract") != '
        '"Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned '
        'when the inclusive start lands on the last in-range bit, while later starts still return '
        'nbits instead of leaking the out-of-range tail."'
    ),
    "manifest_zero_sized_anchor_check": (
        'if find_bit_note.get("zero_sized_unit_test_anchor") != '
        '\'tools/lib/find_bit.zig:test "zero-sized scans ignore populated backing words"\''
    ),
    "manifest_zero_sized_contract_check": (
        'if find_bit_note.get("zero_sized_unit_test_contract") != '
        '"Direct Zig unit coverage keeps zero-length set, zero, and shared-bit scans aligned by '
        'returning 0 even when backing words are populated, so declared nbits stays authoritative '
        'over caller storage."'
    ),
}

REQUIRED_WORKFLOW_SNIPPETS = {
    "self_test_step": "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test",
    "live_step": "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py",
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


def validate_text(prefix: str, source: str, required_snippets: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for label, snippet in required_snippets.items():
        if snippet not in source:
            missing.append(f"{prefix}:{label}")
    return missing


def validate_exact_lines(prefix: str, source: str, required_lines: dict[str, str]) -> list[str]:
    missing: list[str] = []
    lines = {line.strip() for line in source.splitlines()}
    for label, required_line in required_lines.items():
        if required_line not in lines:
            missing.append(f"{prefix}:{label}")
    return missing


def run_check(validator_path: Path, workflow_path: Path, scripts_readme_path: Path) -> int:
    validator_source = validator_path.read_text(encoding="utf-8")
    workflow_source = workflow_path.read_text(encoding="utf-8")
    scripts_readme_source = scripts_readme_path.read_text(encoding="utf-8")

    missing = [
        *validate_text("phase1_validator_find_bit", validator_source, REQUIRED_VALIDATOR_SNIPPETS),
        *validate_exact_lines("phase1_validator_find_bit_workflow", workflow_source, REQUIRED_WORKFLOW_SNIPPETS),
        *validate_text("phase1_validator_find_bit_scripts_readme", scripts_readme_source, REQUIRED_SCRIPTS_README_SNIPPETS),
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
        f"{len(REQUIRED_VALIDATOR_SNIPPETS) + len(REQUIRED_WORKFLOW_SNIPPETS) + len(REQUIRED_SCRIPTS_README_SNIPPETS)}"
    )
    print(f"PHASE1_FIND_BIT_VALIDATOR_PATH={validator_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_WORKFLOW_PATH={workflow_path}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_SCRIPTS_README_PATH={scripts_readme_path}")
    return 0


def expect_missing(
    label: str,
    validator_text: str,
    workflow_text: str,
    scripts_readme_text: str,
    expected: str,
) -> None:
    missing = [
        *validate_text("phase1_validator_find_bit", validator_text, REQUIRED_VALIDATOR_SNIPPETS),
        *validate_exact_lines("phase1_validator_find_bit_workflow", workflow_text, REQUIRED_WORKFLOW_SNIPPETS),
        *validate_text("phase1_validator_find_bit_scripts_readme", scripts_readme_text, REQUIRED_SCRIPTS_README_SNIPPETS),
    ]
    if expected not in missing:
        raise SystemExit(
            f"phase1-find-bit-validator-self-test:{label}:expected={expected!r}:actual={missing!r}"
        )


def run_self_test() -> int:
    validator_baseline = "\n".join(REQUIRED_VALIDATOR_SNIPPETS.values()) + "\n"
    workflow_baseline = "\n".join(REQUIRED_WORKFLOW_SNIPPETS.values()) + "\n"
    scripts_readme_baseline = "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS.values()) + "\n"

    baseline_missing = [
        *validate_text("phase1_validator_find_bit", validator_baseline, REQUIRED_VALIDATOR_SNIPPETS),
        *validate_exact_lines("phase1_validator_find_bit_workflow", workflow_baseline, REQUIRED_WORKFLOW_SNIPPETS),
        *validate_text(
            "phase1_validator_find_bit_scripts_readme",
            scripts_readme_baseline,
            REQUIRED_SCRIPTS_README_SNIPPETS,
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
            workflow_baseline,
            scripts_readme_baseline,
            f"phase1_validator_find_bit:{label}",
        )
        total_cases += 1

    for label, snippet in REQUIRED_WORKFLOW_SNIPPETS.items():
        mutated_workflow_lines = [
            line for line in workflow_baseline.splitlines() if line.strip() != snippet
        ]
        expect_missing(
            label,
            validator_baseline,
            "\n".join(mutated_workflow_lines) + "\n",
            scripts_readme_baseline,
            f"phase1_validator_find_bit_workflow:{label}",
        )
        total_cases += 1

    for label, snippet in REQUIRED_SCRIPTS_README_SNIPPETS.items():
        expect_missing(
            label,
            validator_baseline,
            workflow_baseline,
            scripts_readme_baseline.replace(snippet, "", 1),
            f"phase1_validator_find_bit_scripts_readme:{label}",
        )
        total_cases += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_validator_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        temp_validator = tmp_root / "validate-phase1.py"
        temp_workflow = tmp_root / "zigux-bootstrap.yml"
        temp_scripts_readme = tmp_root / "README.md"
        temp_validator.write_text(validator_baseline, encoding="utf-8")
        temp_workflow.write_text(workflow_baseline, encoding="utf-8")
        temp_scripts_readme.write_text(scripts_readme_baseline, encoding="utf-8")
        if run_check(temp_validator, temp_workflow, temp_scripts_readme) != 0:
            raise SystemExit("phase1-find-bit-validator-self-test:file_check_failed")
        total_cases += 1

    print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed if validate-phase1.py or its published workflow and scripts index hooks "
            "stop naming the shipped find_bit tail-start and zero-sized evidence."
        )
    )
    parser.add_argument(
        "--validator",
        type=Path,
        default=DEFAULT_VALIDATOR,
        help="Path to the validate-phase1.py source to inspect.",
    )
    parser.add_argument(
        "--workflow",
        type=Path,
        default=DEFAULT_WORKFLOW,
        help="Path to the bootstrap workflow to inspect.",
    )
    parser.add_argument(
        "--scripts-readme",
        type=Path,
        default=DEFAULT_SCRIPTS_README,
        help="Path to the scripts/zigux README to inspect.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(args.validator, args.workflow, args.scripts_readme)


if __name__ == "__main__":
    raise SystemExit(main())
