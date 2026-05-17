#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 HVC verify-helper packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

FILES = {
    "verify_helper": "drivers/tty/hvc/hvc_console_verify.zig",
    "cleanup_replay": "zigux/tests/phase11_hvc_cleanup.zig",
}

VERIFY_HELPER_MARKERS = [
    'test "hvc_console verify keeps final-close teardown handoff ordering explicit" {',
    'test "hvc_console verify keeps hung-up and detached teardown matrix truthful" {',
    'test "hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding" {',
    'test "hvc_console verify keeps remove handoff explicit when tty is already absent" {',
    'test "hvc_console verify keeps cleanup prerequisite failures explicit" {',
    "try std.testing.expect(remove.clears_console_slot_binding);",
    "try std.testing.expect(remove.keeps_irq_for_followup_hangup);",
    "try std.testing.expect(remove.teardown_via_hangup_pending);",
    "try std.testing.expect(!tty_gone_remove.tty_vhangup_requested);",
    "try std.testing.expect(!tty_gone_remove.host_io_pending);",
    "try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{",
    "try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{",
    "try std.testing.expectError(error.ConsoleUnavailable, console.summarizeCleanupHandoff(.{}));",
    "try std.testing.expectError(error.ConsoleUnavailable, console.summarizeRemoveHandoff(.{}));",
]

CLEANUP_REPLAY_MARKERS = [
    'test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable" {',
    "const final_cleanup = try console.summarizeCleanupHandoff(.{});",
    "try std.testing.expect(final_cleanup.tty_port_put_requested);",
    "try std.testing.expect(final_cleanup.drops_tty_port_reference);",
    "const hangup_cleanup = try console.summarizeCleanupHandoff(.{",
    ".hung_up = true,",
    "try std.testing.expect(hangup_cleanup.close_skipped);",
    "try std.testing.expect(!hangup_cleanup.final_close);",
    "try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{",
    "try std.testing.expectError(error.CleanupRequiresTtyPortReference, console.summarizeCleanupHandoff(.{",
    "_ = console.teardown();",
    "try std.testing.expectError(error.ConsoleUnavailable, console.summarizeCleanupHandoff(.{}));",
]


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def run_check(root: Path) -> None:
    expect_markers("verify_helper", read_text(root, FILES["verify_helper"]), VERIFY_HELPER_MARKERS)
    expect_markers("cleanup_replay", read_text(root, FILES["cleanup_replay"]), CLEANUP_REPLAY_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["verify_helper"], "\n".join(VERIFY_HELPER_MARKERS) + "\n")
    write(root / FILES["cleanup_replay"], "\n".join(CLEANUP_REPLAY_MARKERS) + "\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_verify_helper_packet_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        cases = [
            ("missing_verify_test", "verify_helper", VERIFY_HELPER_MARKERS[0]),
            ("missing_remove_branch", "verify_helper", VERIFY_HELPER_MARKERS[8]),
            ("missing_cleanup_replay", "cleanup_replay", CLEANUP_REPLAY_MARKERS[2]),
            ("missing_cleanup_unavailable", "cleanup_replay", CLEANUP_REPLAY_MARKERS[-1]),
        ]
        for case_name, label, marker in cases:
            root = tmpdir / case_name
            shutil.copytree(fixture, root, dirs_exist_ok=True)
            path = root / FILES[label]
            write(path, path.read_text(encoding="utf-8").replace(marker, "", 1))
            expect_failure(root, marker)

        missing_file_case = tmpdir / "missing_cleanup_file"
        shutil.copytree(fixture, missing_file_case, dirs_exist_ok=True)
        (missing_file_case / FILES["cleanup_replay"]).unlink()
        expect_failure(missing_file_case, FILES["cleanup_replay"])

        print("PHASE11_HVC_VERIFY_HELPER_PACKET_SELF_TEST=pass")
        print("PHASE11_HVC_VERIFY_HELPER_PACKET_SELF_TEST_CASE_COUNT=5")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_HVC_VERIFY_HELPER_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_VERIFY_HELPER_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
