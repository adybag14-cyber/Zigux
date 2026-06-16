const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "ARTIFACT_DIFF_CONTRACT=pass";
pub const self_test_pass_marker = "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass";

const HELP_LINES = [_][]const u8{
    "usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test]",
    " [expected] [actual]",
    "",
    "Compare two artifacts in a stable mode.",
    "",
    "positional arguments:",
    " expected",
    " actual",
    "",
    "options:",
    " -h, --help show this help message and exit",
    " --mode {text,json,bytes}",
    " --self-test Run built-in deterministic comparison checks.",
};

const MISSING_ARGUMENT_ERROR = [_][]const u8{
    "usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test] [expected] [actual] artifact_diff.zig: error: --mode, expected, and actual are required unless --self-test is set",
};

const INVALID_MODE_ERROR = [_][]const u8{
    "usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test] [expected] [actual] artifact_diff.zig: error: argument --mode: invalid choice: 'yaml' (choose from text, json, bytes)",
};

const TOO_MANY_ARGUMENTS_ERROR = [_][]const u8{
    "usage: artifact_diff.zig [-h] [--mode {text,json,bytes}] [--self-test] [expected] [actual] artifact_diff.zig: error: expected exactly two positional arguments",
};

const HELPER_SELF_TEST_CASES = [_][]const u8{
    "text_pass",
    "text_mismatch",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "bytes_pass",
    "bytes_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "legacy_sha256_alias",
    "missing_mode_value_rejected",
    "missing_positional_arguments_rejected",
    "invalid_mode_rejected",
    "extra_positional_rejected",
};

const HELPER_SELF_TEST_LINES = [_][]const u8{
    "ARTIFACT_DIFF_SELF_TEST=pass",
};

const BASE_CONTRACT_CASES = [_][]const u8{
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
};

const REPEAT_CONTRACT_CASES = [_][]const u8{
    "helper_self_test_repeat",
    "cli_help_output_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "bytes_drift_repeat",
};

const REVIEW_NOTE_MARKERS = [_][]const u8{
    "host-side artifact-diff tooling contract",
    "owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
    "rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
};

const SELF_TEST_CASES = [_][]const u8{
    "catalog_shape",
    "review_note_marker_round_trip",
    "review_note_owner_marker_drift",
    "review_note_marker_drift",
    "cli_help_round_trip",
    "cli_help_line_drift",
    "cli_missing_argument_parser_round_trip",
    "cli_missing_argument_parser_stderr_drift",
    "cli_invalid_mode_parser_round_trip",
    "cli_invalid_mode_parser_stderr_drift",
    "helper_summary_round_trip",
    "contract_summary_round_trip",
    "helper_summary_status_drift",
    "helper_summary_count_drift",
    "helper_summary_duplicate_case_drift",
    "helper_summary_case_order_drift",
    "contract_summary_status_drift",
    "contract_summary_base_count_drift",
    "contract_summary_base_case_order_drift",
    "contract_summary_repeat_count_drift",
    "contract_summary_repeat_case_order_drift",
    "contract_summary_case_count_drift",
    "contract_summary_duplicate_case_drift",
    "contract_summary_case_order_drift",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_help_lines_path = try guard.joinPath(allocator, root, "scripts");
    defer allocator.free(text_help_lines_path);
    const text_help_lines = try guard.readUtf8File(io, allocator, text_help_lines_path);
    defer allocator.free(text_help_lines);
    for (HELP_LINES) |marker| try guard.requireExactLineCount(text_help_lines, marker, 1);
    const text_missing_argument_error_path = try guard.joinPath(allocator, root, "scripts");
    defer allocator.free(text_missing_argument_error_path);
    const text_missing_argument_error = try guard.readUtf8File(io, allocator, text_missing_argument_error_path);
    defer allocator.free(text_missing_argument_error);
    for (MISSING_ARGUMENT_ERROR) |marker| try guard.requireMarker(text_missing_argument_error, marker);
    const text_invalid_mode_error_path = try guard.joinPath(allocator, root, "scripts");
    defer allocator.free(text_invalid_mode_error_path);
    const text_invalid_mode_error = try guard.readUtf8File(io, allocator, text_invalid_mode_error_path);
    defer allocator.free(text_invalid_mode_error);
    for (INVALID_MODE_ERROR) |marker| try guard.requireMarker(text_invalid_mode_error, marker);
    const text_too_many_arguments_error_path = try guard.joinPath(allocator, root, "scripts");
    defer allocator.free(text_too_many_arguments_error_path);
    const text_too_many_arguments_error = try guard.readUtf8File(io, allocator, text_too_many_arguments_error_path);
    defer allocator.free(text_too_many_arguments_error);
    for (TOO_MANY_ARGUMENTS_ERROR) |marker| try guard.requireMarker(text_too_many_arguments_error, marker);
    const text_helper_self_test_cases_path = try guard.joinPath(allocator, root, "scripts");
    defer allocator.free(text_helper_self_test_cases_path);
    const text_helper_self_test_cases = try guard.readUtf8File(io, allocator, text_helper_self_test_cases_path);
    defer allocator.free(text_helper_self_test_cases);
    for (HELPER_SELF_TEST_CASES) |marker| try guard.requireMarker(text_helper_self_test_cases, marker);
    const text_helper_self_test_lines_path = try guard.joinPath(allocator, root, "scripts");
    defer allocator.free(text_helper_self_test_lines_path);
    const text_helper_self_test_lines = try guard.readUtf8File(io, allocator, text_helper_self_test_lines_path);
    defer allocator.free(text_helper_self_test_lines);
    for (HELPER_SELF_TEST_LINES) |marker| try guard.requireExactLineCount(text_helper_self_test_lines, marker, 1);
    const text_base_contract_cases_path = try guard.joinPath(allocator, root, "scripts");
    defer allocator.free(text_base_contract_cases_path);
    const text_base_contract_cases = try guard.readUtf8File(io, allocator, text_base_contract_cases_path);
    defer allocator.free(text_base_contract_cases);
    for (BASE_CONTRACT_CASES) |marker| try guard.requireMarker(text_base_contract_cases, marker);
    const text_repeat_contract_cases_path = try guard.joinPath(allocator, root, "scripts");
    defer allocator.free(text_repeat_contract_cases_path);
    const text_repeat_contract_cases = try guard.readUtf8File(io, allocator, text_repeat_contract_cases_path);
    defer allocator.free(text_repeat_contract_cases);
    for (REPEAT_CONTRACT_CASES) |marker| try guard.requireMarker(text_repeat_contract_cases, marker);
    const text_review_note_markers_path = try guard.joinPath(allocator, root, "scripts");
    defer allocator.free(text_review_note_markers_path);
    const text_review_note_markers = try guard.readUtf8File(io, allocator, text_review_note_markers_path);
    defer allocator.free(text_review_note_markers);
    for (REVIEW_NOTE_MARKERS) |marker| try guard.requireMarker(text_review_note_markers, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, "scripts");
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
