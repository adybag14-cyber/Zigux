#!/usr/bin/env python3
"""Guard the Phase 1 find_bit alias-tail anchors added after closure."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/find_bit.zig")

REQUIRED_ANCHORS = [
    'test "Linux-style next-or aliases clamp tail words and past-end starts"',
    'test "Linux-style clump aliases mask tail bytes and preserve exhausted caller bytes"',
]

REQUIRED_SNIPPETS = [
    "find_next_or_bit(&[_]Word{}, &[_]Word{}, 7, 7)",
    "_find_next_or_bit(&[_]Word{}, &[_]Word{}, 7, 11)",
    "find_next_clump8(&clump, &bitmap, nbits, bits_per_long + 5)",
    "_find_next_clump8(&clump, &bitmap, nbits, bits_per_long + 9)",
]


def root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def collect_failures(repo: Path) -> list[str]:
    helper = repo / HELPER_REL
    if not helper.exists():
        return [f"missing_file:{HELPER_REL.as_posix()}"]

    text = helper.read_text(encoding="utf-8")
    failures: list[str] = []
    for anchor in REQUIRED_ANCHORS:
        count = text.count(anchor)
        if count != 1:
            failures.append(f"find_bit_alias_tail_anchor:{anchor}:expected=1:actual={count}")
    for snippet in REQUIRED_SNIPPETS:
        count = text.count(snippet)
        if count != 1:
            failures.append(f"find_bit_alias_tail_snippet:{snippet}:expected=1:actual={count}")
    return failures


def write_helper(repo: Path, body: str) -> None:
    target = repo / HELPER_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")


def baseline_helper() -> str:
    return "\n".join(REQUIRED_ANCHORS + REQUIRED_SNIPPETS) + "\n"


def expect_failure(repo: Path, label: str, expected: str) -> None:
    failures = collect_failures(repo)
    if expected not in failures:
        raise SystemExit(f"phase1-find-bit-alias-tail:self-test:{label}:missing={expected}:failures={failures}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_alias_tail_") as tmp:
        repo = Path(tmp)
        expect_failure(repo, "missing_helper", f"missing_file:{HELPER_REL.as_posix()}")

        write_helper(repo, baseline_helper())
        failures = collect_failures(repo)
        if failures:
            raise SystemExit(f"phase1-find-bit-alias-tail:self-test:baseline:{failures}")

        write_helper(repo, baseline_helper().replace(REQUIRED_ANCHORS[0], "", 1))
        expect_failure(repo, "missing_next_or_anchor", f"find_bit_alias_tail_anchor:{REQUIRED_ANCHORS[0]}:expected=1:actual=0")

        write_helper(repo, baseline_helper() + REQUIRED_SNIPPETS[3] + "\n")
        expect_failure(repo, "duplicate_underscore_clump_snippet", f"find_bit_alias_tail_snippet:{REQUIRED_SNIPPETS[3]}:expected=1:actual=2")

    print("PHASE1_FIND_BIT_ALIAS_TAIL_ANCHORS_SELF_TEST=pass")
    print("PHASE1_FIND_BIT_ALIAS_TAIL_ANCHORS_SELF_TEST_CASE_COUNT=3")
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
        print("PHASE1_FIND_BIT_ALIAS_TAIL_ANCHORS=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_ALIAS_TAIL_ANCHORS=pass")
    print(f"PHASE1_FIND_BIT_ALIAS_TAIL_HELPER={HELPER_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
