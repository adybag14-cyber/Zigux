const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_DOCS_SHARED_REMINDER=pass";
pub const self_test_pass_marker = "PHASE2_DOCS_SHARED_REMINDER_SELF_TEST=pass";

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "0.17.0-dev.1443+6c25d2bd5",
    "x86_64-linux",
    "x86_64-windows",
};

const markers_1 = [_][]const u8{
    "0.17.0-dev.1443+6c25d2bd5",
    "zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz",
    "make -C zigux phase2-toolchain",
};

const markers_2 = [_][]const u8{
    "0.17.0-dev.1443+6c25d2bd5",
    "x86_64-linux",
    "x86_64-windows",
};

const markers_3 = [_][]const u8{
    "0.17.0-dev.1443+6c25d2bd5",
    "zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz",
};

const markers_4 = [_][]const u8{
    "0.17.0-dev.1443+6c25d2bd5",
    "4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9",
    "0c538cabcea1ef1d114b99f6e9f3099d4c4c22070daa19819511b783c5f40211",
};

const markers_5 = [_][]const u8{
    "0.17.0-dev.1443+6c25d2bd5",
    "zig-x86_64-linux-0.17.0-dev.1443+6c25d2bd5.tar.xz",
};

const contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/zig-toolchain-policy.json", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_3 },
    .{ .rel = "third_party/README.md", .markers = &markers_4 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_5 },
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
