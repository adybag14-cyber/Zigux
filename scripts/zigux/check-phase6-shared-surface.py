#!/usr/bin/env python3
"""Fail-closed Phase 6 shared-surface checks for the current helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


REQUIRED_SNIPPETS = {
    "Documentation/zigux/README.md": [
        "- `Documentation/zigux/phase6-base64-slice.md`",
        "- `Documentation/zigux/phase6-bsearch-slice.md`",
        "- `Documentation/zigux/phase6-checksum-slice.md`",
        "- `Documentation/zigux/phase6-hexdump-slice.md`",
        "- `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/Makefile`, `make -C zigux phase6-validate`, `make -C zigux phase6`, and `make -C zigux phase6-checksum-perf` now keep the current base64, bsearch, checksum, and hexdump helper bundle reviewable through the shared surface checker, the bundled replay, the checksum-only perf gate, and the Linux-style helper lane together, so new helper slices should only land when that shared packet stays green as one unit.",
    ],
    "Documentation/zigux/phase6-base64-slice.md": [
        "- `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- shared kernel-derived encode, decode, variant, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- invalid-input rejection through both `bytes` and `decode` for malformed, embedded-NUL, and variant-mismatched decode inputs",
        "- exhaustive canonical tail acceptance for padded and unpadded std, URL-safe, and IMAP decode paths",
        "- a separate external C-vs-Zig parity packet on `master`",
    ],
    "Documentation/zigux/phase6-bsearch-slice.md": [
        "- comparator-driven descending-order lookup without widening the helper surface",
        "- heterogeneous-key lookup where the key type differs from the element type",
        "- representative lookup work stays inside a bounded binary-search comparison budget for both typed and raw lookup paths",
        "- runtime-selected native comparator pointer parity",
        "- runtime-selected C ABI comparator pointer parity",
        "- runtime-selected raw native comparator pointer parity",
        "- runtime-selected raw C ABI comparator pointer parity, including pointer-return duplicate hits and null misses",
    ],
    "Documentation/zigux/phase6-checksum-slice.md": [
        "- `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- fixture-backed checksum vectors for empty, even, odd, and carry-heavy inputs",
        "- a tiny KUnit-inspired carry-discipline matrix covering all-ones and no-spurious-carry seeded cases",
        "- pseudo-header accumulation parity between `tcpUdpNofold` and manual `partial` plus `blockAdd`",
        "- incremental checksum replacement parity for payload word updates, 16-bit IPv4 header field replacement, diff-based checksum repair, and 32-bit IPv4 address replacement",
        "- helper-local perf smoke on patterned 64-byte and 1501-byte payloads keeps `checksum.compute` within a 150% slowdown ceiling versus the bounded reference loop",
        "- `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
        "- `make -C zigux phase6-checksum-perf`",
        "- The fixture layer stays intentionally small.",
    ],
    "Documentation/zigux/phase6-hexdump-slice.md": [
        "- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`",
        "- serialized fixture vectors derived from `lib/test_hexdump.c`",
        "- serialized required-length vectors for `hexDumpLineLength` and zero-buffer `hexDumpToBuffer`",
        "- native-endian grouped output for 2, 4, and 8 byte cases",
        "- grouped ASCII output stays intact when buffer capacity is exact",
        "- a machine-readable four-case perf fixture packet kept alongside the hexdump vectors so grouped formatter follow-ups reuse one bounded case roster instead of growing ad hoc",
        "- `16B-plain-g1`",
        "- `32B-ascii-g2`",
        "- `16B-ascii-g4`",
        "- `16B-ascii-g8`",
    ],
    "scripts/zigux/README.md": [
        "- the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
        "- `make -C zigux phase6-validate` keeps the shared Phase 6 surface checker wired through the Zigux convenience target.",
        "- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.",
        "- `make -C zigux phase6` keeps that same shared-surface check plus bundled helper replay wired through the Zigux convenience target.",
        "- there is no separate shared `validate-phase6.py`, external portability checker packet beyond `check-phase6-shared-surface.py`, or aggregated `phase6-perf` target on `master`; the shipped dedicated perf replay is `make -C zigux phase6-checksum-perf`, which keeps the checksum slowdown ceiling wired into a Linux-style entrypoint without overstating perf coverage for the rest of the Phase 6 helper packet.",
    ],
    "zigux/tests/README.md": [
        "- keep the shared Phase 6 leaf-helper packet wired through `zigux/tests/phase6_build.zig`, including `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, so the landed `base64`, `bsearch`, `checksum`, and `hexdump` bundle stays reviewable through one bounded helper gate, and keep `zigux/tests/phase6_checksum_perf.zig` plus `make -C zigux phase6-checksum-perf` explicit as the dedicated checksum-only perf route rather than implying a broader Phase 6 packet-wide perf target",
    ],
    "Documentation/zigux/review-checklist.md": [
        "- if the change touches the shared Phase 6 leaf-helper packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-hexdump-slice.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, `make -C zigux phase6`, and `make -C zigux phase6-checksum-perf` still agree on the same bundled `base64`, `bsearch`, `checksum`, and `hexdump` helper packet without implying a removed shared `validate-phase6.py`, a broader external parity checker beyond `check-phase6-shared-surface.py`, or an aggregated `phase6-perf` route?",
    ],
    "zigux/tests/phase6_build.zig": [
        "const test_step = b.step(\"test\", \"Run Phase 6 leaf helper tests\");",
        ".name = \"phase6-base64-tests\"",
        ".name = \"phase6-bsearch-tests\"",
        ".name = \"phase6-checksum-tests\"",
        ".root_source_file = b.path(\"phase6_checksum_perf.zig\"),",
        "const checksum_perf_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum perf gate\");",
        ".name = \"phase6-hexdump-tests\"",
    ],
    "zigux/tests/phase6_base64.zig": [
        "const fixtures = @import(\"fixtures/phase6_base64_vectors.zig\");",
        "for (fixtures.standard_cases) |case| {",
        "for (fixtures.variant_cases) |case| {",
        "for (fixtures.standard_decode_cases) |case| {",
        "for (fixtures.invalid_decode_cases) |case| {",
        "for (fixtures.variant_decode_cases) |case| {",
        "test \"phase 6 base64 reports destination bounds before encoding\" {",
        "test \"phase 6 base64 reports destination bounds before decoding\" {",
    ],
    "zigux/tests/phase6_bsearch.zig": [
        "test \"phase 6 bsearch finds integer keys across the slice\" {",
        "test \"phase 6 bsearch rejects missing integer keys without widening the contract\" {",
        "test \"phase 6 bsearch honors comparator-driven descending order\" {",
        "test \"phase 6 bsearch supports string keys against sorted records\" {",
        "test \"phase 6 bsearch mutable typed lookup supports write-through\" {",
        "test \"phase 6 bsearch treats duplicate keys as found-or-null without claiming stable selection\" {",
        "test \"phase 6 bsearch keeps representative work inside a binary-search budget\" {",
        "test \"phase 6 bsearch raw lookup returns null for empty input without invoking the comparator\" {",
        "test \"phase 6 bsearch raw lookup keeps representative work inside a binary-search budget\" {",
        "test \"phase 6 bsearch accepts runtime-selected native comparator pointers\" {",
        "test \"phase 6 bsearch accepts runtime-selected c abi comparator pointers\" {",
        "test \"phase 6 bsearch accepts runtime-selected raw native comparator pointers\" {",
        "test \"phase 6 bsearch mutable raw lookup supports descending write-through\" {",
        "test \"phase 6 bsearch accepts runtime-selected raw c abi comparator pointers\" {",
        "test \"phase 6 bsearch mutable raw c abi lookup supports write-through\" {",
    ],
    "zigux/tests/phase6_checksum.zig": [
        "test \"fixture-backed compute parity covers the current checksum vectors\" {",
        "test \"partial sums compose across the fixture split matrix\" {",
        "test \"blockSub reverses blockAdd across odd and even fragment boundaries\" {",
        "test \"seeded partial accumulation matches the fixture-backed reference\" {",
        "test \"kunit-inspired carry discipline stays stable on the helper surface\" {",
        "test \"fixture-backed negate cases keep the public checksum helper reviewable\" {",
        "test \"pseudo header accumulation matches the fixture-backed reference checksum\" {",
        "test \"incremental checksum replacement helpers match direct recomputation\" {",
    ],
    "zigux/tests/phase6_hexdump.zig": [
        "test \"phase 6 hexdump serialized linux-derived vectors stay in sync\" {",
        "try std.testing.expectEqual(@as(usize, 10), fixtures.parity_cases.len);",
        "test \"phase 6 hexdump serialized overflow vectors stay in sync\" {",
        "test \"phase 6 hexdump serialized required-length vectors stay in sync\" {",
        "try std.testing.expectEqual(@as(usize, 9), fixtures.length_cases.len);",
        "test \"phase 6 hexdump perf fixture packet stays in sync\" {",
        "try std.testing.expectEqual(@as(usize, 4), fixtures.perf_cases.len);",
        "test \"phase 6 hexdump uppercase nibble helpers stay aligned with byte packing\" {",
        "test \"phase 6 hexdump parity matrix matches kernel fixture preparation\" {",
        "test \"phase 6 hexdump overflow contract matches truncation expectations\" {",
        "test \"phase 6 hexdump grouped ASCII output stays intact when buffer capacity is exact\" {",
        "test \"phase 6 hexdump covers normalization and empty-buffer edge cases\" {",
    ],
    "zigux/tests/fixtures/phase6_base64_vectors.zig": [
        "const invalid_with_nul = [_]u8{ 'Z', 'g', 0, '=' };",
        "pub const standard_cases = [_]EncodeCase{",
        "pub const variant_cases = [_]VariantCase{",
        "pub const standard_decode_cases = [_]DecodeCase{",
        '.{ .input = "Zg==", .expected = "f", .padding = true, .variant_name = "std" },',
        '.{ .input = "Zm8=", .expected = "fo", .padding = true, .variant_name = "std" },',
        '.{ .input = "Zg", .expected = "f", .padding = false, .variant_name = "std" },',
        '.{ .input = "Zm8", .expected = "fo", .padding = false, .variant_name = "std" },',
        "pub const invalid_decode_cases = [_]InvalidDecodeCase{",
        '.{ .input = "Zh==", .padding = true, .variant_name = "std" },',
        '.{ .input = "Zm9=", .padding = true, .variant_name = "std" },',
        '.{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },',
        '.{ .input = "Zh", .padding = false, .variant_name = "std" },',
        '.{ .input = "Zm9", .padding = false, .variant_name = "std" },',
        '.{ .input = invalid_with_nul[0..], .padding = false, .variant_name = "std" },',
        '.{ .input = "Zg==", .padding = false, .variant_name = "urlsafe" },',
        '.{ .input = "Zg==", .padding = false, .variant_name = "imap" },',
        "pub const variant_decode_cases = [_]DecodeCase{",
        '.{ .input = "APv_f4A=", .expected = &variant_sample, .padding = true, .variant_name = "urlsafe" },',
        '.{ .input = "APv,f4A=", .expected = &variant_sample, .padding = true, .variant_name = "imap" },',
        '.{ .input = "APv_f4A", .expected = &variant_sample, .padding = false, .variant_name = "urlsafe" },',
        '.{ .input = "APv,f4A", .expected = &variant_sample, .padding = false, .variant_name = "imap" },',
    ],
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig": [
        "pub const perf_cases = [_]PerfCase{",
        '.label = "16B-plain-g1"',
        ".max_slowdown_pct = 175,",
        '.label = "32B-ascii-g2"',
        ".max_slowdown_pct = 550,",
        '.label = "16B-ascii-g4"',
        ".max_slowdown_pct = 550,",
        '.label = "16B-ascii-g8"',
        ".max_slowdown_pct = 600,",
    ],
    "zigux/tests/phase6_checksum_perf.zig": [
        "const perf_cases = [_]PerfCase{",
        '.label = "64B"',
        '.label = "1501B"',
        ".max_slowdown_pct = 150,",
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{perf_cases.len});',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF={s}\\n", .{if (failed) "fail" else "pass"});',
    ],
    "zigux/Makefile": [
        "PHONY += phase6-validate phase6-test phase6-checksum-perf phase6",
        "phase6-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
        "phase6-checksum-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6: phase6-validate phase6-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "- name: Self-test Phase 6 shared-surface checker\n        run: python3 scripts/zigux/check-phase6-shared-surface.py --self-test",
        "- name: Check Phase 6 shared surface\n        run: python3 scripts/zigux/check-phase6-shared-surface.py",
        "- name: Run Phase 6 leaf helper tests\n        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "- name: Run Phase 6 checksum perf gate\n        run: zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    ],
}

REQUIRED_SHARED_PATHS = [
    "Documentation/zigux/phase6-bsearch-slice.md",
    "zigux/tests/phase6_bsearch.zig",
]

REQUIRED_EXISTING_PATHS = [
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
    "zigux/tests/phase6_checksum_perf.zig",
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
                raise ValidationError(f"missing expected Phase 6 marker in {rel_path}: {snippet}")

    for rel_path in REQUIRED_SHARED_PATHS:
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing expected Phase 6 shared-surface file: {rel_path}")

    for rel_path in REQUIRED_EXISTING_PATHS:
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing expected Phase 6 shared-surface file: {rel_path}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def restore_path(root: Path, rel_path: str) -> None:
    if rel_path in REQUIRED_SNIPPETS:
        write(root / rel_path, "\n".join(REQUIRED_SNIPPETS[rel_path]) + "\n")
        return
    write(root / rel_path, "present\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        for rel_path, snippets in REQUIRED_SNIPPETS.items():
            write(root / rel_path, "\n".join(snippets) + "\n")
        for rel_path in REQUIRED_SHARED_PATHS:
            path = root / rel_path
            if not path.exists():
                write(path, "present\n")
        for rel_path in REQUIRED_EXISTING_PATHS:
            path = root / rel_path
            if not path.exists():
                write(path, "present\n")

        run_checks(root)

        missing_shared_path = REQUIRED_SHARED_PATHS[0]
        (root / missing_shared_path).unlink()
        try:
            run_checks(root)
        except ValidationError as exc:
            if missing_shared_path not in str(exc):
                raise AssertionError(f"unexpected shared-path failure: {exc}") from exc
        else:
            raise AssertionError("expected shared-path failure")
        restore_path(root, missing_shared_path)

        missing_required_path = REQUIRED_EXISTING_PATHS[-1]
        (root / missing_required_path).unlink()
        try:
            run_checks(root)
        except ValidationError as exc:
            if missing_required_path not in str(exc):
                raise AssertionError(f"unexpected required-path failure: {exc}") from exc
        else:
            raise AssertionError("expected required-path failure")
        restore_path(root, missing_required_path)

        makefile = root / "zigux/Makefile"
        original_makefile = makefile.read_text(encoding="utf-8")
        makefile.write_text(original_makefile.replace("phase6: phase6-validate phase6-test", "phase6: phase6-test"), encoding="utf-8")
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/Makefile" not in str(exc):
                raise AssertionError(f"unexpected Makefile failure: {exc}") from exc
        else:
            raise AssertionError("expected Makefile failure")
        makefile.write_text(original_makefile, encoding="utf-8")

        makefile.write_text(
            original_makefile.replace(
                'phase6-checksum-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe',
                'phase6-checksum-bench:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/Makefile" not in str(exc):
                raise AssertionError(f"unexpected checksum perf target failure: {exc}") from exc
        else:
            raise AssertionError("expected checksum perf target failure")
        makefile.write_text(original_makefile, encoding="utf-8")

        workflow = root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow.read_text(encoding="utf-8")
        workflow.write_text(
            original_workflow.replace(
                "- name: Run Phase 6 checksum perf gate\n        run: zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
                "- name: Run Phase 6 checksum perf smoke\n        run: zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
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

        base64_slice = root / "Documentation/zigux/phase6-base64-slice.md"
        original_base64_slice = base64_slice.read_text(encoding="utf-8")
        base64_slice.write_text(
            original_base64_slice.replace(
                "- shared kernel-derived encode, decode, variant, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig`",
                "- shared base64 notes only",
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

        base64_slice.write_text(
            original_base64_slice.replace(
                "- invalid-input rejection through both `bytes` and `decode` for malformed, embedded-NUL, and variant-mismatched decode inputs",
                "- invalid input notes moved elsewhere",
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/phase6-base64-slice.md" not in str(exc):
                raise AssertionError(f"unexpected base64 invalid-input failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 invalid-input failure")
        base64_slice.write_text(original_base64_slice, encoding="utf-8")

        base64_slice.write_text(
            original_base64_slice.replace(
                "- exhaustive canonical tail acceptance for padded and unpadded std, URL-safe, and IMAP decode paths",
                "- canonical tail acceptance notes moved elsewhere",
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/phase6-base64-slice.md" not in str(exc):
                raise AssertionError(f"unexpected base64 canonical-tail failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 canonical-tail failure")
        base64_slice.write_text(original_base64_slice, encoding="utf-8")

        bsearch_slice = root / "Documentation/zigux/phase6-bsearch-slice.md"
        original_bsearch_slice = bsearch_slice.read_text(encoding="utf-8")
        bsearch_slice.write_text(
            original_bsearch_slice.replace(
                "- representative lookup work stays inside a bounded binary-search comparison budget for both typed and raw lookup paths",
                "- representative lookup claims are omitted",
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

        checksum_slice = root / "Documentation/zigux/phase6-checksum-slice.md"
        original_checksum_slice = checksum_slice.read_text(encoding="utf-8")
        checksum_slice.write_text(
            original_checksum_slice.replace(
                "- helper-local perf smoke on patterned 64-byte and 1501-byte payloads keeps `checksum.compute` within a 150% slowdown ceiling versus the bounded reference loop",
                "- checksum perf details are omitted",
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/phase6-checksum-slice.md" not in str(exc):
                raise AssertionError(f"unexpected checksum slice failure: {exc}") from exc
        else:
            raise AssertionError("expected checksum slice failure")
        checksum_slice.write_text(original_checksum_slice, encoding="utf-8")

        review_checklist = root / "Documentation/zigux/review-checklist.md"
        original_review_checklist = review_checklist.read_text(encoding="utf-8")
        review_checklist.write_text(
            original_review_checklist.replace(
                "`zigux/tests/phase6_checksum_perf.zig`",
                "`zigux/tests/phase6_checksum_perf_missing.zig`",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/review-checklist.md" not in str(exc):
                raise AssertionError(f"unexpected review checklist failure: {exc}") from exc
        else:
            raise AssertionError("expected review checklist failure")
        review_checklist.write_text(original_review_checklist, encoding="utf-8")

        hexdump_slice = root / "Documentation/zigux/phase6-hexdump-slice.md"
        original_hexdump_slice = hexdump_slice.read_text(encoding="utf-8")
        hexdump_slice.write_text(
            original_hexdump_slice.replace(
                "- grouped ASCII output stays intact when buffer capacity is exact",
                "- grouped ASCII output note removed",
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "Documentation/zigux/phase6-hexdump-slice.md" not in str(exc):
                raise AssertionError(f"unexpected hexdump slice failure: {exc}") from exc
        else:
            raise AssertionError("expected hexdump slice failure")
        hexdump_slice.write_text(original_hexdump_slice, encoding="utf-8")

        phase6_build = root / "zigux/tests/phase6_build.zig"
        original_phase6_build = phase6_build.read_text(encoding="utf-8")
        phase6_build.write_text(
            original_phase6_build.replace(
                'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
                'const checksum_perf_step = b.step("phase6-checksum-bench", "Run Phase 6 checksum perf gate");',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_build.zig" not in str(exc):
                raise AssertionError(f"unexpected phase6 build failure: {exc}") from exc
        else:
            raise AssertionError("expected phase6 build failure")
        phase6_build.write_text(original_phase6_build, encoding="utf-8")

        checksum_perf = root / "zigux/tests/phase6_checksum_perf.zig"
        original_checksum_perf = checksum_perf.read_text(encoding="utf-8")
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
                raise AssertionError(f"unexpected checksum perf failure: {exc}") from exc
        else:
            raise AssertionError("expected checksum perf failure")
        checksum_perf.write_text(original_checksum_perf, encoding="utf-8")

        checksum_test = root / "zigux/tests/phase6_checksum.zig"
        original_checksum_test = checksum_test.read_text(encoding="utf-8")
        checksum_test.write_text(
            original_checksum_test.replace(
                'test "pseudo header accumulation matches the fixture-backed reference checksum" {',
                'test "pseudo header coverage moved elsewhere" {',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_checksum.zig" not in str(exc):
                raise AssertionError(f"unexpected checksum test failure: {exc}") from exc
        else:
            raise AssertionError("expected checksum test failure")
        checksum_test.write_text(original_checksum_test, encoding="utf-8")

        base64_test = root / "zigux/tests/phase6_base64.zig"
        original_base64_test = base64_test.read_text(encoding="utf-8")
        base64_test.write_text(
            original_base64_test.replace(
                "for (fixtures.invalid_decode_cases) |case| {",
                "for (inline_invalid_decode_cases) |case| {",
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_base64.zig" not in str(exc):
                raise AssertionError(f"unexpected base64 test failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 test failure")
        base64_test.write_text(original_base64_test, encoding="utf-8")

        base64_test.write_text(
            original_base64_test.replace(
                'test "phase 6 base64 reports destination bounds before encoding" {',
                'test "phase 6 base64 omits encode bound checks" {',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_base64.zig" not in str(exc):
                raise AssertionError(f"unexpected base64 encode-bound failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 encode-bound failure")
        base64_test.write_text(original_base64_test, encoding="utf-8")

        base64_test.write_text(
            original_base64_test.replace(
                'test "phase 6 base64 reports destination bounds before decoding" {',
                'test "phase 6 base64 omits decode bound checks" {',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_base64.zig" not in str(exc):
                raise AssertionError(f"unexpected base64 decode-bound failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 decode-bound failure")
        base64_test.write_text(original_base64_test, encoding="utf-8")

        base64_vectors = root / "zigux/tests/fixtures/phase6_base64_vectors.zig"
        original_base64_vectors = base64_vectors.read_text(encoding="utf-8")
        base64_vectors.write_text(
            original_base64_vectors.replace(
                '.{ .input = "Zg==", .padding = false, .variant_name = "urlsafe" },',
                '.{ .input = "Zm9v", .padding = false, .variant_name = "urlsafe" },',
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/fixtures/phase6_base64_vectors.zig" not in str(exc):
                raise AssertionError(f"unexpected base64 vectors failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 vectors failure")
        base64_vectors.write_text(original_base64_vectors, encoding="utf-8")

        base64_vectors.write_text(
            original_base64_vectors.replace(
                '.{ .input = "Zg", .expected = "f", .padding = false, .variant_name = "std" },',
                '.{ .input = "Zg", .expected = "g", .padding = false, .variant_name = "std" },',
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/fixtures/phase6_base64_vectors.zig" not in str(exc):
                raise AssertionError(f"unexpected base64 canonical std failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 canonical std failure")
        base64_vectors.write_text(original_base64_vectors, encoding="utf-8")

        base64_vectors.write_text(
            original_base64_vectors.replace(
                '.{ .input = "APv,f4A=", .expected = &variant_sample, .padding = true, .variant_name = "imap" },',
                '.{ .input = "APv.f4A=", .expected = &variant_sample, .padding = true, .variant_name = "imap" },',
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/fixtures/phase6_base64_vectors.zig" not in str(exc):
                raise AssertionError(f"unexpected base64 canonical variant failure: {exc}") from exc
        else:
            raise AssertionError("expected base64 canonical variant failure")
        base64_vectors.write_text(original_base64_vectors, encoding="utf-8")

        bsearch_test = root / "zigux/tests/phase6_bsearch.zig"
        original_bsearch_test = bsearch_test.read_text(encoding="utf-8")
        bsearch_test.write_text(
            original_bsearch_test.replace(
                'test "phase 6 bsearch mutable typed lookup supports write-through" {',
                'test "phase 6 bsearch mutable typed lookup drifted" {',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_bsearch.zig" not in str(exc):
                raise AssertionError(f"unexpected bsearch mutable typed failure: {exc}") from exc
        else:
            raise AssertionError("expected bsearch mutable typed failure")
        bsearch_test.write_text(original_bsearch_test, encoding="utf-8")

        bsearch_test.write_text(
            original_bsearch_test.replace(
                'test "phase 6 bsearch treats duplicate keys as found-or-null without claiming stable selection" {',
                'test "phase 6 bsearch duplicate handling drifted" {',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_bsearch.zig" not in str(exc):
                raise AssertionError(f"unexpected bsearch duplicate failure: {exc}") from exc
        else:
            raise AssertionError("expected bsearch duplicate failure")
        bsearch_test.write_text(original_bsearch_test, encoding="utf-8")

        bsearch_test.write_text(
            original_bsearch_test.replace(
                'test "phase 6 bsearch mutable raw lookup supports descending write-through" {',
                'test "phase 6 bsearch mutable raw lookup drifted" {',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_bsearch.zig" not in str(exc):
                raise AssertionError(f"unexpected bsearch mutable raw failure: {exc}") from exc
        else:
            raise AssertionError("expected bsearch mutable raw failure")
        bsearch_test.write_text(original_bsearch_test, encoding="utf-8")

        bsearch_test.write_text(
            original_bsearch_test.replace(
                'test "phase 6 bsearch mutable raw c abi lookup supports write-through" {',
                'test "phase 6 bsearch mutable raw c abi lookup drifted" {',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_bsearch.zig" not in str(exc):
                raise AssertionError(f"unexpected bsearch mutable raw c abi failure: {exc}") from exc
        else:
            raise AssertionError("expected bsearch mutable raw c abi failure")
        bsearch_test.write_text(original_bsearch_test, encoding="utf-8")

        bsearch_test.write_text(
            original_bsearch_test.replace(
                'test "phase 6 bsearch rejects missing integer keys without widening the contract" {',
                'test "phase 6 bsearch missing-key drifted" {',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_bsearch.zig" not in str(exc):
                raise AssertionError(f"unexpected bsearch missing-key failure: {exc}") from exc
        else:
            raise AssertionError("expected bsearch missing-key failure")
        bsearch_test.write_text(original_bsearch_test, encoding="utf-8")

        hexdump_test = root / "zigux/tests/phase6_hexdump.zig"
        original_hexdump_test = hexdump_test.read_text(encoding="utf-8")
        hexdump_test.write_text(
            original_hexdump_test.replace(
                'try std.testing.expectEqual(@as(usize, 4), fixtures.perf_cases.len);',
                'try std.testing.expectEqual(@as(usize, 3), fixtures.perf_cases.len);',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_hexdump.zig" not in str(exc):
                raise AssertionError(f"unexpected hexdump test failure: {exc}") from exc
        else:
            raise AssertionError("expected hexdump test failure")
        hexdump_test.write_text(original_hexdump_test, encoding="utf-8")

        hexdump_test.write_text(
            original_hexdump_test.replace(
                'try std.testing.expectEqual(@as(usize, 10), fixtures.parity_cases.len);',
                'try std.testing.expectEqual(@as(usize, 11), fixtures.parity_cases.len);',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_hexdump.zig" not in str(exc):
                raise AssertionError(f"unexpected hexdump parity failure: {exc}") from exc
        else:
            raise AssertionError("expected hexdump parity failure")
        hexdump_test.write_text(original_hexdump_test, encoding="utf-8")

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
                raise AssertionError(f"unexpected hexdump vectors failure: {exc}") from exc
        else:
            raise AssertionError("expected hexdump vectors failure")
        hexdump_vectors.write_text(original_hexdump_vectors, encoding="utf-8")

        hexdump_vectors.write_text(
            original_hexdump_vectors.replace(
                ".max_slowdown_pct = 600,",
                ".max_slowdown_pct = 650,",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/fixtures/phase6_hexdump_vectors.zig" not in str(exc):
                raise AssertionError(f"unexpected hexdump slowdown failure: {exc}") from exc
        else:
            raise AssertionError("expected hexdump slowdown failure")

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
