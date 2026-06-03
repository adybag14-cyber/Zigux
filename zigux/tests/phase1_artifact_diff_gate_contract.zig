const std = @import("std");

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    WrongMarkerOrder,
    CountMismatch,
};

const repo_files = [_][]const u8{
    "Documentation/zigux/artifact-diff.md",
    "scripts/zigux/README.md",
    "scripts/zigux/artifact_diff.py",
};

const phase1_note_markers = [_][]const u8{
    "Phase 1 still uses `scripts/zigux/artifact_diff.py` as the shared host-side comparison helper behind the committed helper parity fixtures, including `phase1_helpers.json` and the Phase 1 parity reminder packet.",
    "`scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig` keep a focused fixture-backed helper parity replay anchor on current `master`",
};

const helper_mode_markers = [_][]const u8{
    "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
    "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
    "ARTIFACT_DIFF_SELF_TEST=pass",
    "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}",
    "ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES)",
};

const helper_case_markers = [_][]const u8{
    "    \"text_pass\",",
    "    \"text_mismatch\",",
    "    \"json_pass\",",
    "    \"json_mismatch\",",
    "    \"json_invalid_expected\",",
    "    \"json_invalid_actual\",",
    "    \"json_invalid_both\",",
    "    \"json_missing_expected\",",
    "    \"json_missing_actual\",",
    "    \"json_missing_both\",",
    "    \"bytes_pass\",",
    "    \"bytes_drift\",",
    "    \"text_missing_expected\",",
    "    \"text_missing_actual\",",
    "    \"text_missing_both\",",
    "    \"bytes_missing_expected\",",
    "    \"bytes_missing_actual\",",
    "    \"bytes_missing_both\",",
    "    \"legacy_sha256_alias\",",
    "    \"missing_mode_value_rejected\",",
    "    \"missing_positional_arguments_rejected\",",
    "    \"invalid_mode_rejected\",",
    "    \"extra_positional_rejected\",",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return ContractError.MissingMarker;
    if (std.mem.indexOf(u8, haystack[first + needle.len ..], needle) != null) {
        return ContractError.DuplicateMarker;
    }
}

fn requirePresent(haystack: []const u8, needle: []const u8) !void {
    _ = std.mem.indexOf(u8, haystack, needle) orelse return ContractError.MissingMarker;
}

fn requireAll(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try requireOnce(haystack, marker);
    }
}

fn requireAllPresent(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try requirePresent(haystack, marker);
    }
}

fn requireInOrder(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], marker) orelse return ContractError.MissingMarker;
        cursor += relative + marker.len;
    }
}

fn selfTestCasesBlock(helper: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, helper, "SELF_TEST_CASES = [") orelse return ContractError.MissingMarker;
    const relative_end = std.mem.indexOf(u8, helper[start..], "\n]") orelse return ContractError.MissingMarker;
    return helper[start .. start + relative_end];
}

fn requireSelfTestCases(helper: []const u8) !void {
    const cases_block = try selfTestCasesBlock(helper);
    try requireAll(cases_block, &helper_case_markers);
    try requireInOrder(cases_block, &helper_case_markers);
    try requireOnce(helper, "assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")");
}

test "phase1 artifact diff gate keeps current reminder anchors visible" {
    const artifact_note = try readRepoFile(std.testing.allocator, repo_files[0]);
    defer std.testing.allocator.free(artifact_note);
    const scripts_readme = try readRepoFile(std.testing.allocator, repo_files[1]);
    defer std.testing.allocator.free(scripts_readme);

    try requireOnce(artifact_note, phase1_note_markers[0]);
    try requireOnce(scripts_readme, phase1_note_markers[1]);
}

test "artifact diff helper keeps Phase 1 comparison modes and legacy alias stable" {
    const helper = try readRepoFile(std.testing.allocator, repo_files[2]);
    defer std.testing.allocator.free(helper);

    try requireAllPresent(helper, &helper_mode_markers);
    try requireInOrder(helper, &helper_mode_markers);
}

test "artifact diff helper keeps the shipped self-test case spine ordered" {
    const helper = try readRepoFile(std.testing.allocator, repo_files[2]);
    defer std.testing.allocator.free(helper);

    try requireSelfTestCases(helper);
}

test "phase1 artifact diff gate contract watches exactly the expected files" {
    try std.testing.expectEqual(@as(usize, 3), repo_files.len);
    try std.testing.expectEqualStrings("Documentation/zigux/artifact-diff.md", repo_files[0]);
    try std.testing.expectEqualStrings("scripts/zigux/README.md", repo_files[1]);
    try std.testing.expectEqualStrings("scripts/zigux/artifact_diff.py", repo_files[2]);
}
