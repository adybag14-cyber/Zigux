#!/usr/bin/env python3
"""Validate the current Phase 3 policy-and-unsafe survey packet."""

from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")
POLICY_SLICE_PATH = Path("Documentation/zigux/phase3-policy-slice.md")
LOW_LEVEL_SURVEY_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
LAYOUT_ASSERT_PATH = Path("zigux/helpers/layout_assert.zig")
PANIC_POLICY_PATH = Path("zigux/helpers/panic_policy.zig")
ALLOCATOR_POLICY_PATH = Path("zigux/helpers/allocator_policy.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
POLICY_STARTER_PACKET_PATH = Path("zigux/tests/phase3_policy_starter_packet.zig")
POLICY_STARTER_PACKET_BUILD_PATH = Path("zigux/tests/phase3_policy_starter_packet_build.zig")
POLICY_STARTER_PACKET_MANIFEST_PATH = Path("zigux/tests/phase3_policy_starter_packet_manifest.json")
POLICY_DUMP_PATH = Path("zigux/tests/phase3_policy_dump.zig")
POLICY_DUMP_BUILD_PATH = Path("zigux/tests/phase3_policy_dump_build.zig")
POLICY_DUMP_EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_policy_dump_expected.txt")
POLICY_UNSAFE_REPLAY_PATH = Path("zigux/tests/phase3_policy_unsafe.zig")
POLICY_UNSAFE_REPLAY_BUILD_PATH = Path("zigux/tests/phase3_policy_unsafe_build.zig")
LOW_LEVEL_WRAPPER_BUILD_PATH = Path("zigux/tests/phase3_low_level_wrappers_build.zig")

BLOB_FIELDS = {
    "PHASE3_LAYOUT_ASSERT_BLOB_SHA": LAYOUT_ASSERT_PATH,
    "PHASE3_PANIC_POLICY_BLOB_SHA": PANIC_POLICY_PATH,
    "PHASE3_ALLOCATOR_POLICY_BLOB_SHA": ALLOCATOR_POLICY_PATH,
    "PHASE3_UNSAFE_POLICY_BLOB_SHA": UNSAFE_POLICY_PATH,
    "PHASE3_MMIO_BLOB_SHA": MMIO_PATH,
    "PHASE3_UNSAFE_BLOB_SHA": NARROW_PATH,
    "PHASE3_POLICY_SLICE_DOC_BLOB_SHA": POLICY_SLICE_PATH,
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_DOC_BLOB_SHA": LOW_LEVEL_SURVEY_PATH,
}

REQUIRED_NOTE_MARKERS = (
    "PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig",
    "PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig",
    "PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig",
    "PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig",
    "PHASE3_UNSAFE_POLICY_SCOPE=helper-local-unsafe-scope-relay-over-the-shared-narrow-decoder-plus-access-boundary-surface-and-permit-audit-aliases",
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig",
    "PHASE3_POLICY_UNSAFE_SURVEY_GATE=python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "PHASE3_POLICY_STARTER_PACKET_MANIFEST_PATH=zigux/tests/phase3_policy_starter_packet_manifest.json",
    "PHASE3_POLICY_PACKET_GATE=python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "PHASE3_POLICY_PACKET_TEST_GATE=zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py",
    "PHASE3_POLICY_PACKET_MAKE_GATE=make -C zigux phase3-policy-starter-packet-test",
    "PHASE3_POLICY_DUMP_MAKE_GATE=make -C zigux phase3-policy-dump",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_MAKE_GATE=make -C zigux phase3-policy-unsafe-test",
    "PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-layout-assert-panic-policy-allocator-policy-unsafe-policy-mmio-or-narrow-helper-surfaces-or-the-dedicated-policy-unsafe-survey-gate-drift-again",
    "The blob markers above are therefore the authoritative current boundary evidence for this directly coupled policy-and-unsafe packet.",
    "PHASE3_POLICY_UNSAFE_REPLAY_PATH=zigux/tests/phase3_policy_unsafe.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_BUILD_PATH=zigux/tests/phase3_policy_unsafe_build.zig",
    "PHASE3_POLICY_UNSAFE_REPLAY_TEST_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "Current `master` also keeps `zigux/Makefile` plus `.github/workflows/zigux-bootstrap.yml` explicit with both the direct `zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig` replay and the returned `make -C zigux phase3-policy-unsafe-test` wrapper, so this survey should treat those support routes as current bounded packet evidence rather than leaving the dedicated policy-unsafe replay implicit behind the Zig-only route.",
)

REQUIRED_FILE_MARKERS = {
    LAYOUT_ASSERT_PATH: (
        "pub fn assertInteropPolicyLayout() LayoutError!void {",
        "pub fn assertPublishedAbiLayouts() LayoutError!void {",
        "pub fn assertInteropPolicyModeValues() void {",
        "pub fn assertNotifierChainPriorityIncreaseLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout() LayoutError!void {",
        "pub fn assertStatusAndFacilityValues() void {",
        "pub fn assertNotifierResultValues() void {",
    ),
    PANIC_POLICY_PATH: (
        "pub const Escalation = enum {",
        "pub fn escalationFromInteropPolicy(policy: abi.InteropPolicy) ?Escalation {",
        "pub fn permitsWarningOnlyContinuationInteropPolicy(policy: abi.InteropPolicy) bool {",
    ),
    ALLOCATOR_POLICY_PATH: (
        "pub const InitFlow = enum {",
        "pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {",
        "pub fn permitsGlobalFallbackPolicyBytes(mode: u8, reserved: u8) bool {",
        "pub fn initializesOwnedStatePolicyBytes(mode: u8, reserved: u8) bool {",
        "pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.AllocatorMode {",
        "pub fn requiresResetOnInitInteropPolicy(policy: abi.InteropPolicy) bool {",
    ),
    UNSAFE_POLICY_PATH: (
        "pub const AccessBoundary = enum {",
        "pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requiresDedicatedAuditInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn allowsVolatileMmioPolicyBytes(scope: u8, reserved: u8) bool {",
        "pub fn requiresVolatileMmioAccessPolicyBytes(scope: u8, reserved: u8) bool {",
        "pub fn requiresVolatileMmioAccessInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requiresRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {",
        "pub fn requiresRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn constSliceAtByte(",
        "pub fn writeValueAtByte(",
    ),
    MMIO_PATH: (
        "pub fn readInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *const volatile T) PolicyError!T {",
        "pub fn writeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!void {",
        "pub fn exchangeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!T {",
        "pub fn writeMaskedInteropPolicy(",
    ),
    NARROW_PATH: (
        "pub const Surface = enum {",
        "pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?UnsafeScopeTag {",
        "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
        "pub fn constPointerAtInteropPolicy(comptime T: type, address: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) const T {",
        "pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) const T {",
        "pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {",
        "pub fn writeValueAtInteropPolicy(comptime T: type, address: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!void {",
    ),
    MAKEFILE_PATH: (
        "phase3-policy-starter-packet-test:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
        "phase3-policy-dump:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
        "phase3-policy-unsafe-test:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    ),
    WORKFLOW_PATH: (
        "name: Run current Phase 3 policy unsafe replay",
        "run: zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
        "name: Run current Phase 3 policy unsafe make route",
        "run: make -C zigux phase3-policy-unsafe-test",
    ),
    POLICY_STARTER_PACKET_PATH: (
        'test "policy starter packet keeps narrow byte and denial symmetry explicit" {',
        'test "policy starter packet keeps unsafe alias symmetry explicit on shared records" {',
        'test "policy starter packet keeps unsafe require gates explicit on shared records" {',
        'test "policy starter packet keeps unsafe boundary and audit semantics explicit" {',
    ),
    POLICY_STARTER_PACKET_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/layout_assert.zig"),',
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        '.root_source_file = b.path("phase3_policy_starter_packet.zig"),',
        'root_module.addImport("layout_assert", layout_assert);',
        'root_module.addImport("narrow_surface", narrow_surface);',
        '"phase3-policy-starter-packet-test"',
    ),
    POLICY_STARTER_PACKET_MANIFEST_PATH: (
        '"phase": "Phase 3"',
        '"slug": "phase3-policy-starter-packet"',
        '"zigux/tests/phase3_policy_starter_packet_build.zig"',
        '"zigux/tests/phase3_policy_dump_build.zig"',
        '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
        '"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"',
        '"make -C zigux phase3-policy-starter-packet-test"',
        '"make -C zigux phase3"',
    ),
    POLICY_DUMP_PATH: (
        "const RawBridgeReplay = struct {",
        "fn rawBridgeReplay(policy: abi.InteropPolicy) RawBridgeReplay {",
        "const const_ptr = unsafe_policy.constPointerAtInteropPolicy(u32, second_addr, policy) catch {",
        "const const_slice = unsafe_policy.constSliceAtInteropPolicy(u32, first_addr, bridge_words.len, policy) catch {",
        "unsafe_policy.writeValueAtInteropPolicy(u32, second_addr, 73, policy) catch {",
        "const bridge_replay = rawBridgeReplay(policy);",
        '"bridge_read_ok={any}|bridge_write_ok={any}|narrow={s}|narrow_boundary={s}|narrow_surface={s}\\n",',
    ),
    POLICY_DUMP_BUILD_PATH: (
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        '.root_source_file = b.path("phase3_policy_dump.zig"),',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("narrow_surface", narrow_surface);',
        '.name = "phase3-policy-dump",',
        '"Dump the focused Phase 3 policy and unsafe substrate replay surface"',
    ),
    POLICY_DUMP_EXPECTED_PATH: (
        "safe-default|panic=abort|allocator=caller_provided|init_flow=caller_prepared|explicit_caller=true|owned_state=false|reset_on_init=false|unsafe=none|boundary=typed_safe|surface=safe_only|typed_only=true|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|bridge_read_ok=false|bridge_write_ok=false|narrow=none|narrow_boundary=typed_safe|narrow_surface=safe_only",
        "raw-bridge-warn|panic=warn|allocator=arena|init_flow=helper_owned_with_reset|explicit_caller=false|owned_state=true|reset_on_init=true|unsafe=raw_pointer_bridge|boundary=raw_pointer_bridge|surface=raw_pointer_bridge_only|typed_only=false|global_fallback=true|warn_only=true|mmio=false|raw_bridge=true|audit=true|bridge_read_ok=true|bridge_write_ok=true|narrow=raw_pointer_bridge|narrow_boundary=raw_pointer_bridge|narrow_surface=raw_pointer_bridge_only",
        "reserved-invalid|panic=invalid|allocator=invalid|init_flow=invalid|explicit_caller=false|owned_state=false|reset_on_init=false|unsafe=invalid|boundary=invalid|surface=invalid|typed_only=false|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|bridge_read_ok=false|bridge_write_ok=false|narrow=invalid|narrow_boundary=invalid|narrow_surface=invalid",
    ),
    POLICY_UNSAFE_REPLAY_PATH: (
        'test "phase3 policy unsafe replay decodes shared policy records" {',
        'test "phase3 policy unsafe replay keeps helper and narrow gates aligned" {',
        'test "phase3 policy unsafe replay keeps require gates fail closed" {',
        'test "phase3 policy unsafe replay keeps policy consequences explicit" {',
    ),
    POLICY_UNSAFE_REPLAY_BUILD_PATH: (
        '.root_source_file = b.path("phase3_policy_unsafe.zig"),',
        'root_module.addImport("panic_policy", panic_policy);',
        'root_module.addImport("allocator_policy", allocator_policy);',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("narrow", narrow);',
        '"phase3-policy-unsafe-test"',
        '"Run the focused Phase 3 policy and unsafe replay"',
    ),
    LOW_LEVEL_WRAPPER_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        '.root_source_file = b.path("phase3_low_level_wrappers.zig"),',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("narrow", narrow);',
        '"phase3-low-level-wrappers-test"',
    ),
}

SELF_TEST_CASES = (
    ("missing survey gate marker", NOTE_PATH, REQUIRED_NOTE_MARKERS[7], "marker"),
    ("missing low-level wrapper test gate marker", NOTE_PATH, REQUIRED_NOTE_MARKERS[15], "marker"),
    ("missing policy-unsafe make gate marker", NOTE_PATH, REQUIRED_NOTE_MARKERS[16], "marker"),
    ("missing next-step marker", NOTE_PATH, REQUIRED_NOTE_MARKERS[17], "marker"),
    ("missing dedicated replay path marker", NOTE_PATH, REQUIRED_NOTE_MARKERS[19], "marker"),
    ("missing dedicated replay build marker", NOTE_PATH, REQUIRED_NOTE_MARKERS[20], "marker"),
    ("missing policy-unsafe workflow paragraph", NOTE_PATH, REQUIRED_NOTE_MARKERS[22], "marker"),
    (
        "layout assert blob drift",
        LAYOUT_ASSERT_PATH,
        REQUIRED_FILE_MARKERS[LAYOUT_ASSERT_PATH][1],
        "blob",
        "PHASE3_LAYOUT_ASSERT_BLOB_SHA",
    ),
    (
        "unsafe policy raw-bridge require alias drift",
        UNSAFE_POLICY_PATH,
        REQUIRED_FILE_MARKERS[UNSAFE_POLICY_PATH][8],
        "marker",
    ),
    (
        "narrow const-slice marker drift",
        NARROW_PATH,
        REQUIRED_FILE_MARKERS[NARROW_PATH][4],
        "marker",
    ),
    (
        "missing policy replay consequence proof",
        POLICY_UNSAFE_REPLAY_PATH,
        REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_PATH][3],
        "marker",
    ),
    (
        "missing policy replay build route",
        POLICY_UNSAFE_REPLAY_BUILD_PATH,
        REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_BUILD_PATH][5],
        "marker",
    ),
    (
        "missing policy-unsafe make route",
        MAKEFILE_PATH,
        REQUIRED_FILE_MARKERS[MAKEFILE_PATH][5],
        "marker",
    ),
    (
        "missing policy-unsafe workflow route",
        WORKFLOW_PATH,
        REQUIRED_FILE_MARKERS[WORKFLOW_PATH][1],
        "marker",
    ),
    (
        "missing policy dump raw-bridge line",
        POLICY_DUMP_EXPECTED_PATH,
        REQUIRED_FILE_MARKERS[POLICY_DUMP_EXPECTED_PATH][1],
        "marker",
    ),
)

SAMPLE_FILE_TEXT = {
    POLICY_SLICE_PATH: "# sample policy slice\n",
    LOW_LEVEL_SURVEY_PATH: "# sample low-level survey\n",
    LAYOUT_ASSERT_PATH: "\n".join(REQUIRED_FILE_MARKERS[LAYOUT_ASSERT_PATH]) + "\n",
    PANIC_POLICY_PATH: "\n".join(REQUIRED_FILE_MARKERS[PANIC_POLICY_PATH]) + "\n",
    ALLOCATOR_POLICY_PATH: "\n".join(REQUIRED_FILE_MARKERS[ALLOCATOR_POLICY_PATH]) + "\n",
    UNSAFE_POLICY_PATH: "\n".join(REQUIRED_FILE_MARKERS[UNSAFE_POLICY_PATH]) + "\n",
    MMIO_PATH: "\n".join(REQUIRED_FILE_MARKERS[MMIO_PATH]) + "\n",
    NARROW_PATH: "\n".join(REQUIRED_FILE_MARKERS[NARROW_PATH]) + "\n",
    MAKEFILE_PATH: "\n".join(REQUIRED_FILE_MARKERS[MAKEFILE_PATH]) + "\n",
    WORKFLOW_PATH: "\n".join(REQUIRED_FILE_MARKERS[WORKFLOW_PATH]) + "\n",
    POLICY_STARTER_PACKET_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_STARTER_PACKET_PATH]) + "\n",
    POLICY_STARTER_PACKET_BUILD_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_STARTER_PACKET_BUILD_PATH]) + "\n",
    POLICY_STARTER_PACKET_MANIFEST_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_STARTER_PACKET_MANIFEST_PATH]) + "\n",
    POLICY_DUMP_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_DUMP_PATH]) + "\n",
    POLICY_DUMP_BUILD_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_DUMP_BUILD_PATH]) + "\n",
    POLICY_DUMP_EXPECTED_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_DUMP_EXPECTED_PATH]) + "\n",
    POLICY_UNSAFE_REPLAY_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_PATH]) + "\n",
    POLICY_UNSAFE_REPLAY_BUILD_PATH: "\n".join(REQUIRED_FILE_MARKERS[POLICY_UNSAFE_REPLAY_BUILD_PATH]) + "\n",
    LOW_LEVEL_WRAPPER_BUILD_PATH: "\n".join(REQUIRED_FILE_MARKERS[LOW_LEVEL_WRAPPER_BUILD_PATH]) + "\n",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git_blob_sha(text: str) -> str:
    payload = text.encode("utf-8")
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def render_note(sample_files: dict[Path, str]) -> str:
    blob_lines = [
        f"- `{field}={git_blob_sha(sample_files[path])}`"
        for field, path in BLOB_FIELDS.items()
    ]
    marker_lines = [f"- `{marker}`" for marker in REQUIRED_NOTE_MARKERS]
    return "\n".join(["# sample survey", *marker_lines, *blob_lines, ""])


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    note_path = repo_root / NOTE_PATH
    try:
        note_text = _read(note_path)
    except FileNotFoundError:
        return [f"missing repo file: {NOTE_PATH.as_posix()}"]

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"missing {NOTE_PATH.as_posix()} marker: {marker}")

    for field, relative_path in BLOB_FIELDS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        expected_line = f"{field}={git_blob_sha(text)}"
        if expected_line not in note_text:
            issues.append(
                f"wrong {NOTE_PATH.as_posix()} blob marker: expected {expected_line}"
            )

    for relative_path, markers in REQUIRED_FILE_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    return issues


def populate_sample_repo(root: Path) -> None:
    sample_files = dict(SAMPLE_FILE_TEXT)
    sample_files[NOTE_PATH] = render_note(sample_files)
    for relative_path, text in sample_files.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_survey_") as temp_dir:
        root = Path(temp_dir)
        populate_sample_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for case in SELF_TEST_CASES:
            case_name, relative_path, marker, mutation = case[:4]
            populate_sample_repo(root)
            path = root / relative_path
            text = _read(path)
            path.write_text(text.replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            if mutation == "marker":
                expected = f"missing {relative_path.as_posix()} marker: {marker}"
                if expected not in issues:
                    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=fail")
                    print(f"{case_name}: expected issue not reported: {expected}")
                    return 1
            else:
                field_name = case[4]
                if not any(
                    issue.startswith(
                        f"wrong {NOTE_PATH.as_posix()} blob marker: expected {field_name}="
                    )
                    for issue in issues
                ):
                    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=fail")
                    print(f"{case_name}: expected blob-drift issue was not reported")
                    return 1

    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 policy-and-unsafe survey packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_POLICY_UNSAFE_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    print("PHASE3_POLICY_UNSAFE_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
