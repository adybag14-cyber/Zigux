#!/usr/bin/env python3
"""Guard the current Phase 1 find_bit Linux-style alias review anchors."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/find_bit.zig")

REQUIRED_MARKERS = {
    "linux_alias_mirror_test": 'test "Linux-style aliases mirror the primary find helpers, including andnot" {',
    "linux_next_or_tail_alias_test": 'test "Linux-style next-or aliases clamp tail words and past-end starts" {',
    "linux_clump_tail_alias_test": 'test "Linux-style clump aliases mask tail bytes and preserve exhausted caller bytes" {',
    "linux_find_next_or_tail": "find_next_or_bit(&lhs, &rhs, nbits, bits_per_long + 2)",
    "linux_find_next_or_past_end": "find_next_or_bit(&[_]Word{}, &[_]Word{}, 7, 7)",
    "linux_underscore_next_or_past_end": "_find_next_or_bit(&[_]Word{}, &[_]Word{}, 7, 11)",
    "linux_find_first_clump_tail": "try std.testing.expectEqual(@as(usize, bits_per_long), find_first_clump8(&clump, &bitmap, nbits));",
    "linux_underscore_first_clump_tail": "try std.testing.expectEqual(@as(usize, bits_per_long), _find_first_clump8(&clump, &bitmap, nbits));",
    "linux_find_next_clump_exhausted": "try std.testing.expectEqual(@as(usize, nbits), find_next_clump8(&clump, &bitmap, nbits, bits_per_long + 5));",
    "linux_underscore_next_clump_exhausted": "try std.testing.expectEqual(@as(usize, nbits), _find_next_clump8(&clump, &bitmap, nbits, bits_per_long + 9));",
}


def root(path: str | None) -> Path:
    return Path(path).resolve() if path else ROOT.resolve()


def collect_failures(repo: Path) -> list[str]:
    helper = repo / HELPER_REL
    try:
        source = helper.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_file:{HELPER_REL.as_posix()}"]

    failures: list[str] = []
    for label, marker in REQUIRED_MARKERS.items():
        count = source.count(marker)
        if count != 1:
            failures.append(f"find_bit_alias_anchor:{label}:expected=1:actual={count}")
    return failures


def write_sample(repo: Path, *, omit: str | None = None, duplicate: str | None = None) -> None:
    helper = repo / HELPER_REL
    helper.parent.mkdir(parents=True, exist_ok=True)
    lines = [marker for label, marker in REQUIRED_MARKERS.items() if label != omit]
    if duplicate is not None:
        lines.append(REQUIRED_MARKERS[duplicate])
    helper.write_text("\n".join(lines) + "\n", encoding="utf-8")


def expect_failure(repo: Path, label: str, expected: str) -> None:
    failures = collect_failures(repo)
    if expected not in failures:
        raise SystemExit(f"phase1-find-bit-alias-review:self-test:{label}:failures={failures}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_find_bit_alias_review_") as tmp:
        repo = Path(tmp)
        expect_failure(repo, "missing_helper", f"missing_file:{HELPER_REL.as_posix()}")

        write_sample(repo)
        failures = collect_failures(repo)
        if failures:
            raise SystemExit(f"phase1-find-bit-alias-review:self-test:baseline:failures={failures}")

        write_sample(repo, omit="linux_next_or_tail_alias_test")
        expect_failure(repo, "missing_next_or", "find_bit_alias_anchor:linux_next_or_tail_alias_test:expected=1:actual=0")

        write_sample(repo, omit="linux_find_next_clump_exhausted")
        expect_failure(repo, "missing_clump_exhausted", "find_bit_alias_anchor:linux_find_next_clump_exhausted:expected=1:actual=0")

        write_sample(repo, duplicate="linux_underscore_next_or_past_end")
        expect_failure(repo, "duplicate_alias_call", "find_bit_alias_anchor:linux_underscore_next_or_past_end:expected=1:actual=2")

    print("PHASE1_FIND_BIT_ALIAS_REVIEW_ANCHORS_SELF_TEST=pass")
    print("PHASE1_FIND_BIT_ALIAS_REVIEW_ANCHORS_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_ALIAS_REVIEW_ANCHORS=fail")
        for failure in failures:
            print(failure)
        return 1

    print("phase1-find-bit-alias-review-anchors:ok")
    print(f"PHASE1_FIND_BIT_ALIAS_REVIEW_ANCHORS_HELPER={HELPER_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
