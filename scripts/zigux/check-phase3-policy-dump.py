#!/usr/bin/env python3
"""Validate the focused Phase 3 policy dump packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DOC_PATH = Path("Documentation/zigux/phase3-policy-slice.md")
DUMP_PATH = Path("zigux/tests/phase3_policy_dump.zig")
BUILD_PATH = Path("zigux/tests/phase3_policy_dump_build.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_policy_dump_expected.txt")

REQUIRED_DOC_MARKERS = (
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
)

REQUIRED_DUMP_MARKERS = (
    'safe-default',
    'mmio-bug',
    'raw-bridge-warn',
    'reserved-invalid',
    'panic={s}',
    'allocator={s}',
    'init_flow={s}',
    'explicit_caller={any}',
    'owned_state={any}',
    'reset_on_init={any}',
    'unsafe={s}',
    'narrow={s}',
)

REQUIRED_BUILD_MARKERS = (
    '.root_source_file = b.path("../bindings/abi.zig"),',
    '.root_source_file = b.path("../helpers/panic_policy.zig"),',
    '.root_source_file = b.path("../helpers/allocator_policy.zig"),',
    '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
    '.root_source_file = b.path("../unsafe/narrow.zig"),',
    '.root_source_file = b.path("phase3_policy_dump.zig"),',
    '"phase3-policy-dump"',
)

EXPECTED_LINES = (
    "safe-default|panic=abort|allocator=caller_provided|init_flow=caller_prepared|explicit_caller=true|owned_state=false|reset_on_init=false|unsafe=none|typed_only=true|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|narrow=none",
    "mmio-bug|panic=bug|allocator=kernel_heap|init_flow=helper_owned|explicit_caller=false|owned_state=true|reset_on_init=false|unsafe=volatile_mmio|typed_only=false|global_fallback=true|warn_only=false|mmio=true|raw_bridge=false|audit=true|narrow=volatile_mmio",
    "raw-bridge-warn|panic=warn|allocator=arena|init_flow=helper_owned_with_reset|explicit_caller=false|owned_state=true|reset_on_init=true|unsafe=raw_pointer_bridge|typed_only=false|global_fallback=true|warn_only=true|mmio=false|raw_bridge=true|audit=true|narrow=raw_pointer_bridge",
    "reserved-invalid|panic=invalid|allocator=invalid|init_flow=invalid|explicit_caller=false|owned_state=false|reset_on_init=false|unsafe=invalid|typed_only=false|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|narrow=invalid",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    files_and_markers = (
        (DOC_PATH, REQUIRED_DOC_MARKERS),
        (DUMP_PATH, REQUIRED_DUMP_MARKERS),
        (BUILD_PATH, REQUIRED_BUILD_MARKERS),
    )
    for relative_path, markers in files_and_markers:
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    expected_path = repo_root / EXPECTED_PATH
    try:
        expected_lines = _read(expected_path).splitlines()
    except FileNotFoundError:
        issues.append(f"missing repo file: {EXPECTED_PATH.as_posix()}")
    else:
        if expected_lines != list(EXPECTED_LINES):
            issues.append(f"unexpected {EXPECTED_PATH.as_posix()} contents")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_dump_") as temp_dir:
        root = Path(temp_dir)
        _write(root / DOC_PATH, "\n".join(REQUIRED_DOC_MARKERS) + "\n")
        _write(root / DUMP_PATH, "\n".join(REQUIRED_DUMP_MARKERS) + "\n")
        _write(root / BUILD_PATH, "\n".join(REQUIRED_BUILD_MARKERS) + "\n")
        _write(root / EXPECTED_PATH, "\n".join(EXPECTED_LINES) + "\n")

        issues = validate_repo(root)
        if issues:
            print("PHASE3_POLICY_DUMP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

    print("PHASE3_POLICY_DUMP_SELF_TEST=pass")
    print(f"PHASE3_POLICY_DUMP_EXPECTED_LINE_COUNT={len(EXPECTED_LINES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 3 policy dump packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_POLICY_DUMP=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / DUMP_PATH}")
    print(f"validated {args.repo_root / EXPECTED_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
