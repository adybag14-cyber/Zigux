const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_KCONFIG_RANDCONFIG_ENV_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_KCONFIG_RANDCONFIG_ENV_PACKET_SELF_TEST=pass";

const REQUIRED_BRIDGE_MARKERS = [_][]const u8{
    "if \"seed\" in case:",
    "if \"probability\" in case:",
    "cmd.append(f\"seed={case['seed']}\")",
    "cmd.append(f\"probability={case['probability']}\")",
};

const EXPECTED_MANIFEST_PACKET = [_][]const u8{
    "randconfig_expected.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_bridge_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/check_kconfig_bridge.zig");
    defer allocator.free(text_required_bridge_markers_path);
    const text_required_bridge_markers = try guard.readUtf8File(io, allocator, text_required_bridge_markers_path);
    defer allocator.free(text_required_bridge_markers);
    for (REQUIRED_BRIDGE_MARKERS) |marker| try guard.requireMarker(text_required_bridge_markers, marker);
    const text_expected_manifest_packet_path = try guard.joinPath(allocator, root, "scripts\zigux/check_kconfig_bridge.zig");
    defer allocator.free(text_expected_manifest_packet_path);
    const text_expected_manifest_packet = try guard.readUtf8File(io, allocator, text_expected_manifest_packet_path);
    defer allocator.free(text_expected_manifest_packet);
    for (EXPECTED_MANIFEST_PACKET) |marker| try guard.requireMarker(text_expected_manifest_packet, marker);
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
