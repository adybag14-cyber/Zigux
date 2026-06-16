const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass";

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_policy_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "make -C zigux phase3-policy-starter-packet-test",
    "zig run scripts\\zigux/check_phase3_policy_dump.zig --self-test",
    "zig run scripts\\zigux/check_phase3_policy_dump.zig",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "make -C zigux phase3-policy-dump",
    "zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "make -C zigux phase3-policy-unsafe-test",
    "zig run scripts\\zigux/validate_phase3_policy_unsafe_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_policy_unsafe_survey.zig",
    "make -C zigux phase3",
};

const UPDATED_SHARED_REMINDER_MARKER = [_][]const u8{
    "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the dedicated ABI header-family survey follow-through, the focused abi.h next-step note, the shared ABI catalog helper plus manifest-backed inventory companion, the bounded bitmap/cpumask and list/hlist helper slices, the shared tests-root export/UAPI layout route, the named Linux-side boundary-header helper family plus validation relay, and the direct C smoke proof; the docs-root reminder, shared review checklist, tests-root reminder, and scripts-root reminder are now aligned on those already-returned helper-local slices, and no same-lane shared-summary drift remains on current master",
};

const UPDATED_SHARED_REMINDER_NEXT_STEP_MARKER = [_][]const u8{
    "PHASE3_SHARED_REMINDER_NEXT_STEP=keep this note parked unless a fresh current-master reread shows a smaller one-file shared-summary drift around the returned export/UAPI, bitmap/cpumask, list/hlist, shared tests-root layout, named boundary-header helper, or direct C smoke packet",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-policy-slice_md = [_][]const u8{
    "PHASE3_POLICY_SLICE_FILE_COUNT=",
    "PHASE3_POLICY_SLICE_SCOPE=this slice proves shared InteropPolicy layout assertions, panic escalation, allocator-init ownership, and unsafe-scope reviewability by cross-checking the helper-local decoder against zigux/unsafe/narrow.zig, including the newer whole-policy and byte-level review entry points, and by replaying one focused policy dump that now also proves raw-pointer bridge reads and writes over the same bounded records without widening into unsafe wrappers, runtime shims, or broader export-boundary claims",
    "PHASE3_POLICY_NEXT_SAFE_STEP=",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "zig run scripts\\zigux/check_phase3_policy_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_policy_dump.zig --self-test",
    "zig run scripts\\zigux/check_phase3_policy_dump.zig",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "Current `master` now separately serves the shared ABI core replay through `zigux/tests/phase3_abi.zig`, the shared ABI checker through `scripts\\zigux/check_phase3_abi.zig`, and the shared Phase 3 validator entrypoint through `scripts\\zigux/validate_phase3.zig`",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md = [_][]const u8{
    "## Focused policy slice present on `master`",
    "Documentation/zigux/phase3-policy-slice.md",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "scripts\\zigux/check_phase3_policy_dump.zig",
    "scripts\\zigux/check_phase3_abi.zig",
    "scripts\\zigux/validate_phase3.zig",
    "Current `master` also directly serves the same focused policy slice through the reviewer-readable dump route at `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, and `scripts\\zigux/check_phase3_policy_dump.zig`, so the bounded policy packet now exposes both its starter replay and its focused dump companion without widening this note into MMIO, low-level-wrapper, or broader runtime-shim ownership.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-shared-reminder-gap_md = [_][]const u8{
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/phase3_catalog.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
};

const REQUIRED_MARKERS__include_zigux_abi_h = [_][]const u8{
    "#define ZIGUX_PANIC_ABORT 0U",
    "#define ZIGUX_ALLOC_KERNEL_HEAP 1U",
    "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
    "struct zigux_interop_policy {",
};

const REQUIRED_MARKERS__zigux_bindings_abi_zig = [_][]const u8{
    "pub const PanicMode = enum(u8) {",
    "pub const AllocatorMode = enum(u8) {",
    "pub const UnsafeScope = enum(u8) {",
    "pub const InteropPolicy = extern struct {",
};

const REQUIRED_MARKERS__zigux_bindings_notifier_abi_zig = [_][]const u8{
    "pub const NotifierBlock = extern struct {",
};

const REQUIRED_MARKERS__zigux_helpers_layout_assert_zig = [_][]const u8{
    "pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void {",
    "pub fn assertBoundaryHeaderLayout() LayoutError!void {",
    "pub fn assertExportStatusLayout() LayoutError!void {",
    "pub fn assertInteropPolicyLayout() LayoutError!void {",
    "pub fn assertInteropPolicyModeValues() void {",
};

const REQUIRED_MARKERS__zigux_helpers_panic_policy_zig = [_][]const u8{
    "pub const Escalation = enum {",
    "pub fn emitsKernelBug(mode: abi.PanicMode) bool {",
};

const REQUIRED_MARKERS__zigux_helpers_allocator_policy_zig = [_][]const u8{
    "pub const InitFlow = enum {",
    "pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {",
};

const REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig = [_][]const u8{
    "pub const AccessBoundary = enum {",
    "pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
};

const REQUIRED_MARKERS__zigux_unsafe_narrow_zig = [_][]const u8{
    "pub const Surface = enum {",
    "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
    "pub fn permitsNoUnsafePolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn permitsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn requireNoUnsafeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    "pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    "pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_policy_starter_packet_zig = [_][]const u8{
    "test \"policy starter packet decodes shared interop policy records\" {",
    "test \"policy starter packet keeps narrow-surface decoding aligned\" {",
    "test \"policy starter packet keeps narrow byte and denial symmetry explicit\" {",
    "test \"policy starter packet keeps unsafe alias symmetry explicit on shared records\" {",
    "test \"policy starter packet keeps unsafe require gates explicit on shared records\" {",
    "test \"policy starter packet keeps unsafe boundary and audit semantics explicit\" {",
    "test \"policy starter packet keeps unsafe surface mappings explicit\" {",
    "test \"policy starter packet keeps panic and allocator byte guards explicit\" {",
    "test \"panic policy starter packet keeps escalation semantics explicit\" {",
    "test \"allocator policy starter packet keeps init ownership semantics explicit\" {",
    "test \"unsafe policy starter packet keeps access semantics explicit\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_policy_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../helpers/unsafe_policy.zig\"),",
    "root_module.addImport(\"narrow_surface\", narrow_surface);",
    "\"phase3-policy-starter-packet-test\"",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase3-policy-dump_py = [_][]const u8{
    "DOC_PATH = Path(\"Documentation/zigux/phase3-policy-slice.md\")",
    "DUMP_PATH = Path(\"zigux/tests/phase3_policy_dump.zig\")",
    "BUILD_PATH = Path(\"zigux/tests/phase3_policy_dump_build.zig\")",
    "EXPECTED_PATH = Path(\"zigux/tests/fixtures/phase3_policy_dump_expected.txt\")",
    "\"zig run scripts\\zigux/check_phase3_policy_dump.zig --self-test\"",
    "\"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig\"",
};

const REQUIRED_MARKERS__zigux_tests_phase3_policy_starter_packet_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-policy-starter-packet\"",
    "\"status\": \"policy_slice_present\"",
    "\"Documentation/zigux/phase3-policy-unsafe-boundary-survey.md\"",
    "\"zigux/helpers/layout_assert.zig\"",
    "\"zigux/unsafe/narrow.zig\"",
    "\"zigux/tests/phase3_policy_dump.zig\"",
    "\"zigux/tests/phase3_policy_dump_build.zig\"",
    "\"zigux/tests/fixtures/phase3_policy_dump_expected.txt\"",
    "\"zigux/tests/phase3_policy_unsafe.zig\"",
    "\"zigux/tests/phase3_policy_unsafe_build.zig\"",
    "\"scripts\\zigux/check_phase3_policy_dump.zig\"",
    "\"scripts\\zigux/validate_phase3_policy_unsafe_survey.zig\"",
    "\"zig run scripts\\zigux/check_phase3_policy_starter_packet.zig --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_policy_dump.zig --self-test\"",
    "\"zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig\"",
    "\"make -C zigux phase3-policy-unsafe-test\"",
    "\"zig run scripts\\zigux/validate_phase3_policy_unsafe_survey.zig --self-test\"",
    "\"zig run scripts\\zigux/validate_phase3_policy_unsafe_survey.zig\"",
    "\"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig\"",
    "\"make -C zigux phase3-policy-starter-packet-test\"",
    "\"make -C zigux phase3\"",
};

const SELF_TEST_CASES = [_][]const u8{
    "PHASE3_POLICY_SLICE_FILE_COUNT=",
    "PHASE3_POLICY_SLICE_SCOPE=this slice proves shared InteropPolicy layout assertions, panic escalation, allocator-init ownership, and unsafe-scope reviewability by cross-checking the helper-local decoder against zigux/unsafe/narrow.zig, including the newer whole-policy and byte-level review entry points, and by replaying one focused policy dump that now also proves raw-pointer bridge reads and writes over the same bounded records without widening into unsafe wrappers, runtime shims, or broader export-boundary claims",
    "zigux/tests/phase3_policy_dump.zig",
    "zig run scripts\\zigux/check_phase3_policy_dump.zig --self-test",
    "Current `master` now separately serves the shared ABI core replay through `zigux/tests/phase3_abi.zig`, the shared ABI checker through `scripts\\zigux/check_phase3_abi.zig`, and the shared Phase 3 validator entrypoint through `scripts\\zigux/validate_phase3.zig`",
    "Current `master` also directly serves the same focused policy slice through the reviewer-readable dump route at `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, and `scripts\\zigux/check_phase3_policy_dump.zig`, so the bounded policy packet now exposes both its starter replay and its focused dump companion without widening this note into MMIO, low-level-wrapper, or broader runtime-shim ownership.",
    "pub fn assertInteropPolicyLayout() LayoutError!void {",
    "pub fn assertInteropPolicyModeValues() void {",
    "pub fn permitsNoUnsafePolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
    "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    "test \"policy starter packet keeps narrow byte and denial symmetry explicit\" {",
    "test \"policy starter packet keeps unsafe require gates explicit on shared records\" {",
    "test \"policy starter packet keeps unsafe boundary and audit semantics explicit\" {",
    "test \"policy starter packet keeps unsafe surface mappings explicit\" {",
    "test \"policy starter packet keeps panic and allocator byte guards explicit\" {",
    "\"phase3-policy-starter-packet-test\"",
    "EXPECTED_PATH = Path(\"zigux/tests/fixtures/phase3_policy_dump_expected.txt\")",
    "\"Documentation/zigux/phase3-policy-unsafe-boundary-survey.md\"",
    "\"scripts\\zigux/validate_phase3_policy_unsafe_survey.zig\"",
    "\"zig run scripts\\zigux/validate_phase3_policy_unsafe_survey.zig --self-test\"",
    "\"zigux/tests/phase3_policy_dump.zig\"",
    "\"zigux/tests/phase3_policy_unsafe.zig\"",
    "\"zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig\"",
    "\"make -C zigux phase3-policy-unsafe-test\"",
    "\"make -C zigux phase3-policy-starter-packet-test\"",
    "\"make -C zigux phase3\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
    const text_updated_shared_reminder_marker_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice.md");
    defer allocator.free(text_updated_shared_reminder_marker_path);
    const text_updated_shared_reminder_marker = try guard.readUtf8File(io, allocator, text_updated_shared_reminder_marker_path);
    defer allocator.free(text_updated_shared_reminder_marker);
    for (UPDATED_SHARED_REMINDER_MARKER) |marker| try guard.requireMarker(text_updated_shared_reminder_marker, marker);
    const text_updated_shared_reminder_next_step_marker_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice.md");
    defer allocator.free(text_updated_shared_reminder_next_step_marker_path);
    const text_updated_shared_reminder_next_step_marker = try guard.readUtf8File(io, allocator, text_updated_shared_reminder_next_step_marker_path);
    defer allocator.free(text_updated_shared_reminder_next_step_marker);
    for (UPDATED_SHARED_REMINDER_NEXT_STEP_MARKER) |marker| try guard.requireMarker(text_updated_shared_reminder_next_step_marker, marker);
    const text_required_markers__documentation_zigux_phase3-policy-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-policy-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-policy-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-policy-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-policy-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-policy-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-policy-slice_md, marker);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-validator-support-surface/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-validator-support-surface_md, marker);
    const text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-shared-reminder-gap/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md_path);
    const text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-shared-reminder-gap_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-shared-reminder-gap_md, marker);
    const text_required_markers__include_zigux_abi_h_path = try guard.joinPath(allocator, root, "include/zigux/abi/h");
    defer allocator.free(text_required_markers__include_zigux_abi_h_path);
    const text_required_markers__include_zigux_abi_h = try guard.readUtf8File(io, allocator, text_required_markers__include_zigux_abi_h_path);
    defer allocator.free(text_required_markers__include_zigux_abi_h);
    for (REQUIRED_MARKERS__include_zigux_abi_h) |marker| try guard.requireMarker(text_required_markers__include_zigux_abi_h, marker);
    const text_required_markers__zigux_bindings_abi_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/abi/zig");
    defer allocator.free(text_required_markers__zigux_bindings_abi_zig_path);
    const text_required_markers__zigux_bindings_abi_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_abi_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_abi_zig);
    for (REQUIRED_MARKERS__zigux_bindings_abi_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_abi_zig, marker);
    const text_required_markers__zigux_bindings_notifier_abi_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/notifier/abi/zig");
    defer allocator.free(text_required_markers__zigux_bindings_notifier_abi_zig_path);
    const text_required_markers__zigux_bindings_notifier_abi_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_notifier_abi_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_notifier_abi_zig);
    for (REQUIRED_MARKERS__zigux_bindings_notifier_abi_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_notifier_abi_zig, marker);
    const text_required_markers__zigux_helpers_layout_assert_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/layout/assert/zig");
    defer allocator.free(text_required_markers__zigux_helpers_layout_assert_zig_path);
    const text_required_markers__zigux_helpers_layout_assert_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_layout_assert_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_layout_assert_zig);
    for (REQUIRED_MARKERS__zigux_helpers_layout_assert_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_layout_assert_zig, marker);
    const text_required_markers__zigux_helpers_panic_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/panic/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_panic_policy_zig_path);
    const text_required_markers__zigux_helpers_panic_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_panic_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_panic_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_panic_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_panic_policy_zig, marker);
    const text_required_markers__zigux_helpers_allocator_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/allocator/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_allocator_policy_zig_path);
    const text_required_markers__zigux_helpers_allocator_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_allocator_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_allocator_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_allocator_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_allocator_policy_zig, marker);
    const text_required_markers__zigux_helpers_unsafe_policy_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/unsafe/policy/zig");
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    const text_required_markers__zigux_helpers_unsafe_policy_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_unsafe_policy_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_unsafe_policy_zig);
    for (REQUIRED_MARKERS__zigux_helpers_unsafe_policy_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_unsafe_policy_zig, marker);
    const text_required_markers__zigux_unsafe_narrow_zig_path = try guard.joinPath(allocator, root, "zigux/unsafe/narrow/zig");
    defer allocator.free(text_required_markers__zigux_unsafe_narrow_zig_path);
    const text_required_markers__zigux_unsafe_narrow_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_unsafe_narrow_zig_path);
    defer allocator.free(text_required_markers__zigux_unsafe_narrow_zig);
    for (REQUIRED_MARKERS__zigux_unsafe_narrow_zig) |marker| try guard.requireMarker(text_required_markers__zigux_unsafe_narrow_zig, marker);
    const text_required_markers__zigux_tests_phase3_policy_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/policy/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_policy_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_policy_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_policy_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_policy_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_policy_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/policy/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_policy_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_policy_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_policy_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_policy_starter_packet_build_zig, marker);
    const text_required_markers__scripts_zigux_check-phase3-policy-dump_py_path = try guard.joinPath(allocator, root, "scripts/zigux/check-phase3-policy-dump/py");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-policy-dump_py_path);
    const text_required_markers__scripts_zigux_check-phase3-policy-dump_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase3-policy-dump_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-policy-dump_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase3-policy-dump_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase3-policy-dump_py, marker);
    const text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/policy/starter/packet/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json_path);
    const text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase3_policy_starter_packet_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_policy_starter_packet_manifest_json, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
