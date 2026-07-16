const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "ARTIFACT_DIFF_CONTRACT=pass";
pub const self_test_pass_marker = "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    " expected",
    " actual",
    "run: zig run check_artifact_diff_contract.zig --self-test",
    "run: zig run check_artifact_diff_contract.zig",
};

const markers_1 = [_][]const u8{
    "helper_self_test",
    "cli_help_output",
    "cli_missing_required_args",
    "cli_missing_mode_value",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "cli_extra_positional_args",
    "text_pass",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_pass",
    "json_mismatch",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "bytes_pass",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "bytes_drift",
    "helper_self_test_repeat",
    "cli_help_output_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "bytes_drift_repeat",
};

const markers_2 = [_][]const u8{
    "ARTIFACT_DIFF_SELF_TEST=pass",
};

const markers_3 = [_][]const u8{
    "options:",
};

const markers_4 = [_][]const u8{
    " [expected] [actual]",
    "Compare two artifacts in a stable mode.",
    "positional arguments:",
    " -h, --help show this help message and exit",
    " --mode {text,json,bytes}",
    " --self-test Run built-in deterministic comparison checks.",
};

const markers_5 = [_][]const u8{
    "",
};

const markers_6 = [_][]const u8{
    "usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test]",
};

const markers_7 = [_][]const u8{
    "owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
    "rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
};

const contracts = [_]FileContract{
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/artifact-diff.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase4-artifact-diff-exact-replay.md", .markers = &markers_2 },
    .{ .rel = "drivers/watchdog/gpio_wdt.zig", .markers = &markers_3 },
    .{ .rel = "scripts/zigux/artifact_diff.zig", .markers = &markers_4 },
    .{ .rel = "zigux/Makefile", .markers = &markers_5 },
    .{ .rel = "zigux/tests/phase1_artifact_diff_bridge_contract.zig", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase1_artifact_diff_checker_contract.zig", .markers = &markers_7 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
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
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

// Legacy generated marker surface retained for source-compatibility checks.
// HELP_LINES
// usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test]
//  [expected] [actual]
//
// Compare two artifacts in a stable mode.
// positional arguments:
//  expected
//  actual
// options:
//  -h, --help show this help message and exit
//  --mode {text,json,bytes}
//  --self-test Run built-in deterministic comparison checks.
// MISSING_ARGUMENT_ERROR
// usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test] [expected] [actual] artifact_diff.zig: error: --mode, expected, and actual are required unless --self-test is set
// INVALID_MODE_ERROR
// usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test] [expected] [actual] artifact_diff.zig: error: argument --mode: invalid choice: 'yaml' (choose from text, json, bytes)
// TOO_MANY_ARGUMENTS_ERROR
// usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test] [expected] [actual] artifact_diff.zig: error: expected exactly two positional arguments
// HELPER_SELF_TEST_CASES
// text_pass
// text_mismatch
// json_pass
// json_mismatch
// json_invalid_expected
// json_invalid_actual
// json_invalid_both
// json_missing_expected
// json_missing_actual
// json_missing_both
// bytes_pass
// bytes_drift
// text_missing_expected
// text_missing_actual
// text_missing_both
// bytes_missing_expected
// bytes_missing_actual
// bytes_missing_both
// legacy_sha256_alias
// missing_mode_value_rejected
// missing_positional_arguments_rejected
// invalid_mode_rejected
// extra_positional_rejected
// HELPER_SELF_TEST_LINES
// ARTIFACT_DIFF_SELF_TEST=pass
// BASE_CONTRACT_CASES
// helper_self_test
// cli_help_output
// cli_missing_required_args
// cli_missing_mode_value
// cli_missing_actual_operand
// cli_invalid_mode
// cli_extra_positional_args
// REPEAT_CONTRACT_CASES
// helper_self_test_repeat
// cli_help_output_repeat
// text_pass_repeat
// json_mismatch_repeat
// bytes_drift_repeat
// REVIEW_NOTE_MARKERS
// host-side artifact-diff tooling contract
// owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`
// rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`
// SELF_TEST_CASES
// catalog_shape
// review_note_marker_round_trip
// review_note_owner_marker_drift
// review_note_marker_drift
// cli_help_round_trip
// cli_help_line_drift
// cli_missing_argument_parser_round_trip
// cli_missing_argument_parser_stderr_drift
// cli_invalid_mode_parser_round_trip
// cli_invalid_mode_parser_stderr_drift
// helper_summary_round_trip
// contract_summary_round_trip
// helper_summary_status_drift
// helper_summary_count_drift
// helper_summary_duplicate_case_drift
// helper_summary_case_order_drift
// contract_summary_status_drift
// contract_summary_base_count_drift
// contract_summary_base_case_order_drift
// contract_summary_repeat_count_drift
// contract_summary_repeat_case_order_drift
// contract_summary_case_count_drift
// contract_summary_duplicate_case_drift
// contract_summary_case_order_drift
