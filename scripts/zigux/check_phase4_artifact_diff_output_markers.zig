const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_ARTIFACT_DIFF_OUTPUT_MARKERS=pass";
pub const self_test_pass_marker = "PHASE4_ARTIFACT_DIFF_OUTPUT_MARKERS_SELF_TEST=pass";

const SELF_TEST_CASES = [_][]const u8{
    "round_trip",
    "missing_target_file",
    "contract_self_test_marker_drift",
    "contract_live_marker_drift",
    "determinism_self_test_marker_drift",
    "determinism_live_marker_drift",
    "validator_replays_self_test_marker_drift",
    "validator_replays_live_marker_drift",
    "validator_replays_mode_prefix_drift",
    "command_failure_detected",
};

const CHECKS = [_][]const u8{
    "CheckSpeccontract_self_testscripts\\zigux/check_artifact_diff_contract.zig--self-testARTIFACT_DIFF_CONTRACT_SELF_TEST=passARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24",
    "CheckSpeccontract_livescripts\\zigux/check_artifact_diff_contract.zigARTIFACT_DIFF_CONTRACT=passARTIFACT_DIFF_CONTRACT_CASE_COUNT=30",
    "CheckSpecdeterminism_self_testscripts\\zigux/check_phase4_artifact_diff_determinism.zig--self-testPHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=passPHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13",
    "CheckSpecdeterminism_livescripts\\zigux/check_phase4_artifact_diff_determinism.zigPHASE4_ARTIFACT_DIFF_DETERMINISM=passPHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0",
    "CheckSpecvalidator_replays_self_testscripts\\zigux/check_phase4_artifact_diff_validator_replays.zig--self-testPHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=passPHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14",
    "CheckSpecvalidator_replays_livescripts\\zigux/check_phase4_artifact_diff_validator_replays.zigPHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=passPHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=16PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
    const text_checks_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_checks_path);
    const text_checks = try guard.readUtf8File(io, allocator, text_checks_path);
    defer allocator.free(text_checks);
    for (CHECKS) |marker| try guard.requireMarker(text_checks, marker);
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
