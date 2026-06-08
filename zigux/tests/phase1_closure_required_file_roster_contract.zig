const std = @import("std");
const testing = std.testing;

fn readRepoFile(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn between(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingStartMarker;
    const after_start = haystack[start_index + start.len ..];
    const end_index = std.mem.indexOf(u8, after_start, end) orelse return error.MissingEndMarker;
    return after_start[0..end_index];
}

fn markerValue(source: []const u8, marker: []const u8) ![]const u8 {
    const marker_index = std.mem.indexOf(u8, source, marker) orelse return error.MissingMarker;
    const after_marker = source[marker_index..];
    const line_end = std.mem.indexOfScalar(u8, after_marker, '\n') orelse after_marker.len;
    return after_marker[0..line_end];
}

test "validator required-file roster keeps current closure inputs explicit" {
    const validator_source = try readRepoFile("scripts/zigux/validate-phase1-closure.py");
    defer testing.allocator.free(validator_source);

    const required_files = try between(validator_source, "REQUIRED_FILES = (", "EXPECTED_HELPERS = [");

    const expected_required = [_][]const u8{
        "PHASE1_CLOSURE_REL",
        "PHASE1_LANE_NOTE_REL",
        "DOCS_ROOT_REL",
        "REVIEW_CHECKLIST_REL",
        "SCRIPTS_README_REL",
        "DIRECT_OWNER_CHECKER_REL",
        "DIRECT_ANCHOR_MANIFEST_GATE_REL",
        "ROUTE_SUMMARY_CHECKER_REL",
        "BENCH_CHECKER_REL",
        "SHARED_REMINDER_CHECKER_REL",
        "TESTS_README_REL",
        "TESTS_BUILD_REL",
        "PHASE1_HELPERS_REPLAY_REL",
        "PHASE1_HELPERS_BUILD_REL",
        "PHASE1_SMOKE_REL",
        "WORKFLOW_REL",
        "MANIFEST_REL",
        "ZIGUX_MAKEFILE_REL",
        "BITMAP_HELPER_REL",
        "FIND_BIT_HELPER_REL",
        "RBTREE_HELPER_REL",
        "STRING_HELPER_REL",
    };

    for (expected_required) |required_name| {
        try requireContains(required_files, required_name);
    }

    try requireOrder(required_files, "PHASE1_CLOSURE_REL", "PHASE1_LANE_NOTE_REL");
    try requireOrder(required_files, "SHARED_REMINDER_CHECKER_REL", "TESTS_README_REL");
    try requireOrder(required_files, "ZIGUX_MAKEFILE_REL", "BITMAP_HELPER_REL");
    try requireOrder(required_files, "BITMAP_HELPER_REL", "STRING_HELPER_REL");
}

test "broader gap packet stays out of the required-file tuple" {
    const validator_source = try readRepoFile("scripts/zigux/validate-phase1-closure.py");
    defer testing.allocator.free(validator_source);
    const closure_note = try readRepoFile("Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure_note);
    const tests_readme = try readRepoFile("zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);

    const required_files = try between(validator_source, "REQUIRED_FILES = (", "EXPECTED_HELPERS = [");

    try requireAbsent(required_files, "validate-phase1.py");
    try requireAbsent(required_files, "check-phase1-parity.py");
    try requireAbsent(required_files, "phase1_bench.zig");
    try requireAbsent(required_files, "phase1_bench_expectations.json");
    try requireAbsent(required_files, "phase1_helpers_c_harness.c");

    try requireContains(validator_source, "gap_packet");
    try requireContains(validator_source, "PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c");
    try requireContains(closure_note, "broader closure-stack references rather than active current reminder-packet proof");
    try requireContains(tests_readme, "broader Phase 1 closure companions stay outside the narrow direct-readback packet");
}

test "helper roster split remains thirteen total with nine shared and four direct anchors" {
    const validator_source = try readRepoFile("scripts/zigux/validate-phase1-closure.py");
    defer testing.allocator.free(validator_source);

    const expected_helpers = try between(validator_source, "EXPECTED_HELPERS = [", "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    const shared_helpers = try between(validator_source, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [", "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    const direct_helpers = try between(validator_source, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [", "EXPECTED_LANE_RULE_SUMMARY = (");

    try testing.expectEqual(@as(usize, 13), std.mem.count(u8, expected_helpers, "tools/lib/"));
    try testing.expectEqual(@as(usize, 9), std.mem.count(u8, shared_helpers, "tools/lib/"));
    try testing.expectEqual(@as(usize, 4), std.mem.count(u8, direct_helpers, "tools/lib/"));

    try requireContains(shared_helpers, "tools/lib/list_sort.zig");
    try requireAbsent(shared_helpers, "tools/lib/bitmap.zig");
    try requireContains(direct_helpers, "tools/lib/bitmap.zig");
    try requireContains(direct_helpers, "tools/lib/find_bit.zig");
    try requireContains(direct_helpers, "tools/lib/rbtree.zig");
    try requireContains(direct_helpers, "tools/lib/string.zig");

    try requireContains(validator_source, "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above");
    try requireContains(validator_source, "Do not reopen Phase 1 by batching helpers across those two sets in one lane");
}

test "current reminder marker stays narrower than live validator inputs" {
    const validator_source = try readRepoFile("scripts/zigux/validate-phase1-closure.py");
    defer testing.allocator.free(validator_source);
    const closure_note = try readRepoFile("Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure_note);
    const tests_readme = try readRepoFile("zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);

    const reminder_marker = try markerValue(validator_source, "PHASE1_CURRENT_REMINDER_PACKET=");

    try requireContains(reminder_marker, "Documentation/zigux/phase1-closure.md");
    try requireContains(reminder_marker, "scripts/zigux/validate-phase1-closure.py");
    try requireContains(reminder_marker, "zigux/tests/fixtures/phase1_helper_manifest.json");
    try requireContains(reminder_marker, ".github/workflows/zigux-bootstrap.yml");

    try requireAbsent(reminder_marker, "zigux/Makefile");
    try requireAbsent(reminder_marker, "tools/lib/bitmap.zig");
    try requireAbsent(reminder_marker, "tools/lib/find_bit.zig");
    try requireAbsent(reminder_marker, "tools/lib/rbtree.zig");
    try requireAbsent(reminder_marker, "tools/lib/string.zig");

    try requireContains(closure_note, "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md");
    try requireContains(tests_readme, "current direct-readback Phase 1 reminder packet");
    try requireContains(tests_readme, "older Phase 1 wrapper names remain historical packet members rather than active tests-root proof");
}
