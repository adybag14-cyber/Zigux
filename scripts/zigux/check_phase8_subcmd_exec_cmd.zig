const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_SUBCMD_EXEC_CMD_ZIG_TEST=pass";
pub const self_test_pass_marker = "PHASE8_SUBCMD_EXEC_CMD_SELF_TEST=pass";

const REQUIRED_ANCHORS = [_][]const u8{
    "systemPath and getArgvExecPath preserve C-style precedence",
    "EnvMap owns inserted keys so later caller mutations cannot corrupt lookups",
    "extractArgv0Path splits command names from directory prefixes",
    "buildSearchPath rewrites relative entries against the working directory",
    "buildSearchPath preserves root-cwd doubled slashes used by the C helper",
    "buildSearchPath skips rooted argv0 empty directories when assembling PATH",
    "setupPath preserves the inherited exec-path string while normalizing PATH entries",
    "setupPathWithPwd keeps logical PWD when identity matches",
    "setupPathWithPwd falls back to cwd when logical PWD identity does not match",
    "setupPathWithPwd falls back to cwd when logical PWD identity is unavailable",
    "setupPathWithPwd ignores an explicitly empty logical PWD even when identity matches",
    "prepareExecCmd prepends the configured executable name and preserves a trailing null slot",
    "collectExeclArgs keeps the command head and first null terminator",
    "collectExeclArgs rejects a tail that never terminates with null",
    "collectExeclArgs rejects a null terminator that lands in MAX_ARGS",
    "buildDeferredExeclCall keeps the execl handoff pure and launch-free",
};

const REQUIRED_API_SURFACE = [_][]const u8{
    "systemPath",
    "getArgvExecPath",
    "buildSearchPath",
    "setupPath",
    "setupPathWithPwd",
    "prepareExecCmd",
    "collectExeclArgs",
    "buildDeferredExeclCall",
    "buildDeferredExecvCall",
};

const REQUIRED_HANDOFF_FOCUS = [_][]const u8{
    "exec-path precedence stays explicit-over-env-over-prefix",
    "PATH assembly keeps rooted and relative segments aligned with the C helper",
    "logical PWD handoff only wins when file identity matches",
    "execv and execl handoff packets preserve argv order and trailing null behavior",
    "execl argument collection rejects unterminated or over-capacity tails",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_anchors_path = try guard.joinPath(allocator, root, "tools/lib/subcmd/exec-cmd.zig");
    defer allocator.free(text_required_anchors_path);
    const text_required_anchors = try guard.readUtf8File(io, allocator, text_required_anchors_path);
    defer allocator.free(text_required_anchors);
    for (REQUIRED_ANCHORS) |marker| try guard.requireMarker(text_required_anchors, marker);
    const text_required_api_surface_path = try guard.joinPath(allocator, root, "tools/lib/subcmd/exec-cmd.zig");
    defer allocator.free(text_required_api_surface_path);
    const text_required_api_surface = try guard.readUtf8File(io, allocator, text_required_api_surface_path);
    defer allocator.free(text_required_api_surface);
    for (REQUIRED_API_SURFACE) |marker| try guard.requireMarker(text_required_api_surface, marker);
    const text_required_handoff_focus_path = try guard.joinPath(allocator, root, "tools/lib/subcmd/exec-cmd.zig");
    defer allocator.free(text_required_handoff_focus_path);
    const text_required_handoff_focus = try guard.readUtf8File(io, allocator, text_required_handoff_focus_path);
    defer allocator.free(text_required_handoff_focus);
    for (REQUIRED_HANDOFF_FOCUS) |marker| try guard.requireMarker(text_required_handoff_focus, marker);
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
