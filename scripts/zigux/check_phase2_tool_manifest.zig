const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_TOOL_MANIFEST=pass";
pub const self_test_pass_marker = "PHASE2_TOOL_MANIFEST_SELF_TEST=pass";

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "\"phase\": \"Phase 2\"",
    "zig-x86_64-linux-0.17.0-dev.1415+64dfaa568.tar.xz",
    "scripts\\zigux/check_phase2_tool_manifest.zig",
    "scripts\\zigux/check_zig_toolchain.zig",
    "zigux/Makefile",
};

const markers_1 = [_][]const u8{
    "0.17.0-dev.1415+64dfaa568",
    "f72f19cbae9f4e649d7b2c5040aec6ccb93dce08048738bcfdf1a03475cd0c93",
    "6fa26a51b2a9bff2952bb11458c863580731021d65dbb04bc42680cfa5a7140f",
};

const markers_2 = [_][]const u8{
    "Check current Phase 2 tool manifest packet",
};

const markers_3 = [_][]const u8{
    "check_phase2_tool_manifest.zig --self-test",
    "check_phase2_tool_manifest.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/tests/fixtures/phase2_tool_manifest.json", .markers = &markers_0 },
    .{ .rel = "scripts/zigux/zig-toolchain-policy.json", .markers = &markers_1 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_2 },
    .{ .rel = "zigux/Makefile", .markers = &markers_3 },
};

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
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
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
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
