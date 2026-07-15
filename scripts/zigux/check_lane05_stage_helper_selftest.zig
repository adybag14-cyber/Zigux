const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE05_STAGE_HELPER_SELFTEST=pass";
pub const self_test_pass_marker = "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass";

const ARCHIVE_CHECK_STEP = [_][]const u8{
    "- name: Check current pinned Zig archive packet",
};

const ARCHIVE_CHECK_CMD = [_][]const u8{
    "zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
};

const INSTALL_SELF_TEST_STEP = [_][]const u8{
    "- name: Self-test current Zig installer helper",
};

const INSTALL_SELF_TEST_CMD = [_][]const u8{
    "zig run scripts/zigux/install_zig.zig -- --self-test",
};

const STAGE_HELPER_SELF_TEST_STEP = [_][]const u8{
    "- name: Self-test current staged pinned Zig archive helper",
};

const STAGE_HELPER_SELF_TEST_CMD = [_][]const u8{
    "zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test",
};

const CONTRACT_SELF_TEST_STEP = [_][]const u8{
    "- name: Self-test current Lane 05 stage helper contract checker",
};

const CONTRACT_SELF_TEST_CMD = [_][]const u8{
    "zig run scripts/zigux/check_lane05_stage_helper_contract.zig -- --self-test",
};

const CONTRACT_CHECK_STEP = [_][]const u8{
    "- name: Check current Lane 05 stage helper contract packet",
};

const CONTRACT_CHECK_CMD = [_][]const u8{
    "zig run scripts/zigux/check_lane05_stage_helper_contract.zig",
};

const SELF_TEST_STEP = [_][]const u8{
    "- name: Self-test current Lane 05 stage helper selftest checker",
};

const SELF_TEST_CMD = [_][]const u8{
    "zig run scripts/zigux/check_lane05_stage_helper_selftest.zig -- --self-test",
};

const CHECK_STEP = [_][]const u8{
    "- name: Check current Lane 05 stage helper selftest packet",
};

const CHECK_CMD = [_][]const u8{
    "zig run scripts/zigux/check_lane05_stage_helper_selftest.zig",
};

const NEXT_STEP = [_][]const u8{
    "- name: Self-test current Phase 2 fixdep gate checker",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_archive_check_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_check_step_path);
    const text_archive_check_step = try guard.readUtf8File(io, allocator, text_archive_check_step_path);
    defer allocator.free(text_archive_check_step);
    for (ARCHIVE_CHECK_STEP) |marker| try guard.requireMarker(text_archive_check_step, marker);
    const text_archive_check_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_check_cmd_path);
    const text_archive_check_cmd = try guard.readUtf8File(io, allocator, text_archive_check_cmd_path);
    defer allocator.free(text_archive_check_cmd);
    for (ARCHIVE_CHECK_CMD) |marker| try guard.requireMarker(text_archive_check_cmd, marker);
    const text_install_self_test_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_install_self_test_step_path);
    const text_install_self_test_step = try guard.readUtf8File(io, allocator, text_install_self_test_step_path);
    defer allocator.free(text_install_self_test_step);
    for (INSTALL_SELF_TEST_STEP) |marker| try guard.requireMarker(text_install_self_test_step, marker);
    const text_install_self_test_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_install_self_test_cmd_path);
    const text_install_self_test_cmd = try guard.readUtf8File(io, allocator, text_install_self_test_cmd_path);
    defer allocator.free(text_install_self_test_cmd);
    for (INSTALL_SELF_TEST_CMD) |marker| try guard.requireMarker(text_install_self_test_cmd, marker);
    const text_stage_helper_self_test_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_stage_helper_self_test_step_path);
    const text_stage_helper_self_test_step = try guard.readUtf8File(io, allocator, text_stage_helper_self_test_step_path);
    defer allocator.free(text_stage_helper_self_test_step);
    for (STAGE_HELPER_SELF_TEST_STEP) |marker| try guard.requireMarker(text_stage_helper_self_test_step, marker);
    const text_stage_helper_self_test_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_stage_helper_self_test_cmd_path);
    const text_stage_helper_self_test_cmd = try guard.readUtf8File(io, allocator, text_stage_helper_self_test_cmd_path);
    defer allocator.free(text_stage_helper_self_test_cmd);
    for (STAGE_HELPER_SELF_TEST_CMD) |marker| try guard.requireMarker(text_stage_helper_self_test_cmd, marker);
    const text_contract_self_test_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_contract_self_test_step_path);
    const text_contract_self_test_step = try guard.readUtf8File(io, allocator, text_contract_self_test_step_path);
    defer allocator.free(text_contract_self_test_step);
    for (CONTRACT_SELF_TEST_STEP) |marker| try guard.requireMarker(text_contract_self_test_step, marker);
    const text_contract_self_test_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_contract_self_test_cmd_path);
    const text_contract_self_test_cmd = try guard.readUtf8File(io, allocator, text_contract_self_test_cmd_path);
    defer allocator.free(text_contract_self_test_cmd);
    for (CONTRACT_SELF_TEST_CMD) |marker| try guard.requireMarker(text_contract_self_test_cmd, marker);
    const text_contract_check_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_contract_check_step_path);
    const text_contract_check_step = try guard.readUtf8File(io, allocator, text_contract_check_step_path);
    defer allocator.free(text_contract_check_step);
    for (CONTRACT_CHECK_STEP) |marker| try guard.requireMarker(text_contract_check_step, marker);
    const text_contract_check_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_contract_check_cmd_path);
    const text_contract_check_cmd = try guard.readUtf8File(io, allocator, text_contract_check_cmd_path);
    defer allocator.free(text_contract_check_cmd);
    for (CONTRACT_CHECK_CMD) |marker| try guard.requireMarker(text_contract_check_cmd, marker);
    const text_self_test_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_step_path);
    const text_self_test_step = try guard.readUtf8File(io, allocator, text_self_test_step_path);
    defer allocator.free(text_self_test_step);
    for (SELF_TEST_STEP) |marker| try guard.requireMarker(text_self_test_step, marker);
    const text_self_test_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cmd_path);
    const text_self_test_cmd = try guard.readUtf8File(io, allocator, text_self_test_cmd_path);
    defer allocator.free(text_self_test_cmd);
    for (SELF_TEST_CMD) |marker| try guard.requireMarker(text_self_test_cmd, marker);
    const text_check_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_check_step_path);
    const text_check_step = try guard.readUtf8File(io, allocator, text_check_step_path);
    defer allocator.free(text_check_step);
    for (CHECK_STEP) |marker| try guard.requireMarker(text_check_step, marker);
    const text_check_cmd_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_check_cmd_path);
    const text_check_cmd = try guard.readUtf8File(io, allocator, text_check_cmd_path);
    defer allocator.free(text_check_cmd);
    for (CHECK_CMD) |marker| try guard.requireMarker(text_check_cmd, marker);
    const text_next_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_next_step_path);
    const text_next_step = try guard.readUtf8File(io, allocator, text_next_step_path);
    defer allocator.free(text_next_step);
    for (NEXT_STEP) |marker| try guard.requireMarker(text_next_step, marker);
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
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        _ = try runSelfTest(io, allocator);
        return;
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
