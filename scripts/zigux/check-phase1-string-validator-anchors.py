#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
if len(SELF_PATH.parents) >= 3:
    ROOT = SELF_PATH.parents[2]
else:
    ROOT = SELF_PATH.parent

DEFAULT_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase1-closure.md"
DEFAULT_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"

REQUIRED_CLOSURE_SNIPPETS = {
    "strscpy_review": (
        "PHASE1_STRING_STRSCPY_UNIT_REVIEW=string strscpy keeps bounded kernel copy semantics "
        "aligned for exact-fit, truncation, embedded-NUL, and zero-sized destination cases"
    ),
    "sysfs_review": (
        "PHASE1_STRING_SYSFS_UNIT_REVIEW=string sysfsStreq and sysfs_streq treat a single "
        "trailing newline as equivalent to C-string termination while still rejecting "
        "non-terminal newline and content mismatches"
    ),
    "memparse_review": (
        "PHASE1_STRING_MEMPARSE_UNIT_REVIEW=string memparse preserves decimal, hexadecimal, "
        "suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B "
        "forms without changing the parsed value or rest pointer contract"
    ),
    "strscpy_anchor": (
        '- string strscpy unit-test anchor: `tools/lib/string.zig:test '
        '\"strscpy mirrors bounded kernel copy semantics\"`'
    ),
    "sysfs_anchor": (
        '- string sysfs unit-test anchor: `tools/lib/string.zig:test '
        '\"sysfsStreq treats a trailing newline as equivalent to C-string termination\"`'
    ),
    "memparse_anchor": (
        '- string memparse unit-test anchor: `tools/lib/string.zig:test '
        '\"memparse forwards the header-level string helper surface\"`'
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "strscpy_unit_test_anchor": (
        'tools/lib/string.zig:test "strscpy mirrors bounded kernel copy semantics"'
    ),
    "strscpy_unit_test_contract": (
        "Direct Zig unit coverage keeps strscpy aligned with bounded kernel copy semantics for "
        "exact-fit, truncation, embedded-NUL, and zero-sized destination cases."
    ),
    "sysfs_unit_test_anchor": (
        'tools/lib/string.zig:test "sysfsStreq treats a trailing newline as equivalent to '
        'C-string termination"'
    ),
    "sysfs_unit_test_contract": (
        "Direct Zig unit coverage keeps sysfsStreq() and sysfs_streq() aligned by treating a "
        "single trailing newline as equivalent to C-string termination while still rejecting "
        "non-terminal newline and content mismatches."
    ),
    "memparse_unit_test_anchor": (
        'tools/lib/string.zig:test "memparse forwards the header-level string helper surface"'
    ),
    "memparse_unit_test_contract": (
        "Direct Zig unit coverage keeps memparse aligned by preserving decimal, hexadecimal, "
        "suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B "
        "forms without changing the parsed value or rest pointer contract."
    ),
}

def validate_text(prefix: str, source: str, snippets: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for label, snippet in snippets.items():
        if snippet not in source:
            missing.append(f"{prefix}:{label}")
    return missing


def validate_manifest(prefix: str, source: str) -> list[str]:
    missing: list[str] = []
    manifest = json.loads(source)
    notes = manifest.get("helper_review_notes", {})
    string_note = notes.get("tools/lib/string.zig", {})
    if not isinstance(string_note, dict):
        return [f"{prefix}:string_note_missing"]
    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        if string_note.get(field) != expected:
            missing.append(f"{prefix}:{field}")
    return missing


def run_check(
    closure_doc_path: Path,
    manifest_path: Path,
) -> int:
    closure_doc_source = closure_doc_path.read_text(encoding="utf-8")
    manifest_source = manifest_path.read_text(encoding="utf-8")

    missing = [
        *validate_text("phase1_string_closure_doc", closure_doc_source, REQUIRED_CLOSURE_SNIPPETS),
        *validate_manifest("phase1_string_manifest", manifest_source),
    ]
    if missing:
        print("PHASE1_STRING_VALIDATOR_ANCHOR_CHECK=fail")
        print("MISSING_PHASE1_STRING_VALIDATOR_ANCHORS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_STRING_VALIDATOR_ANCHORS_END")
        return 1

    print("PHASE1_STRING_VALIDATOR_ANCHOR_CHECK=pass")
    print(
        "PHASE1_STRING_VALIDATOR_ANCHOR_COUNT="
        f"{len(REQUIRED_CLOSURE_SNIPPETS) + len(REQUIRED_MANIFEST_FIELDS)}"
    )
    return 0


def expect_missing(
    label: str,
    closure_doc_text: str,
    manifest_text: str,
    expected: str,
) -> None:
    missing = [
        *validate_text("phase1_string_closure_doc", closure_doc_text, REQUIRED_CLOSURE_SNIPPETS),
        *validate_manifest("phase1_string_manifest", manifest_text),
    ]
    if expected not in missing:
        raise SystemExit(
            f"phase1-string-validator-self-test:{label}:expected={expected!r}:actual={missing!r}"
        )


def run_self_test() -> int:
    closure_doc_baseline = "\n".join(REQUIRED_CLOSURE_SNIPPETS.values()) + "\n"
    manifest_baseline = json.dumps(
        {
            "helper_review_notes": {
                "tools/lib/string.zig": dict(REQUIRED_MANIFEST_FIELDS),
            }
        },
        indent=2,
    ) + "\n"

    baseline_missing = [
        *validate_text("phase1_string_closure_doc", closure_doc_baseline, REQUIRED_CLOSURE_SNIPPETS),
        *validate_manifest("phase1_string_manifest", manifest_baseline),
    ]
    if baseline_missing:
        raise SystemExit(
            "phase1-string-validator-self-test:baseline_failed:" + ",".join(baseline_missing)
        )

    total_cases = 1

    for label, snippet in REQUIRED_CLOSURE_SNIPPETS.items():
        expect_missing(
            label,
            closure_doc_baseline.replace(snippet, "", 1),
            manifest_baseline,
            f"phase1_string_closure_doc:{label}",
        )
        total_cases += 1

    for field in REQUIRED_MANIFEST_FIELDS:
        mutated = json.loads(manifest_baseline)
        mutated["helper_review_notes"]["tools/lib/string.zig"][field] = "drift"
        expect_missing(
            field,
            closure_doc_baseline,
            json.dumps(mutated, indent=2) + "\n",
            f"phase1_string_manifest:{field}",
        )
        total_cases += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_validator_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        closure_path = tmp_root / "phase1-closure.md"
        manifest_path = tmp_root / "phase1_helper_manifest.json"
        closure_path.write_text(closure_doc_baseline, encoding="utf-8")
        manifest_path.write_text(manifest_baseline, encoding="utf-8")
        if run_check(closure_path, manifest_path) != 0:
            raise SystemExit("phase1-string-validator-self-test:file_check_failed")
        total_cases += 1

    print("PHASE1_STRING_VALIDATOR_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_STRING_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed if the shared Phase 1 validation lane stops naming the shipped string "
            "strscpy, sysfsStreq, or memparse review packet."
        )
    )
    parser.add_argument(
        "--closure-doc",
        type=Path,
        default=DEFAULT_CLOSURE_DOC,
        help="Path to the phase1-closure.md document to inspect.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the phase1 helper manifest to inspect.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(
        args.closure_doc,
        args.manifest,
    )


if __name__ == "__main__":
    raise SystemExit(main())
