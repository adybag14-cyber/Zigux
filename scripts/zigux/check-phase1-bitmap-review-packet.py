#!/usr/bin/env python3
"""Guard the Phase 1 bitmap review packet against helper, manifest, and lane-note drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
BITMAP_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

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

EXPECTED_BITMAP_PACKET = {
    "helper_test_anchors": EXPECTED_BITMAP_HELPER_TEST_ANCHORS,
    "first_word_boundary_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "final_partial_word_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "fill_tail_clamp_anchor": 'test "bitmap full empty and weight ignore out-of-range tail bits"',
    "predicate_tail_mask_anchor": 'test "bitmap tail-masked helpers ignore out-of-range differences"',
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "review_packet_summary": (
        "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, "
        "scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current "
        "master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw "
        "copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend "
        "handling, zero-sized destination-view no-op coverage, tail-masked predicate behavior, "
        "out-of-range tail-bit full or empty or weight masking, caller-window xor clamping, "
        "terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer "
        "preservation, and allocator optional-reset coverage."
    ),
    "parity_fixture_keys": [
        "alloc_words",
        "zalloc_words",
        "zalloc_values",
        "scnprintf",
        "truncated_scnprintf_len",
        "truncated_scnprintf",
        "terminator_only_scnprintf_len",
        "terminator_only_nul",
        "zero_length_scnprintf_len",
    ],
    "partial_xor_review_fields": [
        "partial_xor_nbits",
        "partial_xor_masked_values",
    ],
    "scnprintf_cross_word_anchor": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    "scnprintf_truncation_anchor": 'test "bitmap scnprintf truncates and keeps a terminator slot"',
    "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "copy_zero_and_aligned_anchors": [
        'test "bitmap copy and extend handles zero and aligned counts"',
        'test "bitmap copy helpers keep zero-sized destination views untouched"',
    ],
    "zero_bit_noop_anchor": "",
    "zero_bit_binary_identity_anchor": "",
    "linux_alias_anchor": "",
    "next_safe_step_note": (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor "
        "drift inside the current helper-local packet or committed shared replay drift in the bitmap "
        "parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, "
        "cross-word scnprintf, empty-buffer, and allocator-reset anchors here, while zero-bit and "
        "Linux-style alias follow-through no longer live in the helper-local packet, and if the "
        "separate bitmap closure-validator anchor-sync repair is still outstanding, treat that as the "
        "only other bitmap follow-through."
    ),
}

EXPECTED_BITMAP_LANE_MARKERS = [
    (
        "lane_direct_owner",
        "`PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay "
        "keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are "
        "live companions again, while the older validator-first and make-route names stay historical`",
    ),
    (
        "lane_next_safe_step",
        "`PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new "
        "direct-anchor drift or committed shared replay drift; do not reopen older closure-side or "
        "validator-route cue names by default`",
    ),
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def iter_source_anchor_strings() -> list[str]:
    anchors: list[str] = list(EXPECTED_BITMAP_HELPER_TEST_ANCHORS)
    for key, value in EXPECTED_BITMAP_PACKET.items():
        if key == "phase1_helper_replay_anchor":
            continue
        if isinstance(value, str) and value.startswith('test "'):
            anchors.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.startswith('test "'):
                    anchors.append(item)
    return sorted(set(anchors))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (BITMAP_HELPER_REL, BITMAP_MANIFEST_REL, BITMAP_LANE_NOTE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, BITMAP_HELPER_REL)
    lane_text = load_text(root, BITMAP_LANE_NOTE_REL)
    manifest = load_json(root, BITMAP_MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]

    for anchor in iter_source_anchor_strings():
        failures.extend(
            require_exact_occurrence(helper_text, f"bitmap_helper:{anchor}", anchor)
        )

    for label, marker in EXPECTED_BITMAP_LANE_MARKERS:
        failures.extend(
            require_exact_occurrence(lane_text, f"bitmap_lane:{label}", marker)
        )

    for key, expected in EXPECTED_BITMAP_PACKET.items():
        failures.extend(
            require_exact_value(
                f"bitmap_manifest:review_anchors.tools/lib/bitmap.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/bitmap.zig", key)),
                expected,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/bitmap.zig": EXPECTED_BITMAP_PACKET,
                }
            },
            indent=2,
        )
        + "\n"
    )


def sample_lane_note() -> str:
    return "\n".join(marker for _, marker in EXPECTED_BITMAP_LANE_MARKERS) + "\n"


def build_sample_repo(root: Path) -> None:
    helper_lines = iter_source_anchor_strings()
    write_file(root, BITMAP_HELPER_REL, "\n".join(helper_lines) + "\n")
    write_file(root, BITMAP_MANIFEST_REL, sample_manifest())
    write_file(root, BITMAP_LANE_NOTE_REL, sample_lane_note())


def mutate_manifest(root: Path, key: str) -> None:
    manifest_path = root / BITMAP_MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target = manifest["review_anchors"]["tools/lib/bitmap.zig"]
    value = target[key]
    if isinstance(value, list):
        target[key] = value[1:]
    else:
        target[key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def mutate_line(path: Path, marker: str, duplicate: bool) -> None:
    text = path.read_text(encoding="utf-8")
    if duplicate:
        path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")
    else:
        path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-review-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1
        case_count += 1

    cases: list[tuple[str, str, str | None, bool | None]] = []
    for anchor in iter_source_anchor_strings():
        cases.append(("helper", anchor, None, False))
        cases.append(("helper", anchor, None, True))
    for _, marker in EXPECTED_BITMAP_LANE_MARKERS:
        cases.append(("lane", marker, None, False))
        cases.append(("lane", marker, None, True))
    for key in EXPECTED_BITMAP_PACKET:
        cases.append(("manifest", key, None, None))
    cases.append(("missing_file", BITMAP_HELPER_REL.as_posix(), None, None))
    cases.append(("missing_file", BITMAP_MANIFEST_REL.as_posix(), None, None))
    cases.append(("missing_file", BITMAP_LANE_NOTE_REL.as_posix(), None, None))

    for kind, value, _, duplicate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bitmap-review-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if kind == "helper":
                mutate_line(root / BITMAP_HELPER_REL, value, bool(duplicate))
            elif kind == "lane":
                mutate_line(root / BITMAP_LANE_NOTE_REL, value, bool(duplicate))
            elif kind == "manifest":
                mutate_manifest(root, value)
            else:
                (root / value).unlink()
            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{kind}:{value}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")
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

    print("phase1-bitmap-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
