#!/usr/bin/env python3
"""Require mounted userspace to report the compiled default kernel release."""
import re
import sys
from pathlib import Path


def check(log, expected_release):
    if "ZIGUX_CACHYOS_MEDIA_BOOT_OK" not in log:
        raise ValueError("CachyOS did not reach its mounted-userspace boot marker")
    releases = re.findall(r"ZIGUX_CACHYOS_KERNEL=([A-Za-z0-9.+_-]+)", log)
    if not releases or any(release != expected_release for release in releases):
        raise ValueError(f"CachyOS did not boot the expected compiled kernel {expected_release}")


if __name__ == "__main__":
    check(Path(sys.argv[1]).read_text(errors="replace"), sys.argv[2])
    print("CachyOS mounted userspace and compiled kernel identity: OK")
