#!/usr/bin/env python3
"""Guard the Phase 1 bitmap helper-anchor packet against manifest and helper drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_BITMAP_HELPER_TEST_ANCHORS = [
    'test "bitmap set clear weight and empty full helpers"',
    'test "bitmap range helpers preserve edges across whole-word spans"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy and extend handles zero and aligned counts"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap and andnot equal intersects subset"',
    'test "bitmap tail-masked helpers ignore out-of-range differences"',
    'test "bitmap full empty and weight ignore out-of-range tail bits"',
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
    'test "bitmap scnprintf collapses contiguous ranges"',
    'test "bitmap scnprintf truncates and keeps a terminator slot"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap allocation helpers size zero fill and reset optionals"',
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (BITMAP_HELPER_REL, MANIFEST_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, BITMAP_HELPER_REL)
    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict"]

    bitmap_packet = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_packet, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:expected=dict"]

    helper_test_anchors = bitmap_packet.get("helper_test_anchors")
    if helper_test_anchors != EXPECTED_BITMAP_HELPER_TEST_ANCHORS:
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig.helper_test_anchors:expected_current_packet"]

    for anchor in EXPECTED_BITMAP_HELPER_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(
                helper_text,
                f"{BITMAP_HELPER_REL.as_posix()}:helper_test_anchor",
                anchor,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        BITMAP_HELPER_REL,
        "\n".join(EXPECTED_BITMAP_HELPER_TEST_ANCHORS) + "\n",
    )
    write_file(
        root,
        MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/bitmap.zig": {
                        "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
                    }
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-anchor-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1

    mutation_specs = [
        ("helper_anchor_removed", "helper_anchor", "remove"),
        ("helper_anchor_duplicated", "helper_anchor", "duplicate"),
        ("manifest_anchor_list_mutated", "manifest", "mutate"),
        ("bitmap_helper_missing", "bitmap_helper", "missing_file"),
        ("manifest_missing", "manifest_file", "missing_file"),
    ]

    for name, target, operation in mutation_specs:
        with tempfile.TemporaryDirectory(prefix=f"phase1-bitmap-anchor-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if operation == "remove":
                path = root / BITMAP_HELPER_REL
                marker = EXPECTED_BITMAP_HELPER_TEST_ANCHORS[0]
                text = path.read_text(encoding="utf-8")
                path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")
            elif operation == "duplicate":
                path = root / BITMAP_HELPER_REL
                marker = EXPECTED_BITMAP_HELPER_TEST_ANCHORS[0]
                text = path.read_text(encoding="utf-8")
                path.write_text(text.replace(marker + "\n", marker + "\n" + marker + "\n", 1), encoding="utf-8")
            elif operation == "mutate":
                path = root / MANIFEST_REL
                manifest = json.loads(path.read_text(encoding="utf-8"))
                manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"] = ["drift"]
                path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            elif operation == "missing_file":
                if target == "bitmap_helper":
                    (root / BITMAP_HELPER_REL).unlink()
                else:
                    (root / MANIFEST_REL).unlink()

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-bitmap-helper-anchors:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
