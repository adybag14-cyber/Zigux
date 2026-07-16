const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_ARTIFACT_DIFF_MAKEFILE_CONTRACT=pass";
pub const self_test_pass_marker = "PHASE4_ARTIFACT_DIFF_MAKEFILE_CONTRACT_SELF_TEST=pass";

const SELF_CHECK = [_][]const u8{
    "PHASE4_ARTIFACT_DIFF_MAKEFILE_CONTRACT_SELF_TEST=pass",
};

const CONTRACT_TARGET = [_][]const u8{
    "phase4-artifact-diff-contract",
};

const VALIDATE_TARGET = [_][]const u8{
    "phase4-validate",
};

const EXPECTED_CONTRACT_LINES = [_][]const u8{
    "phase4-artifact-diff-contract:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) run scripts/zigux/artifact_diff.zig -- --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_determinism.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase4_artifact_diff_validator_replays.zig",
};

const EXPECTED_VALIDATE_LINES = [_][]const u8{
    "phase4-validate:",
    "\t$(MAKE) phase4-artifact-diff-contract",
};

const FORBIDDEN_PHASE4_LINES = [_][]const u8{
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase4.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_artifact_diff_contract.zig --self-test",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_artifact_diff_contract.zig",
};

const EXPECTED_SELF_TEST_CASES = [_][]const u8{
    "baseline_round_trip",
    "missing_makefile",
    "contract_missing_determinism_self_test",
    "contract_legacy_contract_self_test",
    "validate_missing_make_delegate",
    "validate_legacy_validator",
    "validate_legacy_contract_check",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_self_check_path = try guard.joinPath(allocator, root, "scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig");
    defer allocator.free(text_self_check_path);
    const text_self_check = try guard.readUtf8File(io, allocator, text_self_check_path);
    defer allocator.free(text_self_check);
    for (SELF_CHECK) |marker| try guard.requireMarker(text_self_check, marker);
    const text_contract_target_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_contract_target_path);
    const text_contract_target = try guard.readUtf8File(io, allocator, text_contract_target_path);
    defer allocator.free(text_contract_target);
    for (CONTRACT_TARGET) |marker| try guard.requireMarker(text_contract_target, marker);
    const text_validate_target_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_validate_target_path);
    const text_validate_target = try guard.readUtf8File(io, allocator, text_validate_target_path);
    defer allocator.free(text_validate_target);
    for (VALIDATE_TARGET) |marker| try guard.requireMarker(text_validate_target, marker);
    const text_expected_contract_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_expected_contract_lines_path);
    const text_expected_contract_lines = try guard.readUtf8File(io, allocator, text_expected_contract_lines_path);
    defer allocator.free(text_expected_contract_lines);
    for (EXPECTED_CONTRACT_LINES) |marker| try guard.requireExactLineCount(text_expected_contract_lines, marker, 1);
    const text_expected_validate_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_expected_validate_lines_path);
    const text_expected_validate_lines = try guard.readUtf8File(io, allocator, text_expected_validate_lines_path);
    defer allocator.free(text_expected_validate_lines);
    for (EXPECTED_VALIDATE_LINES) |marker| try guard.requireExactLineCount(text_expected_validate_lines, marker, 1);
    const text_forbidden_phase4_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_forbidden_phase4_lines_path);
    const text_forbidden_phase4_lines = try guard.readUtf8File(io, allocator, text_forbidden_phase4_lines_path);
    defer allocator.free(text_forbidden_phase4_lines);
    for (FORBIDDEN_PHASE4_LINES) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_phase4_lines, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_expected_self_test_cases_path = try guard.joinPath(allocator, root, "scripts/zigux/check_phase4_artifact_diff_makefile_contract.zig");
    defer allocator.free(text_expected_self_test_cases_path);
    const text_expected_self_test_cases = try guard.readUtf8File(io, allocator, text_expected_self_test_cases_path);
    defer allocator.free(text_expected_self_test_cases);
    for (EXPECTED_SELF_TEST_CASES) |marker| try guard.requireMarker(text_expected_self_test_cases, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE4_ARTIFACT_DIFF_MAKEFILE_CONTRACT_SELF_TEST_CASE_COUNT={d}", .{EXPECTED_SELF_TEST_CASES.len});
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
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
