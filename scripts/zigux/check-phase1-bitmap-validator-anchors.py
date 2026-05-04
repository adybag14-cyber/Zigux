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
DEFAULT_WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
DEFAULT_MAKEFILE = ROOT / "zigux" / "Makefile"

REQUIRED_CLOSURE_SNIPPETS = {
    "header_alias_review": (
        "PHASE1_BITMAP_HEADER_ALIAS_UNIT_REVIEW=bitmap bitmap_zero bitmap_fill bitmap_copy "
        "bitmap_empty and bitmap_full stay aligned with zero fill copy empty and full for "
        "active-word clearing partial-tail fill masking copied-tail preservation and predicate "
        "results across the same declared bit window"
    ),
    "alias_review": (
        "PHASE1_BITMAP_ALIAS_UNIT_REVIEW=bitmap underscore alias entry points preserve the same "
        "caller-selected window semantics as the camelCase helpers for weight bitwise range and "
        "formatting operations"
    ),
    "allocator_alias_review": (
        "PHASE1_BITMAP_ALLOCATOR_ALIAS_UNIT_REVIEW=bitmap bitmap_alloc bitmap_zalloc and "
        "bitmap_free stay aligned with bitmapAlloc bitmapZalloc and bitmapFree for partial-word "
        "sizing zero-filled allocation and optional-handle reset semantics"
    ),
    "xor_review": (
        "PHASE1_BITMAP_XOR_UNIT_REVIEW=bitmap xorBits multiword-tail coverage proves callers can "
        "clamp the last word back to the in-range bits without leaking the out-of-range tail"
    ),
    "tail_mask_review": (
        "PHASE1_BITMAP_TAIL_MASK_UNIT_REVIEW=bitmap tail-masked reduction helpers ignore "
        "out-of-range differences while preserving the in-range window for andBits, andNotBits, "
        "equal, intersects, and subset"
    ),
    "zero_bit_review": (
        "PHASE1_BITMAP_ZERO_BIT_UNIT_REVIEW=bitmap zero-length helper calls stay side-effect "
        "free so zero fill copy copyClearTail orBits xorBits scans and formatting leave "
        "caller-owned buffers untouched when nbits is zero"
    ),
    "empty_review": (
        "PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap bitmap_scnprintf keeps a non-empty caller buffer "
        "untouched when no bits are set, matching the committed empty-bitmap parity fixture "
        "contract"
    ),
    "alias_anchor": (
        "- bitmap alias unit-test anchor: `tools/lib/bitmap.zig:test "
        "\\\"bitmap underscore aliases preserve bitmap helper semantics\\\"`"
    ),
    "double_underscore_anchor": (
        "- bitmap double-underscore alias unit-test anchor: `tools/lib/bitmap.zig:test "
        "\\\"bitmap double-underscore aliases preserve core helper semantics\\\"`"
    ),
    "size_anchor": (
        "- bitmap size unit-test anchor: `tools/lib/bitmap.zig:test "
        "\\\"bitmap size helpers round up to full words in bytes\\\"`"
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "header_alias_unit_test_anchor": (
        'tools/lib/bitmap.zig:test "bitmap header-style aliases preserve zero fill copy and '
        'predicate semantics"'
    ),
    "header_alias_unit_test_contract": (
        "Direct Zig unit coverage keeps bitmap_zero(), bitmap_fill(), bitmap_copy(), "
        "bitmap_empty(), and bitmap_full() aligned with zero(), fill(), copy(), empty(), and "
        "full() for active-word clearing, partial-tail fill masking, copied-tail preservation, "
        "and predicate results across the same declared bit window."
    ),
    "alias_unit_test_anchor": (
        'tools/lib/bitmap.zig:test "bitmap underscore aliases preserve bitmap helper semantics"'
    ),
    "alias_unit_test_contract": (
        "Direct Zig unit coverage keeps bitmap_weight(), bitmap_and(), bitmap_andnot(), "
        "bitmap_or(), bitmap_xor(), bitmap_equal(), bitmap_intersects(), bitmap_subset(), "
        "bitmap_set(), bitmap_clear(), and bitmap_scnprintf() aligned with the camelCase "
        "helpers across the same caller-selected bit window."
    ),
    "allocator_alias_unit_test_anchor": (
        'tools/lib/bitmap.zig:test "bitmap underscore allocator aliases preserve allocation and '
        'ownership semantics"'
    ),
    "allocator_alias_unit_test_contract": (
        "Direct Zig unit coverage keeps bitmap_alloc(), bitmap_zalloc(), and bitmap_free() "
        "aligned with bitmapAlloc(), bitmapZalloc(), and bitmapFree() for partial-word sizing, "
        "zero-filled allocation, and optional-handle reset semantics."
    ),
    "double_underscore_alias_unit_test_anchor": (
        'tools/lib/bitmap.zig:test "bitmap double-underscore aliases preserve core helper '
        'semantics"'
    ),
    "double_underscore_alias_unit_test_contract": (
        "Direct Zig unit coverage keeps __bitmap_weight(), __bitmap_or(), __bitmap_and(), "
        "__bitmap_andnot(), __bitmap_xor(), __bitmap_equal(), __bitmap_intersects(), "
        "__bitmap_subset(), __bitmap_set(), and __bitmap_clear() aligned with the core helpers "
        "across the same caller-selected bit window."
    ),
    "size_unit_test_anchor": (
        'tools/lib/bitmap.zig:test "bitmap size helpers round up to full words in bytes"'
    ),
    "size_unit_test_contract": (
        "Direct Zig unit coverage keeps bitmapSize() and bitmap_size() aligned by rounding "
        "zero-length, partial-word, and multiword bit counts up to the same full-word byte "
        "footprint."
    ),
    "xor_unit_test_anchor": (
        'tools/lib/bitmap.zig:test "bitmap xor across a multiword tail still lets callers clamp the last word"'
    ),
    "xor_unit_test_contract": (
        "Direct Zig unit coverage keeps xorBits() aligned across a multiword tail by proving callers can clamp the last word back to the in-range bits without leaking the out-of-range tail."
    ),
    "tail_mask_unit_test_anchor": (
        'tools/lib/bitmap.zig:test "bitmap tail-masked helpers ignore out-of-range differences"'
    ),
    "tail_mask_unit_test_contract": (
        "Direct Zig unit coverage keeps andBits(), andNotBits(), equal(), intersects(), and "
        "subset() aligned by masking out-of-range tail differences while preserving the declared "
        "in-range window."
    ),
    "zero_bit_unit_test_anchor": (
        'tools/lib/bitmap.zig:test "bitmap zero-bit helpers stay explicit no-ops"'
    ),
    "zero_bit_unit_test_contract": (
        "Direct Zig unit coverage keeps zero-length helper calls explicit and side-effect free so "
        "zero(), fill(), copy(), copyClearTail(), orBits(), xorBits(), scans, and formatting all "
        "leave caller-owned buffers untouched when nbits is zero."
    ),
    "empty_unit_test_anchor": (
        'tools/lib/bitmap.zig:test "bitmap scnprintf leaves the caller buffer untouched for an '
        'empty bitmap"'
    ),
    "empty_unit_test_contract": (
        "Direct Zig unit coverage keeps bitmap_scnprintf() from mutating a non-empty caller "
        "buffer when no bits are set, matching the committed empty-bitmap parity fixture "
        "contract."
    ),
}

REQUIRED_WORKFLOW_LINES = {
    "self_test_step": "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test",
    "live_step": "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py",
}

REQUIRED_MAKEFILE_LINES = {
    "self_test_step": "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test",
    "live_step": "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bitmap-validator-anchors.py",
}


def validate_text(prefix: str, source: str, snippets: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for label, snippet in snippets.items():
        if snippet not in source:
            missing.append(f"{prefix}:{label}")
    return missing


def validate_exact_lines(prefix: str, source: str, required_lines: dict[str, str]) -> list[str]:
    lines = [line.strip() for line in source.splitlines()]
    missing: list[str] = []
    for label, required_line in required_lines.items():
        actual_count = sum(1 for line in lines if line == required_line)
        if actual_count != 1:
            missing.append(f"{prefix}:{label}:expected=1:actual={actual_count}")
    return missing


def validate_manifest(prefix: str, source: str) -> list[str]:
    missing: list[str] = []
    manifest = json.loads(source)
    notes = manifest.get("helper_review_notes", {})
    bitmap = notes.get("tools/lib/bitmap.zig", {})
    if not isinstance(bitmap, dict):
        return [f"{prefix}:bitmap_note_missing"]
    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        if bitmap.get(field) != expected:
            missing.append(f"{prefix}:{field}")
    return missing


def run_check(
    closure_doc_path: Path,
    manifest_path: Path,
    workflow_path: Path,
    makefile_path: Path,
) -> int:
    closure_doc_source = closure_doc_path.read_text(encoding="utf-8")
    manifest_source = manifest_path.read_text(encoding="utf-8")
    workflow_source = workflow_path.read_text(encoding="utf-8")
    makefile_source = makefile_path.read_text(encoding="utf-8")

    missing = [
        *validate_exact_lines("phase1_bitmap_closure_doc", closure_doc_source, REQUIRED_CLOSURE_SNIPPETS),
        *validate_manifest("phase1_bitmap_manifest", manifest_source),
        *validate_exact_lines("phase1_bitmap_workflow", workflow_source, REQUIRED_WORKFLOW_LINES),
        *validate_exact_lines("phase1_bitmap_makefile", makefile_source, REQUIRED_MAKEFILE_LINES),
    ]
    if missing:
        print("PHASE1_BITMAP_VALIDATOR_ANCHOR_CHECK=fail")
        print("MISSING_PHASE1_BITMAP_VALIDATOR_ANCHORS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_BITMAP_VALIDATOR_ANCHORS_END")
        return 1

    print("PHASE1_BITMAP_VALIDATOR_ANCHOR_CHECK=pass")
    print(
        "PHASE1_BITMAP_VALIDATOR_ANCHOR_COUNT="
        f"{len(REQUIRED_CLOSURE_SNIPPETS) + len(REQUIRED_MANIFEST_FIELDS) + len(REQUIRED_WORKFLOW_LINES) + len(REQUIRED_MAKEFILE_LINES)}"
    )
    return 0


def expect_missing(
    label: str,
    closure_doc_text: str,
    manifest_text: str,
    workflow_text: str,
    makefile_text: str,
    expected: str,
) -> None:
    missing = [
        *validate_exact_lines("phase1_bitmap_closure_doc", closure_doc_text, REQUIRED_CLOSURE_SNIPPETS),
        *validate_manifest("phase1_bitmap_manifest", manifest_text),
        *validate_exact_lines("phase1_bitmap_workflow", workflow_text, REQUIRED_WORKFLOW_LINES),
        *validate_exact_lines("phase1_bitmap_makefile", makefile_text, REQUIRED_MAKEFILE_LINES),
    ]
    if expected not in missing:
        raise SystemExit(
            f"phase1-bitmap-validator-self-test:{label}:expected={expected!r}:actual={missing!r}"
        )


def run_self_test() -> int:
    closure_doc_baseline = "\n".join(REQUIRED_CLOSURE_SNIPPETS.values()) + "\n"
    manifest_baseline = json.dumps(
        {
            "helper_review_notes": {
                "tools/lib/bitmap.zig": dict(REQUIRED_MANIFEST_FIELDS),
            }
        },
        indent=2,
    ) + "\n"
    workflow_baseline = "\n".join(REQUIRED_WORKFLOW_LINES.values()) + "\n"
    makefile_baseline = "\n".join(REQUIRED_MAKEFILE_LINES.values()) + "\n"

    baseline_missing = [
        *validate_exact_lines("phase1_bitmap_closure_doc", closure_doc_baseline, REQUIRED_CLOSURE_SNIPPETS),
        *validate_manifest("phase1_bitmap_manifest", manifest_baseline),
        *validate_exact_lines("phase1_bitmap_workflow", workflow_baseline, REQUIRED_WORKFLOW_LINES),
        *validate_exact_lines("phase1_bitmap_makefile", makefile_baseline, REQUIRED_MAKEFILE_LINES),
    ]
    if baseline_missing:
        raise SystemExit(
            "phase1-bitmap-validator-self-test:baseline_failed:" + ",".join(baseline_missing)
        )

    total_cases = 1

    for label, snippet in REQUIRED_CLOSURE_SNIPPETS.items():
        expect_missing(
            label,
            closure_doc_baseline.replace(snippet, "", 1),
            manifest_baseline,
            workflow_baseline,
            makefile_baseline,
            f"phase1_bitmap_closure_doc:{label}:expected=1:actual=0",
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            closure_doc_baseline + snippet + "\n",
            manifest_baseline,
            workflow_baseline,
            makefile_baseline,
            f"phase1_bitmap_closure_doc:{label}:expected=1:actual=2",
        )
        total_cases += 1

    for field in REQUIRED_MANIFEST_FIELDS:
        mutated = json.loads(manifest_baseline)
        mutated["helper_review_notes"]["tools/lib/bitmap.zig"][field] = "drift"
        expect_missing(
            field,
            closure_doc_baseline,
            json.dumps(mutated, indent=2) + "\n",
            workflow_baseline,
            makefile_baseline,
            f"phase1_bitmap_manifest:{field}",
        )
        total_cases += 1

    for label, line in REQUIRED_WORKFLOW_LINES.items():
        mutated_lines = [entry for entry in workflow_baseline.splitlines() if entry.strip() != line]
        expect_missing(
            label,
            closure_doc_baseline,
            manifest_baseline,
            "\n".join(mutated_lines) + "\n",
            makefile_baseline,
            f"phase1_bitmap_workflow:{label}:expected=1:actual=0",
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            closure_doc_baseline,
            manifest_baseline,
            workflow_baseline + line + "\n",
            makefile_baseline,
            f"phase1_bitmap_workflow:{label}:expected=1:actual=2",
        )
        total_cases += 1

    for label, line in REQUIRED_MAKEFILE_LINES.items():
        mutated_lines = [entry for entry in makefile_baseline.splitlines() if entry.strip() != line]
        expect_missing(
            label,
            closure_doc_baseline,
            manifest_baseline,
            workflow_baseline,
            "\n".join(mutated_lines) + "\n",
            f"phase1_bitmap_makefile:{label}:expected=1:actual=0",
        )
        total_cases += 1
        expect_missing(
            f"{label}_duplicate",
            closure_doc_baseline,
            manifest_baseline,
            workflow_baseline,
            makefile_baseline + line + "\n",
            f"phase1_bitmap_makefile:{label}:expected=1:actual=2",
        )
        total_cases += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bitmap_validator_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        closure_path = tmp_root / "phase1-closure.md"
        manifest_path = tmp_root / "phase1_helper_manifest.json"
        workflow_path = tmp_root / "zigux-bootstrap.yml"
        makefile_path = tmp_root / "Makefile"
        closure_path.write_text(closure_doc_baseline, encoding="utf-8")
        manifest_path.write_text(manifest_baseline, encoding="utf-8")
        workflow_path.write_text(workflow_baseline, encoding="utf-8")
        makefile_path.write_text(makefile_baseline, encoding="utf-8")
        if run_check(closure_path, manifest_path, workflow_path, makefile_path) != 0:
            raise SystemExit("phase1-bitmap-validator-self-test:file_check_failed")
        total_cases += 1

    print("PHASE1_BITMAP_VALIDATOR_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed if the shared Phase 1 validation lane stops naming the shipped bitmap "
            "header-alias, underscore-alias, allocator-alias, double-underscore-alias, "
            "size-helper, xor-window, tail-mask, zero-bit, or empty-bitmap review packet."
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
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(
        args.closure_doc,
        args.manifest,
        args.workflow,
        args.makefile,
    )


if __name__ == "__main__":
    raise SystemExit(main())
