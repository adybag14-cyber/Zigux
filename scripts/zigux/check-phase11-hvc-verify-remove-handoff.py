#!/usr/bin/env python3
"""Fail-close the bounded Phase 11 HVC verify-side remove-handoff branches.

This checker is intentionally narrow. It only guards the compile-local
`drivers/tty/hvc/hvc_console_verify.zig` packet that keeps the shipped
verify-side remove-handoff branches explicit when tty teardown outlives the
console binding and when the tty is already absent.

It does not claim live notifier execution, tty registration, khvcd execution,
sysrq execution, or host-backed teardown behavior.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SCRIPT_PATH = "scripts/zigux/check-phase11-hvc-verify-remove-handoff.py"
VERIFY_FILE = "drivers/tty/hvc/hvc_console_verify.zig"

VERIFY_DETACHED_BINDING_MARKERS = [
    'test "hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding" {',
    "const detached_binding = try console.summarizeRemoveHandoff(.{",
    ".console_index_registered = false,",
    ".tty_present = true,",
    "try std.testing.expect(!detached_binding.clears_console_slot_binding);",
    "try std.testing.expect(detached_binding.keeps_irq_for_followup_hangup);",
    "try std.testing.expect(detached_binding.drops_init_kref_port_reference);",
    "try std.testing.expect(detached_binding.tty_vhangup_requested);",
    "try std.testing.expect(detached_binding.tty_kref_put_after_vhangup);",
    "try std.testing.expect(detached_binding.teardown_via_hangup_pending);",
    "try std.testing.expect(detached_binding.host_io_pending);",
]

VERIFY_TTY_ABSENT_MARKERS = [
    'test "hvc_console verify keeps remove handoff explicit when tty is already absent" {',
    "const tty_gone_remove = try console.summarizeRemoveHandoff(.{",
    ".console_index_registered = true,",
    ".tty_present = false,",
    "try std.testing.expect(tty_gone_remove.clears_console_slot_binding);",
    "try std.testing.expect(!tty_gone_remove.keeps_irq_for_followup_hangup);",
    "try std.testing.expect(tty_gone_remove.drops_init_kref_port_reference);",
    "try std.testing.expect(!tty_gone_remove.tty_vhangup_requested);",
    "try std.testing.expect(!tty_gone_remove.tty_kref_put_after_vhangup);",
    "try std.testing.expect(!tty_gone_remove.teardown_via_hangup_pending);",
    "try std.testing.expect(!tty_gone_remove.host_io_pending);",
]

ALL_VERIFY_REMOVE_HANDOFF_MARKERS = (
    VERIFY_DETACHED_BINDING_MARKERS + VERIFY_TTY_ABSENT_MARKERS
)


class CheckError(RuntimeError):
    """Raised when the bounded Phase 11 packet drifts."""


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
    verify_text = read_text(root, VERIFY_FILE)
    expect_markers(
        "phase11_hvc_verify_remove_handoff.detached_binding",
        verify_text,
        VERIFY_DETACHED_BINDING_MARKERS,
    )
    expect_markers(
        "phase11_hvc_verify_remove_handoff.tty_absent",
        verify_text,
        VERIFY_TTY_ABSENT_MARKERS,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    write(root / VERIFY_FILE, "\n".join(ALL_VERIFY_REMOVE_HANDOFF_MARKERS) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected self-test failure containing {expected_fragment!r}, got {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_verify_remove_handoff_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        for index, marker in enumerate(ALL_VERIFY_REMOVE_HANDOFF_MARKERS, start=1):
            case_root = tmpdir / f"case_{index}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            verify_path = case_root / VERIFY_FILE
            verify_path.write_text(
                verify_path.read_text(encoding="utf-8").replace(marker, "__mutated__", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        print("PHASE11_HVC_VERIFY_REMOVE_HANDOFF_SELF_TEST=pass")
        print(
            "PHASE11_HVC_VERIFY_REMOVE_HANDOFF_SELF_TEST_CASE_COUNT="
            f"{len(ALL_VERIFY_REMOVE_HANDOFF_MARKERS)}"
        )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the bounded Phase 11 HVC verify helper keeps the "
            "landed remove-handoff branches explicit."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root to check (defaults to current working directory)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in self-test instead of checking a repo root",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    run_check(args.root)
    print("PHASE11_HVC_VERIFY_REMOVE_HANDOFF=pass")
    print(f"PHASE11_HVC_VERIFY_REMOVE_HANDOFF_ROOT={args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
