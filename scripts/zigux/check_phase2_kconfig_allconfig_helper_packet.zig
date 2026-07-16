const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST=pass";

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
};

const markers_1 = [_][]const u8{
    "helper_local_allconfig_implicit_omission_modes",
    "helper_local_allconfig_explicit_override_modes",
    "allmodconfig",
    "randconfig",
};

const markers_2 = [_][]const u8{
    "check_phase2_kconfig_allconfig_helper_packet.zig --self-test",
    "check_phase2_kconfig_allconfig_helper_packet.zig",
};

const markers_3 = [_][]const u8{
    "check_phase2_kconfig_allconfig_helper_packet.zig -- --self-test",
    "check_phase2_kconfig_allconfig_helper_packet.zig",
};

const markers_4 = [_][]const u8{
    "check_phase2_kconfig_allconfig_helper_packet.zig",
};

const markers_5 = [_][]const u8{
    "check_phase2_kconfig_allconfig_helper_packet.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/kconfig/conf_bridge.zig", .markers = &markers_0 },
    .{ .rel = "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json", .markers = &markers_1 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_2 },
    .{ .rel = "zigux/Makefile", .markers = &markers_3 },
    .{ .rel = "scripts/zigux/validate_phase2.zig", .markers = &markers_4 },
    .{ .rel = "scripts/zigux/validate_phase2_closure.zig", .markers = &markers_5 },
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
