#!/usr/bin/env python3
"""Fail-closed Phase 6 shared-surface checks for the leaf-helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


REQUIRED_SNIPPETS = {
    "Documentation/zigux/README.md": [
        "- `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, `make -C zigux phase6`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf` now keep the current base64, bsearch, checksum, and hexdump helper bundle reviewable through the shared surface checker, the bundled replay, the dedicated checksum and hexdump perf gates, and the Linux-style helper lane together, so new helper slices should only land when that shared packet stays green as one unit.",
        "- the current bounded Phase 6 decision is no longer whether one more tiny external fixture is still worth carrying; the live leaf-helper lane is the bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already kept reviewable through `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/phase6_hexdump_perf.zig`, `make -C zigux phase6`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`, so future follow-up here should reopen only for a concrete parity gap or another similarly small helper-first step inside that same packet.",
    ],
    "scripts/zigux/README.md": [
        "Phase 6 flow - the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
        "- `make -C zigux phase6-validate` keeps the shared Phase 6 surface checker wired through the Zigux convenience target.",
        "- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.",
        "- `make -C zigux phase6` keeps that same shared-surface check plus bundled helper replay wired through the Zigux convenience target.",
        "- there is no separate shared `validate-phase6.py`, external portability checker packet beyond `check-phase6-shared-surface.py`, or aggregated `phase6-perf` target on `master`; the shipped dedicated perf replays are `make -C zigux phase6-checksum-perf` and `make -C zigux phase6-hexdump-perf`, which keep the checksum slowdown ceiling and the formatter-sensitive hexdump fixture packet wired into Linux-style entrypoints without overstating perf coverage for the rest of the Phase 6 helper packet.",
    ],
    "Documentation/zigux/review-checklist.md": [
        "  * if the change touches the shared Phase 6 leaf-helper packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-hexdump-slice.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, `make -C zigux phase6`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf` still agree on the same bundled `base64`, `bsearch`, `checksum`, and `hexdump` helper packet without implying a removed shared `validate-phase6.py`, a broader external parity checker beyond `check-phase6-shared-surface.py`, or an aggregated `phase6-perf` route?",
    ],
    "Documentation/zigux/phase6-base64-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=base64-leaf-helper`",
        "- lane state: helper and fixture slice landed; parked unless a new `base64.c` parity issue appears",
        "- `Variant.imap`",
        "- fixture-backed decode-length parity through `bytes` across the full committed valid std, URL-safe, and IMAP decode corpus",
        "- invalid-input rejection through both `bytes` and `decode` for malformed, embedded-NUL, and variant-mismatched decode inputs",
        "- exhaustive canonical tail acceptance for padded and unpadded std, URL-safe, and IMAP decode paths",
    ],
    "Documentation/zigux/phase6-bsearch-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=bsearch-leaf-helper`",
        "- lane state: helper slice landed; parked unless a new `bsearch.c` parity issue appears",
        "- `searchIndex`",
        "- `bsearchMutable`",
        "- mutable typed and raw lookup write-through parity",
        "- runtime-selected raw C ABI comparator pointer parity, including pointer-return duplicate hits and null misses",
        "The current packet intentionally keeps its representative sorted inputs inline in `zigux/tests/phase6_bsearch.zig` instead of a separate fixture module so the helper bundle stays small and directly reviewable.",
    ],
    "zigux/tests/README.md": [
        "  * `zigux/tests/phase6_hexdump_perf.zig`",
        "  * keep the shared Phase 6 leaf-helper packet wired through `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, including `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, and `make -C zigux phase6`, so the landed `base64`, `bsearch`, `checksum`, and `hexdump` bundle stays reviewable through one bounded helper gate, and keep `zigux/tests/phase6_checksum_perf.zig` plus `make -C zigux phase6-checksum-perf` and `zigux/tests/phase6_hexdump_perf.zig` plus `make -C zigux phase6-hexdump-perf` explicit as the dedicated checksum and hexdump perf routes rather than implying a broader Phase 6 packet-wide perf target",
    ],
    "zigux/tests/phase6_build.zig": [
        'const test_step = b.step("test", "Run Phase 6 leaf helper tests");',
        '.name = "phase6-base64-tests"',
        '.name = "phase6-bsearch-tests"',
        '.name = "phase6-checksum-tests"',
        '.name = "phase6-hexdump-tests"',
        '.name = "phase6-checksum-perf"',
        '.name = "phase6-hexdump-perf"',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
    ],
    "zigux/tests/phase6_base64.zig": [
        'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
        'for (fixtures.standard_cases) |case| {',
        'for (fixtures.variant_cases) |case| {',
        'for (fixtures.standard_decode_cases) |case| {',
        'for (fixtures.invalid_decode_cases) |case| {',
        'for (fixtures.variant_decode_cases) |case| {',
        'test "phase 6 base64 chars reports exact padded and unpadded lengths"',
        'test "phase 6 base64 bytes reports exact decoded lengths for kernel-aligned vectors"',
        'test "phase 6 base64 standard encode parity matches kernel vectors"',
        'test "phase 6 base64 standard decode parity keeps bytes and decode aligned with kernel vectors"',
        'test "phase 6 base64 variant alphabets match the kernel mappings with and without padding"',
        'test "phase 6 base64 variant decode parity keeps bytes and decode aligned with kernel mappings"',
        'test "phase 6 base64 invalid vectors fail bytes and decode together"',
        'test "phase 6 base64 invalid decode vectors leave destination bytes untouched"',
        'test "phase 6 base64 bytes rejects malformed kernel-style vectors"',
        'test "phase 6 base64 reports destination bounds before encoding"',
        'test "phase 6 base64 reports destination bounds before decoding"',
    ],
    "zigux/tests/phase6_bsearch.zig": [
        'test "phase 6 bsearch honors comparator-driven descending order"',
        'test "phase 6 bsearch supports string keys against sorted records"',
        'test "phase 6 bsearch mutable typed lookup supports write-through"',
        'test "phase 6 bsearch treats duplicate keys as found-or-null without claiming stable selection"',
        'test "phase 6 bsearch keeps representative lookup work inside a binary-search budget"',
        'test "phase 6 bsearch raw lookup returns null for empty input without invoking the comparator"',
        'test "phase 6 bsearch raw lookup keeps representative work inside a binary-search budget"',
        'test "phase 6 bsearch accepts runtime-selected native comparator pointers"',
        'test "phase 6 bsearch accepts runtime-selected c abi comparator pointers"',
        'test "phase 6 bsearch accepts runtime-selected raw native comparator pointers"',
        'test "phase 6 bsearch mutable raw lookup supports descending write-through"',
        'test "phase 6 bsearch accepts runtime-selected raw c abi comparator pointers"',
        'test "phase 6 bsearch mutable raw c abi lookup supports write-through"',
    ],
    "Documentation/zigux/phase6-checksum-slice.md": [
        "- lane state: helper and fixture slice landed; parked unless a new `checksum.c` parity issue appears",
        "- `add`",
        "- `replaceByDiff`",
        "- `tcpUdpNofold`",
        "- fixture-backed checksum vectors for empty, even, odd, and carry-heavy inputs",
        "- non-zero seeded `partial` accumulation parity across odd, carry-heavy, and pre-folded seed inputs",
        "- a tiny KUnit-inspired carry-discipline matrix covering all-ones and no-spurious-carry seeded cases",
        "- pseudo-header accumulation parity between `tcpUdpNofold` and manual `partial` plus `blockAdd`",
        "- helper-local perf smoke on patterned 64-byte and 1501-byte payloads keeps `checksum.compute` within a 150% slowdown ceiling versus the bounded reference loop",
    ],
    "Documentation/zigux/phase6-hexdump-slice.md": [
        "- lane state: helper, fixture, and dedicated perf gate slices landed; parked unless a new `hexdump.c` parity issue appears",
        "- `hexDumpLineLength`",
        "- `hexDumpToBuffer`",
        "- serialized required-length vectors for `hexDumpLineLength` and zero-buffer `hexDumpToBuffer`",
        "- a dedicated perf replay that benchmarks the existing four-case perf fixture packet against the committed `fixtures.prepareExpectedLine(...)` reference path",
        "- `16B-plain-g1`",
        "- `32B-ascii-g2`",
        "- `16B-ascii-g4`",
        "- `16B-ascii-g8`",
    ],
    "zigux/tests/phase6_checksum.zig": [
        'test "fixture-backed compute parity covers the current checksum vectors"',
        'test "partial sums compose across the fixture split matrix"',
        'test "blockSub reverses blockAdd across odd and even fragment boundaries"',
        'test "seeded partial accumulation matches the fixture-backed reference"',
        'test "kunit-inspired carry discipline stays stable on the helper surface"',
        'test "fixture-backed negate cases keep the public checksum helper reviewable"',
        'test "from32to16 folds unfolded sums before the final complement"',
        'test "pseudo header accumulation matches the fixture-backed reference checksum"',
        'test "incremental checksum replacement helpers match direct recomputation"',
    ],
    "zigux/tests/phase6_checksum_perf.zig": [
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{perf_cases.len});',
        '        .label = "64B",',
        '        .label = "1501B",',
        '        .iterations = 200_000,',
        '        .iterations = 12_000,',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_SLOWDOWN_PCT={d}\\n", .{ case.label, slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_CHECKSUM={d}\\n", .{ case.label, helper_result.checksum_accumulator });',
        'if (helper_expected != reference_expected) {',
        'if (helper_result.checksum_accumulator != reference_result.checksum_accumulator) {',
        'if (slowdown_pct > case.max_slowdown_pct) {',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF={s}\\n", .{if (failed) "fail" else "pass"});',
        'if (failed) return error.ChecksumPerfRegression;',
    ],
    "zigux/tests/fixtures/phase6_checksum_vectors.zig": [
        "pub const compute_cases = [_]ComputeCase{",
        '.name = "carry-heavy payload"',
        "pub const composition_cases = [_]CompositionCase{",
        '.name = "odd split"',
        "pub const seeded_cases = [_]SeededCase{",
        '.name = "carry-heavy payload with unfolded seed"',
        "pub const pseudo_header_cases = [_]PseudoHeaderCase{",
        '.name = "udp pseudo header"',
        "pub const carry_discipline_cases = [_]CarryDisciplineCase{",
        '.name = "two-byte no-carry seed stays one step below overflow"',
        "pub const negate_cases = [_]NegateCase{",
        '.name = "mixed payload preserves ones complement carry"',
    ],
    "zigux/tests/phase6_hexdump.zig": [
        'test "phase 6 hexdump serialized linux-derived vectors stay in sync"',
        'test "phase 6 hexdump serialized overflow vectors stay in sync"',
        'test "phase 6 hexdump serialized required-length vectors stay in sync"',
        'test "phase 6 hexdump perf fixture packet stays in sync"',
        'test "phase 6 hexdump uppercase nibble helpers stay aligned with byte packing"',
        'test "phase 6 hexdump parity matrix matches kernel fixture preparation"',
        'test "phase 6 hexdump overflow contract matches truncation expectations"',
        'test "phase 6 hexdump grouped ASCII output stays intact when buffer capacity is exact"',
        'test "phase 6 hexdump covers normalization and empty-buffer edge cases"',
    ],
    "zigux/tests/phase6_hexdump_perf.zig": [
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_SLOWDOWN_PCT={d}\\n", .{ case.label, slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_ACCUMULATOR={d}\\n", .{ case.label, helper_result.accumulator });',
        'if (helper_result.accumulator != reference_result.accumulator) {',
        'if (slowdown_pct > case.max_slowdown_pct) {',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF={s}\\n", .{if (failed) "fail" else "pass"});',
        'if (failed) return error.HexdumpPerfRegression;',
    ],
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig": [
        'pub const perf_cases = [_]PerfCase{',
        '.label = "16B-plain-g1"',
        '.label = "32B-ascii-g2"',
        '.label = "16B-ascii-g4"',
        '.label = "16B-ascii-g8"',
        '.max_slowdown_pct = 175',
        '.max_slowdown_pct = 550',
        '.max_slowdown_pct = 600',
    ],
    "zigux/Makefile": [
        "PHONY += phase6-validate phase6-test phase6-checksum-perf phase6-hexdump-perf phase6",
        "phase6-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
        "phase6-checksum-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6-hexdump-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6: phase6-validate phase6-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "- name: Self-test Phase 6 shared-surface checker\n        run: python3 scripts/zigux/check-phase6-shared-surface.py --self-test",
        "- name: Check Phase 6 shared surface\n        run: python3 scripts/zigux/check-phase6-shared-surface.py",
        "- name: Run Phase 6 leaf helper tests\n        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "- name: Run Phase 6 checksum perf gate\n        run: zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
        "- name: Run Phase 6 hexdump perf gate\n        run: zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    ],
}

EXACT_COUNT_MARKERS = {
    "zigux/Makefile": [
        "PHONY += phase6-validate phase6-test phase6-checksum-perf phase6-hexdump-perf phase6",
        "phase6-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
        "phase6-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase6_build.zig",
        "phase6-checksum-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6-hexdump-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6: phase6-validate phase6-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "- name: Self-test Phase 6 shared-surface checker\n        run: python3 scripts/zigux/check-phase6-shared-surface.py --self-test",
        "- name: Check Phase 6 shared surface\n        run: python3 scripts/zigux/check-phase6-shared-surface.py",
        "- name: Run Phase 6 leaf helper tests\n        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "- name: Run Phase 6 checksum perf gate\n        run: zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
        "- name: Run Phase 6 hexdump perf gate\n        run: zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    ],
}

EXACT_OCCURRENCE_MARKERS = {
    "zigux/tests/phase6_checksum_perf.zig": [
        ('.max_slowdown_pct = 150,', 2),
    ],
}

REMOVED_PATHS = [
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/validate-phase6.py",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def run_checks(repo_root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(
                    f"missing expected Phase 6 marker in {rel_path}: {snippet}"
                )

    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        content = read_text(repo_root / rel_path)
        for marker in markers:
            occurrences = content.count(marker)
            if occurrences != 1:
                raise ValidationError(
                    f"expected exactly one Phase 6 marker in {rel_path}, found {occurrences}: {marker}"
                )

    for rel_path, markers in EXACT_OCCURRENCE_MARKERS.items():
        content = read_text(repo_root / rel_path)
        for marker, expected in markers:
            occurrences = content.count(marker)
            if occurrences != expected:
                raise ValidationError(
                    f"expected {expected} occurrences of Phase 6 marker in {rel_path}, found {occurrences}: {marker}"
                )

    for rel_path in REMOVED_PATHS:
        if (repo_root / rel_path).exists():
            raise ValidationError(
                f"removed Phase 6 shared-surface file unexpectedly present: {rel_path}"
            )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        for rel_path, snippets in REQUIRED_SNIPPETS.items():
            exact_markers = EXACT_COUNT_MARKERS.get(rel_path, [])
            occurrence_markers = [
                marker
                for marker, expected in EXACT_OCCURRENCE_MARKERS.get(rel_path, [])
                for _ in range(expected)
            ]
            scaffold_lines = unique_preserving_order(snippets + exact_markers)
            scaffold_lines.extend(occurrence_markers)
            write(
                root / rel_path,
                "\n".join(scaffold_lines) + "\n",
            )

        run_checks(root)

        removed_path = root / REMOVED_PATHS[0]
        write(removed_path, "stale\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if REMOVED_PATHS[0] not in str(exc):
                raise AssertionError(f"unexpected removed-path failure: {exc}") from exc
        else:
            raise AssertionError("expected removed-path failure")
        removed_path.unlink()

        scripts_readme = root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme.read_text(encoding="utf-8")
        scripts_readme.write_text(
            original_scripts_readme.replace(
                "phase6-hexdump-perf",
                "phase6-hexdump-bench",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "scripts/zigux/README.md" not in str(exc):
                raise AssertionError(f"unexpected scripts README failure: {exc}") from exc
        else:
            raise AssertionError("expected scripts README failure")
        scripts_readme.write_text(original_scripts_readme, encoding="utf-8")

        docs_readme = root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme.read_text(encoding="utf-8")
        docs_readme.write_text(
            original_docs_readme.replace(
                "phase6-hexdump-perf",
                "phase6-hexdump-bench",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/README.md" not in str(exc):
                raise AssertionError(f"unexpected docs README failure: {exc}") from exc
        else:
            raise AssertionError("expected docs README failure")
        docs_readme.write_text(original_docs_readme, encoding="utf-8")

        base64_slice = root / "Documentation/zigux/phase6-base64-slice.md"
        original_base64_slice = base64_slice.read_text(encoding="utf-8")
        base64_slice.write_text(
            original_base64_slice.replace(
                "`Variant.imap`",
                "`Variant.smtp`",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/phase6-base64-slice.md" not in str(exc):
                raise AssertionError(f"unexpected base64 slice failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 slice failure")
        base64_slice.write_text(original_base64_slice, encoding="utf-8")

        bsearch_slice = root / "Documentation/zigux/phase6-bsearch-slice.md"
        original_bsearch_slice = bsearch_slice.read_text(encoding="utf-8")
        bsearch_slice.write_text(
            original_bsearch_slice.replace(
                "runtime-selected raw C ABI comparator pointer parity",
                "runtime-selected raw foreign ABI comparator pointer parity",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/phase6-bsearch-slice.md" not in str(exc):
                raise AssertionError(f"unexpected bsearch slice failure: {exc}") from exc
        else:
            raise AssertionError("expected bsearch slice failure")
        bsearch_slice.write_text(original_bsearch_slice, encoding="utf-8")

        workflow = root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow.read_text(encoding="utf-8")
        workflow.write_text(
            original_workflow.replace(
                "Run Phase 6 hexdump perf gate",
                "Run Phase 6 hexdump replay gate",
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if ".github/workflows/zigux-bootstrap.yml" not in str(exc):
                raise AssertionError(f"unexpected workflow failure: {exc}") from exc
        else:
            raise AssertionError("expected workflow failure")
        workflow.write_text(original_workflow, encoding="utf-8")

        workflow.write_text(
            original_workflow
            + "- name: Run Phase 6 hexdump perf gate\n"
            + "        run: zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all\n",
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if ".github/workflows/zigux-bootstrap.yml" not in str(exc):
                raise AssertionError(
                    f"unexpected workflow duplicate failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected workflow duplicate failure")
        workflow.write_text(original_workflow, encoding="utf-8")

        makefile = root / "zigux/Makefile"
        original_makefile = makefile.read_text(encoding="utf-8")
        makefile.write_text(
            original_makefile.replace(
                "phase6-hexdump-perf",
                "phase6-hexdump-bench",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/Makefile" not in str(exc):
                raise AssertionError(f"unexpected Makefile failure: {exc}") from exc
        else:
            raise AssertionError("expected Makefile failure")
        makefile.write_text(original_makefile, encoding="utf-8")

        makefile.write_text(
            original_makefile
            + "\nphase6-hexdump-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe\n",
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/Makefile" not in str(exc):
                raise AssertionError(
                    f"unexpected Makefile duplicate failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected Makefile duplicate failure")
        makefile.write_text(original_makefile, encoding="utf-8")

        tests_readme = root / "zigux/tests/README.md"
        original_tests_readme = tests_readme.read_text(encoding="utf-8")
        tests_readme.write_text(
            original_tests_readme.replace(
                "phase6_hexdump_perf.zig",
                "phase6_hexdump_bench.zig",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/README.md" not in str(exc):
                raise AssertionError(f"unexpected tests README failure: {exc}") from exc
        else:
            raise AssertionError("expected tests README failure")
        tests_readme.write_text(original_tests_readme, encoding="utf-8")

        base64_tests = root / "zigux/tests/phase6_base64.zig"
        original_base64_tests = base64_tests.read_text(encoding="utf-8")
        base64_tests.write_text(
            original_base64_tests.replace(
                'test "phase 6 base64 variant decode parity keeps bytes and decode aligned with kernel mappings"',
                'test "phase 6 base64 variant decode parity stays aligned"',
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_base64.zig" not in str(exc):
                raise AssertionError(
                    f"unexpected base64 replay failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected base64 replay failure")
        base64_tests.write_text(original_base64_tests, encoding="utf-8")

        bsearch_tests = root / "zigux/tests/phase6_bsearch.zig"
        original_bsearch_tests = bsearch_tests.read_text(encoding="utf-8")
        bsearch_tests.write_text(
            original_bsearch_tests.replace(
                'test "phase 6 bsearch accepts runtime-selected raw c abi comparator pointers"',
                'test "phase 6 bsearch accepts runtime-selected raw comparator pointers"',
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_bsearch.zig" not in str(exc):
                raise AssertionError(
                    f"unexpected bsearch replay failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected bsearch replay failure")
        bsearch_tests.write_text(original_bsearch_tests, encoding="utf-8")

        checksum_slice = root / "Documentation/zigux/phase6-checksum-slice.md"
        original_checksum_slice = checksum_slice.read_text(encoding="utf-8")
        checksum_slice.write_text(
            original_checksum_slice.replace(
                "`replaceByDiff`",
                "`replaceByDelta`",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/phase6-checksum-slice.md" not in str(exc):
                raise AssertionError(
                    f"unexpected checksum slice failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected checksum slice failure")
        checksum_slice.write_text(original_checksum_slice, encoding="utf-8")

        hexdump_slice = root / "Documentation/zigux/phase6-hexdump-slice.md"
        original_hexdump_slice = hexdump_slice.read_text(encoding="utf-8")
        hexdump_slice.write_text(
            original_hexdump_slice.replace(
                "`16B-ascii-g8`",
                "`16B-ascii-g16`",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/phase6-hexdump-slice.md" not in str(exc):
                raise AssertionError(
                    f"unexpected hexdump slice failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected hexdump slice failure")
        hexdump_slice.write_text(original_hexdump_slice, encoding="utf-8")

        checksum_tests = root / "zigux/tests/phase6_checksum.zig"
        original_checksum_tests = checksum_tests.read_text(encoding="utf-8")
        checksum_tests.write_text(
            original_checksum_tests.replace(
                'test "pseudo header accumulation matches the fixture-backed reference checksum"',
                'test "pseudo header accumulation matches the reference checksum"',
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_checksum.zig" not in str(exc):
                raise AssertionError(
                    f"unexpected checksum replay failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected checksum replay failure")
        checksum_tests.write_text(original_checksum_tests, encoding="utf-8")

        checksum_perf = root / "zigux/tests/phase6_checksum_perf.zig"
        original_checksum_perf = checksum_perf.read_text(encoding="utf-8")
        checksum_perf.write_text(
            original_checksum_perf.replace(
                "PHASE6_CHECKSUM_PERF={s}",
                "PHASE6_CHECKSUM_BENCH={s}",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_checksum_perf.zig" not in str(exc):
                raise AssertionError(
                    f"unexpected checksum perf failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected checksum perf failure")
        checksum_perf.write_text(original_checksum_perf, encoding="utf-8")

        checksum_perf.write_text(
            original_checksum_perf.replace(
                ".max_slowdown_pct = 150,",
                ".max_slowdown_pct = 175,",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_checksum_perf.zig" not in str(exc):
                raise AssertionError(
                    f"unexpected checksum perf threshold failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected checksum perf threshold failure")
        checksum_perf.write_text(original_checksum_perf, encoding="utf-8")

        checksum_vectors = root / "zigux/tests/fixtures/phase6_checksum_vectors.zig"
        original_checksum_vectors = checksum_vectors.read_text(encoding="utf-8")
        checksum_vectors.write_text(
            original_checksum_vectors.replace(
                '.name = "odd split"',
                '.name = "middle split"',
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/fixtures/phase6_checksum_vectors.zig" not in str(exc):
                raise AssertionError(
                    f"unexpected checksum fixture failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected checksum fixture failure")
        checksum_vectors.write_text(original_checksum_vectors, encoding="utf-8")

        hexdump_tests = root / "zigux/tests/phase6_hexdump.zig"
        original_hexdump_tests = hexdump_tests.read_text(encoding="utf-8")
        hexdump_tests.write_text(
            original_hexdump_tests.replace(
                'test "phase 6 hexdump perf fixture packet stays in sync"',
                'test "phase 6 hexdump perf packet stays in sync"',
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_hexdump.zig" not in str(exc):
                raise AssertionError(
                    f"unexpected hexdump replay failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected hexdump replay failure")
        hexdump_tests.write_text(original_hexdump_tests, encoding="utf-8")

        hexdump_vectors = root / "zigux/tests/fixtures/phase6_hexdump_vectors.zig"
        original_hexdump_vectors = hexdump_vectors.read_text(encoding="utf-8")
        hexdump_vectors.write_text(
            original_hexdump_vectors.replace(
                '.label = "16B-ascii-g8"',
                '.label = "16B-ascii-g16"',
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/fixtures/phase6_hexdump_vectors.zig" not in str(exc):
                raise AssertionError(
                    f"unexpected hexdump fixture failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected hexdump fixture failure")
        hexdump_vectors.write_text(original_hexdump_vectors, encoding="utf-8")

        hexdump_perf = root / "zigux/tests/phase6_hexdump_perf.zig"
        original_hexdump_perf = hexdump_perf.read_text(encoding="utf-8")
        hexdump_perf.write_text(
            original_hexdump_perf.replace(
                "PHASE6_HEXDUMP_PERF={s}",
                "PHASE6_HEXDUMP_BENCH={s}",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_hexdump_perf.zig" not in str(exc):
                raise AssertionError(
                    f"unexpected hexdump perf failure: {exc}"
                ) from exc
        else:
            raise AssertionError("expected hexdump perf failure")
        hexdump_perf.write_text(original_hexdump_perf, encoding="utf-8")

    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 shared surface looks aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
