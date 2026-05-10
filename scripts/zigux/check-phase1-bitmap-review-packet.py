#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase1-closure.md",
    "zigux/tests/fixtures/phase1_helpers.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_helpers.zig",
    "tools/lib/bitmap.zig",
]

REQUIRED_CLOSURE_MARKERS = [
    (
        "closure_partial_xor_review_count",
        "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
        1,
    ),
    (
        "closure_scnprintf_review_count",
        "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
        1,
    ),
    (
        "closure_copy_alias_review_count",
        "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
        1,
    ),
    (
        "closure_cross_word_review_count",
        "PHASE1_BITMAP_SCNPRINTF_CROSS_WORD_REVIEW=helper-local bitmap.scnprintf cross-word range-collapse proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so contiguous runs crossing a machine-word boundary still render as one collapsed range instead of splitting at the word edge",
        1,
    ),
    (
        "closure_zero_sized_destination_view_review_count",
        "PHASE1_BITMAP_ZERO_SIZED_DESTINATION_VIEW_REVIEW=helper-local zero-sized destination-view proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so copyClearTail, bitmap_copy_clear_tail, copyAndExtend, and bitmap_copy_and_extend leave zero-sized destination views untouched instead of clearing caller sentinel storage",
        1,
    ),
    (
        "closure_zero_bit_binary_identity_review_count",
        "PHASE1_BITMAP_ZERO_BIT_BINARY_IDENTITY_REVIEW=helper-local bitmap zero-bit binary identity proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so andBits, andNotBits, equal, intersects, and subset keep empty-window identity semantics without treating zero-bit windows as live data",
        1,
    ),
    (
        "closure_linux_alias_review_count",
        "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
        1,
    ),
]

REQUIRED_PHASE1_HELPERS_MARKERS = [
    ("phase1_helpers_partial_xor_nbits_count", "partial_xor_nbits", 2),
    ("phase1_helpers_partial_xor_masked_values_count", "partial_xor_masked_values", 2),
]

REQUIRED_BITMAP_TEST_MARKERS = [
    (
        "bitmap_partial_xor_test_count",
        'test "bitmap xor keeps caller-selected bit window"',
        1,
    ),
    (
        "bitmap_scnprintf_truncation_test_count",
        'test "bitmap scnprintf reports full length while truncating the buffer"',
        1,
    ),
    (
        "bitmap_copy_alias_test_count",
        'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        1,
    ),
    (
        "bitmap_cross_word_scnprintf_test_count",
        'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
        1,
    ),
    (
        "bitmap_zero_sized_destination_view_test_count",
        'test "bitmap copy helpers keep zero-sized destination views untouched"',
        1,
    ),
    (
        "bitmap_zero_bit_binary_identity_test_count",
        'test "bitmap zero-bit binary helpers stay explicit identity operations"',
        1,
    ),
    (
        "bitmap_linux_alias_test_count",
        'test "bitmap Linux-style aliases mirror the primary helper surface"',
        1,
    ),
]

REQUIRED_BITMAP_FIXTURE_KEYS = [
    "partial_xor_nbits",
    "partial_xor_masked_values",
    "scnprintf",
]

REQUIRED_BITMAP_MANIFEST_FIELDS = {
    "cross_word_scnprintf_anchor": 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
    "zero_sized_destination_view_anchor": 'test "bitmap copy helpers keep zero-sized destination views untouched"',
    "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit binary helpers stay explicit identity operations"',
    "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
}

REQUIRED_BITMAP_REVIEW_PACKET_SUMMARY = (
    "shared Phase 1 fixture keys now own bitmap scnprintf output, tiny-buffer, and partial-window xor replay, while helper-local anchors keep allocator sizing and zero-fill behavior, predicate tail-mask, first-word and final-partial range boundaries, cross-word scnprintf collapse, truncation, copy alias, zero-sized destination-view, zero-bit no-op, zero-bit binary identity, and Linux-style alias behavior review-visible on current master"
)


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg is None:
        return DEFAULT_ROOT
    return Path(root_arg).resolve()


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_exact_count_markers(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    missing: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")
    return missing


def load_json_file(path: Path, label: str) -> tuple[object | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [
            f"{label}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"
        ]


def collect_fixture_markers(fixture: object) -> list[str]:
    missing: list[str] = []
    if not isinstance(fixture, dict):
        return ["phase1_helpers_fixture:json_object"]

    bitmap = fixture.get("bitmap")
    if not isinstance(bitmap, dict):
        return ["phase1_helpers_fixture:bitmap_object"]

    for key in REQUIRED_BITMAP_FIXTURE_KEYS:
        if key not in bitmap:
            missing.append(f"phase1_helpers_fixture:missing_bitmap_key={key}")

    partial_xor_nbits = bitmap.get("partial_xor_nbits")
    if not isinstance(partial_xor_nbits, int):
        missing.append("phase1_helpers_fixture:partial_xor_nbits=int")

    partial_xor_masked_values = bitmap.get("partial_xor_masked_values")
    if not isinstance(partial_xor_masked_values, list):
        missing.append("phase1_helpers_fixture:partial_xor_masked_values=list")
    elif partial_xor_masked_values != [14]:
        missing.append("phase1_helpers_fixture:partial_xor_masked_values=[14]")

    scnprintf = bitmap.get("scnprintf")
    if not isinstance(scnprintf, str):
        missing.append("phase1_helpers_fixture:scnprintf=str")
    elif scnprintf != "1-3,7,10-11":
        missing.append("phase1_helpers_fixture:scnprintf=1-3,7,10-11")

    return missing


def collect_manifest_markers(manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["phase1_helper_manifest:json_object"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["phase1_helper_manifest:review_anchors"]

    bitmap_review = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_review, dict):
        return ["phase1_helper_manifest:bitmap_review_anchor_object"]

    missing: list[str] = []
    for field, expected_value in REQUIRED_BITMAP_MANIFEST_FIELDS.items():
        if bitmap_review.get(field) != expected_value:
            missing.append(f"phase1_helper_manifest:{field}")

    if bitmap_review.get("review_packet_summary") != REQUIRED_BITMAP_REVIEW_PACKET_SUMMARY:
        missing.append("phase1_helper_manifest:review_packet_summary")

    return missing


def write_file(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(tmp_root: Path) -> None:
    write_file(
        tmp_root,
        "Documentation/zigux/phase1-closure.md",
        "\n".join(marker for _, marker, _ in REQUIRED_CLOSURE_MARKERS) + "\n",
    )
    write_file(
        tmp_root,
        "zigux/tests/phase1_helpers.zig",
        "partial_xor_nbits\npartial_xor_masked_values\npartial_xor_nbits\npartial_xor_masked_values\n",
    )
    write_file(
        tmp_root,
        "tools/lib/bitmap.zig",
        "\n".join(marker for _, marker, _ in REQUIRED_BITMAP_TEST_MARKERS) + "\n",
    )
    write_file(
        tmp_root,
        "zigux/tests/fixtures/phase1_helpers.json",
        json.dumps(
            {
                "bitmap": {
                    "partial_xor_nbits": 4,
                    "partial_xor_masked_values": [14],
                    "scnprintf": "1-3,7,10-11",
                }
            }
        )
        + "\n",
    )
    write_file(
        tmp_root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/bitmap.zig": {
                        **REQUIRED_BITMAP_MANIFEST_FIELDS,
                        "review_packet_summary": REQUIRED_BITMAP_REVIEW_PACKET_SUMMARY,
                    }
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bitmap_review_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_fixture_root(tmp_root)

        assert collect_missing_files(tmp_root) == []

        closure = (tmp_root / "Documentation/zigux/phase1-closure.md").read_text(encoding="utf-8")
        assert collect_exact_count_markers(closure, REQUIRED_CLOSURE_MARKERS) == []
        assert (
            "closure_copy_alias_review_count:expected=1:actual=0"
            in collect_exact_count_markers(
                closure.replace(REQUIRED_CLOSURE_MARKERS[2][1] + "\n", "", 1),
                REQUIRED_CLOSURE_MARKERS,
            )
        )

        phase1_helpers = (tmp_root / "zigux/tests/phase1_helpers.zig").read_text(encoding="utf-8")
        assert collect_exact_count_markers(phase1_helpers, REQUIRED_PHASE1_HELPERS_MARKERS) == []
        assert (
            "phase1_helpers_partial_xor_masked_values_count:expected=2:actual=1"
            in collect_exact_count_markers(
                phase1_helpers.replace("partial_xor_masked_values", "", 1),
                REQUIRED_PHASE1_HELPERS_MARKERS,
            )
        )

        bitmap = (tmp_root / "tools/lib/bitmap.zig").read_text(encoding="utf-8")
        assert collect_exact_count_markers(bitmap, REQUIRED_BITMAP_TEST_MARKERS) == []
        assert (
            "bitmap_scnprintf_truncation_test_count:expected=1:actual=0"
            in collect_exact_count_markers(
                bitmap.replace(REQUIRED_BITMAP_TEST_MARKERS[1][1] + "\n", "", 1),
                REQUIRED_BITMAP_TEST_MARKERS,
            )
        )

        fixture, fixture_parse_markers = load_json_file(
            tmp_root / "zigux/tests/fixtures/phase1_helpers.json",
            "phase1_helpers_fixture",
        )
        assert fixture_parse_markers == []
        assert collect_fixture_markers(fixture) == []

        write_file(
            tmp_root,
            "zigux/tests/fixtures/phase1_helpers.json",
            json.dumps({"bitmap": {"partial_xor_nbits": 4, "scnprintf": "1-3,7,10-11"}}) + "\n",
        )
        fixture, fixture_parse_markers = load_json_file(
            tmp_root / "zigux/tests/fixtures/phase1_helpers.json",
            "phase1_helpers_fixture",
        )
        assert fixture_parse_markers == []
        assert (
            "phase1_helpers_fixture:missing_bitmap_key=partial_xor_masked_values"
            in collect_fixture_markers(fixture)
        )

        write_file(tmp_root, "zigux/tests/fixtures/phase1_helpers.json", '{"bitmap":\n')
        fixture, fixture_parse_markers = load_json_file(
            tmp_root / "zigux/tests/fixtures/phase1_helpers.json",
            "phase1_helpers_fixture",
        )
        assert fixture is None
        assert (
            "phase1_helpers_fixture:json_decode_error:Expecting value:line=2:column=1"
            in fixture_parse_markers
        )

        manifest, manifest_parse_markers = load_json_file(
            tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json",
            "phase1_helper_manifest",
        )
        assert manifest_parse_markers == []
        assert collect_manifest_markers(manifest) == []

        write_file(
            tmp_root,
            "zigux/tests/fixtures/phase1_helper_manifest.json",
            json.dumps(
                {
                    "review_anchors": {
                        "tools/lib/bitmap.zig": {
                            **{
                                key: value
                                for key, value in REQUIRED_BITMAP_MANIFEST_FIELDS.items()
                                if key != "linux_alias_anchor"
                            },
                            "review_packet_summary": REQUIRED_BITMAP_REVIEW_PACKET_SUMMARY,
                        }
                    }
                },
                indent=2,
            )
            + "\n",
        )
        manifest, manifest_parse_markers = load_json_file(
            tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json",
            "phase1_helper_manifest",
        )
        assert manifest_parse_markers == []
        assert "phase1_helper_manifest:linux_alias_anchor" in collect_manifest_markers(manifest)

        write_file(
            tmp_root,
            "zigux/tests/fixtures/phase1_helper_manifest.json",
            json.dumps(
                {
                    "review_anchors": {
                        "tools/lib/bitmap.zig": {
                            **REQUIRED_BITMAP_MANIFEST_FIELDS,
                            "review_packet_summary": "wrong",
                        }
                    }
                },
                indent=2,
            )
            + "\n",
        )
        manifest, manifest_parse_markers = load_json_file(
            tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json",
            "phase1_helper_manifest",
        )
        assert manifest_parse_markers == []
        assert "phase1_helper_manifest:review_packet_summary" in collect_manifest_markers(manifest)

    print("PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass")
    print("PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT=9")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the helper-local Phase 1 bitmap review packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    parser.add_argument(
        "--root",
        help="Validate an alternate Zigux tree root instead of the checker checkout root.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BITMAP_REVIEW_PACKET=fail")
        print("MISSING_PHASE1_BITMAP_REVIEW_FILES_START")
        for rel in missing_files:
            print(rel)
        print("MISSING_PHASE1_BITMAP_REVIEW_FILES_END")
        return 1

    closure = (root / "Documentation/zigux/phase1-closure.md").read_text(encoding="utf-8")
    phase1_helpers = (root / "zigux/tests/phase1_helpers.zig").read_text(encoding="utf-8")
    bitmap = (root / "tools/lib/bitmap.zig").read_text(encoding="utf-8")
    fixture, fixture_parse_markers = load_json_file(
        root / "zigux/tests/fixtures/phase1_helpers.json",
        "phase1_helpers_fixture",
    )
    manifest, manifest_parse_markers = load_json_file(
        root / "zigux/tests/fixtures/phase1_helper_manifest.json",
        "phase1_helper_manifest",
    )

    missing_markers = collect_exact_count_markers(closure, REQUIRED_CLOSURE_MARKERS)
    missing_markers.extend(
        collect_exact_count_markers(phase1_helpers, REQUIRED_PHASE1_HELPERS_MARKERS)
    )
    missing_markers.extend(collect_exact_count_markers(bitmap, REQUIRED_BITMAP_TEST_MARKERS))
    missing_markers.extend(fixture_parse_markers)
    if fixture is not None:
        missing_markers.extend(collect_fixture_markers(fixture))
    missing_markers.extend(manifest_parse_markers)
    if manifest is not None:
        missing_markers.extend(collect_manifest_markers(manifest))

    if missing_markers:
        print("PHASE1_BITMAP_REVIEW_PACKET=fail")
        print("MISSING_PHASE1_BITMAP_REVIEW_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE1_BITMAP_REVIEW_MARKERS_END")
        return 1

    print("PHASE1_BITMAP_REVIEW_PACKET=pass")
    print(f"PHASE1_BITMAP_REVIEW_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BITMAP_REVIEW_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_MARKERS) + len(REQUIRED_PHASE1_HELPERS_MARKERS) + len(REQUIRED_BITMAP_TEST_MARKERS) + len(REQUIRED_BITMAP_FIXTURE_KEYS) + len(REQUIRED_BITMAP_MANIFEST_FIELDS) + 1}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
