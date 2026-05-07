#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

REQUIRED_FILES = [
    *EXPECTED_HELPERS,
    "scripts/zigux/artifact_diff.py",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/validate-phase1-closure.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/Makefile",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "zigux/tests/fixtures/phase1_helpers.json",
]

DOC_MARKERS = {
    "docs_root_phase1_packet": [
        "Phase 1 notes - `Documentation/zigux/phase1-closure.md` - `scripts/zigux/README.md` - `scripts/zigux/install-zig.py` - `scripts/zigux/check-phase1-installer-review-surfaces.py`",
        "keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root",
    ],
    "tests_root_phase1_packet": [
        "keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`",
        "`.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root",
    ],
    "review_checklist_phase1_packet": [
        "if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`",
        "`scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche",
    ],
}

PHASE1_IMPORT_MARKERS = [
    '@import("argv_split")',
    '@import("bitmap")',
    '@import("cmdline")',
    '@import("ctype")',
    '@import("find_bit")',
    '@import("hweight")',
    '@import("list_sort")',
    '@import("rbtree")',
    '@import("slab")',
    '@import("str_error_r")',
    '@import("string")',
    '@import("vsprintf")',
    '@import("zalloc")',
    '@embedFile("fixtures/phase1_helpers.json")',
]

PHASE1_REPLAY_MARKERS = [
    "fixture.find_bit.tail_clamped_first",
    "fixture.find_bit.tail_zero_clamped_next",
    "fixture.find_bit.tail_and_clamped_next",
    "fixture.bitmap.partial_xor_nbits",
    "fixture.bitmap.partial_xor_masked_values",
    "fixture.string.replace_char",
    "fixture.string.replace_char_end",
    "fixture.string.replace_char_cstr_end",
    "fixture.string.replace_char_cstr_bytes",
    "fixture.string.memchr_inv_index",
    "fixture.string.memchr_inv_none",
    "fixture.rbtree.find_found_key",
    "fixture.rbtree.find_missing",
    "fixture.rbtree.find_first_serial",
    "fixture.rbtree.next_match_serials",
    "fixture.rbtree.next_match_terminal_null",
]

HELPER_FOLLOWUP_TESTS = [
    'test "phase 1 string replaceChar stops at embedded NUL"',
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
]

SOURCE_MARKERS = {
    "find_bit_test_anchor": (
        "tools/lib/find_bit.zig",
        [
            'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
            'test "low-level underscore aliases mirror the primary find helpers"',
        ],
    ),
    "bitmap_test_anchor": (
        "tools/lib/bitmap.zig",
        [
            'test "bitmap range helpers honor exact first-word boundaries"',
            'test "bitmap predicates ignore out-of-range tail bits"',
            'test "bitmap zero-bit helpers stay explicit no-ops"',
        ],
    ),
    "string_test_anchor": (
        "tools/lib/string.zig",
        [
            'test "memparse applies suffixes before signed clamping"',
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        ],
    ),
    "rbtree_test_anchor": (
        "tools/lib/rbtree.zig",
        [
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
        ],
    ),
}

EXPECTED_MANIFEST_HELPER_FIELDS = {
    "tools/lib/bitmap.zig": {
        "helper_test_anchors": [
            'test "bitmap predicates ignore out-of-range tail bits"',
        ],
        "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
        "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
        "partial_xor_review_fields": ["partial_xor_nbits", "partial_xor_masked_values"],
    },
    "tools/lib/find_bit.zig": {
        "tail_clamp_fixture_keys": [
            "tail_clamped_first",
            "tail_clamped_next",
            "tail_zero_clamped_first",
            "tail_zero_clamped_next",
            "tail_and_clamped_first",
            "tail_and_clamped_next",
        ],
    },
    "tools/lib/rbtree.zig": {
        "helper_test_anchors": [
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
        ],
        "parity_fixture_keys": [
            "find_found_key",
            "find_missing",
            "find_first_serial",
            "next_match_serials",
            "next_match_terminal_null",
        ],
    },
    "tools/lib/string.zig": {
        "helper_test_anchors": [
            'test "memparse applies suffixes before signed clamping"',
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        ],
        "memparse_review_anchors": [
            'test "memparse applies suffixes before signed clamping"',
        ],
        "parity_fixture_keys": [
            "replace_char",
            "replace_char_end",
            "replace_char_cstr_end",
            "replace_char_cstr_bytes",
            "memchr_inv_index",
            "memchr_inv_none",
        ],
    },
}

def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]

def collect_marker_counts(text: str, label: str, markers: list[str]) -> list[str]:
    mismatches: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            mismatches.append(f"{label}:{marker}:expected=1:actual={count}")
    return mismatches

def collect_presence_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count < 1:
            missing.append(f"{label}:{marker}:expected>=1:actual={count}")
    return missing

def extract_test_body(text: str, title: str) -> str | None:
    anchor = f'test "{title}"'
    start = text.find(anchor)
    if start == -1:
        return None
    next_start = text.find('\ntest "', start + len(anchor))
    return text[start:] if next_start == -1 else text[start:next_start]

def collect_phase1_fixture_mismatches(root: Path) -> list[str]:
    fixture = json.loads((root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json").read_text(encoding="utf-8"))
    mismatches: list[str] = []
    if sorted(fixture.keys()) != sorted(["argv_split","bitmap","cmdline","ctype","find_bit","hweight","list_sort","rbtree","slab","str_error_r","string","vsprintf","zalloc"]):
        mismatches.append("phase1_fixture_shape:top_level_keys")
    find_bit = fixture.get("find_bit")
    if not isinstance(find_bit, dict):
        return ["phase1_fixture_find_bit:find_bit:expected=object:actual=missing"]
    bits_per_long = find_bit.get("bits_per_long")
    if not isinstance(bits_per_long, int) or bits_per_long <= 0:
        return [f"phase1_fixture_find_bit:bits_per_long:expected=positive-integer:actual={bits_per_long!r}"]
    tail_expected = bits_per_long + 5
    for field in ("tail_clamped_first","tail_clamped_next","tail_zero_clamped_first","tail_zero_clamped_next","tail_and_clamped_first","tail_and_clamped_next"):
        if find_bit.get(field) != tail_expected:
            mismatches.append(f"phase1_fixture_find_bit:{field}:expected={tail_expected}:actual={find_bit.get(field)!r}")
    bitmap = fixture.get("bitmap")
    if not isinstance(bitmap, dict):
        mismatches.append("phase1_fixture_bitmap:bitmap:expected=object:actual=missing")
    else:
        if bitmap.get("partial_xor_nbits") != 4:
            mismatches.append(f"phase1_fixture_bitmap:partial_xor_nbits:expected=4:actual={bitmap.get('partial_xor_nbits')!r}")
        if bitmap.get("partial_xor_masked_values") != [14]:
            mismatches.append("phase1_fixture_bitmap:partial_xor_masked_values")
    string = fixture.get("string")
    if not isinstance(string, dict):
        mismatches.append("phase1_fixture_string:string:expected=object:actual=missing")
    else:
        if string.get("memchr_inv_index") != 4:
            mismatches.append(f"phase1_fixture_string:memchr_inv_index:expected=4:actual={string.get('memchr_inv_index')!r}")
        if string.get("memchr_inv_none") is not True:
            mismatches.append("phase1_fixture_string:memchr_inv_none")
    rbtree = fixture.get("rbtree")
    if not isinstance(rbtree, dict):
        mismatches.append("phase1_fixture_rbtree:rbtree:expected=object:actual=missing")
    else:
        for field in ("find_found_key", "find_missing", "find_first_serial", "next_match_serials"):
            if field not in rbtree:
                mismatches.append(f"phase1_fixture_rbtree:{field}:expected=present:actual=missing")
        if rbtree.get("next_match_terminal_null") is not True:
            mismatches.append("phase1_fixture_rbtree:next_match_terminal_null")
    return mismatches

def collect_phase1_manifest_review_mismatches(root: Path) -> list[str]:
    manifest = json.loads((root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json").read_text(encoding="utf-8"))
    mismatches: list[str] = []
    if manifest.get("phase") != "Phase 1":
        mismatches.append("phase1_manifest:phase")
    if manifest.get("status") != "closed":
        mismatches.append("phase1_manifest:status")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        mismatches.append("phase1_manifest:helpers")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        mismatches.append("phase1_manifest:helper_count")
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return mismatches + ["phase1_manifest:review_anchors"]
    for helper, expected_fields in EXPECTED_MANIFEST_HELPER_FIELDS.items():
        helper_review = review_anchors.get(helper)
        if not isinstance(helper_review, dict):
            mismatches.append(f"phase1_manifest_review_anchor:missing_helper={helper}")
            continue
        for field, expected in expected_fields.items():
            actual = helper_review.get(field)
            if isinstance(expected, list):
                if not isinstance(actual, list):
                    mismatches.append(f"phase1_manifest_review_anchor:value={helper}:{field}")
                    continue
                for item in expected:
                    if item not in actual:
                        mismatches.append(f"phase1_manifest_review_anchor:value={helper}:{field}:{item}")
            elif actual != expected:
                mismatches.append(f"phase1_manifest_review_anchor:value={helper}:{field}")
    return mismatches

def collect_missing_markers(root: Path) -> list[str]:
    docs_readme = (root / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
    phase1_helpers = (root / "zigux" / "tests" / "phase1_helpers.zig").read_text(encoding="utf-8")
    missing: list[str] = []
    for label, markers in DOC_MARKERS.items():
        text = {"docs_root_phase1_packet": docs_readme, "tests_root_phase1_packet": tests_readme, "review_checklist_phase1_packet": review_checklist}[label]
        missing.extend(collect_marker_counts(text, label, markers))
    missing.extend(collect_marker_counts(phase1_helpers, "phase1_import_marker", PHASE1_IMPORT_MARKERS))
    missing.extend(collect_marker_counts(phase1_helpers, "helper_test_anchor", HELPER_FOLLOWUP_TESTS))
    replay_body = extract_test_body(phase1_helpers, "phase 1 helper ports match committed parity fixture")
    if replay_body is None:
        missing.append('phase1_parity_test:test "phase 1 helper ports match committed parity fixture":expected=1:actual=0')
    else:
        missing.extend(collect_presence_markers(replay_body, "phase1_parity_replay_marker", PHASE1_REPLAY_MARKERS))
    for label, (path, markers) in SOURCE_MARKERS.items():
        text = (root / path).read_text(encoding="utf-8")
        missing.extend(collect_marker_counts(text, label, markers))
    missing.extend(collect_phase1_fixture_mismatches(root))
    missing.extend(collect_phase1_manifest_review_mismatches(root))
    return missing

def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith(".json"):
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("\n", encoding="utf-8")

def run_self_test() -> None:
    test_text = (
        'test "phase 1 helper ports match committed parity fixture" {\n'
        'fixture.bitmap.partial_xor_nbits\n'
        'bitmap.lastWordMask(fixture.bitmap.partial_xor_nbits)\n'
        'fixture.bitmap.partial_xor_masked_values\n'
        'fixture.string.replace_char\n'
        'fixture.string.replace_char_end\n'
        'fixture.string.replace_char_cstr_end\n'
        'fixture.string.replace_char_cstr_bytes\n'
        'fixture.string.memchr_inv_index\n'
        'fixture.string.memchr_inv_none\n'
        'fixture.rbtree.find_found_key\n'
        'fixture.rbtree.find_missing\n'
        'fixture.rbtree.find_first_serial\n'
        'fixture.rbtree.next_match_serials\n'
        'fixture.rbtree.next_match_terminal_null\n'
        '}\n\n'
        'test "phase 1 string replaceChar stops at embedded NUL" {\n}\n'
    )
    replay = extract_test_body(test_text, "phase 1 helper ports match committed parity fixture")
    assert replay is not None
    assert not collect_presence_markers(replay, "phase1_parity_replay_marker", ["fixture.bitmap.partial_xor_nbits","fixture.bitmap.partial_xor_masked_values","fixture.string.replace_char","fixture.string.replace_char_end","fixture.string.replace_char_cstr_end","fixture.string.replace_char_cstr_bytes","fixture.string.memchr_inv_index","fixture.string.memchr_inv_none","fixture.rbtree.find_found_key","fixture.rbtree.find_missing","fixture.rbtree.find_first_serial","fixture.rbtree.next_match_serials","fixture.rbtree.next_match_terminal_null"])
    assert extract_test_body(test_text, "missing") is None
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        make_fixture_root(tmp_root)
        (tmp_root / "Documentation" / "zigux" / "README.md").write_text(DOC_MARKERS["docs_root_phase1_packet"][0] + "\n" + DOC_MARKERS["docs_root_phase1_packet"][1] + "\n", encoding="utf-8")
        (tmp_root / "zigux" / "tests" / "README.md").write_text(DOC_MARKERS["tests_root_phase1_packet"][0] + "\n" + DOC_MARKERS["tests_root_phase1_packet"][1] + "\n", encoding="utf-8")
        (tmp_root / "Documentation" / "zigux" / "review-checklist.md").write_text(DOC_MARKERS["review_checklist_phase1_packet"][0] + "\n" + DOC_MARKERS["review_checklist_phase1_packet"][1] + "\n", encoding="utf-8")
        (tmp_root / "tools" / "lib" / "bitmap.zig").write_text('\n'.join(SOURCE_MARKERS["bitmap_test_anchor"][1]) + '\n', encoding="utf-8")
        (tmp_root / "tools" / "lib" / "find_bit.zig").write_text('\n'.join(SOURCE_MARKERS["find_bit_test_anchor"][1]) + '\n', encoding="utf-8")
        (tmp_root / "tools" / "lib" / "string.zig").write_text('\n'.join(SOURCE_MARKERS["string_test_anchor"][1]) + '\n', encoding="utf-8")
        (tmp_root / "tools" / "lib" / "rbtree.zig").write_text('\n'.join(SOURCE_MARKERS["rbtree_test_anchor"][1]) + '\n', encoding="utf-8")
        (tmp_root / "zigux" / "tests" / "phase1_helpers.zig").write_text('\n'.join(PHASE1_IMPORT_MARKERS) + '\n' + 'test "phase 1 helper ports match committed parity fixture" {\n' + '\n'.join(PHASE1_REPLAY_MARKERS) + '\n}\n' + '\n'.join(HELPER_FOLLOWUP_TESTS) + '\n', encoding="utf-8")
        (tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json").write_text(json.dumps({"argv_split": {},"bitmap": {"partial_xor_nbits": 4, "partial_xor_masked_values": [14]},"cmdline": {},"ctype": {},"find_bit": {"bits_per_long": 64,"tail_clamped_first": 69,"tail_clamped_next": 69,"tail_zero_clamped_first": 69,"tail_zero_clamped_next": 69,"tail_and_clamped_first": 69,"tail_and_clamped_next": 69},"hweight": {},"list_sort": {},"rbtree": {"find_found_key": 41,"find_missing": True,"find_first_serial": 3,"next_match_serials": [3, 4],"next_match_terminal_null": True},"slab": {},"str_error_r": {},"string": {"replace_char": "a_b","replace_char_end": 3,"replace_char_cstr_end": 2,"replace_char_cstr_bytes": [97, 95, 0, 45, 122],"memchr_inv_index": 4,"memchr_inv_none": True},"vsprintf": {},"zalloc": {}}, separators=(",", ":")), encoding="utf-8")
        (tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json").write_text(json.dumps({"phase": "Phase 1","status": "closed","helper_count": len(EXPECTED_HELPERS),"helpers": EXPECTED_HELPERS,"review_anchors": EXPECTED_MANIFEST_HELPER_FIELDS}, indent=2) + "\n", encoding="utf-8")
        assert not collect_missing_markers(tmp_root)
    print("PHASE1_VALIDATION_SELF_TEST=pass")
    print("PHASE1_VALIDATION_SELF_TEST_CASE_COUNT=5")

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 helper packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    missing = collect_missing_files(ROOT)
    if missing:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_FILES_END")
        return 1
    missing_markers = collect_missing_markers(ROOT)
    if missing_markers:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_MARKERS_END")
        return 1
    print("PHASE1_VALIDATION=pass")
    print(f"PHASE1_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE1_REQUIRED_MARKER_COUNT=" f"{sum(len(markers) for markers in DOC_MARKERS.values()) + len(PHASE1_IMPORT_MARKERS) + len(PHASE1_REPLAY_MARKERS) + len(HELPER_FOLLOWUP_TESTS) + sum(len(markers) for _, markers in SOURCE_MARKERS.values())}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
