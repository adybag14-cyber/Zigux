#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
MMIO_REL = "zigux/helpers/mmio.zig"
INTEROP_POLICY_REL = "zigux/helpers/interop_policy.zig"
POLICY_TEST_REL = "zigux/tests/phase3_policy_unsafe.zig"
POLICY_BUILD_REL = "zigux/tests/phase3_policy_unsafe_build.zig"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig",
    "PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay",
    "PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`zigux/helpers/mmio.zig` is now the shipped second boundary helper that consumes `DecodedInteropPolicy` directly outside the focused `phase3_policy_unsafe` test packet",
    "That same focused replay now reaches the typed-policy MMIO surface through `read8Policy()`, `write8Policy()`, `read16Policy()`, `write16Policy()`, `read32Policy()`, `write32Policy()`, `read64Policy()`, and `write64Policy()` so the whole width-specific decoded-policy MMIO family stays attached to the same narrow boundary packet instead of leaving 8-bit, 16-bit, or 64-bit governance implicit.",
    "the current tree does not yet ship a third Phase 3 boundary helper that consumes `DecodedInteropPolicy` directly beyond the focused replay and the scoped MMIO helper",
    "and it now also exposes direct raw-pointer bridge readers through `constSliceAt()`, `constPointerAt()`, and `readValueAt()` without widening the packet into a broader runtime caller surface",
    "- `zigux/helpers/interop_policy.zig` now proves typed decoding through the focused replay, keeps direct raw-pointer bridge reads reviewable through `constSliceAt()`, `constPointerAt()`, and `readValueAt()`, and still stays inside the same bounded policy record rather than widening into a broader runtime surface",
)

REQUIRED_MMIO_SNIPPETS = (
    "fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag {",
    "pub fn readScopedWithPolicy(",
    "pub fn writeScopedWithPolicy(",
    "pub fn read8Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u8 {",
    "pub fn write8Policy(",
    "pub fn read16Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u16 {",
    "pub fn write16Policy(",
    "pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
    "pub fn write32Policy(",
    "pub fn read64Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u64 {",
    "pub fn write64Policy(",
    'test "phase3 mmio wrapper consumes decoded interop policy"',
)

REQUIRED_INTEROP_POLICY_SNIPPETS = (
    "    pub fn constSliceAt(",
    "        return narrow.scopedConstSliceAt(T, self.unsafe_scope, base, len);",
    "    pub fn constPointerAt(",
    "        return narrow.scopedConstPointerAt(T, self.unsafe_scope, addr);",
    "    pub fn readValueAt(",
    "        return narrow.scopedConstValueAt(T, self.unsafe_scope, addr);",
    'test "phase3 interop policy decoder keeps raw-pointer bridge consumers explicit"',
)

REQUIRED_POLICY_TEST_SNIPPETS = (
    'test "phase3 policy gate reaches a second boundary helper through decoded policy"',
    "const none_policy = try interop_policy.decode(.{",
    "try mmio.writeScopedWithPolicy(u32, mmio_policy, base32, 0, 0x10213243);",
    "try std.testing.expectEqual(@as(u32, 0x10213243), regs32[0]);",
    "try std.testing.expectEqual(@as(u32, 0x10213243), try mmio.readScopedWithPolicy(u32, mmio_policy, base32, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u32, raw_pointer_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScopedWithPolicy(u32, raw_pointer_policy, base32, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u32, none_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScopedWithPolicy(u32, none_policy, base32, 0));",
    "try mmio.write8Policy(mmio_policy, base32, 0, 0x2a);",
    "try std.testing.expectEqual(@as(u8, 0x2a), try mmio.read8Policy(mmio_policy, base32, 0));",
    "try mmio.write16Policy(mmio_policy, base32, 2, 0x7bcd);",
    "try std.testing.expectEqual(@as(u16, 0x7bcd), try mmio.read16Policy(mmio_policy, base32, 2));",
    "try mmio.write32Policy(mmio_policy, base32, @sizeOf(u32), 0xdecafbad);",
    "try std.testing.expectEqual(@as(u32, 0xdecafbad), try mmio.read32Policy(mmio_policy, base32, @sizeOf(u32)));",
    "try mmio.write64Policy(mmio_policy, base64, @sizeOf(u64), 0x1111_2222_3333_4444);",
    "try std.testing.expectEqual(@as(u64, 0x1111_2222_3333_4444), try mmio.read64Policy(mmio_policy, base64, @sizeOf(u64)));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(raw_pointer_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Policy(raw_pointer_policy, base32, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(none_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Policy(none_policy, base32, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Policy(raw_pointer_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Policy(raw_pointer_policy, base32, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Policy(none_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Policy(none_policy, base32, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base32, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(none_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(none_policy, base32, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(raw_pointer_policy, base64, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Policy(raw_pointer_policy, base64, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(none_policy, base64, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Policy(none_policy, base64, 0));",
    'test "phase3 policy gate reaches raw-pointer bridge consumers through decoded policy"',
    "const none_policy = try interop_policy.decode(.{",
    "try std.testing.expectError(error.UnsafeScopeDenied, none_policy.constSliceAt(u32, base, words.len));",
    "try std.testing.expectError(error.UnsafeScopeDenied, none_policy.constPointerAt(u32, base));",
    "try std.testing.expectError(error.UnsafeScopeDenied, none_policy.readValueAt(u32, base));",
    "const words_slice = try raw_pointer_policy.constSliceAt(u32, base, words.len);",
    "const second_word = try raw_pointer_policy.constPointerAt(u32, base + @sizeOf(u32));",
    "try std.testing.expectEqual(@as(u32, 11), try raw_pointer_policy.readValueAt(u32, base + @sizeOf(u32)));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio_policy.constSliceAt(u32, base, words.len));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio_policy.constPointerAt(u32, base));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio_policy.readValueAt(u32, base));",
    "try std.testing.expectError(error.MisalignedAccess, raw_pointer_policy.constSliceAt(u32, base + 1, 1));",
    "try std.testing.expectError(error.MisalignedAccess, raw_pointer_policy.constPointerAt(u32, base + 1));",
    "try std.testing.expectError(error.MisalignedAccess, raw_pointer_policy.readValueAt(u32, base + 1));",
    "try std.testing.expectError(error.AddressOverflow, raw_pointer_policy.constSliceAt(u32, 4, std.math.maxInt(usize)));",
)

REQUIRED_POLICY_BUILD_SNIPPETS = (
    "const rbtree_bindings_module = b.createModule(.{",
    '.root_source_file = b.path("../bindings/rbtree.zig"),',
    "const layout_assert_module = b.createModule(.{",
    'layout_assert_module.addImport("abi_bindings", abi_bindings_module);',
    'layout_assert_module.addImport("rbtree_bindings", rbtree_bindings_module);',
    "const interop_policy_module = b.createModule(.{",
    'interop_policy_module.addImport("abi_bindings", abi_bindings_module);',
    'interop_policy_module.addImport("panic_policy", panic_policy_module);',
    'interop_policy_module.addImport("allocator_policy", allocator_policy_module);',
    'interop_policy_module.addImport("narrow_unsafe", narrow_unsafe_module);',
    "const mmio_module = b.createModule(.{",
    'mmio_module.addImport("abi_bindings", abi_bindings_module);',
    'mmio_module.addImport("interop_policy", interop_policy_module);',
    'mmio_module.addImport("narrow_unsafe", narrow_unsafe_module);',
    'root_module.addImport("interop_policy", interop_policy_module);',
    'root_module.addImport("layout_assert", layout_assert_module);',
    'root_module.addImport("mmio", mmio_module);',
    '"phase3-policy-unsafe-test",',
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _check_snippets(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = _read_text(root, SURVEY_REL, issues)
    mmio = _read_text(root, MMIO_REL, issues)
    interop_policy = _read_text(root, INTEROP_POLICY_REL, issues)
    policy_test = _read_text(root, POLICY_TEST_REL, issues)
    policy_build = _read_text(root, POLICY_BUILD_REL, issues)

    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        _check_snippets(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)
    if mmio:
        _check_snippets(mmio, REQUIRED_MMIO_SNIPPETS, "missing_mmio_snippet", issues)
    if interop_policy:
        _check_snippets(interop_policy, REQUIRED_INTEROP_POLICY_SNIPPETS, "missing_interop_policy_snippet", issues)
    if policy_test:
        _check_snippets(policy_test, REQUIRED_POLICY_TEST_SNIPPETS, "missing_policy_test_snippet", issues)
    if policy_build:
        _check_snippets(policy_build, REQUIRED_POLICY_BUILD_SNIPPETS, "missing_policy_build_snippet", issues)

    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_mmio_consumer_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write(
            root,
            SURVEY_REL,
            "\n".join(
                (
                    "# Phase 3 Policy and Unsafe Boundary Survey",
                    "",
                    "- `PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig`",
                    "- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`",
                    "- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer`",
                    "",
                    *REQUIRED_SURVEY_SNIPPETS,
                    "",
                )
            ) + "\n",
        )
        _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
        _write(root, INTEROP_POLICY_REL, "\n".join(REQUIRED_INTEROP_POLICY_SNIPPETS) + "\n")
        _write(root, POLICY_TEST_REL, "\n".join(REQUIRED_POLICY_TEST_SNIPPETS) + "\n")
        _write(root, POLICY_BUILD_REL, "\n".join(REQUIRED_POLICY_BUILD_SNIPPETS) + "\n")
        assert validate(root) == []

        _write(root, POLICY_TEST_REL, "\n".join(snippet for snippet in REQUIRED_POLICY_TEST_SNIPPETS if "write64Policy" not in snippet) + "\n")
        issues = validate(root)
        assert "missing_policy_test_snippet:try mmio.write64Policy(mmio_policy, base64, @sizeOf(u64), 0x1111_2222_3333_4444);" in issues

        _write(root, POLICY_TEST_REL, "\n".join(REQUIRED_POLICY_TEST_SNIPPETS) + "\n")
        _write(root, SURVEY_REL, "\n".join(
            (
                "# Phase 3 Policy and Unsafe Boundary Survey",
                "",
                "- `PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig`",
                "- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`",
                "- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer`",
                "",
                REQUIRED_SURVEY_SNIPPETS[0],
                REQUIRED_SURVEY_SNIPPETS[2],
                REQUIRED_SURVEY_SNIPPETS[3],
                "",
            )
        ) + "\n")
        issues = validate(root)
        assert f"missing_survey_snippet:{REQUIRED_SURVEY_SNIPPETS[1]}" in issues
        assert f"missing_survey_snippet:{REQUIRED_SURVEY_SNIPPETS[4]}" in issues

        _write(root, SURVEY_REL, "\n".join(
            (
                "# Phase 3 Policy and Unsafe Boundary Survey",
                "",
                "- `PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig`",
                "- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`",
                "- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer`",
                "",
                *REQUIRED_SURVEY_SNIPPETS,
                "",
            )
        ) + "\n")
        _write(root, INTEROP_POLICY_REL, "\n".join(snippet for snippet in REQUIRED_INTEROP_POLICY_SNIPPETS if "constPointerAt" not in snippet and "readValueAt" not in snippet) + "\n")
        issues = validate(root)
        assert "missing_interop_policy_snippet:    pub fn constPointerAt(" in issues
        assert "missing_interop_policy_snippet:    pub fn readValueAt(" in issues

        _write(root, INTEROP_POLICY_REL, "\n".join(REQUIRED_INTEROP_POLICY_SNIPPETS) + "\n")
        _write(root, MMIO_REL, "\n".join(snippet for snippet in REQUIRED_MMIO_SNIPPETS if snippet != "pub fn read64Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u64 {") + "\n")
        issues = validate(root)
        assert "missing_mmio_snippet:pub fn read64Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u64 {" in issues

        _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
        _write(root, POLICY_TEST_REL, "\n".join(snippet for snippet in REQUIRED_POLICY_TEST_SNIPPETS if snippet != "try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u32, none_policy, base32, 0, 1));") + "\n")
        issues = validate(root)
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u32, none_policy, base32, 0, 1));" in issues

        _write(root, POLICY_TEST_REL, "\n".join(REQUIRED_POLICY_TEST_SNIPPETS) + "\n")
        _write(
            root,
            POLICY_TEST_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_POLICY_TEST_SNIPPETS
                if "none_policy.constSliceAt" not in snippet and "none_policy.constPointerAt" not in snippet and "none_policy.readValueAt" not in snippet
            )
            + "\n",
        )
        issues = validate(root)
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, none_policy.constSliceAt(u32, base, words.len));" in issues
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, none_policy.constPointerAt(u32, base));" in issues
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, none_policy.readValueAt(u32, base));" in issues

        _write(root, POLICY_TEST_REL, "\n".join(REQUIRED_POLICY_TEST_SNIPPETS) + "\n")
        _write(
            root,
            POLICY_TEST_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_POLICY_TEST_SNIPPETS
                if "mmio.write8Policy(none_policy" not in snippet
                and "mmio.read8Policy(none_policy" not in snippet
                and "mmio.write16Policy(none_policy" not in snippet
                and "mmio.read16Policy(none_policy" not in snippet
                and "mmio.write32Policy(none_policy" not in snippet
                and "mmio.read32Policy(none_policy" not in snippet
                and "mmio.write64Policy(none_policy" not in snippet
                and "mmio.read64Policy(none_policy" not in snippet
            )
            + "\n",
        )
        issues = validate(root)
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(none_policy, base32, 0, 1));" in issues
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Policy(none_policy, base32, 0));" in issues
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Policy(none_policy, base32, 0, 1));" in issues
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Policy(none_policy, base32, 0));" in issues
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(none_policy, base32, 0, 1));" in issues
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(none_policy, base32, 0));" in issues
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(none_policy, base64, 0, 1));" in issues
        assert "missing_policy_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Policy(none_policy, base64, 0));" in issues

        _write(root, POLICY_TEST_REL, "\n".join(REQUIRED_POLICY_TEST_SNIPPETS) + "\n")
        _write(root, SURVEY_REL, "\n".join(
            (
                "# Phase 3 Policy and Unsafe Boundary Survey",
                "",
                "- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`",
                "- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer`",
                "",
                *REQUIRED_SURVEY_SNIPPETS,
                "",
            )
        ) + "\n")
        issues = validate(root)
        assert "missing_survey_marker:PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig" in issues

        _write(root, SURVEY_REL, "\n".join(
            (
                "# Phase 3 Policy and Unsafe Boundary Survey",
                "",
                "- `PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig`",
                "- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`",
                "- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer`",
                "",
                *REQUIRED_SURVEY_SNIPPETS,
                "",
            )
        ) + "\n")
        _write(root, POLICY_BUILD_REL, "\n".join(snippet for snippet in REQUIRED_POLICY_BUILD_SNIPPETS if snippet != 'layout_assert_module.addImport("rbtree_bindings", rbtree_bindings_module);') + "\n")
        issues = validate(root)
        assert 'missing_policy_build_snippet:layout_assert_module.addImport("rbtree_bindings", rbtree_bindings_module);' in issues

        _write(root, POLICY_BUILD_REL, "\n".join(REQUIRED_POLICY_BUILD_SNIPPETS) + "\n")
        _write(root, POLICY_BUILD_REL, "\n".join(snippet for snippet in REQUIRED_POLICY_BUILD_SNIPPETS if snippet != 'root_module.addImport("layout_assert", layout_assert_module);') + "\n")
        issues = validate(root)
        assert 'missing_policy_build_snippet:root_module.addImport("layout_assert", layout_assert_module);' in issues

    print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the Phase 3 policy/unsafe packet still records and tests the full typed-policy MMIO consumer surface and direct raw-pointer bridge readers without widening into neighboring shared ABI dump governance."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())