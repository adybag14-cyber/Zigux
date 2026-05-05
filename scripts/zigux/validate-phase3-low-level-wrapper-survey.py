#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DOC_REL = "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"

ATOMIC_REL = "zigux/helpers/atomic.zig"
BARRIER_REL = "zigux/helpers/barrier.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
LOW_LEVEL_BUILD_REL = "zigux/tests/phase3_low_level_wrappers_build.zig"
LOW_LEVEL_TEST_REL = "zigux/tests/phase3_low_level_wrappers.zig"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
ABI_SLICE_DOC_REL = "Documentation/zigux/phase3-abi-slice.md"


def require_tokens(issues: list[str], text: str, prefix: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        if token not in text:
            issues.append(f"{prefix}:{token}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    doc_path = root / DOC_REL
    if not doc_path.exists():
        return [f"missing_doc:{DOC_REL}"]
    doc = doc_path.read_text(encoding="utf-8")

    required_paths = {
        "PHASE3_ATOMIC_PATH": ATOMIC_REL,
        "PHASE3_BARRIER_PATH": BARRIER_REL,
        "PHASE3_MMIO_PATH": MMIO_REL,
        "PHASE3_LOW_LEVEL_BUILD_PATH": LOW_LEVEL_BUILD_REL,
        "PHASE3_LOW_LEVEL_TEST_PATH": LOW_LEVEL_TEST_REL,
    }
    for key, rel in required_paths.items():
        if f"{key}={rel}" not in doc:
            issues.append(f"missing_doc_marker:{key}={rel}")
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    required_doc_markers = (
        "PHASE3_ATOMIC_BLOB_SHA=",
        "PHASE3_BARRIER_BLOB_SHA=",
        "PHASE3_MMIO_BLOB_SHA=",
        "PHASE3_LOW_LEVEL_BUILD_BLOB_SHA=",
        "PHASE3_LOW_LEVEL_TEST_BLOB_SHA=",
        "PHASE3_ABI_SLICE_DOC_BLOB_SHA=",
        "PHASE3_ABI_MANIFEST_BLOB_SHA=",
        "PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
        "PHASE3_BOUNDARY_GAP=helper-surface-and-focused-proof-packet-no-longer-match",
    )
    for marker in required_doc_markers:
        if marker not in doc:
            issues.append(f"missing_doc_marker:{marker}")

    atomic_text = (root / ATOMIC_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        atomic_text,
        "atomic_missing_token",
        (
            "pub fn load",
            "pub fn store",
            "pub fn exchange",
            "pub fn fetchAdd",
            "pub fn fetchSub",
            "pub fn fetchAnd",
            "pub fn fetchOr",
            "pub fn fetchXor",
            "pub fn fetchMin",
            "pub fn fetchMax",
            "pub fn compareExchange",
            "pub fn compareExchangeWeak",
        ),
    )

    barrier_text = (root / BARRIER_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        barrier_text,
        "barrier_missing_token",
        (
            "pub fn acquire",
            "pub fn release",
            "pub fn full",
            "pub fn acquireRelease",
        ),
    )

    mmio_text = (root / MMIO_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        mmio_text,
        "mmio_missing_token",
        (
            "pub fn range",
            "pub fn read32",
            "pub fn write32",
            "narrow.pointerAt",
        ),
    )

    build_text = (root / LOW_LEVEL_BUILD_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        build_text,
        "low_level_build_missing_token",
        (
            '.root_source_file = b.path("phase3_low_level_wrappers.zig")',
            'const interop_policy_module = b.createModule(',
            'const layout_assert_module = b.createModule(',
            'const mmio_helpers_module = b.createModule(',
            'low_level_root_module.addImport("interop_policy", interop_policy_module);',
            'low_level_root_module.addImport("layout_assert", layout_assert_module);',
            'low_level_root_module.addImport("mmio_helpers", mmio_helpers_module);',
            '"phase3-low-level-wrappers-test"',
        ),
    )

    low_level_test_text = (root / LOW_LEVEL_TEST_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        low_level_test_text,
        "low_level_test_missing_token",
        (
            'const interop_policy = @import("interop_policy");',
            'const layout_assert = @import("layout_assert");',
            'const mmio = @import("mmio_helpers");',
            'const narrow = @import("narrow_unsafe");',
            "mmio.write8(",
            "mmio.read8(",
            "mmio.write16(",
            "mmio.read16(",
            "mmio.write32(",
            "mmio.read32(",
            "mmio.write64(",
            "mmio.read64(",
            "mmio.write8Scoped(",
            "mmio.read8Scoped(",
            "mmio.write16Scoped(",
            "mmio.read16Scoped(",
            "mmio.write32Scoped(",
            "mmio.read32Scoped(",
            "mmio.write64Scoped(",
            "mmio.read64Scoped(",
            "mmio.write8Policy(",
            "mmio.read8Policy(",
            "mmio.write16Policy(",
            "mmio.read16Policy(",
            "mmio.write32Policy(",
            "mmio.read32Policy(",
            "mmio.write64Policy(",
            "mmio.read64Policy(",
            "layout_assert.assertMmioRangeLayout();",
            "narrow.permitsVolatileMmio(",
            "narrow.permitsRawPointerBridge(",
        ),
    )

    manifest_text = (root / ABI_MANIFEST_REL).read_text(encoding="utf-8")
    for rel in (ATOMIC_REL, BARRIER_REL, MMIO_REL):
        if rel not in manifest_text:
            issues.append(f"manifest_missing_entry:{rel}")

    abi_slice_text = (root / ABI_SLICE_DOC_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        abi_slice_text,
        "abi_slice_missing_token",
        (
            "`zigux/helpers/atomic.zig`",
            "`zigux/helpers/barrier.zig`",
            "`zigux/helpers/mmio.zig`",
        ),
    )

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_") as tmp_dir:
        root = Path(tmp_dir)
        for rel in (
            ATOMIC_REL,
            BARRIER_REL,
            MMIO_REL,
            LOW_LEVEL_BUILD_REL,
            LOW_LEVEL_TEST_REL,
            ABI_MANIFEST_REL,
            ABI_SLICE_DOC_REL,
            DOC_REL,
        ):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)

        (root / ATOMIC_REL).write_text(
            "\n".join(
                [
                    "pub fn load() void {}",
                    "pub fn store() void {}",
                    "pub fn exchange() void {}",
                    "pub fn fetchAdd() void {}",
                    "pub fn fetchSub() void {}",
                    "pub fn fetchAnd() void {}",
                    "pub fn fetchOr() void {}",
                    "pub fn fetchXor() void {}",
                    "pub fn fetchMin() void {}",
                    "pub fn fetchMax() void {}",
                    "pub fn compareExchange() void {}",
                    "pub fn compareExchangeWeak() void {}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / BARRIER_REL).write_text(
            "\n".join(
                [
                    "pub fn acquire() void {}",
                    "pub fn release() void {}",
                    "pub fn full() void {}",
                    "pub fn acquireRelease() void {}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / MMIO_REL).write_text(
            "\n".join(
                [
                    "pub fn range() void {}",
                    "pub fn read32() void {}",
                    "pub fn write32() void {}",
                    "const p = narrow.pointerAt(u32, 0, 0);",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / LOW_LEVEL_BUILD_REL).write_text(
            "\n".join(
                [
                    'const interop_policy_module = b.createModule(.{});',
                    'const layout_assert_module = b.createModule(.{});',
                    'const mmio_helpers_module = b.createModule(.{});',
                    '.root_source_file = b.path("phase3_low_level_wrappers.zig"),',
                    'low_level_root_module.addImport("interop_policy", interop_policy_module);',
                    'low_level_root_module.addImport("layout_assert", layout_assert_module);',
                    'low_level_root_module.addImport("mmio_helpers", mmio_helpers_module);',
                    '"phase3-low-level-wrappers-test"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / LOW_LEVEL_TEST_REL).write_text(
            "\n".join(
                [
                    'const interop_policy = @import("interop_policy");',
                    'const layout_assert = @import("layout_assert");',
                    'const mmio = @import("mmio_helpers");',
                    'const narrow = @import("narrow_unsafe");',
                    "mmio.write8(base, 0, 0);",
                    "mmio.read8(base, 0);",
                    "mmio.write16(base, 0, 0);",
                    "mmio.read16(base, 0);",
                    "mmio.write32(base, 0, 0);",
                    "mmio.read32(base, 0);",
                    "mmio.write64(base64, 0, 0);",
                    "mmio.read64(base64, 0);",
                    "mmio.write8Scoped(scope, base, 0, 0);",
                    "mmio.read8Scoped(scope, base, 0);",
                    "mmio.write16Scoped(scope, base, 0, 0);",
                    "mmio.read16Scoped(scope, base, 0);",
                    "mmio.write32Scoped(scope, base, 0, 0);",
                    "mmio.read32Scoped(scope, base, 0);",
                    "mmio.write64Scoped(scope, base64, 0, 0);",
                    "mmio.read64Scoped(scope, base64, 0);",
                    "mmio.write8Policy(policy, base, 0, 0);",
                    "mmio.read8Policy(policy, base, 0);",
                    "mmio.write16Policy(policy, base, 0, 0);",
                    "mmio.read16Policy(policy, base, 0);",
                    "mmio.write32Policy(policy, base, 0, 0);",
                    "mmio.read32Policy(policy, base, 0);",
                    "mmio.write64Policy(policy, base64, 0, 0);",
                    "mmio.read64Policy(policy, base64, 0);",
                    "layout_assert.assertMmioRangeLayout();",
                    "narrow.permitsVolatileMmio(.volatile_mmio);",
                    "narrow.permitsRawPointerBridge(.raw_pointer_bridge);",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / ABI_MANIFEST_REL).write_text(
            "\n".join(
                [
                    "{",
                    f'  "files": ["{ATOMIC_REL}", "{BARRIER_REL}", "{MMIO_REL}"]',
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / ABI_SLICE_DOC_REL).write_text(
            "\n".join(
                [
                    "`zigux/helpers/atomic.zig`",
                    "`zigux/helpers/barrier.zig`",
                    "`zigux/helpers/mmio.zig`",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / DOC_REL).write_text(
            "\n".join(
                [
                    f"PHASE3_ATOMIC_PATH={ATOMIC_REL}",
                    f"PHASE3_BARRIER_PATH={BARRIER_REL}",
                    f"PHASE3_MMIO_PATH={MMIO_REL}",
                    f"PHASE3_LOW_LEVEL_BUILD_PATH={LOW_LEVEL_BUILD_REL}",
                    f"PHASE3_LOW_LEVEL_TEST_PATH={LOW_LEVEL_TEST_REL}",
                    "PHASE3_ATOMIC_BLOB_SHA=abc",
                    "PHASE3_BARRIER_BLOB_SHA=def",
                    "PHASE3_MMIO_BLOB_SHA=ghi",
                    "PHASE3_LOW_LEVEL_BUILD_BLOB_SHA=jkl",
                    "PHASE3_LOW_LEVEL_TEST_BLOB_SHA=mno",
                    "PHASE3_ABI_SLICE_DOC_BLOB_SHA=pqr",
                    "PHASE3_ABI_MANIFEST_BLOB_SHA=stu",
                    "PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
                    "PHASE3_BOUNDARY_GAP=helper-surface-and-focused-proof-packet-no-longer-match",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        issues = validate(root)
        assert issues == [], issues

        (root / LOW_LEVEL_BUILD_REL).write_text(
            (root / LOW_LEVEL_BUILD_REL).read_text(encoding="utf-8").replace(
                'low_level_root_module.addImport("mmio_helpers", mmio_helpers_module);',
                "",
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert (
            'low_level_build_missing_token:low_level_root_module.addImport("mmio_helpers", mmio_helpers_module);'
            in issues
        )

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate the Phase 3 low-level wrapper survey markers against live repo state.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated self-test coverage in a temporary workspace.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail")
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_ISSUES_END")
        return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
