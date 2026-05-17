#!/usr/bin/env python3
"""Fail-close the bounded Phase 11 HVC verify-side remove-handoff branch.

This checker is intentionally narrow. It only guards the compile-local
`drivers/tty/hvc/hvc_console_verify.zig` packet that keeps the shipped
verify-side remove-handoff branch explicit when the tty is already absent.

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

VERIFY_REMOVE_HANDOFF_MARKERS = [
    'test "hvc_console verify keeps remove handoff explicit when tty is already absent" {',
    "const summary = summarizeRemoveWhenTtyAlreadyAbsent(.{",
    ".tty_present = false,",
    ".console_lock_slot_cleared = true,",
    ".vtermno_and_cons_ops_released = true,",
    ".tty_port_put_ordered = true,",
    ".tty_vhangup_follow_through = true,",
    ".tty_kref_put_release = true,",
    ".keep_irq_until_hangup = true,",
    "try std.testing.expect(!summary.tty_present);",
    "try std.testing.expect(summary.tty_already_absent);",
    "try std.testing.expect(summary.remove_handoff.console_lock_slot_cleared);",
    "try std.testing.expect(summary.remove_handoff.tty_port_put_ordered);",
    "try std.testing.expect(summary.remove_handoff.keep_irq_until_hangup);",
    "try std.testing.expect(summary.keeps_live_remove_execution_out_of_scope);",
]


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
    expect_markers("phase11_hvc_verify_remove_handoff", verify_text, VERIFY_REMOVE_HANDOFF_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    write(root / VERIFY_FILE, "\n".join(VERIFY_REMOVE_HANDOFF_MARKERS) + "\n")


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

        for index, marker in enumerate(VERIFY_REMOVE_HANDOFF_MARKERS, start=1):
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
            f"{len(VERIFY_REMOVE_HANDOFF_MARKERS)}"
        )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the bounded Phase 11 HVC verify helper keeps the "
            "landed remove-handoff branch explicit."
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
