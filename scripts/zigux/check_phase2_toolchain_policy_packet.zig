const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_TOOLCHAIN_POLICY_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_TOOLCHAIN_POLICY_PACKET_SELF_TEST=pass";

const EXPECTED_TARGETS = [_][]const u8{
    "x86_64-linux",
};

const EXPECTED_REQUIRED_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-validate",
};

const WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_zig_toolchain.zig -- --policy-only",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
};

const BOOTSTRAP_MARKERS = [_][]const u8{
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig -- --policy-only`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig -- --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "keeps the minimum version in lockstep",
    "limits archive digests to `x86_64-linux`",
};

const MAKEFILE_LINES = [_][]const u8{
    "phase2-toolchain:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --policy-only",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --archive-only --allow-missing",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_targets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_targets_path);
    const text_expected_targets = try guard.readUtf8File(io, allocator, text_expected_targets_path);
    defer allocator.free(text_expected_targets);
    for (EXPECTED_TARGETS) |marker| try guard.requireMarker(text_expected_targets, marker);
    const text_expected_required_routes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_required_routes_path);
    const text_expected_required_routes = try guard.readUtf8File(io, allocator, text_expected_required_routes_path);
    defer allocator.free(text_expected_required_routes);
    for (EXPECTED_REQUIRED_ROUTES) |marker| try guard.requireMarker(text_expected_required_routes, marker);
    const text_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_lines_path);
    const text_workflow_lines = try guard.readUtf8File(io, allocator, text_workflow_lines_path);
    defer allocator.free(text_workflow_lines);
    for (WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_workflow_lines, marker, 1);
    const text_bootstrap_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bootstrap_markers_path);
    const text_bootstrap_markers = try guard.readUtf8File(io, allocator, text_bootstrap_markers_path);
    defer allocator.free(text_bootstrap_markers);
    for (BOOTSTRAP_MARKERS) |marker| try guard.requireMarker(text_bootstrap_markers, marker);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
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
