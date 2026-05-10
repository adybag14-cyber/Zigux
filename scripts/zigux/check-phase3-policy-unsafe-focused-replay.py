#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


TEST_FILE = "zigux/tests/phase3_policy_unsafe.zig"
BUILD_FILE = "zigux/tests/phase3_policy_unsafe_build.zig"
DOC_FILE = "Documentation/zigux/phase3-abi-slice.md"

TEST_MARKERS = (
    'const layout_assert = @import("layout_assert");',
    'const panic_policy = @import("panic_policy");',
    'const allocator_policy = @import("allocator_policy");',
    'const mmio = @import("mmio_helpers");',
    'const narrow = @import("narrow_unsafe");',
    'test "phase3 focused policy and unsafe replay keeps layout and policy bytes explicit" {',
    'layout_assert.assertInteropPolicyLayout();',
    'layout_assert.assertMmioRangeLayout();',
    'layout_assert.assertRbtreeRootViewLayout();',
    'panic_policy.modeFromInteropPolicy(raw_policy)',
    'allocator_policy.modeFromInteropPolicy(raw_policy)',
    'narrow.constPointerAtInteropPolicyBytes(',
    'mmio.rangeInteropPolicy(mmio_base, 16, 4, mmio_policy)',
    'mmio.write32InteropPolicyByte(mmio_base, 4, 0xc001_d00d, @intFromEnum(abi.UnsafeScope.volatile_mmio));',
    'try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64InteropPolicyBytes(mmio_base, 8, 0, 0, 0));',
)

BUILD_MARKERS = (
    '.root_source_file = b.path("phase3_policy_unsafe.zig")',
    '.root_source_file = b.path("../helpers/layout_assert.zig")',
    '.root_source_file = b.path("../helpers/panic_policy.zig")',
    '.root_source_file = b.path("../helpers/allocator_policy.zig")',
    '.root_source_file = b.path("../helpers/mmio.zig")',
    '.root_source_file = b.path("../unsafe/narrow.zig")',
    'root_module.addImport("mmio_helpers", mmio_helpers_module);',
    'root_module.addImport("narrow_unsafe", narrow_unsafe_module);',
    'const tests = b.addTest(.{ .name = "phase3-policy-unsafe-tests", .root_module = root_module });',
    'const test_step = b.step("test", "Run Phase 3 focused policy/unsafe tests");',
)

DOC_MARKERS = (
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/helpers/mmio.zig",
    "raw_pointer_bridge",
    "volatile_mmio",
    "zigux/tests/phase3_policy_unsafe.zig",
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


def check_repo_root(repo_root: Path) -> None:
    require_markers(repo_root / TEST_FILE, TEST_MARKERS)
    require_markers(repo_root / BUILD_FILE, BUILD_MARKERS)
    require_markers(repo_root / DOC_FILE, DOC_MARKERS)


def write_fixture(root: Path) -> None:
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / TEST_FILE).write_text("\n".join(TEST_MARKERS) + "\n", encoding="utf-8")
    (root / BUILD_FILE).write_text("\n".join(BUILD_MARKERS) + "\n", encoding="utf-8")
    (root / DOC_FILE).write_text("\n".join(DOC_MARKERS) + "\n", encoding="utf-8")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase3_policy_unsafe_checker_"))
    try:
        write_fixture(tmpdir)
        check_repo_root(tmpdir)

        test_path = tmpdir / TEST_FILE
        original_test = test_path.read_text(encoding="utf-8")
        test_path.write_text(original_test.replace(TEST_MARKERS[-1], ""), encoding="utf-8")
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            if TEST_FILE not in str(exc):
                raise
        else:
            raise AssertionError("expected missing test marker failure")
        test_path.write_text(original_test, encoding="utf-8")

        build_path = tmpdir / BUILD_FILE
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(original_build.replace(BUILD_MARKERS[-1], ""), encoding="utf-8")
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            if BUILD_FILE not in str(exc):
                raise
        else:
            raise AssertionError("expected missing build marker failure")
        build_path.write_text(original_build, encoding="utf-8")

        doc_path = tmpdir / DOC_FILE
        original_doc = doc_path.read_text(encoding="utf-8")
        doc_path.write_text(original_doc.replace(DOC_MARKERS[-1], ""), encoding="utf-8")
        try:
            check_repo_root(tmpdir)
        except CheckFailure as exc:
            if DOC_FILE not in str(exc):
                raise
        else:
            raise AssertionError("expected missing doc marker failure")

        print("PHASE3_POLICY_UNSAFE_FOCUSED_REPLAY_SELF_TEST=pass")
        print("PHASE3_POLICY_UNSAFE_FOCUSED_REPLAY_SELF_TEST_CASE_COUNT=4")
    finally:
        shutil.rmtree(tmpdir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail closed on the focused Phase 3 policy/unsafe replay packet."
    )
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
        print("PHASE3_POLICY_UNSAFE_FOCUSED_REPLAY=pass")
        return 0
    except CheckFailure as exc:
        print(f"PHASE3_POLICY_UNSAFE_FOCUSED_REPLAY=fail:{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
