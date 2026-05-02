#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
if SELF_PATH.parent.name == "zigux" and SELF_PATH.parent.parent.name == "scripts":
    ROOT = SELF_PATH.parents[2]
else:
    ROOT = SELF_PATH.parent


MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_REL = Path("tools/lib/bitmap.zig")
BITMAP_NOTE_KEY = "tools/lib/bitmap.zig"

EXPECTED_BITMAP_REVIEW_FIELDS = {
    "header_alias_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap header-style aliases preserve zero fill copy and predicate semantics"',
    "header_alias_unit_test_contract": (
        "Direct Zig unit coverage keeps bitmap_zero(), bitmap_fill(), bitmap_copy(), "
        "bitmap_empty(), and bitmap_full() aligned with zero(), fill(), copy(), empty(), "
        "and full() for active-word clearing, partial-tail fill masking, copied-tail "
        "preservation, and predicate results across the same declared bit window."
    ),
    "empty_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    "empty_unit_test_contract": (
        "Direct Zig unit coverage keeps bitmap_scnprintf() from mutating a non-empty caller "
        "buffer when no bits are set, matching the committed empty-bitmap parity fixture contract."
    ),
}

EXPECTED_BITMAP_SOURCE_MARKERS = [
    'test "bitmap header-style aliases preserve zero fill copy and predicate semantics"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(block: str, items: list[str]) -> int:
    print("PHASE1_BITMAP_REVIEW_SURFACE=fail")
    print(f"{block}_START")
    for item in items:
        print(item)
    print(f"{block}_END")
    return 1


def validate_tree(root: Path) -> tuple[int, list[str]]:
    missing: list[str] = []

    manifest_path = root / MANIFEST_REL
    bitmap_path = root / BITMAP_REL

    if not manifest_path.exists():
        missing.append(f"file:{MANIFEST_REL.as_posix()}")
    if not bitmap_path.exists():
        missing.append(f"file:{BITMAP_REL.as_posix()}")
    if missing:
        return 1, missing

    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        return 1, ["manifest:expected_object"]

    review_notes = manifest.get("helper_review_notes")
    if not isinstance(review_notes, dict):
        missing.append("manifest:helper_review_notes:expected_object")
        return 1, missing

    bitmap_note = review_notes.get(BITMAP_NOTE_KEY)
    if not isinstance(bitmap_note, dict):
        missing.append(f"manifest:{BITMAP_NOTE_KEY}:expected_object")
        return 1, missing

    for key, expected in EXPECTED_BITMAP_REVIEW_FIELDS.items():
        if bitmap_note.get(key) != expected:
            missing.append(f"manifest:{BITMAP_NOTE_KEY}:{key}")

    bitmap_text = bitmap_path.read_text(encoding="utf-8")
    for marker in EXPECTED_BITMAP_SOURCE_MARKERS:
        if marker not in bitmap_text:
            missing.append(f"bitmap_source:{marker}")

    return (1 if missing else 0), missing


def write_fixture_tree(root: Path) -> None:
    (root / MANIFEST_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / BITMAP_REL.parent).mkdir(parents=True, exist_ok=True)

    manifest = {
        "helper_review_notes": {
            BITMAP_NOTE_KEY: dict(EXPECTED_BITMAP_REVIEW_FIELDS),
        }
    }
    manifest_path = root / MANIFEST_REL
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    bitmap_text = "\n".join(
        [
            EXPECTED_BITMAP_SOURCE_MARKERS[0],
            EXPECTED_BITMAP_SOURCE_MARKERS[1],
            "",
        ]
    )
    (root / BITMAP_REL).write_text(bitmap_text, encoding="utf-8")


def expect_missing(label: str, root: Path, expected: str) -> None:
    code, missing = validate_tree(root)
    if code == 0:
        raise SystemExit(f"phase1-bitmap-review-self-test:{label}:unexpected_pass")
    if expected not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase1-bitmap-review-self-test:{label}:expected_missing:{expected}:actual:{actual}"
        )


def run_self_test() -> int:
    total_cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bitmap_review_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        code, missing = validate_tree(tmp_root)
        if code != 0:
            raise SystemExit(
                f"phase1-bitmap-review-self-test:baseline_failed:{','.join(missing)}"
            )

        manifest_path = tmp_root / MANIFEST_REL
        manifest = load_json(manifest_path)
        assert isinstance(manifest, dict)

        mutated = json.loads(json.dumps(manifest))
        mutated["helper_review_notes"][BITMAP_NOTE_KEY]["empty_unit_test_anchor"] = ""
        manifest_path.write_text(json.dumps(mutated, indent=2) + "\n", encoding="utf-8")
        expect_missing(
            "manifest_empty_anchor",
            tmp_root,
            f"manifest:{BITMAP_NOTE_KEY}:empty_unit_test_anchor",
        )
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        total_cases += 1

        mutated = json.loads(json.dumps(manifest))
        mutated["helper_review_notes"][BITMAP_NOTE_KEY]["header_alias_unit_test_contract"] = ""
        manifest_path.write_text(json.dumps(mutated, indent=2) + "\n", encoding="utf-8")
        expect_missing(
            "manifest_header_alias_contract",
            tmp_root,
            f"manifest:{BITMAP_NOTE_KEY}:header_alias_unit_test_contract",
        )
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        total_cases += 1

        bitmap_path = tmp_root / BITMAP_REL
        bitmap_path.write_text(
            EXPECTED_BITMAP_SOURCE_MARKERS[1] + "\n",
            encoding="utf-8",
        )
        expect_missing(
            "bitmap_source_header_alias",
            tmp_root,
            f"bitmap_source:{EXPECTED_BITMAP_SOURCE_MARKERS[0]}",
        )
        bitmap_path.write_text(
            "\n".join(EXPECTED_BITMAP_SOURCE_MARKERS) + "\n",
            encoding="utf-8",
        )
        total_cases += 1

    print("PHASE1_BITMAP_REVIEW_SURFACE_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_REVIEW_SURFACE_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the parked Phase 1 bitmap review-surface manifest and source anchors."
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    code, missing = validate_tree(ROOT)
    if code != 0:
        return fail("MISSING_PHASE1_BITMAP_REVIEW_SURFACE", missing)

    print("PHASE1_BITMAP_REVIEW_SURFACE=pass")
    print(f"PHASE1_BITMAP_REVIEW_SURFACE_MARKER_COUNT={len(EXPECTED_BITMAP_REVIEW_FIELDS) + len(EXPECTED_BITMAP_SOURCE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
