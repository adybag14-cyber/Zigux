const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE05_ARCHIVE_PARTS_WORKFLOW=pass";
pub const self_test_pass_marker = "LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST=pass";

const WORKFLOW_NAME = [_][]const u8{
    "name: zigux-bootstrap-archive-parts-packet",
};

const PUSH_BRANCH = [_][]const u8{
    "branches: [ master ]",
};

const CHECKER_PATH = [_][]const u8{
    "- 'scripts\\zigux/check_lane05_archive_parts_workflow.zig'",
};

const PACKET_CHECKER_PATH = [_][]const u8{
    "- 'scripts\\zigux/check_lane05_archive_parts_packet.zig'",
};

const POLICY_PATH = [_][]const u8{
    "- 'scripts/zigux/zig-toolchain-policy.json'",
};

const THIRD_PARTY_PATH = [_][]const u8{
    "- 'third_party/**'",
};

const WORKFLOW_PATH_FILTER = [_][]const u8{
    "- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'",
};

const PERMISSIONS = [_][]const u8{
    "contents: read",
};

const CHECKOUT_STEP = [_][]const u8{
    "- name: Checkout workspace snapshot",
};

const SETUP_PYTHON_STEP = [_][]const u8{
    "- name: Setup Python",
};

const COMPILE_STEP = [_][]const u8{
    "- name: Compile current Lane 05 archive-parts workflow scripts",
};

const COMPILE_CMD = [_][]const u8{
    "python3 -m py_compile scripts\\zigux/check_zig_toolchain.zig scripts\\zigux/check_lane05_archive_parts_packet.zig scripts\\zigux/check_lane05_archive_parts_workflow.zig",
};

const WORKFLOW_CHECKER_SELF_TEST_STEP = [_][]const u8{
    "- name: Self-test current Lane 05 archive-parts workflow checker",
};

const WORKFLOW_CHECKER_SELF_TEST_CMD = [_][]const u8{
    "zig run scripts\\zigux/check_lane05_archive_parts_workflow.zig --self-test",
};

const WORKFLOW_CHECKER_STEP = [_][]const u8{
    "- name: Check current Lane 05 archive-parts workflow packet",
};

const WORKFLOW_CHECKER_CMD = [_][]const u8{
    "zig run scripts\\zigux/check_lane05_archive_parts_workflow.zig",
};

const PACKET_SELF_TEST_STEP = [_][]const u8{
    "- name: Self-test current Lane 05 archive parts packet checker",
};

const PACKET_SELF_TEST_CMD = [_][]const u8{
    "zig run scripts\\zigux/check_lane05_archive_parts_packet.zig --self-test",
};

const PACKET_CHECK_STEP = [_][]const u8{
    "- name: Check current Lane 05 archive parts packet",
};

const PACKET_CHECK_CMD = [_][]const u8{
    "zig run scripts\\zigux/check_lane05_archive_parts_packet.zig --allow-missing",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_name_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_workflow_name_path);
    const text_workflow_name = try guard.readUtf8File(io, allocator, text_workflow_name_path);
    defer allocator.free(text_workflow_name);
    for (WORKFLOW_NAME) |marker| try guard.requireMarker(text_workflow_name, marker);
    const text_push_branch_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_push_branch_path);
    const text_push_branch = try guard.readUtf8File(io, allocator, text_push_branch_path);
    defer allocator.free(text_push_branch);
    for (PUSH_BRANCH) |marker| try guard.requireMarker(text_push_branch, marker);
    const text_checker_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_checker_path_path);
    const text_checker_path = try guard.readUtf8File(io, allocator, text_checker_path_path);
    defer allocator.free(text_checker_path);
    for (CHECKER_PATH) |marker| try guard.requireMarker(text_checker_path, marker);
    const text_packet_checker_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_packet_checker_path_path);
    const text_packet_checker_path = try guard.readUtf8File(io, allocator, text_packet_checker_path_path);
    defer allocator.free(text_packet_checker_path);
    for (PACKET_CHECKER_PATH) |marker| try guard.requireMarker(text_packet_checker_path, marker);
    const text_policy_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_policy_path_path);
    const text_policy_path = try guard.readUtf8File(io, allocator, text_policy_path_path);
    defer allocator.free(text_policy_path);
    for (POLICY_PATH) |marker| try guard.requireMarker(text_policy_path, marker);
    const text_third_party_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_third_party_path_path);
    const text_third_party_path = try guard.readUtf8File(io, allocator, text_third_party_path_path);
    defer allocator.free(text_third_party_path);
    for (THIRD_PARTY_PATH) |marker| try guard.requireMarker(text_third_party_path, marker);
    const text_workflow_path_filter_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_workflow_path_filter_path);
    const text_workflow_path_filter = try guard.readUtf8File(io, allocator, text_workflow_path_filter_path);
    defer allocator.free(text_workflow_path_filter);
    for (WORKFLOW_PATH_FILTER) |marker| try guard.requireMarker(text_workflow_path_filter, marker);
    const text_permissions_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_permissions_path);
    const text_permissions = try guard.readUtf8File(io, allocator, text_permissions_path);
    defer allocator.free(text_permissions);
    for (PERMISSIONS) |marker| try guard.requireMarker(text_permissions, marker);
    const text_checkout_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_checkout_step_path);
    const text_checkout_step = try guard.readUtf8File(io, allocator, text_checkout_step_path);
    defer allocator.free(text_checkout_step);
    for (CHECKOUT_STEP) |marker| try guard.requireMarker(text_checkout_step, marker);
    const text_setup_python_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_setup_python_step_path);
    const text_setup_python_step = try guard.readUtf8File(io, allocator, text_setup_python_step_path);
    defer allocator.free(text_setup_python_step);
    for (SETUP_PYTHON_STEP) |marker| try guard.requireMarker(text_setup_python_step, marker);
    const text_compile_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_compile_step_path);
    const text_compile_step = try guard.readUtf8File(io, allocator, text_compile_step_path);
    defer allocator.free(text_compile_step);
    for (COMPILE_STEP) |marker| try guard.requireMarker(text_compile_step, marker);
    const text_compile_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_compile_cmd_path);
    const text_compile_cmd = try guard.readUtf8File(io, allocator, text_compile_cmd_path);
    defer allocator.free(text_compile_cmd);
    for (COMPILE_CMD) |marker| try guard.requireMarker(text_compile_cmd, marker);
    const text_workflow_checker_self_test_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_workflow_checker_self_test_step_path);
    const text_workflow_checker_self_test_step = try guard.readUtf8File(io, allocator, text_workflow_checker_self_test_step_path);
    defer allocator.free(text_workflow_checker_self_test_step);
    for (WORKFLOW_CHECKER_SELF_TEST_STEP) |marker| try guard.requireMarker(text_workflow_checker_self_test_step, marker);
    const text_workflow_checker_self_test_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_workflow_checker_self_test_cmd_path);
    const text_workflow_checker_self_test_cmd = try guard.readUtf8File(io, allocator, text_workflow_checker_self_test_cmd_path);
    defer allocator.free(text_workflow_checker_self_test_cmd);
    for (WORKFLOW_CHECKER_SELF_TEST_CMD) |marker| try guard.requireMarker(text_workflow_checker_self_test_cmd, marker);
    const text_workflow_checker_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_workflow_checker_step_path);
    const text_workflow_checker_step = try guard.readUtf8File(io, allocator, text_workflow_checker_step_path);
    defer allocator.free(text_workflow_checker_step);
    for (WORKFLOW_CHECKER_STEP) |marker| try guard.requireMarker(text_workflow_checker_step, marker);
    const text_workflow_checker_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_workflow_checker_cmd_path);
    const text_workflow_checker_cmd = try guard.readUtf8File(io, allocator, text_workflow_checker_cmd_path);
    defer allocator.free(text_workflow_checker_cmd);
    for (WORKFLOW_CHECKER_CMD) |marker| try guard.requireMarker(text_workflow_checker_cmd, marker);
    const text_packet_self_test_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_packet_self_test_step_path);
    const text_packet_self_test_step = try guard.readUtf8File(io, allocator, text_packet_self_test_step_path);
    defer allocator.free(text_packet_self_test_step);
    for (PACKET_SELF_TEST_STEP) |marker| try guard.requireMarker(text_packet_self_test_step, marker);
    const text_packet_self_test_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_packet_self_test_cmd_path);
    const text_packet_self_test_cmd = try guard.readUtf8File(io, allocator, text_packet_self_test_cmd_path);
    defer allocator.free(text_packet_self_test_cmd);
    for (PACKET_SELF_TEST_CMD) |marker| try guard.requireMarker(text_packet_self_test_cmd, marker);
    const text_packet_check_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_packet_check_step_path);
    const text_packet_check_step = try guard.readUtf8File(io, allocator, text_packet_check_step_path);
    defer allocator.free(text_packet_check_step);
    for (PACKET_CHECK_STEP) |marker| try guard.requireMarker(text_packet_check_step, marker);
    const text_packet_check_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap-archive-parts-packet.yml");
    defer allocator.free(text_packet_check_cmd_path);
    const text_packet_check_cmd = try guard.readUtf8File(io, allocator, text_packet_check_cmd_path);
    defer allocator.free(text_packet_check_cmd);
    for (PACKET_CHECK_CMD) |marker| try guard.requireMarker(text_packet_check_cmd, marker);
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
