#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SURVEY_REL = Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")
ABI_SLICE_REL = Path("Documentation/zigux/phase3-abi-slice.md")
ABI_MANIFEST_REL = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
LOW_LEVEL_TEST_REL = Path("zigux/tests/phase3_low_level_wrappers.zig")
LOW_LEVEL_BUILD_REL = Path("zigux/tests/phase3_low_level_wrappers_build.zig")

SURVEY_REQUIRED = (
    "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet",
    "PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py",
    "The current tree still does not ship a dedicated `phase3_policy_unsafe` replay pair",
)

ABI_SLICE_REQUIRED = (
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/mmio.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
)

ABI_SLICE_FORBIDDEN = (
    "zigux/tests/phase3_policy_unsafe.zig",
    "zigux/tests/phase3_policy_unsafe_build.zig",
)

MANIFEST_REQUIRED = (
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/mmio.zig",
    "zigux/unsafe/narrow.zig",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
)

MANIFEST_FORBIDDEN = ABI_SLICE_FORBIDDEN

LOW_LEVEL_TEST_REQUIRED = (
    "const scoped_mut_slice = try narrow.sliceAtInteropPolicy(u32, base, values.len, raw_policy);",
    "const scoped_mut_slice_bytes = try narrow.sliceAtInteropPolicyBytes(u32, base, values.len, 2, 0);",
    "const scoped_mut_slice_byte = try narrow.sliceAtByte(u32, base, values.len, 2);",
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.sliceAtInteropPolicy(u32, base, values.len, no_unsafe_policy));",
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.sliceAtInteropPolicyBytes(u32, base, values.len, 2, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, narrow.sliceAtByte(u32, base, values.len, 1));",
)

LOW_LEVEL_BUILD_REQUIRED = (
    "../unsafe/narrow.zig",
    "../helpers/mmio.zig",
    "../helpers/allocator_policy.zig",
    "../helpers/panic_policy.zig",
    "phase3_low_level_wrappers.zig",
    "phase3-low-level-wrappers-test",
)


class CheckFailure(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CheckFailure(f"missing_repo_path:{path.as_posix()}") from None


def require_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"missing_marker:{path.as_posix()}:{marker}")


def forbid_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker in text:
            raise CheckFailure(f"stale_marker:{path.as_posix()}:{marker}")


def check_repo_root(repo_root: Path) -> None:
    require_markers(repo_root / SURVEY_REL, SURVEY_REQUIRED)
    require_markers(repo_root / ABI_SLICE_REL, ABI_SLICE_REQUIRED)
    forbid_markers(repo_root / ABI_SLICE_REL, ABI_SLICE_FORBIDDEN)
    require_markers(repo_root / ABI_MANIFEST_REL, MANIFEST_REQUIRED)
    forbid_markers(repo_root / ABI_MANIFEST_REL, MANIFEST_FORBIDDEN)
    require_markers(repo_root / LOW_LEVEL_TEST_REL, LOW_LEVEL_TEST_REQUIRED)
    require_markers(repo_root / LOW_LEVEL_BUILD_REL, LOW_LEVEL_BUILD_REQUIRED)


def write_fixture(root: Path) -> None:
    (root / SURVEY_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / ABI_MANIFEST_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / ABI_SLICE_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / LOW_LEVEL_TEST_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / SURVEY_REL).write_text("\n".join(SURVEY_REQUIRED) + "\n", encoding="utf-8")
    (root / ABI_SLICE_REL).write_text("\n".join(ABI_SLICE_REQUIRED) + "\n", encoding="utf-8")
    (root / ABI_MANIFEST_REL).write_text("\n".join(MANIFEST_REQUIRED) + "\n", encoding="utf-8")
    (root / LOW_LEVEL_TEST_REL).write_text("\n".join(LOW_LEVEL_TEST_REQUIRED) + "\n", encoding="utf-8")
    (root / LOW_LEVEL_BUILD_REL).write_text("\n".join(LOW_LEVEL_BUILD_REQUIRED) + "\n", encoding="utf-8")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase3_policy_unsafe_packet_checker_"))
    try:
        write_fixture(tmpdir)
        check_repo_root(tmpdir)

        survey_path = tmpdir / SURVEY_REL
        survey_path.write_text(survey_path.read_text(encoding="utf-8").replace(SURVEY_REQUIRED[1], ""), encoding="utf-8")
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            assert SURVEY_REL.as_posix() in str(exc)
        else:
            raise AssertionError("expected missing survey marker failure")

        write_fixture(tmpdir)
        abi_slice_path = tmpdir / ABI_SLICE_REL
        abi_slice_path.write_text(
            abi_slice_path.read_text(encoding="utf-8").replace(ABI_SLICE_REQUIRED[0] + "\n", ""),
            encoding="utf-8",
        )
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            assert ABI_SLICE_REL.as_posix() in str(exc)
            assert ABI_SLICE_REQUIRED[0] in str(exc)
        else:
            raise AssertionError("expected missing abi-slice policy packet marker failure")

        write_fixture(tmpdir)
        abi_slice_path = tmpdir / ABI_SLICE_REL
        abi_slice_path.write_text(abi_slice_path.read_text(encoding="utf-8") + ABI_SLICE_FORBIDDEN[0] + "\n", encoding="utf-8")
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            assert ABI_SLICE_REL.as_posix() in str(exc)
        else:
            raise AssertionError("expected stale abi-slice marker failure")

        write_fixture(tmpdir)
        manifest_path = tmpdir / ABI_MANIFEST_REL
        manifest_path.write_text(manifest_path.read_text(encoding="utf-8").replace(MANIFEST_REQUIRED[5] + "\n", ""), encoding="utf-8")
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            assert ABI_MANIFEST_REL.as_posix() in str(exc)
            assert MANIFEST_REQUIRED[5] in str(exc)
        else:
            raise AssertionError("expected missing manifest marker failure")

        write_fixture(tmpdir)
        low_level_test_path = tmpdir / LOW_LEVEL_TEST_REL
        low_level_test_path.write_text(
            low_level_test_path.read_text(encoding="utf-8").replace(LOW_LEVEL_TEST_REQUIRED[0] + "\n", ""),
            encoding="utf-8",
        )
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            assert LOW_LEVEL_TEST_REL.as_posix() in str(exc)
            assert LOW_LEVEL_TEST_REQUIRED[0] in str(exc)
        else:
            raise AssertionError("expected missing low-level raw-pointer bridge marker failure")

        write_fixture(tmpdir)
        low_level_build_path = tmpdir / LOW_LEVEL_BUILD_REL
        low_level_build_path.write_text(
            low_level_build_path.read_text(encoding="utf-8").replace(LOW_LEVEL_BUILD_REQUIRED[-1] + "\n", ""),
            encoding="utf-8",
        )
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            assert LOW_LEVEL_BUILD_REL.as_posix() in str(exc)
            assert LOW_LEVEL_BUILD_REQUIRED[-1] in str(exc)
        else:
            raise AssertionError("expected missing low-level build anchor failure")

        print("PHASE3_POLICY_UNSAFE_PACKET_SELF_TEST=pass")
        print("PHASE3_POLICY_UNSAFE_PACKET_SELF_TEST_CASE_COUNT=7")
    finally:
        shutil.rmtree(tmpdir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fail closed on the current shared Phase 3 policy/unsafe packet.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.self_test:
            run_self_test()
            return 0
        check_repo_root(args.repo_root)
        print("PHASE3_POLICY_UNSAFE_PACKET=pass")
        return 0
    except CheckFailure as exc:
        print(f"PHASE3_POLICY_UNSAFE_PACKET=fail:{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())