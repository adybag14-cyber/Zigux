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
VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase1.py"

REQUIRED_SNIPPETS = {
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
    "manifest_tail_start_anchor_marker": '"tail_start_unit_test_anchor"',
    "manifest_tail_start_contract_marker": '"tail_start_unit_test_contract"',
    "manifest_zero_sized_anchor_marker": '"zero_sized_unit_test_anchor"',
    "manifest_zero_sized_contract_marker": '"zero_sized_unit_test_contract"',
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


def validate_text(source: str) -> list[str]:
    missing: list[str] = []
    for label, snippet in REQUIRED_SNIPPETS.items():
        if snippet not in source:
            missing.append(f"phase1_validator_find_bit:{label}")
    return missing


def run_check(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    missing = validate_text(source)
    if missing:
        print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_CHECK=fail")
        print("MISSING_PHASE1_FIND_BIT_VALIDATOR_ANCHORS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_FIND_BIT_VALIDATOR_ANCHORS_END")
        return 1

    print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_CHECK=pass")
    print(f"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_COUNT={len(REQUIRED_SNIPPETS)}")
    print(f"PHASE1_FIND_BIT_VALIDATOR_PATH={path}")
    return 0


def expect_missing(label: str, text: str, expected: str) -> None:
    missing = validate_text(text)
    if expected not in missing:
        raise SystemExit(
            f"phase1-find-bit-validator-self-test:{label}:expected={expected!r}:actual={missing!r}"
        )


def run_self_test() -> int:
    baseline = "\n".join(REQUIRED_SNIPPETS.values()) + "\n"
    if validate_text(baseline):
        raise SystemExit("phase1-find-bit-validator-self-test:baseline_failed")

    total_cases = 1
    for label, snippet in REQUIRED_SNIPPETS.items():
        expect_missing(label, baseline.replace(snippet, ""), f"phase1_validator_find_bit:{label}")
        total_cases += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_validator_") as tmp_dir:
        temp_validator = Path(tmp_dir) / "validate-phase1.py"
        temp_validator.write_text(baseline, encoding="utf-8")
        if run_check(temp_validator) != 0:
            raise SystemExit("phase1-find-bit-validator-self-test:file_check_failed")
        total_cases += 1

    print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed if validate-phase1.py stops checking the shipped find_bit tail-start and zero-sized evidence."
    )
    parser.add_argument(
        "--validator",
        type=Path,
        default=VALIDATOR,
        help="Path to the validate-phase1.py source to inspect.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(args.validator)


if __name__ == "__main__":
    raise SystemExit(main())
