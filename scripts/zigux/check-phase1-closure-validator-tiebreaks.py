#!/usr/bin/env python3
"""Guard the Phase 1 closure validator tie-break strings against manifest drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

BITMAP_KEY = "tools/lib/bitmap.zig"
FIND_BIT_KEY = "tools/lib/find_bit.zig"

EXPECTED_BITMAP_NEXT_SAFE_STEP = (
    "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
    "direct-anchor drift inside the current helper-local packet or committed shared replay "
    "drift in the bitmap parity fields; current master still ships direct fill-tail clamp, "
    "copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors "
    "here, while zero-bit and Linux-style alias follow-through no longer live in the "
    "helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is "
    "still outstanding, treat that as the only other bitmap follow-through."
)

EXPECTED_FIND_BIT_FIRST_ANCHOR = (
    'test "find first and next set bits across words, with andnot gaps explicit"'
)
EXPECTED_FIND_BIT_UNDERSCORE_ALIAS = (
    'test "low-level underscore aliases mirror the primary find helpers, including andnot"'
)
EXPECTED_FIND_BIT_LINUX_ALIAS = (
    'test "Linux-style aliases mirror the primary find helpers, including andnot"'
)
EXPECTED_FIND_BIT_NEXT_SAFE_STEP = (
    "If this helper lane reopens, keep find_bit parked unless a fresh reread finds "
    "direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, "
    "zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), "
    "underscore-alias, Linux-style alias coverage including the shipped andnot scan "
    "entry points, or tail-word skip anchors, or committed tail-clamped replay drift; "
    "do not reopen older saved validator cues or neighboring helper families."
)

FORBIDDEN_VALIDATOR_STRINGS = {
    'test "find first and next set bits across words"',
    'test "low-level underscore aliases mirror the primary find helpers"',
    'test "Linux-style aliases mirror the primary find helpers"',
    (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new "
        "direct-anchor drift inside the current helper-local packet or committed shared replay "
        "drift in the bitmap parity fields; current master still ships direct fill-tail clamp, "
        "copy-alias, zero-bit logical, cross-word scnprintf, truncation, empty-buffer, "
        "Linux-style alias, and allocator-reset anchors here, so leave those helper-local tests "
        "as the bounded bitmap-only review packet unless one of those named anchors drifts or "
        "the separate bitmap closure-validator anchor-sync repair is still outstanding."
    ),
    (
        "If this helper lane reopens, keep find_bit parked unless a fresh reread finds "
        "direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, "
        "zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), "
        "underscore-alias, Linux-style alias, or tail-word skip anchors, or committed "
        "tail-clamped replay drift; do not reopen older saved validator cues or neighboring "
        "helper families."
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def mutate_manifest(root: Path, mutate: callable) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (VALIDATOR_REL, MANIFEST_REL):
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    validator_text = load_text(root, VALIDATOR_REL)
    manifest = json.loads(load_text(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}"]

    bitmap_review = review_anchors.get(BITMAP_KEY)
    if not isinstance(bitmap_review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.{BITMAP_KEY}:expected=dict:actual={type(bitmap_review).__name__}"]

    find_bit_review = review_anchors.get(FIND_BIT_KEY)
    if not isinstance(find_bit_review, dict):
        return [f"{MANIFEST_REL.as_posix()}:review_anchors.{FIND_BIT_KEY}:expected=dict:actual={type(find_bit_review).__name__}"]

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{BITMAP_KEY}:next_safe_step_note",
            bitmap_review.get("next_safe_step_note"),
            EXPECTED_BITMAP_NEXT_SAFE_STEP,
        )
    )

    helper_test_anchors = find_bit_review.get("helper_test_anchors")
    if not isinstance(helper_test_anchors, list):
        failures.append(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{FIND_BIT_KEY}:helper_test_anchors:expected=list:actual={type(helper_test_anchors).__name__}"
        )
    else:
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.{FIND_BIT_KEY}:helper_test_anchors[0]",
                helper_test_anchors[0] if helper_test_anchors else None,
                EXPECTED_FIND_BIT_FIRST_ANCHOR,
            )
        )
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.{FIND_BIT_KEY}:helper_test_anchors[-2]",
                helper_test_anchors[-2] if len(helper_test_anchors) >= 2 else None,
                EXPECTED_FIND_BIT_UNDERSCORE_ALIAS,
            )
        )
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.{FIND_BIT_KEY}:helper_test_anchors[-1]",
                helper_test_anchors[-1] if helper_test_anchors else None,
                EXPECTED_FIND_BIT_LINUX_ALIAS,
            )
        )

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{FIND_BIT_KEY}:underscore_alias_anchor",
            find_bit_review.get("underscore_alias_anchor"),
            EXPECTED_FIND_BIT_UNDERSCORE_ALIAS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{FIND_BIT_KEY}:linux_alias_anchor",
            find_bit_review.get("linux_alias_anchor"),
            EXPECTED_FIND_BIT_LINUX_ALIAS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.{FIND_BIT_KEY}:next_safe_step_note",
            find_bit_review.get("next_safe_step_note"),
            EXPECTED_FIND_BIT_NEXT_SAFE_STEP,
        )
    )

    for label, needle in (
        ("bitmap_next_safe_step_note", EXPECTED_BITMAP_NEXT_SAFE_STEP),
        ("find_bit_first_anchor", EXPECTED_FIND_BIT_FIRST_ANCHOR),
        ("find_bit_underscore_alias_anchor", EXPECTED_FIND_BIT_UNDERSCORE_ALIAS),
        ("find_bit_linux_alias_anchor", EXPECTED_FIND_BIT_LINUX_ALIAS),
        ("find_bit_next_safe_step_note", EXPECTED_FIND_BIT_NEXT_SAFE_STEP),
    ):
        failures.extend(
            require_exact_occurrence(
                validator_text,
                f"{VALIDATOR_REL.as_posix()}:{label}",
                needle,
            )
        )

    for forbidden in FORBIDDEN_VALIDATOR_STRINGS:
        count = validator_text.count(forbidden)
        if count:
            failures.append(
                f"{VALIDATOR_REL.as_posix()}:forbidden_string:actual_count={count}:{forbidden}"
            )

    return failures


def make_fixture_tree(root: Path) -> None:
    write_text(
        root / VALIDATOR_REL,
        "\n".join(
            [
                "# fixture validator",
                EXPECTED_BITMAP_NEXT_SAFE_STEP,
                EXPECTED_FIND_BIT_FIRST_ANCHOR,
                EXPECTED_FIND_BIT_UNDERSCORE_ALIAS,
                EXPECTED_FIND_BIT_LINUX_ALIAS,
                EXPECTED_FIND_BIT_NEXT_SAFE_STEP,
                "",
            ]
        ),
    )
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    BITMAP_KEY: {
                        "next_safe_step_note": EXPECTED_BITMAP_NEXT_SAFE_STEP,
                    },
                    FIND_BIT_KEY: {
                        "helper_test_anchors": [
                            EXPECTED_FIND_BIT_FIRST_ANCHOR,
                            'test "find zero bits respects the declared bit count"',
                            EXPECTED_FIND_BIT_UNDERSCORE_ALIAS,
                            EXPECTED_FIND_BIT_LINUX_ALIAS,
                        ],
                        "underscore_alias_anchor": EXPECTED_FIND_BIT_UNDERSCORE_ALIAS,
                        "linux_alias_anchor": EXPECTED_FIND_BIT_LINUX_ALIAS,
                        "next_safe_step_note": EXPECTED_FIND_BIT_NEXT_SAFE_STEP,
                    },
                }
            },
            indent=2,
        )
        + "\n",
    )


def write_sample_root(root: Path) -> None:
    make_fixture_tree(root)


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "bad_bitmap_manifest_note",
            lambda root: write_text(
                root / MANIFEST_REL,
                replace_once(
                    load_text(root, MANIFEST_REL),
                    EXPECTED_BITMAP_NEXT_SAFE_STEP,
                    "drifted bitmap note",
                ),
            ),
        ),
        (
            "missing_bitmap_validator_note",
            lambda root: write_text(
                root / VALIDATOR_REL,
                replace_once(
                    load_text(root, VALIDATOR_REL),
                    EXPECTED_BITMAP_NEXT_SAFE_STEP + "\n",
                    "",
                ),
            ),
        ),
        (
            "bad_find_bit_manifest_anchor",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"][FIND_BIT_KEY]["helper_test_anchors"].__setitem__(
                    0, 'test "find first and next set bits across words"'
                ),
            ),
        ),
        (
            "forbidden_find_bit_validator_anchor",
            lambda root: write_text(
                root / VALIDATOR_REL,
                replace_once(
                    load_text(root, VALIDATOR_REL),
                    EXPECTED_FIND_BIT_FIRST_ANCHOR,
                    'test "find first and next set bits across words"',
                ),
            ),
        ),
        (
            "bad_find_bit_manifest_alias",
            lambda root: mutate_manifest(
                root,
                lambda manifest: (
                    manifest["review_anchors"][FIND_BIT_KEY].__setitem__(
                        "underscore_alias_anchor",
                        'test "low-level underscore aliases mirror the primary find helpers"',
                    ),
                    manifest["review_anchors"][FIND_BIT_KEY]["helper_test_anchors"].__setitem__(
                        -2,
                        'test "low-level underscore aliases mirror the primary find helpers"',
                    ),
                ),
            ),
        ),
        (
            "forbidden_find_bit_validator_alias",
            lambda root: write_text(
                root / VALIDATOR_REL,
                replace_once(
                    load_text(root, VALIDATOR_REL),
                    EXPECTED_FIND_BIT_LINUX_ALIAS,
                    'test "Linux-style aliases mirror the primary find helpers"',
                ),
            ),
        ),
        (
            "bad_find_bit_manifest_next_step",
            lambda root: mutate_manifest(
                root,
                lambda manifest: manifest["review_anchors"][FIND_BIT_KEY].__setitem__(
                    "next_safe_step_note",
                    "drifted find_bit note",
                ),
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-validator-tiebreaks-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-validator-tiebreaks:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-validator-tiebreaks:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_VALIDATOR_TIEBREAKS_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_TIEBREAKS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run checker self-tests",
    )
    parser.add_argument(
        "--write-sample-root",
        help="write a sample root that matches the current validator tie-break packet",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_TIEBREAKS=pass")
    print("PHASE1_CLOSURE_VALIDATOR_TIEBREAKS_PACKET=bitmap_and_find_bit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
