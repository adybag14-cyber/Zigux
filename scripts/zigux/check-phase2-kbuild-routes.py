#!/usr/bin/env python3
"""Guard the shared Phase 2 kbuild route contract.

This checker is intentionally narrow: it verifies that the Phase 2 toolchain
packet still keeps its shared make entrypoints, workflow wiring, and closure
surface aligned around the same fixdep/genksyms/kconfig tool family.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "makefile": Path("zigux/Makefile"),
    "workflow": Path(".github/workflows/zigux-bootstrap.yml"),
    "readme": Path("scripts/zigux/README.md"),
    "closure": Path("Documentation/zigux/phase2-closure.md"),
}

REQUIRED_MARKERS = {
    "makefile": (
        "phase2-tools:",
        "phase2-cross:",
        "validate-phase2.py",
        "check-fixdep-diff.py",
        "check-genksyms-bridge.py --self-test",
        "check-kconfig-bridge.py",
        "check-phase2-cross.py",
    ),
    "workflow": (
        "make -C zigux phase2-tools",
        "make -C zigux phase2-cross",
    ),
    "readme": (
        "phase2-tools",
        "phase2-cross",
        "fixdep",
        "genksyms",
        "kconfig",
    ),
    "closure": (
        "phase2-tools",
        "phase2-cross",
        "fixdep",
        "genksyms",
        "kconfig",
    ),
}

DEFAULT_ZIG_VERSION = "0.17.0-dev.87+9b177a7d2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 2 kbuild/toolchain routes stay aligned."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to inspect (defaults to the current working directory).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in synthetic contract tests instead of inspecting a repo tree.",
    )
    parser.add_argument(
        "--zig",
        type=Path,
        help="Optional Zig executable to version-check against the expected Phase 2 pin.",
    )
    parser.add_argument(
        "--expected-zig-version",
        default=DEFAULT_ZIG_VERSION,
        help="Expected Zig version when --zig is provided.",
    )
    return parser.parse_args()


def collect_failures(
    repo_root: Path, zig_path: Path | None = None, expected_zig_version: str = DEFAULT_ZIG_VERSION
) -> list[str]:
    failures: list[str] = []

    for key, relative_path in REQUIRED_FILES.items():
        path = repo_root / relative_path
        if not path.is_file():
            failures.append(f"missing-file:{relative_path.as_posix()}")
            continue

        text = path.read_text(encoding="utf-8")
        for marker in REQUIRED_MARKERS[key]:
            if marker not in text:
                failures.append(f"missing-marker:{relative_path.as_posix()}:{marker}")

    if zig_path is not None:
        if not zig_path.is_file():
            failures.append(f"missing-zig:{zig_path}")
        else:
            result = subprocess.run(
                [os.fspath(zig_path), "version"],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                failures.append(f"zig-version-command-failed:{zig_path}")
            else:
                actual = result.stdout.strip()
                if actual != expected_zig_version:
                    failures.append(
                        f"zig-version-mismatch:{zig_path}:{actual}:expected={expected_zig_version}"
                    )

    return failures


def run_check(repo_root: Path, zig_path: Path | None, expected_zig_version: str) -> int:
    failures = collect_failures(repo_root, zig_path, expected_zig_version)
    if failures:
        print("PHASE2_KBUILD_ROUTES=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE2_KBUILD_ROUTES=pass")
    return 0


def write_fixture(root: Path) -> None:
    for key, relative_path in REQUIRED_FILES.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        markers = "\n".join(REQUIRED_MARKERS[key])
        path.write_text(markers + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = 0

    with tempfile.TemporaryDirectory(prefix="phase2-kbuild-routes-") as tmp:
        root = Path(tmp)
        write_fixture(root)

        cases += 1
        fake_zig = root / "zig"
        fake_zig.write_text("#!/bin/sh\nprintf '%s\\n' '" + DEFAULT_ZIG_VERSION + "'\n", encoding="utf-8")
        fake_zig.chmod(0o755)
        if collect_failures(root, fake_zig):
            print("PHASE2_KBUILD_ROUTES_SELF_TEST=fail")
            print("case=baseline")
            return 1

        cases += 1
        broken_makefile = root / REQUIRED_FILES["makefile"]
        broken_makefile.write_text(
            broken_makefile.read_text(encoding="utf-8").replace(
                "check-genksyms-bridge.py --self-test", "check-genksyms-bridge.py"
            ),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        expected = "missing-marker:zigux/Makefile:check-genksyms-bridge.py --self-test"
        if expected not in failures:
            print("PHASE2_KBUILD_ROUTES_SELF_TEST=fail")
            print("case=makefile-marker")
            return 1

        cases += 1
        write_fixture(root)
        (root / REQUIRED_FILES["workflow"]).unlink()
        failures = collect_failures(root, fake_zig)
        expected = "missing-file:.github/workflows/zigux-bootstrap.yml"
        if expected not in failures:
            print("PHASE2_KBUILD_ROUTES_SELF_TEST=fail")
            print("case=workflow-file")
            return 1

        cases += 1
        write_fixture(root)
        fake_zig.write_text("#!/bin/sh\nprintf '%s\\n' '0.17.0-dev.bad'\n", encoding="utf-8")
        failures = collect_failures(root, fake_zig)
        expected = f"zig-version-mismatch:{fake_zig}:0.17.0-dev.bad:expected={DEFAULT_ZIG_VERSION}"
        if expected not in failures:
            print("PHASE2_KBUILD_ROUTES_SELF_TEST=fail")
            print("case=zig-pin")
            return 1

    print("PHASE2_KBUILD_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_KBUILD_ROUTES_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    zig_path = args.zig.resolve() if args.zig else None
    return run_check(args.repo_root.resolve(), zig_path, args.expected_zig_version)


if __name__ == "__main__":
    sys.exit(main())
