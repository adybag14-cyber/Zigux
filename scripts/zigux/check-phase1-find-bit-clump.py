#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
if SELF_PATH.parent.name == "zigux" and SELF_PATH.parent.parent.name == "scripts":
    ROOT = SELF_PATH.parents[2]
else:
    ROOT = SELF_PATH.parent

TARGET = Path("tools/lib/find_bit.zig")
MANIFEST = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FUNCTION_MARKERS = {
    "find_next_clump8": "pub fn findNextClump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
    "find_next_clump8_alias": "pub fn find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
    "find_next_clump8_underscore": "pub fn _find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
    "find_first_clump8": "pub fn findFirstClump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
    "find_first_clump8_alias": "pub fn find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
    "find_first_clump8_underscore": "pub fn _find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
}

REQUIRED_TEST_MARKERS = {
    "byte_alignment": 'test "clump8 scans align to the containing byte and return its value" {',
    "tail_reachable": 'test "clump8 scans keep tail bytes reachable from partial final words" {',
    "tail_mask": 'test "clump8 scans mask tail bits beyond nbits" {',
    "no_match_preserves_byte": 'test "clump8 scans leave the caller byte untouched when no set bit remains" {',
}

REQUIRED_ALIAS_EXPECTATIONS = {
    "underscore_first": "try std.testing.expectEqual(@as(usize, 0), _find_first_clump8(&clump, &clump_map, 8));",
    "underscore_next": "try std.testing.expectEqual(@as(usize, 0), _find_next_clump8(&clump, &clump_map, 8, 0));",
    "linux_first": "try std.testing.expectEqual(@as(usize, 0), find_first_clump8(&clump, &[_]Word{@as(Word, 1)}, 8));",
    "linux_next": "try std.testing.expectEqual(@as(usize, 0), find_next_clump8(&clump, &[_]Word{@as(Word, 1)}, 8, 0));",
}

REQUIRED_MANIFEST_SUMMARY_FRAGMENTS = (
    "clump8",
    "getValue8()",
    "findLastBit()",
)


def validate_exact_lines(section: str, text: str, markers: dict[str, str]) -> list[str]:
    failures: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for label, marker in markers.items():
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            failures.append(f"{section}:{label}:expected=1:actual={count}")
    return failures


def validate_manifest(root: Path) -> list[str]:
    path = root / MANIFEST
    if not path.exists():
        return [f"missing_file:{MANIFEST.as_posix()}"]

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid_json:{MANIFEST.as_posix()}:{exc.lineno}:{exc.colno}:{exc.msg}"]

    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"manifest:review_anchors:expected=dict:actual={type(review_anchors).__name__}"]

    find_bit_anchor = review_anchors.get(TARGET.as_posix())
    if not isinstance(find_bit_anchor, dict):
        return [f"manifest:{TARGET.as_posix()}:expected=dict:actual={type(find_bit_anchor).__name__}"]

    helper_test_anchors = find_bit_anchor.get("helper_test_anchors")
    if not isinstance(helper_test_anchors, list):
        return [
            "manifest:helper_test_anchors:expected=list:actual="
            f"{type(helper_test_anchors).__name__}"
        ]

    failures: list[str] = []
    for label, marker in REQUIRED_TEST_MARKERS.items():
        count = sum(1 for current in helper_test_anchors if current == marker.removesuffix(" {"))
        if count != 1:
            failures.append(f"manifest:helper_test_anchors:{label}:expected=1:actual={count}")

    review_packet_summary = find_bit_anchor.get("review_packet_summary")
    if not isinstance(review_packet_summary, str):
        failures.append(
            "manifest:review_packet_summary:expected=str:actual="
            f"{type(review_packet_summary).__name__}"
        )
    else:
        for fragment in REQUIRED_MANIFEST_SUMMARY_FRAGMENTS:
            if fragment not in review_packet_summary:
                failures.append(f"manifest:review_packet_summary:missing={fragment}")

    next_safe_step_note = find_bit_anchor.get("next_safe_step_note")
    if not isinstance(next_safe_step_note, str):
        failures.append(
            "manifest:next_safe_step_note:expected=str:actual="
            f"{type(next_safe_step_note).__name__}"
        )
    else:
        for fragment in REQUIRED_MANIFEST_SUMMARY_FRAGMENTS:
            if fragment not in next_safe_step_note:
                failures.append(f"manifest:next_safe_step_note:missing={fragment}")

    return failures


def validate(root: Path) -> list[str]:
    path = root / TARGET
    if not path.exists():
        return [f"missing_file:{TARGET.as_posix()}"]

    text = path.read_text(encoding="utf-8")
    missing: list[str] = []
    missing.extend(validate_exact_lines("function", text, REQUIRED_FUNCTION_MARKERS))
    missing.extend(validate_exact_lines("test", text, REQUIRED_TEST_MARKERS))
    missing.extend(validate_exact_lines("alias", text, REQUIRED_ALIAS_EXPECTATIONS))
    missing.extend(validate_manifest(root))
    return missing


def build_manifest_fixture() -> str:
    clump_tests = [marker.removesuffix(" {") for marker in REQUIRED_TEST_MARKERS.values()]
    manifest = {
        "review_anchors": {
            TARGET.as_posix(): {
                "helper_test_anchors": clump_tests,
                "review_packet_summary": (
                    "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, "
                    "while helper-local anchors keep same-word start-mask, clump8, "
                    "getValue8(), and findLastBit() review-visible on current master"
                ),
                "next_safe_step_note": (
                    "If this helper lane reopens, keep find_bit parked unless a fresh reread "
                    "finds direct-anchor drift inside clump8, getValue8(), or findLastBit()."
                ),
            }
        }
    }
    return json.dumps(manifest, indent=2) + "\n"


def build_fixture(root: Path) -> None:
    (root / TARGET.parent).mkdir(parents=True, exist_ok=True)
    (root / MANIFEST.parent).mkdir(parents=True, exist_ok=True)
    lines = [
        "pub fn findNextClump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
        "    _ = clump;",
        "    _ = addr;",
        "    _ = nbits;",
        "    _ = offset;",
        "    return 0;",
        "}",
        "",
        "pub fn find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
        "    return findNextClump8(clump, addr, nbits, offset);",
        "}",
        "",
        "pub fn _find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
        "    return findNextClump8(clump, addr, nbits, offset);",
        "}",
        "",
        "pub fn findFirstClump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
        "    return findNextClump8(clump, addr, nbits, 0);",
        "}",
        "",
        "pub fn find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
        "    return findFirstClump8(clump, addr, nbits);",
        "}",
        "",
        "pub fn _find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
        "    return findFirstClump8(clump, addr, nbits);",
        "}",
        "",
        'test "clump8 scans align to the containing byte and return its value" {',
        "}",
        "",
        'test "clump8 scans keep tail bytes reachable from partial final words" {',
        "}",
        "",
        'test "clump8 scans mask tail bits beyond nbits" {',
        "}",
        "",
        'test "clump8 scans leave the caller byte untouched when no set bit remains" {',
        "}",
        "",
        "try std.testing.expectEqual(@as(usize, 0), _find_first_clump8(&clump, &clump_map, 8));",
        "try std.testing.expectEqual(@as(usize, 0), _find_next_clump8(&clump, &clump_map, 8, 0));",
        "try std.testing.expectEqual(@as(usize, 0), find_first_clump8(&clump, &[_]Word{@as(Word, 1)}, 8));",
        "try std.testing.expectEqual(@as(usize, 0), find_next_clump8(&clump, &[_]Word{@as(Word, 1)}, 8, 0));",
    ]
    (root / TARGET).write_text("\n".join(lines) + "\n", encoding="utf-8")
    (root / MANIFEST).write_text(build_manifest_fixture(), encoding="utf-8")


def run_self_test() -> int:
    cases = [
        ("missing_file", "missing_file:tools/lib/find_bit.zig"),
        ("missing_manifest", "missing_file:zigux/tests/fixtures/phase1_helper_manifest.json"),
        ("missing_test", "test:tail_mask:expected=1:actual=0"),
        ("missing_alias_expectation", "alias:linux_next:expected=1:actual=0"),
        ("missing_function", "function:find_first_clump8_underscore:expected=1:actual=0"),
        ("missing_manifest_anchor", "manifest:helper_test_anchors:tail_mask:expected=1:actual=0"),
        ("missing_manifest_summary", "manifest:review_packet_summary:missing=findLastBit()"),
        ("missing_manifest_next_step", "manifest:next_safe_step_note:missing=getValue8()"),
        ("duplicate_test", "test:tail_mask:expected=1:actual=2"),
        ("duplicate_manifest_anchor", "manifest:helper_test_anchors:tail_mask:expected=1:actual=2"),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_clump_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        if validate(tmp_root) != [cases[0][1]]:
            raise SystemExit("phase1-find-bit-clump:self-test:missing_file")

        build_fixture(tmp_root)
        (tmp_root / MANIFEST).unlink()
        if cases[1][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_manifest")

        build_fixture(tmp_root)
        if validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:baseline")

        text = (tmp_root / TARGET).read_text(encoding="utf-8")

        (tmp_root / TARGET).writeText if False else None
        (tmp_root / TARGET).write_text(
            text.replace(REQUIRED_TEST_MARKERS["tail_mask"] + "\n", "", 1),
            encoding="utf-8",
        )
        if cases[2][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_test")

        build_fixture(tmp_root)
        text = (tmp_root / TARGET).read_text(encoding="utf-8")
        (tmp_root / TARGET).write_text(
            text.replace(REQUIRED_ALIAS_EXPECTATIONS["linux_next"] + "\n", "", 1),
            encoding="utf-8",
        )
        if cases[3][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_alias")

        build_fixture(tmp_root)
        text = (tmp_root / TARGET).read_text(encoding="utf-8")
        (tmp_root / TARGET).write_text(
            text.replace(REQUIRED_FUNCTION_MARKERS["find_first_clump8_underscore"] + "\n", "", 1),
            encoding="utf-8",
        )
        if cases[4][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_function")

        build_fixture(tmp_root)
        anchor = REQUIRED_TEST_MARKERS["tail_mask"].removesuffix(" {")
        manifest = json.loads((tmp_root / MANIFEST).read_text(encoding="utf-8"))
        helper_anchors = manifest["review_anchors"][TARGET.as_posix()]["helper_test_anchors"]
        helper_anchors.remove(anchor)
        (tmp_root / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if cases[5][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_manifest_anchor")

        build_fixture(tmp_root)
        manifest_text = (tmp_root / MANIFEST).read_text(encoding="utf-8")
        (tmp_root / MANIFEST).write_text(
            manifest_text.replace("findLastBit()", "findLastBit", 1),
            encoding="utf-8",
        )
        if cases[6][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_manifest_summary")

        build_fixture(tmp_root)
        manifest_text = (tmp_root / MANIFEST).read_text(encoding="utf-8")
        last_occurrence = manifest_text.rfind("getValue8()")
        (tmp_root / MANIFEST).write_text(
            manifest_text[:last_occurrence] + "getValue8" + manifest_text[last_occurrence + len("getValue8()"):],
            encoding="utf-8",
        )
        if cases[7][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_manifest_next_step")

        build_fixture(tmp_root)
        text = (tmp_root / TARGET).read_text(encoding="utf-8")
        (tmp_root / TARGET).write_text(
            text.replace(
                REQUIRED_TEST_MARKERS["tail_mask"],
                REQUIRED_TEST_MARKERS["tail_mask"] + "\n" + REQUIRED_TEST_MARKERS["tail_mask"],
                1,
            ),
            encoding="utf-8",
        )
        if cases[8][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:duplicate_test")

        build_fixture(tmp_root)
        manifest = json.loads((tmp_root / MANIFEST).read_text(encoding="utf-8"))
        helper_anchors = manifest["review_anchors"][TARGET.as_posix()]["helper_test_anchors"]
        helper_anchors.append(anchor)
        (tmp_root / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if cases[9][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:duplicate_manifest_anchor")

    print("PHASE1_FIND_BIT_CLUMP_SELF_TEST=pass")
    print("PHASE1_FIND_BIT_CLUMP_SELF_TEST_CASE_COUNT=10")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return run_self_test()

    missing = validate(ROOT)
    if missing:
        print("PHASE1_FIND_BIT_CLUMP_VALIDATION=fail")
        print("MISSING_PHASE1_FIND_BIT_CLUMP_MARKERS_START")
        for marker in missing:
            print(marker)
        print("MISSING_PHASE1_FIND_BIT_CLUMP_MARKERS_END")
        return 1

    print("PHASE1_FIND_BIT_CLUMP_VALIDATION=pass")
    print(f"PHASE1_FIND_BIT_CLUMP_FUNCTION_MARKER_COUNT={len(REQUIRED_FUNCTION_MARKERS)}")
    print(f"PHASE1_FIND_BIT_CLUMP_TEST_MARKER_COUNT={len(REQUIRED_TEST_MARKERS)}")
    print(f"PHASE1_FIND_BIT_CLUMP_ALIAS_MARKER_COUNT={len(REQUIRED_ALIAS_EXPECTATIONS)}")
    print(f"PHASE1_FIND_BIT_CLUMP_MANIFEST_FRAGMENT_COUNT={len(REQUIRED_MANIFEST_SUMMARY_FRAGMENTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())