const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_DIRECT_CROSS_ROUTE=pass";
pub const self_test_pass_marker = "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass";

const ROUTE = [_][]const u8{
    "make -C zigux phase2-cross",
};

const MAKEFILE_LINES = [_][]const u8{
    "phase2-cross:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig",
};

const ALLOWED_VALIDATION_MODES = [_][]const u8{
    "archive_required",
    "route_contract_only",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_route_path = try guard.joinPath(allocator, root, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(text_route_path);
    const text_route = try guard.readUtf8File(io, allocator, text_route_path);
    defer allocator.free(text_route);
    for (ROUTE) |marker| try guard.requireMarker(text_route, marker);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
    const text_allowed_validation_modes_path = try guard.joinPath(allocator, root, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(text_allowed_validation_modes_path);
    const text_allowed_validation_modes = try guard.readUtf8File(io, allocator, text_allowed_validation_modes_path);
    defer allocator.free(text_allowed_validation_modes);
    for (ALLOWED_VALIDATION_MODES) |marker| try guard.requireMarker(text_allowed_validation_modes, marker);
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
