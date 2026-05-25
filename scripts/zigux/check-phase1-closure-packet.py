#!/usr/bin/env python3
"""Guard the current Phase 1 closure-note reminder packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_NOTE_REL = "Documentation/zigux/phase1-closure.md"
MAKEFILE_REL = "zigux/Makefile"

DIRECT_PACKET_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
)

BROADER_COMPANION_GAPS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
)

REQUIRED_CLOSURE_LINES = (
    "- `PHASE1_STATUS=parked`",
    "- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "- `PHASE1_HELPER_COUNT=13`",
    "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    "- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
    "- `PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    "- `PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    "- `PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
    "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "- `PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp the last word without leaking out-of-range bits into the asserted view`",
    "- `PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched when no bits are set, matching both the direct Zig unit test and the committed parity fixture`",
    "- `PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`",
    "- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
    "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
)

REQUIRED_CLOSURE_FRAGMENTS = (
    "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
    "A current helper-family tie-breaker inside that packet is the `bitmap` direct-anchor route: keep `tools/lib/bitmap.zig` parked unless a fresh reread finds new direct-anchor drift inside the manifest-backed fill-tail clamp, copy-alias, cross-word `scnprintf()`, exact-word-boundary equality fast-path masking, empty-buffer, allocator-reset, zero-bit logical short-circuit, Linux-style alias mirror, caller-window or multiword-tail `xorBits()`/`orBits()` clamp witnesses, or weighted tail-count clamp, or drift in the already-committed bitmap replay fields summarized by the manifest; do not reopen older closure-side or validator-route cue names by default.",
    "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default.",
    "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness.",
    "A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local `strscpy()` or `strscpyPad()` copy-and-pad anchors, memparse safety anchors, matched-prefix-length or suffix-boundary anchors, sysfs newline-aware equality or lookup-order anchors through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, C-string list lookup anchors through `matchString()` and `match_string()`, lexical-compare and search-or-length boundary anchors through `strcmp()`, `strlen()`, `strnlen()`, `strchr()`, `strrchr()`, `strchrNul()`, and `strchrnul()`, counted-search anchors through `strpbrk()`, `strcspn()`, `strnchr()`, `strnchrNul()` or `strnchrnul()`, and `strspn()`, embedded-NUL trim preservation, or moving-earliest-dirty-byte `memchrInv()` coverage, or unless committed `replaceChar` parity bytes or current string fixture keys drift; do not reopen missing closure-side validator names by default.",
    "Current `master` now also spells the helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors directly in the shipped manifest-backed string review packet beside the `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, and `strtomem_pad()` byte-copy anchors.",
)

FORBIDDEN_MAKEFILE_LINES = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    want = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in DIRECT_PACKET_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_direct_packet_file:{relative_path}")

    if not (root / MAKEFILE_REL).is_file():
        failures.append(f"missing_makefile:{MAKEFILE_REL}")

    for relative_path in BROADER_COMPANION_GAPS:
        if (root / relative_path).exists():
            failures.append(f"unexpected_broader_companion_presence:{relative_path}")

    if failures:
        return failures

    closure_text = read_text(root, CLOSURE_NOTE_REL)
    for marker in REQUIRED_CLOSURE_LINES:
        count = count_exact_line(closure_text, marker)
        if count != 1:
            failures.append(f"closure_line_count:{marker}:expected=1:actual={count}")

    for fragment in REQUIRED_CLOSURE_FRAGMENTS:
        count = closure_text.count(fragment)
        if count != 1:
            failures.append(
                f"closure_fragment_count:{fragment}:expected=1:actual={count}"
            )

    makefile_text = read_text(root, MAKEFILE_REL)
    phase1_route_summary_count = count_exact_line(makefile_text, "phase1-route-summary:")
    if phase1_route_summary_count != 1:
        failures.append(
            "makefile_phase1_route_summary:expected=1:"
            f"actual={phase1_route_summary_count}"
        )

    for marker in FORBIDDEN_MAKEFILE_LINES:
        count = count_exact_line(makefile_text, marker)
        if count != 0:
            failures.append(f"makefile_forbidden_line:{marker}:expected=0:actual={count}")

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    closure_lines = []
    for marker in REQUIRED_CLOSURE_LINES:
        closure_lines.append(marker)
    for fragment in REQUIRED_CLOSURE_FRAGMENTS:
        closure_lines.append(fragment)

    for relative_path in DIRECT_PACKET_FILES:
        if relative_path == CLOSURE_NOTE_REL:
            write_text(root, relative_path, "\n".join(closure_lines) + "\n")
        else:
            write_text(root, relative_path, f"placeholder for {relative_path}\n")
    write_text(root, MAKEFILE_REL, "phase1-route-summary:\n")


def remove_exact_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return
    raise ValueError(f"missing marker {marker!r} in {relative_path}")


def duplicate_exact_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing marker {marker!r} in {relative_path}")


def remove_fragment(root: Path, relative_path: str, fragment: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    if fragment not in text:
        raise ValueError(f"missing fragment {fragment!r} in {relative_path}")
    path.write_text(text.replace(fragment, "", 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, ...] | None]] = [("success", None)]

    for relative_path in DIRECT_PACKET_FILES:
        cases.append((f"missing_direct_packet:{relative_path}", ("remove_file", relative_path)))
    cases.append(("missing_makefile", ("remove_file", MAKEFILE_REL)))
    for relative_path in BROADER_COMPANION_GAPS:
        cases.append((f"unexpected_gap_presence:{relative_path}", ("add_file", relative_path)))
    for marker in REQUIRED_CLOSURE_LINES:
        cases.append((f"missing_line:{marker}", ("remove_line", CLOSURE_NOTE_REL, marker)))
        cases.append((f"duplicate_line:{marker}", ("duplicate_line", CLOSURE_NOTE_REL, marker)))
    for fragment in REQUIRED_CLOSURE_FRAGMENTS:
        cases.append((f"missing_fragment:{fragment}", ("remove_fragment", CLOSURE_NOTE_REL, fragment)))
    cases.append(("missing_route_summary", ("remove_line", MAKEFILE_REL, "phase1-route-summary:")))
    for marker in FORBIDDEN_MAKEFILE_LINES:
        cases.append((f"forbidden_makefile:{marker}", ("add_line", MAKEFILE_REL, marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "remove_file":
                    (root / mutation[1]).unlink()
                elif kind == "add_file":
                    write_text(root, mutation[1], "unexpected broader companion\n")
                elif kind == "remove_line":
                    remove_exact_line(root, mutation[1], mutation[2])
                elif kind == "duplicate_line":
                    duplicate_exact_line(root, mutation[1], mutation[2])
                elif kind == "remove_fragment":
                    remove_fragment(root, mutation[1], mutation[2])
                elif kind == "add_line":
                    path = root / mutation[1]
                    text = path.read_text(encoding="utf-8")
                    path.write_text(text + mutation[2] + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        build_sample_repo(args.write_sample_root)
        print(f"PHASE1_CLOSURE_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_PACKET=pass")
    print(f"PHASE1_CLOSURE_PACKET_DIRECT_FILE_COUNT={len(DIRECT_PACKET_FILES)}")
    print(
        "PHASE1_CLOSURE_PACKET_BROADER_COMPANION_GAP_COUNT="
        f"{len(BROADER_COMPANION_GAPS)}"
    )
    print(
        "PHASE1_CLOSURE_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_LINES) + len(REQUIRED_CLOSURE_FRAGMENTS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
