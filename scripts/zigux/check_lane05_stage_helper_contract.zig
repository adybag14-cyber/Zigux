const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");
const policy = @import("toolchain_policy.zig");

pub const live_pass_marker = "LANE05_STAGE_HELPER_CONTRACT=pass";
pub const self_test_pass_marker = "LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass";

const STAGE_HELPER_REL = "scripts/zigux/stage_pinned_zig_archive.zig";
const README_REL = "third_party/README.md";
const POLICY_REL = "scripts/zigux/zig-toolchain-policy.json";

const HELPER_MARKERS = [_][]const u8{
    "toolchain_policy_rel = \"scripts/zigux/zig-toolchain-policy.json\"",
    "third_party_rel = \"third_party\"",
    "STAGE_PINNED_ZIG_ARCHIVE=pass",
    "STAGE_PINNED_ZIG_ARCHIVE=fail",
    "STAGE_PINNED_ZIG_ARCHIVE_TARGET=",
    "STAGE_PINNED_ZIG_ARCHIVE_FILENAME=",
    "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=",
    "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=",
    "STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=",
    "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=",
    "STAGE_PINNED_ZIG_ARCHIVE_STATUS=",
    "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=",
};

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) guard.GuardError!void {
    try guard.requireOrder(text, earlier, later);
}

fn checkStageHelper(text: []const u8) !void {
    for (HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    try requireOrder(text, "STAGE_PINNED_ZIG_ARCHIVE_TARGET=", "STAGE_PINNED_ZIG_ARCHIVE_FILENAME=");
    try requireOrder(text, "STAGE_PINNED_ZIG_ARCHIVE_FILENAME=", "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=");
    try requireOrder(text, "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=", "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=");
    try requireOrder(text, "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=", "STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=");
    try requireOrder(text, "STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=", "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=");
    try requireOrder(text, "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=", "STAGE_PINNED_ZIG_ARCHIVE_STATUS=");
}

fn checkReadme(io: Io, allocator: std.mem.Allocator, root: []const u8, target: []const u8, channel: []const u8, sha256: []const u8) !void {
    const readme_path = try guard.joinPath(allocator, root, README_REL);
    defer allocator.free(readme_path);
    const readme = try guard.readUtf8File(io, allocator, readme_path);
    defer allocator.free(readme);

    const markers = [_][]const u8{
        "# Zigux third-party archives",
        target,
        channel,
        sha256,
        "59264068",
    };
    for (markers) |marker| try guard.requireMarker(readme, marker);
}

fn loadContract(io: Io, allocator: std.mem.Allocator, root: []const u8) !struct { target: []const u8, channel: []const u8, sha256: []const u8 } {
    const policy_path = try guard.joinPath(allocator, root, POLICY_REL);
    defer allocator.free(policy_path);
    const json_bytes = try guard.readUtf8File(io, allocator, policy_path);
    defer allocator.free(json_bytes);
    var loaded = try policy.loadPolicyFromJson(allocator, json_bytes);
    defer policy.freePolicy(allocator, &loaded);
    const target = blk: {
        for (loaded.upgrade_policy.archive_target_scope) |candidate| {
            if (std.mem.eql(u8, candidate, "x86_64-linux")) break :blk candidate;
        }
        return error.MissingLinuxTarget;
    };
    const sha = loaded.archive_sha256.get(target) orelse return error.MissingSha;
    return .{
        .target = try allocator.dupe(u8, target),
        .channel = try allocator.dupe(u8, loaded.channel),
        .sha256 = try allocator.dupe(u8, sha),
    };
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const contract = try loadContract(io, allocator, root);
    defer {
        allocator.free(contract.target);
        allocator.free(contract.channel);
        allocator.free(contract.sha256);
    }

    const helper_path = try guard.joinPath(allocator, root, STAGE_HELPER_REL);
    defer allocator.free(helper_path);
    const helper = try guard.readUtf8File(io, allocator, helper_path);
    defer allocator.free(helper);
    try checkStageHelper(helper);
    try checkReadme(io, allocator, root, contract.target, contract.channel, contract.sha256);
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
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
        if (std.mem.eql(u8, arg, "--root")) {
            index += 1;
            if (index >= args.len) std.process.exit(2);
            explicit_root = args[index];
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
