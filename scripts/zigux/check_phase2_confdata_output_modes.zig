const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_CONFDATA_OUTPUT_MODE_GATE=pass";
pub const self_test_pass_marker = "PHASE2_CONFDATA_OUTPUT_MODE_SELF_TEST=pass";

const source_markers = [_][]const u8{
    "test \"confdata bridge emits auto.conf symbol export lines\"",
    "try emitAutoConfExports(&capture, summary);",
    "test \"confdata bridge emits autoconf header symbol export lines\"",
    "try emitAutoconfHeaderExports(&capture, summary);",
    "test \"confdata bridge parses explicit output modes\"",
    "OutputMode.parse(\"auto.conf\")",
    "OutputMode.parse(\"autoconf.h\")",
};
const workflow_markers = [_][]const u8{
    "- 'scripts/zigux/check_phase2_confdata_output_modes.zig'",
    "- name: Setup pinned Zig toolchain",
    "canonical_tag = \"upstream-6c25d2bd58e4\"",
    "zig test scripts/zigux/check_phase2_confdata_output_modes.zig",
    "zig run scripts/zigux/check_phase2_confdata_output_modes.zig -- --self-test",
    "zig run scripts/zigux/check_phase2_confdata_output_modes.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const source_path = try guard.joinPath(allocator, root, "scripts/zigux/kconfig/confdata_bridge.zig");
    defer allocator.free(source_path);
    const source = try guard.readUtf8File(io, allocator, source_path);
    defer allocator.free(source);
    for (source_markers) |marker| try guard.requireMarker(source, marker);

    const workflow_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-phase2-confdata-output-modes.yml");
    defer allocator.free(workflow_path);
    const workflow = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(workflow);
    for (workflow_markers) |marker| try guard.requireMarker(workflow, marker);
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

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
