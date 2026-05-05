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
        "- `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, and `make -C zigux phase6` now keep the current base64, bsearch, checksum, and hexdump helper bundle reviewable through the shared surface checker, the bundled replay, and the Linux-style helper lane together, so new helper slices should only land when that shared packet stays green as one unit.",
    ],
    "Documentation/zigux/phase6-base64-slice.md": [
        "- `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- shared kernel-derived encode, decode, variant, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig`",
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
    ],
    "scripts/zigux/README.md": [
        "- the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
        "- `make -C zigux phase6-validate` keeps the shared Phase 6 surface checker wired through the Zigux convenience target.",
        "- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.",
        "- `make -C zigux phase6` keeps that same shared-surface check plus bundled helper replay wired through the Zigux convenience target.",
        "- there is no separate shared `validate-phase6.py`, external portability checker packet beyond `check-phase6-shared-surface.py`, or aggregated `phase6-perf` target on `master`; the shipped dedicated perf replay is `make -C zigux phase6-checksum-perf`, which keeps the checksum slowdown ceiling wired into a Linux-style entrypoint without overstating perf coverage for the rest of the Phase 6 helper packet.",
    ],
    "zigux/tests/README.md": [
        "- keep the shared Phase 6 leaf-helper packet wired through `zigux/tests/phase6_build.zig`, including `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, so the landed `base64`, `bsearch`, `checksum`, and `hexdump` bundle stays reviewable through one bounded helper gate, and keep `zigux/tests/phase6_checksum_perf.zig` plus `make -C zigux phase6-checksum-perf` explicit as the dedicated checksum-only perf route rather than implying a broader Phase 6 packet-wide perf target",
    ],
    "Documentation/zigux/review-checklist.md": [
        "- if the change touches the shared Phase 6 leaf-helper packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-hexdump-slice.md`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/Makefile`, and `make -C zigux phase6` still agree on the same bundled `base64`, `bsearch`, `checksum`, and `hexdump` helper packet without implying a removed shared `validate-phase6.py`, external parity checker, or `phase6-perf` route?",
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
    ],
    "zigux/tests/phase6_bsearch.zig": [
        "test \"phase 6 bsearch honors comparator-driven descending order\" {",
        "test \"phase 6 bsearch supports string keys against sorted records\" {",
        "test \"phase 6 bsearch keeps representative lookup work inside a binary-search budget\" {",
        "test \"phase 6 bsearch raw lookup returns null for empty input without invoking the comparator\" {",
        "test \"phase 6 bsearch raw lookup keeps representative work inside a binary-search budget\" {",
        "test \"phase 6 bsearch accepts runtime-selected native comparator pointers\" {",
        "test \"phase 6 bsearch accepts runtime-selected c abi comparator pointers\" {",
        "test \"phase 6 bsearch accepts runtime-selected raw native comparator pointers\" {",
        "test \"phase 6 bsearch accepts runtime-selected raw c abi comparator pointers\" {",
    ],
    "zigux/tests/fixtures/phase6_base64_vectors.zig": [
        "pub const standard_cases = [_]EncodeCase{",
        "pub const variant_cases = [_]VariantCase{",
        "pub const standard_decode_cases = [_]DecodeCase{",
        "pub const invalid_decode_cases = [_]InvalidDecodeCase{",
        "pub const variant_decode_cases = [_]DecodeCase{",
    ],
    "zigux/tests/phase6_checksum_perf.zig": [
        "const perf_cases = [_]PerfCase{",
        ".label = \"64B\"",
        ".label = \"1501B\"",
        ".max_slowdown_pct = 150,",
        "try stdout_writer.interface.print(\"PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n\", .{perf_cases.len});",
        "try stdout_writer.interface.print(\"PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\\n\", .{ case.label, case.max_slowdown_pct });",
        "try stdout_writer.interface.print(\"PHASE6_CHECKSUM_PERF={s}\\n\", .{if (failed) \"fail\" else \"pass\"});",
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

        bsearch_test = root / "zigux/tests/phase6_bsearch.zig"
        original_bsearch_test = bsearch_test.read_text(encoding="utf-8")
        bsearch_test.write_text(
            original_bsearch_test.replace(
                'test "phase 6 bsearch accepts runtime-selected raw c abi comparator pointers" {',
                'test "phase 6 bsearch accepts raw comparator pointers" {',
            ),
            encoding="utf-8",
        )
        try:
            run_checks(root)
        except ValidationError as exc:
            if "zigux/tests/phase6_bsearch.zig" not in str(exc):
                raise AssertionError(f"unexpected bsearch test failure: {exc}") from exc
        else:
            raise AssertionError("expected bsearch test failure")

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
