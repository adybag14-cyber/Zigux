#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 HVC verify-helper packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileExpectation:
    relative_path: str
    required_fragments: tuple[str, ...]


FILE_EXPECTATIONS = (
    FileExpectation(
        "drivers/tty/hvc/hvc_console_verify.zig",
        (
            "pub const CleanupTrigger = enum",
            "final_close_only",
            "hangup_only",
            "final_close_and_hangup",
            "pub const CleanupPrerequisiteSummary = struct",
            "trigger: CleanupTrigger",
            'test "hvc_console verify keeps hangup-only cleanup prerequisites explicit"',
            'test "hvc_console verify keeps cleanup prerequisite failures explicit"',
            'test "hvc_console verify keeps attached remove handoff explicit before tty detach"',
            'test "hvc_console verify keeps remove handoff explicit when tty is already absent"',
            'test "hvc_console verify keeps non-kernel sysrq literal fallback from implying notifier callbacks"',
        ),
    ),
    FileExpectation(
        "zigux/tests/phase11_hvc_cleanup.zig",
        (
            "pub const CleanupTrigger = enum",
            "final_close_only",
            "hangup_only",
            "final_close_and_hangup",
            "trigger: CleanupTrigger",
            "summary.trigger",
            "summary.trigger == .final_close_only",
            "summary.trigger == .hangup_only",
            "summary.trigger == .final_close_and_hangup",
        ),
    ),
)


class ValidationError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {relative_path}") from exc


def validate(root: Path) -> None:
    for expectation in FILE_EXPECTATIONS:
        text = read_text(root, expectation.relative_path)
        for fragment in expectation.required_fragments:
            if fragment not in text:
                raise ValidationError(
                    f"{expectation.relative_path} is missing required fragment: {fragment!r}"
                )


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path) -> None:
    write_text(
        root,
        "drivers/tty/hvc/hvc_console_verify.zig",
        "\n".join(
            (
                "pub const CleanupTrigger = enum {",
                "    final_close_only,",
                "    hangup_only,",
                "    final_close_and_hangup,",
                "};",
                "pub const CleanupPrerequisiteSummary = struct {",
                "    trigger: CleanupTrigger,",
                "};",
                'test "hvc_console verify keeps hangup-only cleanup prerequisites explicit" {}',
                'test "hvc_console verify keeps cleanup prerequisite failures explicit" {}',
                'test "hvc_console verify keeps attached remove handoff explicit before tty detach" {}',
                'test "hvc_console verify keeps remove handoff explicit when tty is already absent" {}',
                'test "hvc_console verify keeps non-kernel sysrq literal fallback from implying notifier callbacks" {}',
            )
        )
        + "\n",
    )
    write_text(
        root,
        "zigux/tests/phase11_hvc_cleanup.zig",
        "\n".join(
            (
                "pub const CleanupTrigger = enum {",
                "    final_close_only,",
                "    hangup_only,",
                "    final_close_and_hangup,",
                "};",
                "const CleanupSummary = struct {",
                "    trigger: CleanupTrigger,",
                "};",
                "test \"phase11 hvc cleanup keeps explicit cleanup triggers reviewable\" {",
                "    const summary = CleanupSummary{ .trigger = .final_close_only };",
                "    _ = summary.trigger;",
                "    _ = summary.trigger == .final_close_only;",
                "    _ = summary.trigger == .hangup_only;",
                "    _ = summary.trigger == .final_close_and_hangup;",
                "}",
            )
        )
        + "\n",
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        validate(root)
    except ValidationError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r} in {exc!r}") from exc
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> int:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase11-hvc-verify-packet-"))
    total_cases = 0
    try:
        make_fixture(temp_dir)
        validate(temp_dir)
        total_cases += 1

        verify_file = temp_dir / "drivers/tty/hvc/hvc_console_verify.zig"
        verify_text = verify_file.read_text(encoding="utf-8")
        verify_file.write_text(
            verify_text.replace(
                'test "hvc_console verify keeps cleanup prerequisite failures explicit" {}\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(temp_dir, "cleanup prerequisite failures explicit")
        total_cases += 1

        make_fixture(temp_dir)
        verify_file = temp_dir / "drivers/tty/hvc/hvc_console_verify.zig"
        verify_text = verify_file.read_text(encoding="utf-8")
        verify_file.write_text(
            verify_text.replace(
                'test "hvc_console verify keeps remove handoff explicit when tty is already absent" {}\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(temp_dir, "tty is already absent")
        total_cases += 1

        make_fixture(temp_dir)
        cleanup_file = temp_dir / "zigux/tests/phase11_hvc_cleanup.zig"
        cleanup_text = cleanup_file.read_text(encoding="utf-8")
        cleanup_file.write_text(
            cleanup_text.replace("    trigger: CleanupTrigger,\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(temp_dir, "trigger: CleanupTrigger")
        total_cases += 1

        make_fixture(temp_dir)
        cleanup_file = temp_dir / "zigux/tests/phase11_hvc_cleanup.zig"
        cleanup_text = cleanup_file.read_text(encoding="utf-8")
        cleanup_file.write_text(
            cleanup_text.replace("    _ = summary.trigger == .final_close_and_hangup;\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(temp_dir, "summary.trigger == .final_close_and_hangup")
        total_cases += 1

        make_fixture(temp_dir)
        verify_file = temp_dir / "drivers/tty/hvc/hvc_console_verify.zig"
        verify_text = verify_file.read_text(encoding="utf-8")
        verify_file.write_text(
            verify_text.replace(
                'test "hvc_console verify keeps non-kernel sysrq literal fallback from implying notifier callbacks" {}\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(temp_dir, "non-kernel sysrq literal fallback")
        total_cases += 1
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"PHASE11_HVC_VERIFY_PACKET_SELF_TEST=pass cases={total_cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 11 HVC verify-helper packet for teardown drift."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to the Zigux repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in fixture cases instead of validating a repository checkout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    try:
        validate(Path(args.repo_root).resolve())
    except ValidationError as exc:
        print(f"PHASE11_HVC_VERIFY_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_VERIFY_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
