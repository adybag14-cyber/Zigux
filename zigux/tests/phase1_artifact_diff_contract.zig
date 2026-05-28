const std = @import("std");

const RequiredMarker = struct {
    label: []const u8,
    needle: []const u8,
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.Io.Threaded.global_single_threaded.io(),
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, marker: RequiredMarker) !void {
    std.testing.expect(std.mem.indexOf(u8, haystack, marker.needle) != null) catch |err| {
        std.debug.print("missing {s}: {s}\n", .{ marker.label, marker.needle });
        return err;
    };
}

fn expectAnyContains(haystack: []const u8, label: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) return;
    }
    std.debug.print("missing {s}; accepted markers:\n", .{label});
    for (needles) |needle| std.debug.print("  {s}\n", .{needle});
    return error.TestExpectedEqual;
}

test "phase 1 artifact diff note keeps helper route and output contract explicit" {
    const artifact_diff_note = try readRepoFile(std.testing.allocator, "Documentation/zigux/artifact-diff.md");
    defer std.testing.allocator.free(artifact_diff_note);

    const markers = [_]RequiredMarker{
        .{ .label = "Phase 1 artifact-diff route", .needle = "Phase 1" },
        .{ .label = "shared helper path", .needle = "scripts/zigux/artifact_diff.py" },
        .{ .label = "Phase 1 parity fixture", .needle = "phase1_helpers.json" },
        .{ .label = "primary status line", .needle = "ARTIFACT_DIFF" },
        .{ .label = "mode line", .needle = "MODE" },
        .{ .label = "expected path line", .needle = "EXPECTED" },
        .{ .label = "actual path line", .needle = "ACTUAL" },
        .{ .label = "missing expected marker", .needle = "EXPECTED_EXISTS" },
        .{ .label = "missing actual marker", .needle = "ACTUAL_EXISTS" },
        .{ .label = "malformed JSON marker", .needle = "EXPECTED_JSON_ERROR" },
        .{ .label = "artifact-diff contract checker", .needle = "check-artifact-diff-contract.py" },
    };
    inline for (markers) |marker| try expectContains(artifact_diff_note, marker);
}

test "phase 1 artifact diff helper keeps deterministic self-test catalog anchors" {
    const artifact_diff_helper = try readRepoFile(std.testing.allocator, "scripts/zigux/artifact_diff.py");
    defer std.testing.allocator.free(artifact_diff_helper);

    const markers = [_]RequiredMarker{
        .{ .label = "self-test catalog", .needle = "EXPECTED_SELF_TEST_CASES" },
        .{ .label = "text pass case", .needle = "text_pass" },
        .{ .label = "text mismatch case", .needle = "text_mismatch" },
        .{ .label = "JSON pass case", .needle = "json_pass" },
        .{ .label = "JSON mismatch case", .needle = "json_mismatch" },
        .{ .label = "expected JSON failure", .needle = "json_invalid_expected" },
        .{ .label = "actual JSON failure", .needle = "json_invalid_actual" },
        .{ .label = "missing expected artifact", .needle = "text_missing_expected" },
        .{ .label = "missing actual artifact", .needle = "text_missing_actual" },
        .{ .label = "published self-test status", .needle = "ARTIFACT_DIFF_SELF_TEST=pass" },
        .{ .label = "published self-test count", .needle = "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT" },
        .{ .label = "published self-test catalog", .needle = "ARTIFACT_DIFF_SELF_TEST_CASES" },
    };
    inline for (markers) |marker| try expectContains(artifact_diff_helper, marker);

    try expectAnyContains(artifact_diff_helper, "binary artifact comparison mode", &.{
        "bytes_pass",
        "sha256_pass",
    });
    try expectAnyContains(artifact_diff_helper, "binary artifact drift mode", &.{
        "bytes_drift",
        "sha256_drift",
    });
}

test "phase 1 artifact diff contract checker keeps replay catalog anchors" {
    const artifact_diff_contract = try readRepoFile(std.testing.allocator, "scripts/zigux/check-artifact-diff-contract.py");
    defer std.testing.allocator.free(artifact_diff_contract);

    const markers = [_]RequiredMarker{
        .{ .label = "contract base catalog", .needle = "BASE_CONTRACT_CASES" },
        .{ .label = "contract repeat catalog", .needle = "REPEAT_CONTRACT_CASES" },
        .{ .label = "contract self-test catalog", .needle = "SELF_TEST_CASES" },
        .{ .label = "helper self-test replay", .needle = "helper_self_test" },
        .{ .label = "CLI help replay", .needle = "cli_help_output" },
        .{ .label = "missing args replay", .needle = "cli_missing_required_args" },
        .{ .label = "invalid mode replay", .needle = "cli_invalid_mode" },
        .{ .label = "repeat helper self-test replay", .needle = "helper_self_test_repeat" },
        .{ .label = "repeat text replay", .needle = "text_pass_repeat" },
        .{ .label = "catalog shape self-test", .needle = "catalog_shape" },
        .{ .label = "review note marker self-test", .needle = "review_note_marker_round_trip" },
        .{ .label = "contract status line", .needle = "ARTIFACT_DIFF_CONTRACT=pass" },
        .{ .label = "contract case count", .needle = "ARTIFACT_DIFF_CONTRACT_CASE_COUNT" },
        .{ .label = "contract case catalog", .needle = "ARTIFACT_DIFF_CONTRACT_CASES" },
    };
    inline for (markers) |marker| try expectContains(artifact_diff_contract, marker);
}
