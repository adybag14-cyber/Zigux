#!/usr/bin/env python3
"""Fail-closed checks for the bounded Phase 11 watchdog stop-parity gap."""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile


BCM2835_STOP_MARKERS = (
    "pub const StopSummary = struct {",
    "pub fn stop(self: *Bcm2835WdtLab) StopSummary {",
    "running_after_stop",
    "full_reset_armed_after_stop",
)

DW_WDT_STOP_MARKERS = (
    "pub const StopSummary = struct {",
    "pub fn stopSummary(self: *DwWdtLab) StopSummary {",
    "reset_control_stop",
    "continued_heartbeat",
    'test "phase11 dw_wdt stop summary keeps idle, stoppable, and unstoppable paths distinct"',
)


def read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> list[str]:
    return [f"{label}: missing {marker}" for marker in markers if marker not in text]


def run_check(repo_root: pathlib.Path) -> list[str]:
    bcm2835_text = read_text(repo_root / "drivers/watchdog/bcm2835_wdt.zig")
    dw_wdt_text = read_text(repo_root / "drivers/watchdog/dw_wdt.zig")

    errors: list[str] = []
    errors.extend(require_markers("bcm2835_stop_surface", bcm2835_text, BCM2835_STOP_MARKERS))
    errors.extend(require_markers("dw_wdt_stop_surface", dw_wdt_text, DW_WDT_STOP_MARKERS))
    return errors


def run_self_test() -> int:
    bcm2835_text = "\n".join(BCM2835_STOP_MARKERS)
    dw_wdt_text = "\n".join(DW_WDT_STOP_MARKERS)

    assert not require_markers("bcm2835_stop_surface", bcm2835_text, BCM2835_STOP_MARKERS)
    assert not require_markers("dw_wdt_stop_surface", dw_wdt_text, DW_WDT_STOP_MARKERS)

    missing = require_markers(
        "dw_wdt_stop_surface",
        dw_wdt_text.replace(DW_WDT_STOP_MARKERS[1], ""),
        DW_WDT_STOP_MARKERS,
    )
    assert len(missing) == 1
    assert "pub fn stopSummary(self: *DwWdtLab) StopSummary {" in missing[0]

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = pathlib.Path(tmpdir)
        bcm2835_path = repo_root / "drivers/watchdog/bcm2835_wdt.zig"
        dw_wdt_path = repo_root / "drivers/watchdog/dw_wdt.zig"
        bcm2835_path.parent.mkdir(parents=True, exist_ok=True)
        dw_wdt_path.parent.mkdir(parents=True, exist_ok=True)
        bcm2835_path.write_text(bcm2835_text, encoding="utf-8")
        dw_wdt_path.write_text(dw_wdt_text, encoding="utf-8")
        assert not run_check(repo_root)

        dw_wdt_path.write_text("\n".join(DW_WDT_STOP_MARKERS[:-1]), encoding="utf-8")
        errors = run_check(repo_root)
        assert len(errors) == 1
        assert DW_WDT_STOP_MARKERS[-1] in errors[0]

    print("self-test passed")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    errors = run_check(pathlib.Path(args.repo_root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("phase11 watchdog stop parity packet ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
