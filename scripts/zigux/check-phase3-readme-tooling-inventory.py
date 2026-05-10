#!/usr/bin/env python3
"""Fail-close the Phase 3 tooling inventory reminder and shared Phase 4 route markers."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


README_PATH = Path("scripts/zigux/README.md")
REQUIRED_MARKERS = (
    "validate-phase3.py",
    "validate_phase3_selftest.py",
    "check-phase3-selftest-surface.py",
    "check-phase3-readme-tooling-inventory.py",
    "check-phase3-abi-dump-gate.py",
    "check-phase3-catalog-selftest.py",
    "validate-phase3-policy-unsafe-survey.py",
    "check-phase3-policy-byte-guards.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-abi-header-family-survey.py",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "validate-phase3-abi-bindings-syntax.py",
    "survey-phase3-abi-constant-parity.py",
    "phase3_catalog.py",
    "phase3_check_lib.py",
    "generate-phase3-check-wrappers.py",
    "run-phase3-checks.py",
    "generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog",
    "zigux/uapi/dev_t.zig",
    "python3 scripts/zigux/phase3_catalog.py --self-test",
    "python3 scripts/zigux/phase3_catalog.py --audit-doc-sync",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
    "validate-phase4.py",
    "check-artifact-diff-contract.py",
    "check-phase4-gate-evidence.py",
    "check-phase4-artifact-diff-determinism.py",
    "check-phase4-workflow-route-counts.py",
    "make -C zigux phase4-validate",
    "make -C zigux phase4",
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing scripts README: {path}") from exc


def validate_text(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def run_self_test() -> int:
    sample = "\n".join(REQUIRED_MARKERS)
    missing = validate_text(sample)
    if missing:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    broken = validate_text(sample.replace("Documentation/zigux/phase3-abi-h-boundary-next-step.md", "", 1))
    if "Documentation/zigux/phase3-abi-h-boundary-next-step.md" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected missing marker was not reported")
        return 1

    broken = validate_text(sample.replace("validate-phase3-abi-header-family-survey.py", "", 1))
    if "validate-phase3-abi-header-family-survey.py" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected header-family validator marker was not reported")
        return 1

    broken = validate_text(sample.replace("check-phase4-gate-evidence.py", "", 1))
    if "check-phase4-gate-evidence.py" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected phase4 gate-evidence marker was not reported")
        return 1

    broken = validate_text(sample.replace("make -C zigux phase4-validate", "", 1))
    if "make -C zigux phase4-validate" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected phase4 validate route marker was not reported")
        return 1

    broken = validate_text(sample.replace("check-phase4-workflow-route-counts.py", "", 1))
    if "check-phase4-workflow-route-counts.py" not in broken:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected phase4 workflow-route-counts marker was not reported")
        return 1

    broken = validate_text(
        sample.replace(
            "generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog",
            "",
            1,
        )
    )
    if (
        "generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog"
        not in broken
    ):
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print("expected compatibility-entrypoint marker was not reported")
        return 1

    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in validator coverage without reading repo files",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    readme_path = args.repo_root / README_PATH
    text = load_text(readme_path)
    missing = validate_text(text)
    if missing:
        for marker in missing:
            print(f"missing marker: {marker}", file=sys.stderr)
        return 1

    print(f"validated {readme_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
