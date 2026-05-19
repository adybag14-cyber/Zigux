#!/usr/bin/env python3
"""Validate the current Phase 3 policy/unsafe boundary survey packet."""

from __future__ import annotations

import argparse
import hashlib
import re
import tempfile
from pathlib import Path


SURVEY_PATH = Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")
POLICY_SLICE_PATH = Path("Documentation/zigux/phase3-policy-slice.md")
LOW_LEVEL_SURVEY_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
LAYOUT_ASSERT_PATH = Path("zigux/helpers/layout_assert.zig")
PANIC_POLICY_PATH = Path("zigux/helpers/panic_policy.zig")
ALLOCATOR_POLICY_PATH = Path("zigux/helpers/allocator_policy.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
POLICY_PACKET_GATE_PATH = Path("scripts/zigux/check-phase3-policy-starter-packet.py")
POLICY_DUMP_GATE_PATH = Path("scripts/zigux/check-phase3-policy-dump.py")
LOW_LEVEL_GATE_PATH = Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")

REQUIRED_SURVEY_MARKERS = (
    "# Phase 3 Policy and Unsafe Boundary Survey",
    "PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig",
    "PHASE3_POLICY_PACKET_GATE=python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-helper-local-policy-slice-and-the-directly-coupled-low-level-wrapper-packet",
    "PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-the-helper-local-policy-slice-or-the-directly-coupled-low-level-wrapper-survey-drifts-again",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
)

REQUIRED_COMPANION_MARKERS = {
    POLICY_SLICE_PATH: (
        "PHASE3_POLICY_SLICE_FILE_COUNT=",
        "zigux/helpers/unsafe_policy.zig",
        "zigux/tests/phase3_policy_starter_packet_manifest.json",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
        "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
    ),
    LOW_LEVEL_SURVEY_PATH: (
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=",
        "zigux/helpers/mmio.zig",
        "zigux/helpers/unsafe_policy.zig",
        "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    LAYOUT_ASSERT_PATH: (
        "pub fn assertInteropPolicyLayout() LayoutError!void {",
    ),
    PANIC_POLICY_PATH: (
        "pub const Escalation = enum {",
        "pub fn emitsKernelBug(mode: abi.PanicMode) bool {",
    ),
    ALLOCATOR_POLICY_PATH: (
        "pub const InitFlow = enum {",
        "pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {",
    ),
    UNSAFE_POLICY_PATH: (
        "pub const AccessBoundary = enum {",
        "pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    ),
    MMIO_PATH: (
        "pub fn readScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *const volatile T) PolicyError!T {",
        "pub fn writeMaskedInteropPolicyBytes(",
    ),
    NARROW_PATH: (
        "pub const Surface = enum {",
        "pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {",
        "pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {",
    ),
    POLICY_PACKET_GATE_PATH: (
        "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass",
        "PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES=",
    ),
    POLICY_DUMP_GATE_PATH: (
        "PHASE3_POLICY_DUMP_SELF_TEST=pass",
        "PHASE3_POLICY_DUMP_EXPECTED_LINE_COUNT=",
    ),
    LOW_LEVEL_GATE_PATH: (
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=",
    ),
}

DECLARED_BLOB_FIELDS = {
    "PHASE3_LAYOUT_ASSERT_BLOB_SHA": LAYOUT_ASSERT_PATH,
    "PHASE3_PANIC_POLICY_BLOB_SHA": PANIC_POLICY_PATH,
    "PHASE3_ALLOCATOR_POLICY_BLOB_SHA": ALLOCATOR_POLICY_PATH,
    "PHASE3_UNSAFE_POLICY_BLOB_SHA": UNSAFE_POLICY_PATH,
    "PHASE3_MMIO_BLOB_SHA": MMIO_PATH,
    "PHASE3_UNSAFE_BLOB_SHA": NARROW_PATH,
    "PHASE3_POLICY_SLICE_DOC_BLOB_SHA": POLICY_SLICE_PATH,
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_DOC_BLOB_SHA": LOW_LEVEL_SURVEY_PATH,
}

SELF_TEST_LAYOUT_ASSERT = """\
pub fn assertInteropPolicyLayout() LayoutError!void {
}
"""

SELF_TEST_PANIC_POLICY = """\
pub const Escalation = enum {
    immediate_abort,
};
pub fn emitsKernelBug(mode: abi.PanicMode) bool {
    _ = mode;
    return false;
}
"""

SELF_TEST_ALLOCATOR_POLICY = """\
pub const InitFlow = enum {
    caller_prepared,
};
pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {
    _ = mode;
    return false;
}
"""

SELF_TEST_UNSAFE_POLICY = """\
pub const AccessBoundary = enum {
    typed_safe,
};
pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {
    _ = policy;
    return true;
}
pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {
    _ = policy;
    return false;
}
pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    _ = policy;
    return false;
}
"""

SELF_TEST_MMIO = """\
pub fn readScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *const volatile T) PolicyError!T {
    _ = .{ T, scope, ptr };
    return undefined;
}
pub fn writeMaskedInteropPolicyBytes(
) void {}
"""

SELF_TEST_NARROW = """\
pub const Surface = enum {
    safe_only,
};
pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {
    _ = .{ T, address, byte_len, unsafe_scope, reserved };
    return undefined;
}
pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {
    _ = .{ T, address, value, unsafe_scope, reserved };
}
"""

SELF_TEST_POLICY_SLICE = """\
# Phase 3 Policy Slice
- `PHASE3_POLICY_SLICE_FILE_COUNT=sample`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `python3 scripts/zigux/check-phase3-policy-dump.py --self-test`
"""

SELF_TEST_LOW_LEVEL_SURVEY = """\
# Phase 3 Low-Level Wrapper Boundary Survey
- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=sample`
- `zigux/helpers/mmio.zig`
- `zigux/helpers/unsafe_policy.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
"""

SELF_TEST_POLICY_PACKET_GATE = """\
PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass
PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES=1
"""

SELF_TEST_POLICY_DUMP_GATE = """\
PHASE3_POLICY_DUMP_SELF_TEST=pass
PHASE3_POLICY_DUMP_EXPECTED_LINE_COUNT=4
"""

SELF_TEST_LOW_LEVEL_GATE = """\
PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass
PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=4
"""

SELF_TEST_SURVEY_TEMPLATE = """\
# Phase 3 Policy and Unsafe Boundary Survey
- `PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA={layout_assert_sha}`
- `PHASE3_PANIC_POLICY_BLOB_SHA={panic_policy_sha}`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA={allocator_policy_sha}`
- `PHASE3_UNSAFE_POLICY_BLOB_SHA={unsafe_policy_sha}`
- `PHASE3_MMIO_BLOB_SHA={mmio_sha}`
- `PHASE3_UNSAFE_BLOB_SHA={narrow_sha}`
- `PHASE3_POLICY_SLICE_DOC_BLOB_SHA={policy_slice_sha}`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_DOC_BLOB_SHA={low_level_sha}`
- `PHASE3_POLICY_PACKET_GATE=python3 scripts/zigux/check-phase3-policy-starter-packet.py`
- `PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py`
- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-helper-local-policy-slice-and-the-directly-coupled-low-level-wrapper-packet`
- `PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-the-helper-local-policy-slice-or-the-directly-coupled-low-level-wrapper-survey-drifts-again`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
"""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _git_blob_sha(text: str) -> str:
    data = text.encode("utf-8")
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def _extract_declared_blob(text: str, field: str) -> str | None:
    match = re.search(rf"{re.escape(field)}=([0-9a-f]{{40}})", text)
    return match.group(1) if match else None


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    survey_path = repo_root / SURVEY_PATH
    try:
        survey_text = _read(survey_path)
    except FileNotFoundError:
        return [f"missing repo file: {SURVEY_PATH.as_posix()}"]

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey_text:
            issues.append(f"missing {SURVEY_PATH.as_posix()} marker: {marker}")

    for field, rel_path in DECLARED_BLOB_FIELDS.items():
        target_path = repo_root / rel_path
        try:
            target_text = _read(target_path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue

        declared_sha = _extract_declared_blob(survey_text, field)
        if declared_sha is None:
            issues.append(f"missing {SURVEY_PATH.as_posix()} blob marker: {field}")
            continue

        actual_sha = _git_blob_sha(target_text)
        if declared_sha != actual_sha:
            issues.append(
                f"{SURVEY_PATH.as_posix()} wrong {field}: {declared_sha} != {actual_sha}"
            )

    for rel_path, markers in REQUIRED_COMPANION_MARKERS.items():
        path = repo_root / rel_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    return issues


def _populate_self_test_repo(root: Path) -> None:
    files = {
        LAYOUT_ASSERT_PATH: SELF_TEST_LAYOUT_ASSERT,
        PANIC_POLICY_PATH: SELF_TEST_PANIC_POLICY,
        ALLOCATOR_POLICY_PATH: SELF_TEST_ALLOCATOR_POLICY,
        UNSAFE_POLICY_PATH: SELF_TEST_UNSAFE_POLICY,
        MMIO_PATH: SELF_TEST_MMIO,
        NARROW_PATH: SELF_TEST_NARROW,
        POLICY_SLICE_PATH: SELF_TEST_POLICY_SLICE,
        LOW_LEVEL_SURVEY_PATH: SELF_TEST_LOW_LEVEL_SURVEY,
        POLICY_PACKET_GATE_PATH: SELF_TEST_POLICY_PACKET_GATE,
        POLICY_DUMP_GATE_PATH: SELF_TEST_POLICY_DUMP_GATE,
        LOW_LEVEL_GATE_PATH: SELF_TEST_LOW_LEVEL_GATE,
    }

    for rel_path, text in files.items():
        _write(root / rel_path, text)

    _write(
        root / SURVEY_PATH,
        SELF_TEST_SURVEY_TEMPLATE.format(
            layout_assert_sha=_git_blob_sha(SELF_TEST_LAYOUT_ASSERT),
            panic_policy_sha=_git_blob_sha(SELF_TEST_PANIC_POLICY),
            allocator_policy_sha=_git_blob_sha(SELF_TEST_ALLOCATOR_POLICY),
            unsafe_policy_sha=_git_blob_sha(SELF_TEST_UNSAFE_POLICY),
            mmio_sha=_git_blob_sha(SELF_TEST_MMIO),
            narrow_sha=_git_blob_sha(SELF_TEST_NARROW),
            policy_slice_sha=_git_blob_sha(SELF_TEST_POLICY_SLICE),
            low_level_sha=_git_blob_sha(SELF_TEST_LOW_LEVEL_SURVEY),
        ),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_survey_") as tmp_dir:
        root = Path(tmp_dir)
        _populate_self_test_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_POLICY_UNSAFE_BOUNDARY_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        survey_path = root / SURVEY_PATH
        survey_text = _read(survey_path)
        _write(
            survey_path,
            survey_text.replace(
                "PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected = (
            "missing Documentation/zigux/phase3-policy-unsafe-boundary-survey.md marker: "
            "PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py"
        )
        if expected not in issues:
            print("PHASE3_POLICY_UNSAFE_BOUNDARY_SURVEY_SELF_TEST=fail")
            print(f"expected missing survey marker was not reported: {expected}")
            return 1

        _populate_self_test_repo(root)
        _write(root / MMIO_PATH, SELF_TEST_MMIO + "\n// drift\n")
        issues = validate_repo(root)
        expected_prefix = (
            "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md wrong "
            "PHASE3_MMIO_BLOB_SHA:"
        )
        if not any(issue.startswith(expected_prefix) for issue in issues):
            print("PHASE3_POLICY_UNSAFE_BOUNDARY_SURVEY_SELF_TEST=fail")
            print(f"expected blob mismatch was not reported: {expected_prefix}")
            return 1

        _populate_self_test_repo(root)
        _write(
            root / LOW_LEVEL_GATE_PATH,
            SELF_TEST_LOW_LEVEL_GATE.replace(
                "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=4\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected = (
            "missing scripts/zigux/validate-phase3-low-level-wrapper-survey.py marker: "
            "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT="
        )
        if expected not in issues:
            print("PHASE3_POLICY_UNSAFE_BOUNDARY_SURVEY_SELF_TEST=fail")
            print(f"expected missing companion marker was not reported: {expected}")
            return 1

    print("PHASE3_POLICY_UNSAFE_BOUNDARY_SURVEY_SELF_TEST=pass")
    print("PHASE3_POLICY_UNSAFE_BOUNDARY_SURVEY_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 policy/unsafe boundary survey packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_POLICY_UNSAFE_BOUNDARY_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / SURVEY_PATH}")
    print(f"validated {args.repo_root / POLICY_SLICE_PATH}")
    print(f"validated {args.repo_root / LOW_LEVEL_SURVEY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
