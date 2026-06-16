#!/usr/bin/env python3
"""Thin wrapper that delegates install-zig to the Zig implementation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_SCRIPT = ROOT / "scripts" / "zigux" / "install_zig.zig"


def resolve_zig_executable() -> str:
    policy_path = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
    if policy_path.exists():
        import json

        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        channel = str(payload["channel"])
        target = str(payload["upgrade_policy"]["archive_target_scope"][0])
        pinned_root = ROOT / ".zig-toolchain" / f"zig-{target}-{channel}"
        for candidate in (
            pinned_root / "zig",
            pinned_root / "zig.exe",
            pinned_root / "bin" / "zig",
            pinned_root / "bin" / "zig.exe",
        ):
            if candidate.is_file():
                return str(candidate)

    local_root = ROOT / ".zig-toolchain"
    if local_root.exists():
        for pattern in ("*/zig", "*/zig.exe", "*/bin/zig", "*/bin/zig.exe", "zig", "zig.exe", "bin/zig", "bin/zig.exe"):
            for candidate in sorted(local_root.glob(pattern)):
                if candidate.is_file():
                    return str(candidate)

    return "zig"


def main() -> int:
    zig = resolve_zig_executable()
    if "--self-test" in sys.argv[1:]:
        run_completed = subprocess.run(
            [zig, "run", str(ZIG_SCRIPT), "--", "--self-test"],
            cwd=ROOT,
            check=False,
        )
        if run_completed.returncode == 0:
            return 0
        test_completed = subprocess.run(
            [
                zig,
                "test",
                str(ZIG_SCRIPT),
                "--test-filter",
                "installer self-test completes",
            ],
            cwd=ROOT,
            check=False,
        )
        return int(test_completed.returncode)
    command = [zig, "run", str(ZIG_SCRIPT), "--", *sys.argv[1:]]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())