const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE05_ZIG_PATH_EXPORT=pass";
pub const self_test_pass_marker = "LANE05_ZIG_PATH_EXPORT_SELF_TEST=pass";

const SETUP_STEP = [_][]const u8{
    "- name: Setup pinned Zig toolchain",
};

const FAILURE_GATE = [_][]const u8{
    "if [ \"$download_success\" -ne 1 ]; then",
};

const FAILURE_MESSAGE = [_][]const u8{
    "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org",
};

const FINAL_ZIG_PATH = [_][]const u8{
    "zig_path=\"$extract_root/zig\"",
};

const PATH_EXPORT = [_][]const u8{
    "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
};

const FINAL_VERSION = [_][]const u8{
    "\"$zig_path\" version",
};

const NEXT_STEP = [_][]const u8{
    "- name: Compile current scripts",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_setup_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_setup_step_path);
    const text_setup_step = try guard.readUtf8File(io, allocator, text_setup_step_path);
    defer allocator.free(text_setup_step);
    for (SETUP_STEP) |marker| try guard.requireMarker(text_setup_step, marker);
    const text_failure_gate_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_failure_gate_path);
    const text_failure_gate = try guard.readUtf8File(io, allocator, text_failure_gate_path);
    defer allocator.free(text_failure_gate);
    for (FAILURE_GATE) |marker| try guard.requireMarker(text_failure_gate, marker);
    const text_failure_message_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_failure_message_path);
    const text_failure_message = try guard.readUtf8File(io, allocator, text_failure_message_path);
    defer allocator.free(text_failure_message);
    for (FAILURE_MESSAGE) |marker| try guard.requireMarker(text_failure_message, marker);
    const text_final_zig_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_final_zig_path_path);
    const text_final_zig_path = try guard.readUtf8File(io, allocator, text_final_zig_path_path);
    defer allocator.free(text_final_zig_path);
    for (FINAL_ZIG_PATH) |marker| try guard.requireMarker(text_final_zig_path, marker);
    const text_path_export_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_path_export_path);
    const text_path_export = try guard.readUtf8File(io, allocator, text_path_export_path);
    defer allocator.free(text_path_export);
    for (PATH_EXPORT) |marker| try guard.requireMarker(text_path_export, marker);
    const text_final_version_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_final_version_path);
    const text_final_version = try guard.readUtf8File(io, allocator, text_final_version_path);
    defer allocator.free(text_final_version);
    for (FINAL_VERSION) |marker| try guard.requireMarker(text_final_version, marker);
    const text_next_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_next_step_path);
    const text_next_step = try guard.readUtf8File(io, allocator, text_next_step_path);
    defer allocator.free(text_next_step);
    for (NEXT_STEP) |marker| try guard.requireMarker(text_next_step, marker);
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
