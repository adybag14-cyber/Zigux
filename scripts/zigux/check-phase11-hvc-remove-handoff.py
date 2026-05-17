#!/usr/bin/env python3
"""Fail-close the landed Phase 11 HVC remove-handoff verify pair."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


VERIFY_FILE = Path("drivers/tty/hvc/hvc_console_verify.zig")

ORDERED_MARKERS = [
    'test "hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding" {',
    "try std.testing.expect(detached_binding.keeps_irq_for_followup_hangup);",
    "try std.testing.expect(detached_binding.tty_vhangup_requested);",
    "try std.testing.expect(detached_binding.tty_kref_put_after_vhangup);",
    "try std.testing.expect(detached_binding.teardown_via_hangup_pending);",
    "try std.testing.expect(detached_binding.host_io_pending);",
    'test "hvc_console verify keeps remove handoff explicit when tty is already absent" {',
    "try std.testing.expect(tty_gone_remove.clears_console_slot_binding);",
    "try std.testing.expect(!tty_gone_remove.keeps_irq_for_followup_hangup);",
    "try std.testing.expect(!tty_gone_remove.tty_vhangup_requested);",
    "try std.testing.expect(!tty_gone_remove.tty_kref_put_after_vhangup);",
    "try std.testing.expect(!tty_gone_remove.teardown_via_hangup_pending);",
    "try std.testing.expect(!tty_gone_remove.host_io_pending);",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_repo_root(repo_root: Path) -> list[str]:
    verify_text = read_text(repo_root / VERIFY_FILE)
    missing: list[str] = []

    last_index = -1
    for marker in ORDERED_MARKERS:
        index = verify_text.find(marker)
        if index < 0:
            missing.append(f"{VERIFY_FILE}:{marker}")
            continue
        if index <= last_index:
            missing.append(f"{VERIFY_FILE}:out_of_order:{marker}")
            continue
        last_index = index

    return missing


def expect_case(root: Path, expected_fragment: str) -> bool:
    missing = validate_repo_root(root)
    return bool(missing) and any(expected_fragment in item for item in missing)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        verify_path = root / VERIFY_FILE
        verify_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_text = "\n".join(ORDERED_MARKERS) + "\n"
        verify_path.write_text(baseline_text, encoding="utf-8")

        if validate_repo_root(root):
            print("PHASE11_HVC_REMOVE_HANDOFF_SELF_TEST=fail")
            return 1

        for marker in ORDERED_MARKERS:
            verify_path.write_text(
                baseline_text.replace(marker, "", 1),
                encoding="utf-8",
            )
            if not expect_case(root, marker):
                print("PHASE11_HVC_REMOVE_HANDOFF_SELF_TEST=fail")
                return 1

        swapped_markers = ORDERED_MARKERS.copy()
        swapped_markers[0], swapped_markers[1] = swapped_markers[1], swapped_markers[0]
        verify_path.write_text("\n".join(swapped_markers) + "\n", encoding="utf-8")
        if not expect_case(root, f"{VERIFY_FILE}:out_of_order:"):
            print("PHASE11_HVC_REMOVE_HANDOFF_SELF_TEST=fail")
            return 1

    print("PHASE11_HVC_REMOVE_HANDOFF_SELF_TEST=pass")
    print(
        "PHASE11_HVC_REMOVE_HANDOFF_SELF_TEST_CASE_COUNT="
        f"{len(ORDERED_MARKERS) + 2}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    missing = validate_repo_root(args.repo_root)
    if missing:
        for item in missing:
            print(item, file=sys.stderr)
        return 1

    print("PHASE11_HVC_REMOVE_HANDOFF_CHECK=pass")
    print(f"PHASE11_HVC_REMOVE_HANDOFF_MARKER_COUNT={len(ORDERED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
