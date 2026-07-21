const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_KCONFIG_ROUTE_HOOKS=pass";
pub const self_test_pass_marker = "PHASE2_KCONFIG_ROUTE_HOOKS_SELF_TEST=pass";

const REQUIRED_PHONY_TARGET = [_][]const u8{
    "phase2-kconfig",
};

const REQUIRED_MAKEFILE_TARGET = [_][]const u8{
    "phase2-kconfig: phase2-toolchain",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig -- --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_kconfig_bridge.zig -- --self-test",
    "run: zig run scripts\\zigux/check_kconfig_bridge.zig",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_phony_target_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_phony_target_path);
    const text_required_phony_target = try guard.readUtf8File(io, allocator, text_required_phony_target_path);
    defer allocator.free(text_required_phony_target);
    for (REQUIRED_PHONY_TARGET) |marker| try guard.requireMarker(text_required_phony_target, marker);
    const text_required_makefile_target_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_makefile_target_path);
    const text_required_makefile_target = try guard.readUtf8File(io, allocator, text_required_makefile_target_path);
    defer allocator.free(text_required_makefile_target);
    for (REQUIRED_MAKEFILE_TARGET) |marker| try guard.requireMarker(text_required_makefile_target, marker);
    const text_required_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_makefile_lines_path);
    const text_required_makefile_lines = try guard.readUtf8File(io, allocator, text_required_makefile_lines_path);
    defer allocator.free(text_required_makefile_lines);
    for (REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_required_makefile_lines, marker, 1);
    const text_required_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_workflow_lines_path);
    const text_required_workflow_lines = try guard.readUtf8File(io, allocator, text_required_workflow_lines_path);
    defer allocator.free(text_required_workflow_lines);
    for (REQUIRED_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_required_workflow_lines, marker, 1);
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
