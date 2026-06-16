const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_IOMAP_MMIO_SAFETY_SURVEY_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "shared MMIO safety substrate in `zigux/helpers/mmio.zig`",
    "`unsafe_scope = 1` with `reserved = 0` is the allowed volatile-MMIO byte-policy form",
    "`unsafe_scope = 0` is denied with `error.UnsafeScopeDenied`",
    "`unsafe_scope = 2` is denied for MMIO",
    "non-zero reserved byte is rejected as `error.InvalidInteropPolicy`",
    "denied MMIO writes stay side-effect free",
    "the shipped helper descriptor in `lib/devres.zig` keeps `.touches_live_mmio = false`",
    "the shared MMIO helper owns the actual volatile-MMIO access gate",
    "pub fn allowsInteropPolicyBytes",
    "pub fn requireInteropPolicyBytes",
    "pub fn readScoped",
    "pub fn writeScoped",
    "pub fn readInteropPolicyBytes",
    "pub fn writeInteropPolicyBytes",
    "pub fn exchangeInteropPolicyBytes",
    "pub fn writeMaskedInteropPolicyBytes",
    "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff",
    "phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates",
    "phase3 low-level wrappers keep MMIO single-byte interop-policy shorthands explicit",
    "phase3 low-level wrappers keep whole-record MMIO interop-policy helpers explicit",
    "phase3 low-level wrappers keep direct MMIO scope gates explicit",
    "expectError(error.UnsafeScopeDenied, mmio.writeInteropPolicyBytes(u32, 0, 0, register_ptr, state))",
    "expectError(error.InvalidInteropPolicy, mmio.readInteropPolicyBytes(u32, 1, 1, const_register_ptr))",
    "try mmio.writeInteropPolicyBytes(u32, 1, 0, register_ptr, state)",
    "expectError(error.UnsafeScopeDenied, mmio.writeScoped(u32, raw_scope, register_ptr, 0xAABB_CCDD))",
    ".touches_live_mmio = false",
    ".provides_of_iomap_planning = true",
    "pub fn planDeviceTreeIomap",
    "pure `devm_of_iomap()` planning surface",
    "does not claim live MMIO mapping state",
    "phase13 devres iomap planning stops before managed ioremap resource when translation is missing",
    "phase13 devres iomap planning preserves translated size on request-region denial",
    "phase13 devres iomap planning releases the requested region when remap later fails",
    "phase13 devres iomap cleanup handoff materializes helper-first iounmap cleanup after successful remap",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
