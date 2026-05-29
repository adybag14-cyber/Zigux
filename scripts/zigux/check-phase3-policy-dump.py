#!/usr/bin/env python3
"""Validate the focused Phase 3 policy dump packet."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


DOC_PATH = Path("Documentation/zigux/phase3-policy-slice.md")
DUMP_PATH = Path("zigux/tests/phase3_policy_dump.zig")
BUILD_PATH = Path("zigux/tests/phase3_policy_dump_build.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_policy_dump_expected.txt")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_DOC_MARKERS = (
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-dump.py",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "make -C zigux phase3-policy-dump",
    "make -C zigux phase3",
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
    'boundary={s}',
    'surface={s}',
    'typed_only={any}',
    'global_fallback={any}',
    'warn_only={any}',
    'mmio={any}',
    'raw_bridge={any}',
    'audit={any}',
    'bridge_read_ok={any}',
    'bridge_write_ok={any}',
    'narrow={s}',
    'narrow_boundary={s}',
    'narrow_surface={s}',
    'std.debug.print(',
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

REQUIRED_MAKEFILE_MARKERS = (
    "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
    "phase3-policy-dump:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
)

REQUIRED_WORKFLOW_MARKERS = (
    "Run current Phase 3 policy dump replay",
    "run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "Run current Phase 3 policy dump make wrapper",
    "run: make -C zigux phase3-policy-dump",
)

EXPECTED_LINES = (
    "safe-default|panic=abort|allocator=caller_provided|init_flow=caller_prepared|explicit_caller=true|owned_state=false|reset_on_init=false|unsafe=none|boundary=typed_safe|surface=safe_only|typed_only=true|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|bridge_read_ok=false|bridge_write_ok=false|narrow=none|narrow_boundary=typed_safe|narrow_surface=safe_only",
    "mmio-bug|panic=bug|allocator=kernel_heap|init_flow=helper_owned|explicit_caller=false|owned_state=true|reset_on_init=false|unsafe=volatile_mmio|boundary=volatile_mmio_window|surface=mmio_only|typed_only=false|global_fallback=true|warn_only=false|mmio=true|raw_bridge=false|audit=true|bridge_read_ok=false|bridge_write_ok=false|narrow=volatile_mmio|narrow_boundary=volatile_mmio_window|narrow_surface=mmio_only",
    "raw-bridge-warn|panic=warn|allocator=arena|init_flow=helper_owned_with_reset|explicit_caller=false|owned_state=true|reset_on_init=true|unsafe=raw_pointer_bridge|boundary=raw_pointer_bridge|surface=raw_pointer_bridge_only|typed_only=false|global_fallback=true|warn_only=true|mmio=false|raw_bridge=true|audit=true|bridge_read_ok=true|bridge_write_ok=true|narrow=raw_pointer_bridge|narrow_boundary=raw_pointer_bridge|narrow_surface=raw_pointer_bridge_only",
    "reserved-invalid|panic=invalid|allocator=invalid|init_flow=invalid|explicit_caller=false|owned_state=false|reset_on_init=false|unsafe=invalid|boundary=invalid|surface=invalid|typed_only=false|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|bridge_read_ok=false|bridge_write_ok=false|narrow=invalid|narrow_boundary=invalid|narrow_surface=invalid",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _expected_output() -> str:
    return "\n".join(EXPECTED_LINES) + "\n"


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    files_and_markers = (
        (DOC_PATH, REQUIRED_DOC_MARKERS),
        (DUMP_PATH, REQUIRED_DUMP_MARKERS),
        (BUILD_PATH, REQUIRED_BUILD_MARKERS),
        (MAKEFILE_PATH, REQUIRED_MAKEFILE_MARKERS),
        (WORKFLOW_PATH, REQUIRED_WORKFLOW_MARKERS),
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


def verify_replay(repo_root: Path, zig_executable: str) -> list[str]:
    command = [
        zig_executable,
        "build",
        "phase3-policy-dump",
        "--build-file",
        BUILD_PATH.as_posix(),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return [f"phase3 policy dump replay unavailable: {exc}"]

    issues: list[str] = []
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        issues.append(f"phase3 policy dump replay failed: {detail}")
        return issues

    if completed.stdout:
        issues.append("unexpected stdout from phase3 policy dump replay")

    if completed.stderr != _expected_output():
        issues.append("unexpected phase3 policy dump replay stderr output")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_dump_") as temp_dir:
        root = Path(temp_dir)
        _write(root / DOC_PATH, "\n".join(REQUIRED_DOC_MARKERS) + "\n")
        _write(root / DUMP_PATH, "\n".join(REQUIRED_DUMP_MARKERS) + "\n")
        _write(root / BUILD_PATH, "\n".join(REQUIRED_BUILD_MARKERS) + "\n")
        _write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n")
        _write(root / WORKFLOW_PATH, "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n")
        _write(root / EXPECTED_PATH, "\n".join(EXPECTED_LINES) + "\n")

        issues = validate_repo(root)
        if issues:
            print("PHASE3_POLICY_DUMP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (
                DOC_PATH,
                "python3 scripts/zigux/check-phase3-policy-dump.py --self-test\n",
                "missing Documentation/zigux/phase3-policy-slice.md marker: python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
            ),
            (
                DOC_PATH,
                "make -C zigux phase3-policy-dump\n",
                "missing Documentation/zigux/phase3-policy-slice.md marker: make -C zigux phase3-policy-dump",
            ),
            (
                DUMP_PATH,
                "typed_only={any}\n",
                "missing zigux/tests/phase3_policy_dump.zig marker: typed_only={any}",
            ),
            (
                DUMP_PATH,
                "audit={any}\n",
                "missing zigux/tests/phase3_policy_dump.zig marker: audit={any}",
            ),
            (
                BUILD_PATH,
                '"phase3-policy-dump"\n',
                'missing zigux/tests/phase3_policy_dump_build.zig marker: "phase3-policy-dump"',
            ),
            (
                MAKEFILE_PATH,
                "phase3-policy-dump:\n",
                "missing zigux/Makefile marker: phase3-policy-dump:",
            ),
            (
                WORKFLOW_PATH,
                "Run current Phase 3 policy dump make wrapper\n",
                "missing .github/workflows/zigux-bootstrap.yml marker: Run current Phase 3 policy dump make wrapper",
            ),
            (
                WORKFLOW_PATH,
                "run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig\n",
                "missing .github/workflows/zigux-bootstrap.yml marker: run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
            ),
        )

        for rel_path, marker, expected in cases:
            path = root / rel_path
            original = _read(path)
            _write(path, original.replace(marker, "", 1))
            issues = validate_repo(root)
            if expected not in issues:
                print("PHASE3_POLICY_DUMP_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1
            _write(path, original)

        expected_path = root / EXPECTED_PATH
        original_expected = _read(expected_path)
        _write(expected_path, original_expected.replace("|audit=false", "|audit=maybe", 1))
        issues = validate_repo(root)
        expected = "unexpected zigux/tests/fixtures/phase3_policy_dump_expected.txt contents"
        if expected not in issues:
            print("PHASE3_POLICY_DUMP_SELF_TEST=fail")
            print("expected fixture drift was not reported")
            return 1

    print("PHASE3_POLICY_DUMP_SELF_TEST=pass")
    print(f"PHASE3_POLICY_DUMP_SELF_TEST_CASE_COUNT={len(cases) + 2}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 3 policy dump packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--zig", default="zig", help="Zig executable to use for live replay verification")
    parser.add_argument(
        "--skip-replay",
        action="store_true",
        help="only check the tracked files and fixture without running the dump replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if not args.skip_replay:
        issues.extend(verify_replay(args.repo_root, args.zig))
    if issues:
        print("PHASE3_POLICY_DUMP=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / DUMP_PATH}")
    print(f"validated {args.repo_root / EXPECTED_PATH}")
    if not args.skip_replay:
        print(f"verified replay {args.repo_root / BUILD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())