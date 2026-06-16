const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "KCONFIG_SYMBOL_EXPORT_PARITY=pass";
pub const self_test_pass_marker = "KCONFIG_SYMBOL_EXPORT_PARITY_SELF_TEST=pass";

const REQUIRED_PUBLIC_EXPORTS = [_][]const u8{
    "pub const EntryKind = enum {",
    "pub const Entry = struct {",
    "pub const Summary = struct {",
    "pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {",
    "pub fn deinitSummary(allocator: std.mem.Allocator, summary: *Summary) void {",
    "pub fn runConfdataBridge(allocator: std.mem.Allocator, input: []const u8, writer: anytype) !void {",
};

const REQUIRED_ENTRY_KINDS = [_][]const u8{
    "tristate",
    "string",
    "value",
    "unset",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_public_exports_path = try guard.joinPath(allocator, root, "scripts/zigux/kconfig/confdata_bridge.zig");
    defer allocator.free(text_required_public_exports_path);
    const text_required_public_exports = try guard.readUtf8File(io, allocator, text_required_public_exports_path);
    defer allocator.free(text_required_public_exports);
    for (REQUIRED_PUBLIC_EXPORTS) |marker| try guard.requireMarker(text_required_public_exports, marker);
    const text_required_entry_kinds_path = try guard.joinPath(allocator, root, "scripts/zigux/kconfig/confdata_bridge.zig");
    defer allocator.free(text_required_entry_kinds_path);
    const text_required_entry_kinds = try guard.readUtf8File(io, allocator, text_required_entry_kinds_path);
    defer allocator.free(text_required_entry_kinds);
    for (REQUIRED_ENTRY_KINDS) |marker| try guard.requireMarker(text_required_entry_kinds, marker);
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
