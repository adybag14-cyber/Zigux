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

SURVEY_REQUIRED = (
    "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet",
    "PHASE3_NEXT_BOUNDED_STEP=keep-the-shared-abi-manifest-and-shared-abi-slice-markers-in-this-survey-aligned-with-current-master-until-a-real-policy-or-unsafe-helper-expansion-lands",
    "`zigux/helpers/panic_policy.zig` now keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes`",
    "`zigux/helpers/allocator_policy.zig` now keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, `requiresExplicitCallerInteropPolicy`, `requiresExplicitCallerByte`, `permitsGlobalFallbackPolicyBytes`, `permitsGlobalFallbackInteropPolicy`, and `permitsGlobalFallbackByte`",
    "`zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small",
    "The current tree no longer ships a dedicated `phase3_policy_unsafe` replay pair",
)

ABI_SLICE_REQUIRED = (
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
)

ABI_SLICE_FORBIDDEN = (
    "zigux/tests/phase3_policy_unsafe.zig",
    "zigux/tests/phase3_policy_unsafe_build.zig",
)

MANIFEST_REQUIRED = (
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
)

MANIFEST_FORBIDDEN = ABI_SLICE_FORBIDDEN

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


def write_fixture(root: Path) -> None:
    (root / SURVEY_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / ABI_MANIFEST_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / ABI_SLICE_REL.parent).mkdir(parents=True, exist_ok=True)
    (root / SURVEY_REL).write_text("\n".join(SURVEY_REQUIRED) + "\n", encoding="utf-8")
    (root / ABI_SLICE_REL).write_text("\n".join(ABI_SLICE_REQUIRED) + "\n", encoding="utf-8")
    (root / ABI_MANIFEST_REL).write_text("\n".join(MANIFEST_REQUIRED) + "\n", encoding="utf-8")


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
        abi_slice_path.write_text(abi_slice_path.read_text(encoding="utf-8") + ABI_SLICE_FORBIDDEN[0] + "\n", encoding="utf-8")
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            assert ABI_SLICE_REL.as_posix() in str(exc)
        else:
            raise AssertionError("expected stale abi-slice marker failure")

        write_fixture(tmpdir)
        manifest_path = tmpdir / ABI_MANIFEST_REL
        manifest_path.write_text(manifest_path.read_text(encoding="utf-8").replace(MANIFEST_REQUIRED[3] + "\n", ""), encoding="utf-8")
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            assert ABI_MANIFEST_REL.as_posix() in str(exc)
        else:
            raise AssertionError("expected missing manifest marker failure")

        print("PHASE3_POLICY_UNSAFE_PACKET_SELF_TEST=pass")
        print("PHASE3_POLICY_UNSAFE_PACKET_SELF_TEST_CASE_COUNT=4")
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
