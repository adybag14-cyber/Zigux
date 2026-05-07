#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
PANIC_POLICY_REL = "zigux/helpers/panic_policy.zig"
ALLOCATOR_POLICY_REL = "zigux/helpers/allocator_policy.zig"
UNSAFE_NARROW_REL = "zigux/unsafe/narrow.zig"

REQUIRED_SURVEY_SNIPPETS = (
    "`PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`",
    "`zigux/helpers/panic_policy.zig` now keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes` so unknown panic modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.",
    "`zigux/helpers/allocator_policy.zig` now keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, and `permitsGlobalFallbackPolicyBytes` so unknown allocator modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.",
    "`zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it now also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.",
)

REQUIRED_PANIC_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.PanicMode {",
    "if (reserved != 0) return null;",
    "pub fn actionForInteropPolicyBytes(mode: u8, reserved: u8) ?Action {",
    "return actionFor(modeFromInteropPolicyBytes(mode, reserved) orelse return null);",
    "pub fn canReturnInteropPolicyBytes(mode: u8, reserved: u8) bool {",
    "return actionForInteropPolicyBytes(mode, reserved) == .warn_and_return;",
    "try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(2, 1));",
    "try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicyBytes(2, 1));",
    "try std.testing.expect(!canReturnInteropPolicyBytes(2, 1));",
)

REQUIRED_ALLOCATOR_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.AllocatorMode {",
    "if (reserved != 0) return null;",
    "pub fn requiresExplicitCallerPolicyBytes(mode: u8, reserved: u8) bool {",
    "return modeFromInteropPolicyBytes(mode, reserved) == .caller_provided;",
    "pub fn permitsGlobalFallbackPolicyBytes(mode: u8, reserved: u8) bool {",
    "return switch (modeFromInteropPolicyBytes(mode, reserved) orelse return false) {",
    "try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(2, 1));",
    "try std.testing.expect(!requiresExplicitCallerPolicyBytes(2, 1));",
    "try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));",
)

REQUIRED_UNSAFE_SNIPPETS = (
    "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
    "if (reserved != 0) return null;",
    "try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));",
    "try std.testing.expect(!permitsRawPointerBridgePolicyBytes(2, 1));",
)


def require_snippets(issues: list[str], text: str, prefix: str, snippets: tuple[str, ...]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"missing_{prefix}_snippet:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = (root / SURVEY_REL).read_text(encoding="utf-8")
    panic = (root / PANIC_POLICY_REL).read_text(encoding="utf-8")
    allocator = (root / ALLOCATOR_POLICY_REL).read_text(encoding="utf-8")
    unsafe = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8")

    require_snippets(issues, survey, "survey", REQUIRED_SURVEY_SNIPPETS)
    require_snippets(issues, panic, "panic", REQUIRED_PANIC_SNIPPETS)
    require_snippets(issues, allocator, "allocator", REQUIRED_ALLOCATOR_SNIPPETS)
    require_snippets(issues, unsafe, "unsafe", REQUIRED_UNSAFE_SNIPPETS)
    return issues


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_valid_workspace(root: Path) -> None:
    write(root / SURVEY_REL, "\n".join(["# survey", *REQUIRED_SURVEY_SNIPPETS, ""]))
    write(root / PANIC_POLICY_REL, "\n".join([*REQUIRED_PANIC_SNIPPETS, ""]))
    write(root / ALLOCATOR_POLICY_REL, "\n".join([*REQUIRED_ALLOCATOR_SNIPPETS, ""]))
    write(root / UNSAFE_NARROW_REL, "\n".join([*REQUIRED_UNSAFE_SNIPPETS, ""]))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_byte_guard_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == []

        broken_survey = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes`",
            "modeFromByte`, `actionForByte`, and `canReturnByte`",
            1,
        )
        write(root / SURVEY_REL, broken_survey)
        issues = validate(root)
        assert any(issue.startswith("missing_survey_snippet:") for issue in issues)

        build_valid_workspace(root)
        broken_dump_gate = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "`PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`\n",
            "",
            1,
        )
        write(root / SURVEY_REL, broken_dump_gate)
        issues = validate(root)
        assert (
            "missing_survey_snippet:`PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`"
            in issues
        )

        build_valid_workspace(root)
        broken_panic = (root / PANIC_POLICY_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(!canReturnInteropPolicyBytes(2, 1));\n",
            "",
            1,
        )
        write(root / PANIC_POLICY_REL, broken_panic)
        issues = validate(root)
        assert (
            "missing_panic_snippet:try std.testing.expect(!canReturnInteropPolicyBytes(2, 1));" in issues
        )

        build_valid_workspace(root)
        broken_allocator = (root / ALLOCATOR_POLICY_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));\n",
            "",
            1,
        )
        write(root / ALLOCATOR_POLICY_REL, broken_allocator)
        issues = validate(root)
        assert (
            "missing_allocator_snippet:try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));"
            in issues
        )

        build_valid_workspace(root)
        broken_unsafe = (root / UNSAFE_NARROW_REL).read_text(encoding="utf-8").replace(
            "try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));\n",
            "",
            1,
        )
        write(root / UNSAFE_NARROW_REL, broken_unsafe)
        issues = validate(root)
        assert "missing_unsafe_snippet:try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));" in issues

    print("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST=pass")
    print("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 3 policy helpers and survey still guard InteropPolicy reserved bytes."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_POLICY_BYTE_GUARDS=fail")
        print("PHASE3_POLICY_BYTE_GUARDS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_POLICY_BYTE_GUARDS_ISSUES_END")
        return 1

    print("PHASE3_POLICY_BYTE_GUARDS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
