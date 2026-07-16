const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass",
    "PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES=",
};

const live_output_markers = [_][]const u8{
    "PHASE3_POLICY_STARTER_PACKET=pass",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
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
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "Current `master` now separately serves the shared ABI core replay through `zigux/tests/phase3_abi.zig`, the shared ABI checker through `scripts\\zigux/check_phase3_abi.zig`, and the shared Phase 3 validator entrypoint through `scripts\\zigux/validate_phase3.zig`",
};

const markers_1 = [_][]const u8{
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

const markers_2 = [_][]const u8{
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/phase3_catalog.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
};

const markers_3 = [_][]const u8{
    "#define ZIGUX_PANIC_ABORT 0U",
    "#define ZIGUX_ALLOC_KERNEL_HEAP 1U",
    "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
    "struct zigux_interop_policy {",
};

const markers_4 = [_][]const u8{
    "pub const PanicMode = enum(u8) {",
    "pub const AllocatorMode = enum(u8) {",
    "pub const UnsafeScope = enum(u8) {",
    "pub const InteropPolicy = extern struct {",
};

const markers_5 = [_][]const u8{
    "pub const NotifierBlock = extern struct {",
};

const markers_6 = [_][]const u8{
    "pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void {",
    "pub fn assertBoundaryHeaderLayout() LayoutError!void {",
    "pub fn assertExportStatusLayout() LayoutError!void {",
    "pub fn assertInteropPolicyLayout() LayoutError!void {",
    "pub fn assertInteropPolicyModeValues() void {",
};

const markers_7 = [_][]const u8{
    "pub const Escalation = enum {",
    "pub fn emitsKernelBug(mode: abi.PanicMode) bool {",
};

const markers_8 = [_][]const u8{
    "pub const InitFlow = enum {",
    "pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {",
};

const markers_9 = [_][]const u8{
    "pub const AccessBoundary = enum {",
    "pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
    "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
};

const markers_10 = [_][]const u8{
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

const markers_11 = [_][]const u8{
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

const markers_12 = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../helpers/unsafe_policy.zig\"),",
    "root_module.addImport(\"narrow_surface\", narrow_surface);",
    "\"phase3-policy-starter-packet-test\"",
};

const markers_13 = [_][]const u8{
    "Documentation/zigux/phase3-policy-slice.md",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "\"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig\"",
};

const markers_14 = [_][]const u8{
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
    "\"zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig\"",
    "\"make -C zigux phase3-policy-unsafe-test\"",
    "\"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig\"",
    "\"make -C zigux phase3-policy-starter-packet-test\"",
    "\"make -C zigux phase3\"",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-policy-slice.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase3-validator-support-surface.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase3-shared-reminder-gap.md", .markers = &markers_2 },
    .{ .rel = "include/zigux/abi.h", .markers = &markers_3 },
    .{ .rel = "zigux/bindings/abi.zig", .markers = &markers_4 },
    .{ .rel = "zigux/bindings/notifier_abi.zig", .markers = &markers_5 },
    .{ .rel = "zigux/helpers/layout_assert.zig", .markers = &markers_6 },
    .{ .rel = "zigux/helpers/panic_policy.zig", .markers = &markers_7 },
    .{ .rel = "zigux/helpers/allocator_policy.zig", .markers = &markers_8 },
    .{ .rel = "zigux/helpers/unsafe_policy.zig", .markers = &markers_9 },
    .{ .rel = "zigux/unsafe/narrow.zig", .markers = &markers_10 },
    .{ .rel = "zigux/tests/phase3_policy_starter_packet.zig", .markers = &markers_11 },
    .{ .rel = "zigux/tests/phase3_policy_starter_packet_build.zig", .markers = &markers_12 },
    .{ .rel = "scripts/zigux/check_phase3_policy_dump.zig", .markers = &markers_13 },
    .{ .rel = "zigux/tests/phase3_policy_starter_packet_manifest.json", .markers = &markers_14 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "=")) {
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len });
        } else {
            try guard.printLine(io, "{s}", .{marker});
        }
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try printOutputMarkers(io, &self_test_output_markers);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
