#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
PARITY_SCRIPT_PATH = Path("scripts/zigux/check-phase6-base64-c-parity.py")

SELF_TEST_CASE_COUNT = 10
PARITY_CASE_COUNT = 122
VARIANT_ENCODE_VECTORS = 30
VARIANT_DECODE_VECTORS = 20
CATALOG_EVIDENCE_SELF_TEST_CASE_COUNT = 11

CATALOG_MARKERS = [
    "shared packet posture: parked after the current helper-local parity and perf surface cleared the bounded Phase 6 goal",
    f"PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}",
    f"PHASE6_BASE64_C_PARITY_CASES={PARITY_CASE_COUNT}",
]

CATALOG_FIXTURE_MARKERS = [
    f"{VARIANT_ENCODE_VECTORS} variant encode vectors",
    f"{VARIANT_DECODE_VECTORS} variant decode vectors",
]

CATALOG_REVIEW_MARKERS = [
    "`python3 scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test` and `python3 scripts/zigux/check-phase6-base64-catalog-evidence.py` now keep the shared base64 review packet fail-closed",
]

PARITY_SCRIPT_MARKERS = [
    'print("PHASE6_BASE64_C_PARITY_SELF_TEST=pass")',
    f'print("PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")',
    'print("PHASE6_BASE64_C_PARITY=pass")',
    'print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")',
]

EXPECTED_CHECKS = [
    "python3 scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test",
    "python3 scripts/zigux/check-phase6-base64-catalog-evidence.py",
]


def read_text(root: Path, relpath: Path) -> str:
    return (root / relpath).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    missing: list[str] = []

    for relpath in (CATALOG_PATH, MANIFEST_PATH, PARITY_SCRIPT_PATH):
        if not (root / relpath).exists():
            missing.append(f"missing_file:{relpath.as_posix()}")
    if missing:
        return missing

    catalog = read_text(root, CATALOG_PATH)
    for marker in CATALOG_MARKERS:
        if marker not in catalog:
            missing.append(f"catalog:missing:{marker}")
    for marker in CATALOG_FIXTURE_MARKERS:
        if marker not in catalog:
            missing.append(f"catalog_fixture:missing:{marker}")
    for marker in CATALOG_REVIEW_MARKERS:
        if marker not in catalog:
            missing.append(f"catalog_review:missing:{marker}")

    parity_script = read_text(root, PARITY_SCRIPT_PATH)
    for marker in PARITY_SCRIPT_MARKERS:
        if marker not in parity_script:
            missing.append(f"parity_script:missing:{marker}")

    manifest = json.loads(read_text(root, MANIFEST_PATH))
    base64 = manifest.get("determinism_evidence", {}).get("base64", {})
    if base64.get("variant_encode_vectors") != VARIANT_ENCODE_VECTORS:
        missing.append("manifest:base64:variant_encode_vectors")
    if base64.get("variant_decode_vectors") != VARIANT_DECODE_VECTORS:
        missing.append("manifest:base64:variant_decode_vectors")
    if base64.get("c_parity_self_test_cases") != SELF_TEST_CASE_COUNT:
        missing.append("manifest:base64:c_parity_self_test_cases")
    if base64.get("c_parity_cases") != PARITY_CASE_COUNT:
        missing.append("manifest:base64:c_parity_cases")

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        missing.append("manifest:exact_checks")
    else:
        for check in EXPECTED_CHECKS:
            actual_count = sum(1 for item in exact_checks if item == check)
            if actual_count != 1:
                missing.append(
                    f"manifest:exact_checks:expected=1:actual={actual_count}:{check}"
                )

    return missing


def write(root: Path, relpath: Path, content: str) -> None:
    target = root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_self_test_tree(root: Path) -> None:
    write(
        root,
        CATALOG_PATH,
        "\n".join(["# x", *CATALOG_MARKERS, *CATALOG_FIXTURE_MARKERS, *CATALOG_REVIEW_MARKERS]) + "\n",
    )
    write(root, PARITY_SCRIPT_PATH, "\n".join(PARITY_SCRIPT_MARKERS) + "\n")
    write(
        root,
        MANIFEST_PATH,
        json.dumps(
            {
                "determinism_evidence": {
                    "base64": {
                        "variant_encode_vectors": VARIANT_ENCODE_VECTORS,
                        "variant_decode_vectors": VARIANT_DECODE_VECTORS,
                        "c_parity_self_test_cases": SELF_TEST_CASE_COUNT,
                        "c_parity_cases": PARITY_CASE_COUNT,
                    }
                },
                "exact_checks": EXPECTED_CHECKS,
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            count = 0
            build_self_test_tree(root)
            if validate(root):
                raise AssertionError("pass tree should validate")
            count += 1

            build_self_test_tree(root)
            write(root, CATALOG_PATH, "# x\nPHASE6_BASE64_C_PARITY_CASES=122\n")
            if f"catalog:missing:{CATALOG_MARKERS[0]}" not in validate(root):
                raise AssertionError("missing parked posture marker failure")
            count += 1

            build_self_test_tree(root)
            write(root, CATALOG_PATH, "# x\nPHASE6_BASE64_C_PARITY_CASES=122\n")
            if f"catalog:missing:PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}" not in validate(root):
                raise AssertionError("missing catalog self-test marker failure")
            count += 1

            build_self_test_tree(root)
            write(root, CATALOG_PATH, "\n".join(["# x", *CATALOG_MARKERS, *CATALOG_FIXTURE_MARKERS]) + "\n")
            if f"catalog_review:missing:{CATALOG_REVIEW_MARKERS[0]}" not in validate(root):
                raise AssertionError("missing catalog review marker failure")
            count += 1

            build_self_test_tree(root)
            write(root, CATALOG_PATH, "\n".join(["# x", *CATALOG_MARKERS, CATALOG_FIXTURE_MARKERS[1], *CATALOG_REVIEW_MARKERS]) + "\n")
            if f"catalog_fixture:missing:{CATALOG_FIXTURE_MARKERS[0]}" not in validate(root):
                raise AssertionError("missing catalog fixture marker failure")
            count += 1

            build_self_test_tree(root)
            manifest = json.loads(read_text(root, MANIFEST_PATH))
            manifest["determinism_evidence"]["base64"]["variant_encode_vectors"] = 24
            write(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
            if "manifest:base64:variant_encode_vectors" not in validate(root):
                raise AssertionError("missing manifest variant encode count failure")
            count += 1

            build_self_test_tree(root)
            manifest = json.loads(read_text(root, MANIFEST_PATH))
            manifest["determinism_evidence"]["base64"]["c_parity_self_test_cases"] = 9
            write(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
            if "manifest:base64:c_parity_self_test_cases" not in validate(root):
                raise AssertionError("missing manifest self-test count failure")
            count += 1

            build_self_test_tree(root)
            manifest = json.loads(read_text(root, MANIFEST_PATH))
            manifest["exact_checks"] = manifest["exact_checks"][:-1]
            write(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
            if (
                "manifest:exact_checks:expected=1:actual=0:python3 scripts/zigux/check-phase6-base64-catalog-evidence.py"
                not in validate(root)
            ):
                raise AssertionError("missing manifest exact-check failure")
            count += 1

            build_self_test_tree(root)
            manifest = json.loads(read_text(root, MANIFEST_PATH))
            manifest["exact_checks"] = [
                EXPECTED_CHECKS[0],
                EXPECTED_CHECKS[0],
                EXPECTED_CHECKS[1],
            ]
            write(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
            if (
                "manifest:exact_checks:expected=1:actual=2:python3 scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test"
                not in validate(root)
            ):
                raise AssertionError("missing manifest duplicate exact-check failure")
            count += 1

            build_self_test_tree(root)
            write(root, PARITY_SCRIPT_PATH, 'print("PHASE6_BASE64_C_PARITY_SELF_TEST=pass")\n')
            if 'parity_script:missing:print("PHASE6_BASE64_C_PARITY=pass")' not in validate(root):
                raise AssertionError("missing parity script marker failure")
            count += 1

            build_self_test_tree(root)
            (root / MANIFEST_PATH).unlink()
            if f"missing_file:{MANIFEST_PATH.as_posix()}" not in validate(root):
                raise AssertionError("missing manifest file failure")
            count += 1

            if count != CATALOG_EVIDENCE_SELF_TEST_CASE_COUNT:
                raise AssertionError(
                    f"expected {CATALOG_EVIDENCE_SELF_TEST_CASE_COUNT} self-test cases, got {count}"
                )
    except AssertionError as exc:
        print("PHASE6_BASE64_CATALOG_EVIDENCE_SELF_TEST=fail")
        print(f"PHASE6_BASE64_CATALOG_EVIDENCE_SELF_TEST_REASON={exc}")
        return 1

    print("PHASE6_BASE64_CATALOG_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE6_BASE64_CATALOG_EVIDENCE_SELF_TEST_CASE_COUNT={CATALOG_EVIDENCE_SELF_TEST_CASE_COUNT}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 6 base64 catalog evidence matches the shipped parity script."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()

    missing = validate(ROOT)
    if missing:
        print("PHASE6_BASE64_CATALOG_EVIDENCE=fail")
        print("PHASE6_BASE64_CATALOG_EVIDENCE_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE6_BASE64_CATALOG_EVIDENCE_MISSING_END")
        return 1

    print("PHASE6_BASE64_CATALOG_EVIDENCE=pass")
    print(f"PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    print(f"PHASE6_BASE64_C_PARITY_CASES={PARITY_CASE_COUNT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())