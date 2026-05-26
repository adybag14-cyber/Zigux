#!/usr/bin/env python3
"""Guard the Phase 1 bitmap complement-tail closure packet against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")

EXPECTED_HELPER_TEST_MARKER = (
    'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched" {'
)
EXPECTED_HELPER_ASSERT_MARKER = (
    "try std.testing.expectEqual((~src[1]) & lastWordMask(nbits), direct[1]);"
)
EXPECTED_HELPER_ALIAS_MARKER = "bitmap_complement(&alias, &src, nbits);"

EXPECTED_MANIFEST_ANCHOR = EXPECTED_HELPER_TEST_MARKER[:-2] + '"'
EXPECTED_MANIFEST_SUMMARY = (
    "helper-local complement-tail masking stays explicit through the direct bitmap tests because "
    "the shared Phase 1 replay still does not carry a dedicated complement-tail fixture field, "
    "so partial-tail masking and zero-sized caller-view no-op behavior remain review-visible at "
    "the helper surface"
)

CLOSURE_MARKER_PREFIX = "`PHASE1_BITMAP_DIRECT_REVIEW="
CLOSURE_REQUIRED_FRAGMENT = "complement-tail masking"


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_helper(text: str) -> list[str]:
    failures: list[str] = []
    for label, marker in (
        ("helper_test_marker", EXPECTED_HELPER_TEST_MARKER),
        ("helper_assert_marker", EXPECTED_HELPER_ASSERT_MARKER),
        ("helper_alias_marker", EXPECTED_HELPER_ALIAS_MARKER),
    ):
        count = text.count(marker)
        if count != 1:
            failures.append(f"{label}:expected=1:actual={count}")
    return failures


def validate_manifest(text: str) -> list[str]:
    failures: list[str] = []
    data = json.loads(text)
    review_anchors = data.get("review_anchors", {})
    bitmap = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap, dict):
        return ["manifest_bitmap_review_anchors:expected=dict"]

    if bitmap.get("complement_tail_anchor") != EXPECTED_MANIFEST_ANCHOR:
        failures.append(
            "manifest_complement_tail_anchor:"
            f"expected={EXPECTED_MANIFEST_ANCHOR!r}:actual={bitmap.get('complement_tail_anchor')!r}"
        )
    if bitmap.get("complement_tail_review_summary") != EXPECTED_MANIFEST_SUMMARY:
        failures.append(
            "manifest_complement_tail_review_summary:"
            f"expected={EXPECTED_MANIFEST_SUMMARY!r}:actual={bitmap.get('complement_tail_review_summary')!r}"
        )
    return failures


def validate_closure(text: str) -> list[str]:
    failures: list[str] = []
    marker_count = text.count(CLOSURE_MARKER_PREFIX)
    if marker_count != 1:
        failures.append(f"closure_bitmap_direct_review_marker:expected=1:actual={marker_count}")
        return failures

    line = next(
        (line for line in text.splitlines() if line.startswith(CLOSURE_MARKER_PREFIX)),
        "",
    )
    if CLOSURE_REQUIRED_FRAGMENT not in line:
        failures.append(
            "closure_bitmap_direct_review_fragment_missing:"
            f"required={CLOSURE_REQUIRED_FRAGMENT!r}"
        )
    return failures


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_files = (BITMAP_HELPER_REL, MANIFEST_REL, CLOSURE_REL)
    for rel in required_files:
        if not (root / rel).is_file():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    failures.extend(validate_helper(load_text(root / BITMAP_HELPER_REL)))
    failures.extend(validate_manifest(load_text(root / MANIFEST_REL)))
    failures.extend(validate_closure(load_text(root / CLOSURE_REL)))
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    helper_text = "\n".join(
        [
            EXPECTED_HELPER_TEST_MARKER,
            EXPECTED_HELPER_ALIAS_MARKER,
            EXPECTED_HELPER_ASSERT_MARKER,
            "}",
            "",
        ]
    )
    manifest = {
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "complement_tail_anchor": EXPECTED_MANIFEST_ANCHOR,
                "complement_tail_review_summary": EXPECTED_MANIFEST_SUMMARY,
            }
        }
    }
    closure_text = "\n".join(
        [
            "# Phase 1 Closure",
            "",
            (
                "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap packet keeps "
                "complement-tail masking review-visible through the closure note`"
            ),
            "",
        ]
    )

    write_text(root / BITMAP_HELPER_REL, helper_text)
    write_text(root / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
    write_text(root / CLOSURE_REL, closure_text)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-complement-tail-") as tmp:
        root = Path(tmp)

        failures = collect_failures(root)
        assert failures == [
            f"missing_file:{BITMAP_HELPER_REL.as_posix()}",
            f"missing_file:{MANIFEST_REL.as_posix()}",
            f"missing_file:{CLOSURE_REL.as_posix()}",
        ], failures
        case_count += 1

        write_sample_root(root)
        failures = collect_failures(root)
        assert failures == [], failures
        case_count += 1

        write_text(
            root / BITMAP_HELPER_REL,
            load_text(root / BITMAP_HELPER_REL).replace(EXPECTED_HELPER_ASSERT_MARKER + "\n", "", 1),
        )
        failures = collect_failures(root)
        assert failures == ["helper_assert_marker:expected=1:actual=0"], failures
        case_count += 1

        write_sample_root(root)
        manifest = json.loads(load_text(root / MANIFEST_REL))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["complement_tail_review_summary"] = "drifted"
        write_text(root / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(root)
        assert len(failures) == 1 and failures[0].startswith(
            "manifest_complement_tail_review_summary:"
        ), failures
        case_count += 1

        write_sample_root(root)
        write_text(
            root / CLOSURE_REL,
            load_text(root / CLOSURE_REL).replace(CLOSURE_REQUIRED_FRAGMENT, "tail wording drift", 1),
        )
        failures = collect_failures(root)
        assert failures == [
            f"closure_bitmap_direct_review_fragment_missing:required={CLOSURE_REQUIRED_FRAGMENT!r}"
        ], failures
        case_count += 1

    print("PHASE1_BITMAP_COMPLEMENT_TAIL_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_COMPLEMENT_TAIL_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument(
        "--write-sample-root",
        help="write a minimal current-like sample tree to the given path",
    )
    parser.add_argument("--self-test", action="store_true", help="run self-test cases")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print(f"PHASE1_BITMAP_COMPLEMENT_TAIL_PACKET_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BITMAP_COMPLEMENT_TAIL_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BITMAP_COMPLEMENT_TAIL_PACKET=pass")
    print(f"PHASE1_BITMAP_COMPLEMENT_TAIL_PACKET_HELPER={BITMAP_HELPER_REL.as_posix()}")
    print(f"PHASE1_BITMAP_COMPLEMENT_TAIL_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_BITMAP_COMPLEMENT_TAIL_PACKET_CLOSURE_NOTE={CLOSURE_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
