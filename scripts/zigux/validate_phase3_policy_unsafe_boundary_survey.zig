const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_UNSAFE_BOUNDARY_SURVEY=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_UNSAFE_BOUNDARY_SURVEY_SELF_TEST=pass";

const REQUIRED_SURVEY_MARKERS = [_][]const u8{
    "# Phase 3 Policy and Unsafe Boundary Survey",
    "PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig",
    "PHASE3_POLICY_PACKET_GATE=zig run scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "PHASE3_POLICY_DUMP_GATE=zig run scripts\\zigux/check_phase3_policy_dump.zig",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_BOUNDARY_GAP=no-further-policy-unsafe-gap-beyond-keeping-the-helper-local-packet-dedicated-replay-pair-and-the-directly-coupled-low-level-wrapper-packet-aligned",
    "PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-layout-assert-panic-policy-allocator-policy-unsafe-policy-mmio-or-narrow-helper-surfaces-or-the-dedicated-policy-unsafe-survey-gate-drift-again",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
};

const SELF_TEST_LAYOUT_ASSERT = [_][]const u8{
    "pub fn assertInteropPolicyLayout() LayoutError!void {\n}\n",
};

const SELF_TEST_PANIC_POLICY = [_][]const u8{
    "pub const Escalation = enum {\n    immediate_abort,\n};\npub fn emitsKernelBug(mode: abi.PanicMode) bool {\n    _ = mode;\n    return false;\n}\n",
};

const SELF_TEST_ALLOCATOR_POLICY = [_][]const u8{
    "pub const InitFlow = enum {\n    caller_prepared,\n};\npub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {\n    _ = mode;\n    return false;\n}\n",
};

const SELF_TEST_UNSAFE_POLICY = [_][]const u8{
    "pub const AccessBoundary = enum {\n    typed_safe,\n};\npub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {\n    _ = policy;\n    return true;\n}\npub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {\n    _ = policy;\n    return false;\n}\npub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {\n    _ = policy;\n    return false;\n}\n",
};

const SELF_TEST_MMIO = [_][]const u8{
    "pub fn readScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *const volatile T) PolicyError!T {\n    _ = .{ T, scope, ptr };\n    return undefined;\n}\npub fn writeMaskedInteropPolicyBytes(\n) void {}\n",
};

const SELF_TEST_NARROW = [_][]const u8{
    "pub const Surface = enum {\n    safe_only,\n};\npub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {\n    _ = .{ T, address, byte_len, unsafe_scope, reserved };\n    return undefined;\n}\npub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {\n    _ = .{ T, address, value, unsafe_scope, reserved };\n}\n",
};

const SELF_TEST_POLICY_SLICE = [_][]const u8{
    "# Phase 3 Policy Slice\n- `PHASE3_POLICY_SLICE_FILE_COUNT=sample`\n- `zigux/helpers/unsafe_policy.zig`\n- `zigux/tests/phase3_policy_starter_packet_manifest.json`\n- `zig run scripts\\zigux/check_phase3_policy_starter_packet.zig`\n- `zig run scripts\\zigux/check_phase3_policy_dump.zig -- --self-test`\n",
};

const SELF_TEST_LOW_LEVEL_SURVEY = [_][]const u8{
    "# Phase 3 Low-Level Wrapper Boundary Survey\n- `PHASE3_LOW_LEVEL_WRAPPER_SCOPE=sample`\n- `zigux/helpers/mmio.zig`\n- `zigux/helpers/unsafe_policy.zig`\n- `scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig`\n- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`\n",
};

const SELF_TEST_POLICY_PACKET_GATE = [_][]const u8{
    "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass\nPHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES=1\n",
};

const SELF_TEST_POLICY_DUMP_GATE = [_][]const u8{
    "PHASE3_POLICY_DUMP_SELF_TEST=pass\nPHASE3_POLICY_DUMP_EXPECTED_LINE_COUNT=4\n",
};

const SELF_TEST_LOW_LEVEL_GATE = [_][]const u8{
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass\nPHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT=4\n",
};

const SELF_TEST_SURVEY_TEMPLATE = [_][]const u8{
    "# Phase 3 Policy and Unsafe Boundary Survey\n- `PHASE3_UNSAFE_POLICY_PATH=zigux/helpers/unsafe_policy.zig`\n- `PHASE3_LAYOUT_ASSERT_BLOB_SHA={layout_assert_sha}`\n- `PHASE3_PANIC_POLICY_BLOB_SHA={panic_policy_sha}`\n- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA={allocator_policy_sha}`\n- `PHASE3_UNSAFE_POLICY_BLOB_SHA={unsafe_policy_sha}`\n- `PHASE3_MMIO_BLOB_SHA={mmio_sha}`\n- `PHASE3_UNSAFE_BLOB_SHA={narrow_sha}`\n- `PHASE3_POLICY_SLICE_DOC_BLOB_SHA={policy_slice_sha}`\n- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_DOC_BLOB_SHA={low_level_sha}`\n- `PHASE3_POLICY_PACKET_GATE=zig run scripts\\zigux/check_phase3_policy_starter_packet.zig`\n- `PHASE3_POLICY_DUMP_GATE=zig run scripts\\zigux/check_phase3_policy_dump.zig`\n- `PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig`\n- `PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`\n- `PHASE3_BOUNDARY_GAP=no-further-policy-unsafe-gap-beyond-keeping-the-helper-local-packet-dedicated-replay-pair-and-the-directly-coupled-low-level-wrapper-packet-aligned`\n- `PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-layout-assert-panic-policy-allocator-policy-unsafe-policy-mmio-or-narrow-helper-surfaces-or-the-dedicated-policy-unsafe-survey-gate-drift-again`\n- `Documentation/zigux/phase3-policy-slice.md`\n- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_survey_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_required_survey_markers_path);
    const text_required_survey_markers = try guard.readUtf8File(io, allocator, text_required_survey_markers_path);
    defer allocator.free(text_required_survey_markers);
    for (REQUIRED_SURVEY_MARKERS) |marker| try guard.requireMarker(text_required_survey_markers, marker);
    const text_self_test_layout_assert_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_layout_assert_path);
    const text_self_test_layout_assert = try guard.readUtf8File(io, allocator, text_self_test_layout_assert_path);
    defer allocator.free(text_self_test_layout_assert);
    for (SELF_TEST_LAYOUT_ASSERT) |marker| try guard.requireMarker(text_self_test_layout_assert, marker);
    const text_self_test_panic_policy_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_panic_policy_path);
    const text_self_test_panic_policy = try guard.readUtf8File(io, allocator, text_self_test_panic_policy_path);
    defer allocator.free(text_self_test_panic_policy);
    for (SELF_TEST_PANIC_POLICY) |marker| try guard.requireMarker(text_self_test_panic_policy, marker);
    const text_self_test_allocator_policy_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_allocator_policy_path);
    const text_self_test_allocator_policy = try guard.readUtf8File(io, allocator, text_self_test_allocator_policy_path);
    defer allocator.free(text_self_test_allocator_policy);
    for (SELF_TEST_ALLOCATOR_POLICY) |marker| try guard.requireMarker(text_self_test_allocator_policy, marker);
    const text_self_test_unsafe_policy_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_unsafe_policy_path);
    const text_self_test_unsafe_policy = try guard.readUtf8File(io, allocator, text_self_test_unsafe_policy_path);
    defer allocator.free(text_self_test_unsafe_policy);
    for (SELF_TEST_UNSAFE_POLICY) |marker| try guard.requireMarker(text_self_test_unsafe_policy, marker);
    const text_self_test_mmio_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_mmio_path);
    const text_self_test_mmio = try guard.readUtf8File(io, allocator, text_self_test_mmio_path);
    defer allocator.free(text_self_test_mmio);
    for (SELF_TEST_MMIO) |marker| try guard.requireMarker(text_self_test_mmio, marker);
    const text_self_test_narrow_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_narrow_path);
    const text_self_test_narrow = try guard.readUtf8File(io, allocator, text_self_test_narrow_path);
    defer allocator.free(text_self_test_narrow);
    for (SELF_TEST_NARROW) |marker| try guard.requireMarker(text_self_test_narrow, marker);
    const text_self_test_policy_slice_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_policy_slice_path);
    const text_self_test_policy_slice = try guard.readUtf8File(io, allocator, text_self_test_policy_slice_path);
    defer allocator.free(text_self_test_policy_slice);
    for (SELF_TEST_POLICY_SLICE) |marker| try guard.requireMarker(text_self_test_policy_slice, marker);
    const text_self_test_low_level_survey_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_low_level_survey_path);
    const text_self_test_low_level_survey = try guard.readUtf8File(io, allocator, text_self_test_low_level_survey_path);
    defer allocator.free(text_self_test_low_level_survey);
    for (SELF_TEST_LOW_LEVEL_SURVEY) |marker| try guard.requireMarker(text_self_test_low_level_survey, marker);
    const text_self_test_policy_packet_gate_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_policy_packet_gate_path);
    const text_self_test_policy_packet_gate = try guard.readUtf8File(io, allocator, text_self_test_policy_packet_gate_path);
    defer allocator.free(text_self_test_policy_packet_gate);
    for (SELF_TEST_POLICY_PACKET_GATE) |marker| try guard.requireMarker(text_self_test_policy_packet_gate, marker);
    const text_self_test_policy_dump_gate_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_policy_dump_gate_path);
    const text_self_test_policy_dump_gate = try guard.readUtf8File(io, allocator, text_self_test_policy_dump_gate_path);
    defer allocator.free(text_self_test_policy_dump_gate);
    for (SELF_TEST_POLICY_DUMP_GATE) |marker| try guard.requireMarker(text_self_test_policy_dump_gate, marker);
    const text_self_test_low_level_gate_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_low_level_gate_path);
    const text_self_test_low_level_gate = try guard.readUtf8File(io, allocator, text_self_test_low_level_gate_path);
    defer allocator.free(text_self_test_low_level_gate);
    for (SELF_TEST_LOW_LEVEL_GATE) |marker| try guard.requireMarker(text_self_test_low_level_gate, marker);
    const text_self_test_survey_template_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md");
    defer allocator.free(text_self_test_survey_template_path);
    const text_self_test_survey_template = try guard.readUtf8File(io, allocator, text_self_test_survey_template_path);
    defer allocator.free(text_self_test_survey_template);
    for (SELF_TEST_SURVEY_TEMPLATE) |marker| try guard.requireMarker(text_self_test_survey_template, marker);
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
