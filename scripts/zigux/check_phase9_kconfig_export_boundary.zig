const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_KCONFIG_EXPORT_BOUNDARY_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "`scripts/zigux/kconfig/conf_bridge.zig` keeps the current mode and flag bridge for `syncconfig`, `defconfig`, and the bounded allconfig sentinel family",
    "`scripts/zigux/kconfig/confdata_bridge.zig` keeps the current config-file parsing bridge for `CONFIG_` keys, unset markers, quoted strings, line-normalization edge cases, and bounded symbol-export projections for `auto.conf` plus `autoconf.h`",
    "`zigux/kernel/export_shim.zig` keeps the current direct Phase 3 export-boundary surface through `ExportStatus`, boundary-header validation, and interop-policy validation",
    "`rust/exports.c` does not materialize on the trusted current-`master` direct-read path",
};

const CONF_BRIDGE_MARKERS = [_][]const u8{
    "pub const Mode = enum {",
    ".syncconfig => \"--syncconfig\"",
    ".defconfig => \"--defconfig\"",
    "fn modeUsesAllConfigSentinel(mode: Mode) bool {",
};

const CONFDATA_BRIDGE_MARKERS = [_][]const u8{
    "const config_prefix = \"CONFIG_\";",
    "fn truncateAtFirstNull(text: []const u8) []const u8 {",
    "fn parseUnsetSymbol(line: []const u8) ?[]const u8 {",
    "pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {",
    "pub fn emitAutoConfExports(writer: anytype, summary: Summary) !void {",
    "pub fn emitAutoconfHeaderExports(writer: anytype, summary: Summary) !void {",
};

const EXPORT_SHIM_MARKERS = [_][]const u8{
    "pub const ExportStatus = abi.ExportStatus;",
    "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
    "pub fn validateInteropPolicy(policy: InteropPolicy) ExportStatus {",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CONF_BRIDGE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CONFDATA_BRIDGE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (EXPORT_SHIM_MARKERS) |marker| try guard.requireMarker(text, marker);
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
