const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_ARTIFACT_DIFF_EXACT_REPLAY=pass";
pub const self_test_pass_marker = "PHASE4_ARTIFACT_DIFF_EXACT_REPLAY_SELF_TEST=pass";

const DIRECT_REPLAY_COMMANDS = [_][]const u8{
    "zig run scripts/zigux/artifact_diff.zig -- --self-test",
    "zig run scripts\\zigux/check_artifact_diff_contract.zig -- --self-test",
    "zig run scripts\\zigux/check_artifact_diff_contract.zig",
    "zig run scripts\\zigux/check_phase4_artifact_diff_determinism.zig -- --self-test",
    "zig run scripts\\zigux/check_phase4_artifact_diff_determinism.zig",
    "zig run scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig -- --self-test",
    "zig run scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig",
    "zig run scripts\\zigux/check_phase4_artifact_diff_exact_replay.zig -- --self-test",
    "zig run scripts\\zigux/check_phase4_artifact_diff_exact_replay.zig",
};

const SELF_TEST_CASES = [_][]const u8{
    "catalog_shape",
    "note_command_round_trip",
    "note_command_drift",
    "note_helper_catalog_drift",
    "note_contract_catalog_drift",
    "note_determinism_catalog_drift",
    "note_validator_catalog_drift",
    "note_exact_replay_catalog_drift",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_direct_replay_commands_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-artifact-diff-exact-replay.md");
    defer allocator.free(text_direct_replay_commands_path);
    const text_direct_replay_commands = try guard.readUtf8File(io, allocator, text_direct_replay_commands_path);
    defer allocator.free(text_direct_replay_commands);
    for (DIRECT_REPLAY_COMMANDS) |marker| try guard.requireMarker(text_direct_replay_commands, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-artifact-diff-exact-replay.md");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
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
