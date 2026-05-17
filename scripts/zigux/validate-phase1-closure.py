#!/usr/bin/env python3
"""Validate the current Phase 1 closure note against the live reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    MANIFEST_REL,
    FIND_BIT_HELPER_REL,
)

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

EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS = [
    'test "find first and next set bits across words"',
    'test "find zero bits respects the declared bit count"',
    'test "find and bit returns the first shared set bit"',
    'test "underscore entry points reuse the public helper behavior"',
    'test "single-word next scans honor start masks"',
    'test "single-word first scans clamp to the declared bit window"',
    'test "single-word next scans clamp partial windows before returning nbits"',
    'test "word-boundary next scans start fresh on the next word"',
    'test "zero-bit windows return without reading bitmap words"',
    'test "zero-sized scans ignore populated backing words"',
    'test "next scans past nbits return without reading bitmap words"',
    'test "tail mask ignores set bits beyond nbits"',
    'test "tail mask ignores zero bits beyond nbits"',
    'test "tail mask ignores shared bits beyond nbits"',
    'test "tail-word next set scans skip earlier in-range matches before clamping"',
    'test "clump8 scans align to the containing byte and return its value"',
    'test "clump8 scans keep tail bytes reachable from partial final words"',
    'test "clump8 scans mask tail bits beyond nbits"',
    'test "clump8 scans leave the caller byte untouched when no set bit remains"',
    'test "getValue8 reads aligned bytes from bitmap words"',
    'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "find last bit scans backward across words"',
    'test "find last bit ignores storage beyond an exact word boundary"',
    'test "find last bit clamps tail words to nbits"',
    'test "find last bit returns nbits when no set bits remain"',
    'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    'test "low-level underscore aliases mirror the primary find helpers"',
    'test "Linux-style aliases mirror the primary find helpers"',
]

EXPECTED_FIND_BIT_REVIEW_FIELDS = {
    "same_word_start_masks": 'test "single-word next scans honor start masks"',
    "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_contract": (
        "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned "
        "when the inclusive start lands on the last in-range bit of the final partial word, "
        "while later starts still return nbits instead of leaking the out-of-range tail."
    ),
    "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
    "zero_sized_short_circuit_anchor": 'test "zero-sized scans ignore populated backing words"',
    "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
    "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
    "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers"',
    "tail_word_set_skip_anchor": 'test "tail-word next set scans skip earlier in-range matches before clamping"',
    "tail_word_skip_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    "tail_clamp_fixture_keys": [
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_clamped_last",
        "tail_clamped_empty_last",
    ],
    "review_packet_summary": (
        "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while "
        "helper-local anchors keep same-word start-mask, head-word and tail-word "
        "inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, "
        "tail-word set or zero or shared skip, underscore-alias, and Linux-style alias "
        "behavior review-visible on current master"
    ),
    "next_safe_step_note": (
        "If this helper lane reopens, keep find_bit parked unless a fresh reread finds "
        "direct-anchor drift inside same-word start-mask, inclusive-boundary, "
        "zero-window, zero-sized short-circuit, past-nbits, underscore-alias, "
        "Linux-style alias, or tail-word skip anchors, or committed tail-clamped replay "
        "drift; do not reopen older saved validator cues or neighboring helper families."
    ),
}

EXPECTED_MARKERS = {
    "status": "`PHASE1_STATUS=parked`",
    "restore_state": "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "helper_count": "`PHASE1_HELPER_COUNT=13`",
    "reminder_packet": (
        "`PHASE1_CURRENT_REMINDER_PACKET="
        "Documentation/zigux/phase1-closure.md,"
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md,"
        "Documentation/zigux/README.md,"
        "Documentation/zigux/review-checklist.md,"
        "scripts/zigux/README.md,"
        "scripts/zigux/check-phase1-string-review-packet.py,"
        "scripts/zigux/check-phase1-direct-owner-markers.py,"
        "scripts/zigux/validate-phase1-closure.py,"
        "zigux/tests/README.md,"
        "zigux/tests/build.zig,"
        "zigux/tests/phase1_host_tools_smoke.zig,"
        "zigux/tests/fixtures/phase1_helper_manifest.json`"
    ),
    "gap_packet": (
        "`PHASE1_CURRENT_GAP_PACKET="
        "scripts/zigux/validate-phase1.py,"
        "scripts/zigux/check-phase1-parity.py,"
        "zigux/tests/phase1_helpers.zig,"
        "zigux/tests/phase1_bench.zig,"
        "zigux/tests/fixtures/phase1_bench_expectations.json,"
        "zigux/tests/fixtures/phase1_helpers_c_harness.c,"
        "zigux/Makefile`"
    ),
    "closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "shared_tests_route": "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "next_step": (
        "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface against the restored closure note "
        "and closure validator`"
    ),
}

FORBIDDEN_MARKERS = (
    "`PHASE1_CLOSURE_RESTORE_STATE=docs_only`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=add scripts/zigux/validate-phase1-closure.py on current master and then sync one shared reminder surface against this restored closure note`",
    "scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-parity.py",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    if actual != expected:
        return [f"{label}:expected={expected!r}:actual={actual!r}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for label, marker in EXPECTED_MARKERS.items():
        failures.extend(
            require_exact_occurrence(closure_text, f"phase1_closure:{label}", marker)
        )

    for marker in FORBIDDEN_MARKERS:
        if marker in closure_text:
            failures.append(f"phase1_closure:forbidden={marker}")

    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1")
    )
    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed")
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:helper_count",
            manifest.get("helper_count"),
            len(EXPECTED_HELPERS),
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:helpers",
            manifest.get("helpers"),
            EXPECTED_HELPERS,
        )
    )

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        failures.append(
            f"{MANIFEST_REL.as_posix()}:review_anchors:expected=dict:actual={type(review_anchors).__name__}"
        )
        return failures

    bitmap_review = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_review, dict):
        failures.append(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:expected=dict:actual={type(bitmap_review).__name__}"
        )
        return failures

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/bitmap.zig:helper_test_anchors",
            bitmap_review.get("helper_test_anchors"),
            EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
        )
    )

    find_bit_review = review_anchors.get("tools/lib/find_bit.zig")
    if not isinstance(find_bit_review, dict):
        failures.append(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:expected=dict:actual={type(find_bit_review).__name__}"
        )
        return failures

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:helper_test_anchors",
            find_bit_review.get("helper_test_anchors"),
            EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
        )
    )

    for key, expected in EXPECTED_FIND_BIT_REVIEW_FIELDS.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig:{key}",
                find_bit_review.get(key),
                expected,
            )
        )

    find_bit_text = load_text(root, FIND_BIT_HELPER_REL)
    for anchor in EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(
                find_bit_text,
                f"{FIND_BIT_HELPER_REL.as_posix()}:helper_test_anchor",
                anchor,
            )
        )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(
        root / PHASE1_CLOSURE_REL,
        "\n".join(
            [
                "# Phase 1 Closure",
                "",
                EXPECTED_MARKERS["status"],
                EXPECTED_MARKERS["restore_state"],
                EXPECTED_MARKERS["helper_count"],
                EXPECTED_MARKERS["reminder_packet"],
                EXPECTED_MARKERS["gap_packet"],
                EXPECTED_MARKERS["closure_validator"],
                EXPECTED_MARKERS["shared_tests_route"],
                EXPECTED_MARKERS["validator_state"],
                EXPECTED_MARKERS["next_step"],
                "",
            ]
        ),
    )
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
                "review_anchors": {
                    "tools/lib/bitmap.zig": {
                        "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
                    },
                    "tools/lib/find_bit.zig": {
                        "helper_test_anchors": EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
                        **EXPECTED_FIND_BIT_REVIEW_FIELDS,
                    },
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / FIND_BIT_HELPER_REL, "\n".join(EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS) + "\n")


def run_self_test() -> int:
    cases = [
        ("baseline", None, True),
        (
            "missing_restore_state",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(
                    load_text(root, PHASE1_CLOSURE_REL),
                    EXPECTED_MARKERS["restore_state"],
                    "`PHASE1_CLOSURE_RESTORE_STATE=docs_only`",
                ),
            ),
            False,
        ),
        (
            "missing_validator_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(
                    load_text(root, PHASE1_CLOSURE_REL),
                    EXPECTED_MARKERS["closure_validator"],
                    "`PHASE1_CLOSURE_VALIDATOR=missing`",
                ),
            ),
            False,
        ),
        (
            "missing_file",
            lambda root: (root / PHASE1_SMOKE_REL).unlink(),
            False,
        ),
        (
            "bad_status",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "parked",
                        "helper_count": len(EXPECTED_HELPERS),
                        "helpers": EXPECTED_HELPERS,
                        "review_anchors": {
                            "tools/lib/bitmap.zig": {
                                "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
                            },
                            "tools/lib/find_bit.zig": {
                                "helper_test_anchors": EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
                                **EXPECTED_FIND_BIT_REVIEW_FIELDS,
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "bad_helper_count",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": 12,
                        "helpers": EXPECTED_HELPERS,
                        "review_anchors": {
                            "tools/lib/bitmap.zig": {
                                "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
                            },
                            "tools/lib/find_bit.zig": {
                                "helper_test_anchors": EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
                                **EXPECTED_FIND_BIT_REVIEW_FIELDS,
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "bad_helper_list",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": len(EXPECTED_HELPERS),
                        "helpers": EXPECTED_HELPERS[:-1],
                        "review_anchors": {
                            "tools/lib/bitmap.zig": {
                                "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
                            },
                            "tools/lib/find_bit.zig": {
                                "helper_test_anchors": EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
                                **EXPECTED_FIND_BIT_REVIEW_FIELDS,
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "bad_bitmap_helper_anchors",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": len(EXPECTED_HELPERS),
                        "helpers": EXPECTED_HELPERS,
                        "review_anchors": {
                            "tools/lib/bitmap.zig": {
                                "helper_test_anchors": ["drift"],
                            },
                            "tools/lib/find_bit.zig": {
                                "helper_test_anchors": EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
                                **EXPECTED_FIND_BIT_REVIEW_FIELDS,
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "bad_find_bit_helper_anchors",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": len(EXPECTED_HELPERS),
                        "helpers": EXPECTED_HELPERS,
                        "review_anchors": {
                            "tools/lib/bitmap.zig": {
                                "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
                            },
                            "tools/lib/find_bit.zig": {
                                "helper_test_anchors": ["drift"],
                                **EXPECTED_FIND_BIT_REVIEW_FIELDS,
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "bad_find_bit_review_field",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": len(EXPECTED_HELPERS),
                        "helpers": EXPECTED_HELPERS,
                        "review_anchors": {
                            "tools/lib/bitmap.zig": {
                                "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
                            },
                            "tools/lib/find_bit.zig": {
                                "helper_test_anchors": EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS,
                                **(EXPECTED_FIND_BIT_REVIEW_FIELDS | {"same_word_start_masks": "drift"}),
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
            False,
        ),
        (
            "missing_find_bit_source_anchor",
            lambda root: write_text(
                root / FIND_BIT_HELPER_REL,
                replace_once(
                    load_text(root, FIND_BIT_HELPER_REL),
                    EXPECTED_FIND_BIT_HELPER_TEST_ANCHORS[4] + "\n",
                    "",
                ),
            ),
            False,
        ),
        (
            "forbidden_old_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL) + "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`\n",
            ),
            False,
        ),
    ]

    for name, mutate, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-selftest-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"phase1-closure-self-test:{name}:unexpected={failures}")
                return 1

    print("PHASE1_CLOSURE_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run validator self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
