#!/usr/bin/env python3
"""Guard the live Phase 4 artifact-diff Makefile contract."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = Path("zigux/Makefile")

SELF_CHECK = "scripts/zigux/check-phase4-artifact-diff-makefile-contract.py"
CONTRACT_TARGET = "phase4-artifact-diff-contract"
VALIDATE_TARGET = "phase4-validate"

EXPECTED_CONTRACT_LINES = (
    "phase4-artifact-diff-contract:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {SELF_CHECK} --self-test",
    f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {SELF_CHECK}",
)

EXPECTED_VALIDATE_LINES = (
    "phase4-validate:",
    "\t$(MAKE) phase4-artifact-diff-contract",
)

FORBIDDEN_PHASE4_LINES = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py",
)

EXPECTED_SELF_TEST_CASES = (
    "baseline_round_trip",
    "missing_makefile",
    "contract_missing_determinism_self_test",
    "contract_legacy_contract_self_test",
    "validate_missing_make_delegate",
    "validate_legacy_validator",
    "validate_legacy_contract_check",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()



def read(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc



def write(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def extract_target_block(text: str, target: str) -> list[str]:
    lines = text.splitlines()
    header = f"{target}:"
    for index, line in enumerate(lines):
        if line == header:
            block = [line]
            for follower in lines[index + 1 :]:
                if follower.startswith("\t"):
                    block.append(follower)
                    continue
                if follower == "":
                    block.append(follower)
                    continue
                break
            return [line for line in block if line != ""]
    raise RuntimeError(f"missing required target: {target}")



def require_ordered_prefix(block: list[str], expected: tuple[str, ...], label: str) -> None:
    if len(block) < len(expected):
        raise RuntimeError(f"{label} is too short: expected prefix {expected}, got {block}")
    actual_prefix = tuple(block[: len(expected)])
    if actual_prefix != expected:
        raise RuntimeError(f"{label} drifted: expected prefix {expected}, got {actual_prefix}")



def require_forbidden_absent(block: list[str], forbidden: tuple[str, ...], label: str) -> None:
    present = [line for line in forbidden if line in block]
    if present:
        raise RuntimeError(f"{label} still carries retired lines: {present}")



def check(root: Path) -> None:
    makefile = read(root, MAKEFILE)
    contract_block = extract_target_block(makefile, CONTRACT_TARGET)
    validate_block = extract_target_block(makefile, VALIDATE_TARGET)
    require_ordered_prefix(contract_block, EXPECTED_CONTRACT_LINES, CONTRACT_TARGET)
    require_ordered_prefix(validate_block, EXPECTED_VALIDATE_LINES, VALIDATE_TARGET)
    require_forbidden_absent(contract_block, FORBIDDEN_PHASE4_LINES, CONTRACT_TARGET)
    require_forbidden_absent(validate_block, FORBIDDEN_PHASE4_LINES, VALIDATE_TARGET)



def baseline_makefile() -> str:
    return "\n".join(
        [
            "PYTHON ?= python3",
            "ZIGUX_ROOT := ..",
            "",
            "phase4-validate:",
            "\t$(MAKE) phase4-artifact-diff-contract",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-remaining-gap-matrix.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-reversible-delivery-pins.py",
            "",
            "phase4-artifact-diff-contract:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
            f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {SELF_CHECK} --self-test",
            f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {SELF_CHECK}",
            "",
            "phase4-test:",
            "\techo test",
            "",
        ]
    )



def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="phase4-artifact-diff-makefile-") as tmp:
        root = Path(tmp)
        write(root, MAKEFILE, baseline_makefile())
        check(root)
        covered.append("baseline_round_trip")

        (root / MAKEFILE).unlink()
        try:
            check(root)
        except RuntimeError as exc:
            if str(exc) != "missing required file: zigux/Makefile":
                raise AssertionError(f"missing_makefile message drifted: {exc}") from exc
            covered.append("missing_makefile")
        else:
            raise AssertionError("expected missing_makefile to fail closed")

        write(root, MAKEFILE, baseline_makefile().replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test\n",
            "",
            1,
        ))
        try:
            check(root)
        except RuntimeError:
            covered.append("contract_missing_determinism_self_test")
        else:
            raise AssertionError("expected contract_missing_determinism_self_test to fail closed")

        write(root, MAKEFILE, baseline_makefile().replace(
            f"\tcd $(ZIGUX_ROOT) && $(PYTHON) {SELF_CHECK} --self-test\n",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py --self-test\n",
            1,
        ))
        try:
            check(root)
        except RuntimeError:
            covered.append("contract_legacy_contract_self_test")
        else:
            raise AssertionError("expected contract_legacy_contract_self_test to fail closed")

        write(root, MAKEFILE, baseline_makefile().replace(
            "\t$(MAKE) phase4-artifact-diff-contract\n",
            "",
            1,
        ))
        try:
            check(root)
        except RuntimeError:
            covered.append("validate_missing_make_delegate")
        else:
            raise AssertionError("expected validate_missing_make_delegate to fail closed")

        write(root, MAKEFILE, baseline_makefile().replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py\n",
            1,
        ))
        try:
            check(root)
        except RuntimeError:
            covered.append("validate_legacy_validator")
        else:
            raise AssertionError("expected validate_legacy_validator to fail closed")

        write(root, MAKEFILE, baseline_makefile().replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py\n",
            1,
        ))
        try:
            check(root)
        except RuntimeError:
            covered.append("validate_legacy_contract_check")
        else:
            raise AssertionError("expected validate_legacy_contract_check to fail closed")

    if tuple(covered) != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"self-test catalog drifted: expected {EXPECTED_SELF_TEST_CASES}, got {tuple(covered)}"
        )

    print("PHASE4_ARTIFACT_DIFF_MAKEFILE_CONTRACT_SELF_TEST=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_MAKEFILE_CONTRACT_SELF_TEST_CASE_COUNT="
        f"{len(EXPECTED_SELF_TEST_CASES)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_MAKEFILE_CONTRACT_SELF_TEST_CASES="
        + ",".join(EXPECTED_SELF_TEST_CASES)
    )
    return 0



def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    try:
        run_self_test()
        check(args.root.resolve())
    except (AssertionError, RuntimeError) as exc:
        print(f"PHASE4_ARTIFACT_DIFF_MAKEFILE_CONTRACT=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_ARTIFACT_DIFF_MAKEFILE_CONTRACT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
