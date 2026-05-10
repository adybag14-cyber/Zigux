#!/usr/bin/env python3

"""Fail-closed Phase 6 checksum packet review-surface checks."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


REQUIRED_SNIPPETS = {
    "Documentation/zigux/phase6-checksum-slice.md": [
        "`PHASE6_SLICE=checksum-leaf-helper`",
        "`zigux/tests/phase6_checksum_c_parity.zig`",
        "`scripts/zigux/check-phase6-checksum-c-parity.py`",
        "`zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`",
        "`make -C zigux phase6-checksum-perf`",
        "`replaceByDiff`",
        "`tcpUdpV6Nofold`",
    ],
    "Documentation/zigux/phase6-helper-parity-catalog.md": [
        "`lib/checksum.c`",
        "`zigux/tests/phase6_checksum.zig`",
        "`zigux/tests/phase6_checksum_c_parity.zig`",
        "`zigux/tests/phase6_checksum_perf.zig`",
        "`zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`",
        "`scripts/zigux/check-phase6-checksum-c-parity.py`",
        "`make -C zigux phase6-checksum-perf`",
    ],
    "Documentation/zigux/phase6-perf-gate-survey.md": [
        "`make -C zigux phase6-checksum-perf`",
        "`make -C zigux phase6-perf` now exists as a narrow convenience wrapper for `phase6-checksum-perf` plus `phase6-hexdump-perf`",
        "`zigux/tests/phase6_checksum_perf.zig`",
        "`64B` at `iterations = 200_000`",
        "`1501B` at `iterations = 12_000`",
    ],
    "zigux/tests/phase6_checksum.zig": [
        'test "blockSub reverses blockAdd across odd and even fragment boundaries" {',
        'test "pseudo header accumulation matches the fixture-backed reference checksum" {',
        'test "ipv6 pseudo header accumulation stays aligned across representative lanes" {',
    ],
    "zigux/tests/phase6_checksum_c_parity.zig": [
        'try writer.print("compute\\t{s}\\t0x{x:0>4}\\n", .{ case.name, checksum.compute(case.bytes) });',
        'try writer.print("tcpudp-v6-nofold\\tudp pseudo header v6\\t0x{x:0>8}\\n",',
        'try writer.print("replace4\\tipv4-saddr\\t0x{x:0>4}\\n", .{checksum.replace4(checksum_before_addr_change, old_saddr, new_saddr)});',
    ],
    "zigux/tests/phase6_checksum_perf.zig": [
        '.{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150',
        '.{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150',
        "error.ChecksumPerfMatrixMismatch",
    ],
    "zigux/tests/fixtures/phase6_checksum_vectors.zig": [
        'pub const perf_cases = [_]PerfCase{',
        '.label = "64B"',
        '.label = "1501B"',
        'test "phase 6 checksum perf fixture packet stays bounded to the documented matrix" {',
    ],
    "scripts/zigux/check-phase6-checksum-c-parity.py": [
        'assert_equal("expected_surface_case_count", expected_case_count, 41)',
        'print("PHASE6_CHECKSUM_C_PARITY_SELF_TEST=pass")',
        'print("PHASE6_CHECKSUM_C_PARITY_SELF_TEST_CASE_COUNT=12")',
    ],
    "zigux/tests/phase6_build.zig": [
        '.name = "phase6-checksum-tests"',
        '.root_source_file = b.path("phase6_checksum_perf.zig")',
        '.name = "phase6-checksum-perf"',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
    ],
    "zigux/Makefile": [
        "PHONY += phase6-validate phase6-test phase6-hexdump-test phase6-perf phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6",
        "phase6-checksum-perf:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6-perf: phase6-checksum-perf phase6-hexdump-perf",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "run: python3 scripts/zigux/check-phase6-shared-surface.py --self-test",
        "run: python3 scripts/zigux/check-phase6-shared-surface.py",
        "run: zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    ],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def validate(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for relative_path, snippets in REQUIRED_SNIPPETS.items():
        text = read_text(repo_root / relative_path)
        for snippet in snippets:
            if snippet not in text:
                missing.append(f"{relative_path}: {snippet}")
    return missing


def write_fixture(root: Path) -> None:
    for relative_path, snippets in REQUIRED_SNIPPETS.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(snippets) + "\n", encoding="utf-8")


def expect_failure(repo_root: Path, needle: str) -> None:
    missing = validate(repo_root)
    if needle not in missing:
        raise ValidationError(f"expected self-test failure for {needle!r}, got {missing!r}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_fixture(root)

        missing = validate(root)
        if missing:
            raise ValidationError(f"self-test positive case failed: {missing!r}")

        slice_path = root / "Documentation/zigux/phase6-checksum-slice.md"
        slice_text = slice_path.read_text(encoding="utf-8")
        removed = "`make -C zigux phase6-checksum-perf`"
        slice_path.write_text(slice_text.replace(removed, "", 1), encoding="utf-8")
        expect_failure(root, f"Documentation/zigux/phase6-checksum-slice.md: {removed}")

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8")
        removed_workflow = "run: zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all"
        workflow_path.write_text(workflow_text.replace(removed_workflow, "", 1), encoding="utf-8")
        expect_failure(root, f".github/workflows/zigux-bootstrap.yml: {removed_workflow}")

        print("PHASE6_CHECKSUM_PACKET_SELF_TEST=pass")
        print("PHASE6_CHECKSUM_PACKET_REQUIRED_FILE_COUNT=%d" % len(REQUIRED_SNIPPETS))
        print(
            "PHASE6_CHECKSUM_PACKET_REQUIRED_SNIPPET_COUNT=%d"
            % sum(len(snippets) for snippets in REQUIRED_SNIPPETS.values())
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = validate(Path(args.repo_root).resolve())
    if missing:
        print("PHASE6_CHECKSUM_PACKET=fail")
        print("MISSING_PHASE6_CHECKSUM_PACKET_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE6_CHECKSUM_PACKET_MARKERS_END")
        return 1

    print("PHASE6_CHECKSUM_PACKET=pass")
    print("PHASE6_CHECKSUM_PACKET_REQUIRED_FILE_COUNT=%d" % len(REQUIRED_SNIPPETS))
    print(
        "PHASE6_CHECKSUM_PACKET_REQUIRED_SNIPPET_COUNT=%d"
        % sum(len(snippets) for snippets in REQUIRED_SNIPPETS.values())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
