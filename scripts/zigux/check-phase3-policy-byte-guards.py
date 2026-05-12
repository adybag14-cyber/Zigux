#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
PANIC_REL = "zigux/helpers/panic_policy.zig"
ALLOCATOR_REL = "zigux/helpers/allocator_policy.zig"
NARROW_REL = "zigux/unsafe/narrow.zig"
FOCUSED_REPLAY_REL = "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"
MMIO_CONSUMER_REL = "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py",
    "dedicated reserved-byte and typed-wrapper guard",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "shared dump gate",
)

REQUIRED_PANIC_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.PanicMode {",
    "pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {",
    "pub fn actionForInteropPolicyBytes(mode: u8, reserved: u8) ?Action {",
    "pub fn canReturnInteropPolicyBytes(mode: u8, reserved: u8) bool {",
    'try std.testing.expectEqual(@as(?abi.PanicMode, null), modeFromInteropPolicyBytes(2, 1));',
    'try std.testing.expectEqual(@as(?Action, null), actionForInteropPolicyBytes(2, 1));',
    'try std.testing.expect(!canReturnInteropPolicyBytes(2, 1));',
)

REQUIRED_ALLOCATOR_SNIPPETS = (
    "pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.AllocatorMode {",
    "pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {",
    "pub fn requiresExplicitCallerPolicyBytes(mode: u8, reserved: u8) bool {",
    "pub fn permitsGlobalFallbackPolicyBytes(mode: u8, reserved: u8) bool {",
    'try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(2, 1));',
    'try std.testing.expect(!recognizesInteropPolicyBytes(2, 1));',
    'try std.testing.expect(!requiresExplicitCallerPolicyBytes(2, 1));',
    'try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));',
)

REQUIRED_NARROW_SNIPPETS = (
    "pub fn permitsRawPointerBridgeByte(unsafe_scope: u8) bool {",
    "pub fn requireRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {",
    "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    'try std.testing.expect(permitsRawPointerBridgeByte(2));',
    'try std.testing.expect(!permitsRawPointerBridgePolicyBytes(2, 1));',
    'try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(reserved_policy));',
)

REQUIRED_FOCUSED_REPLAY_SNIPPETS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
)

REQUIRED_MMIO_CONSUMER_SNIPPETS = (
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "zigux/helpers/mmio.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
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
    panic = _read_text(root, PANIC_REL, issues)
    allocator = _read_text(root, ALLOCATOR_REL, issues)
    narrow = _read_text(root, NARROW_REL, issues)
    focused_replay = _read_text(root, FOCUSED_REPLAY_REL, issues)
    mmio_consumer = _read_text(root, MMIO_CONSUMER_REL, issues)

    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
    if panic:
        _check_snippets(panic, REQUIRED_PANIC_SNIPPETS, "missing_panic_snippet", issues)
    if allocator:
        _check_snippets(allocator, REQUIRED_ALLOCATOR_SNIPPETS, "missing_allocator_snippet", issues)
    if narrow:
        _check_snippets(narrow, REQUIRED_NARROW_SNIPPETS, "missing_narrow_snippet", issues)
    if focused_replay:
        _check_snippets(focused_replay, REQUIRED_FOCUSED_REPLAY_SNIPPETS, "missing_focused_replay_snippet", issues)
    if mmio_consumer:
        _check_snippets(mmio_consumer, REQUIRED_MMIO_CONSUMER_SNIPPETS, "missing_mmio_consumer_snippet", issues)
    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_byte_guards_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS) + "\n")
        _write(root, PANIC_REL, "\n".join(REQUIRED_PANIC_SNIPPETS) + "\n")
        _write(root, ALLOCATOR_REL, "\n".join(REQUIRED_ALLOCATOR_SNIPPETS) + "\n")
        _write(root, NARROW_REL, "\n".join(REQUIRED_NARROW_SNIPPETS) + "\n")
        _write(root, FOCUSED_REPLAY_REL, "\n".join(REQUIRED_FOCUSED_REPLAY_SNIPPETS) + "\n")
        _write(root, MMIO_CONSUMER_REL, "\n".join(REQUIRED_MMIO_CONSUMER_SNIPPETS) + "\n")
        assert validate(root) == []

        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS[1:]) + "\n")
        issues = validate(root)
        assert f"missing_survey_marker:{REQUIRED_SURVEY_MARKERS[0]}" in issues

        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS[:1] + REQUIRED_SURVEY_MARKERS[2:]) + "\n")
        issues = validate(root)
        assert f"missing_survey_marker:{REQUIRED_SURVEY_MARKERS[1]}" in issues

        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_survey_marker:{REQUIRED_SURVEY_MARKERS[-1]}" in issues

        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS) + "\n")
        _write(root, NARROW_REL, "\n".join(REQUIRED_NARROW_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_narrow_snippet:{REQUIRED_NARROW_SNIPPETS[-1]}" in issues

        _write(root, NARROW_REL, "\n".join(REQUIRED_NARROW_SNIPPETS) + "\n")
        _write(root, PANIC_REL, "\n".join(REQUIRED_PANIC_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_panic_snippet:{REQUIRED_PANIC_SNIPPETS[-1]}" in issues

        _write(root, PANIC_REL, "\n".join(REQUIRED_PANIC_SNIPPETS) + "\n")
        _write(root, ALLOCATOR_REL, "\n".join(REQUIRED_ALLOCATOR_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_allocator_snippet:{REQUIRED_ALLOCATOR_SNIPPETS[-1]}" in issues

        _write(root, ALLOCATOR_REL, "\n".join(REQUIRED_ALLOCATOR_SNIPPETS) + "\n")
        _write(root, FOCUSED_REPLAY_REL, "\n".join(REQUIRED_FOCUSED_REPLAY_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_focused_replay_snippet:{REQUIRED_FOCUSED_REPLAY_SNIPPETS[-1]}" in issues

        _write(root, FOCUSED_REPLAY_REL, "\n".join(REQUIRED_FOCUSED_REPLAY_SNIPPETS) + "\n")
        _write(root, MMIO_CONSUMER_REL, "\n".join(REQUIRED_MMIO_CONSUMER_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert f"missing_mmio_consumer_snippet:{REQUIRED_MMIO_CONSUMER_SNIPPETS[-1]}" in issues

    print("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST=pass")
    print("PHASE3_POLICY_BYTE_GUARDS_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail closed on the Phase 3 policy-byte and reserved-byte guard packet.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_POLICY_BYTE_GUARDS=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_POLICY_BYTE_GUARDS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
