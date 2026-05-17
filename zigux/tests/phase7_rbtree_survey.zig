const std = @import("std");

const active_lane_key = "P7-L13";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 rbtree survey keeps the direct tests-root anchor aligned with repo reality" {
    const allocator = std.testing.allocator;

    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);
    const string_helpers_slice = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(string_helpers_slice);
    const string_helpers_test = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(string_helpers_test);
    const string_helpers_survey = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_survey.zig");
    defer allocator.free(string_helpers_survey);
    const string_helpers_manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(string_helpers_manifest);

    try std.testing.expectEqualStrings("P7-L13", active_lane_key);

    try expectContains(
        tests_readme,
        "current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    );
    try expectContains(
        tests_readme,
        "repo-reality warning for the broader Phase 7 rbtree packet:",
    );
    for ([_][]const u8{
        "`Documentation/zigux/phase7-rbtree-slice.md`",
        "`scripts/zigux/check-phase7-rbtree-parity.py`",
        "`zigux/tests/phase7_rbtree.zig`",
        "`zigux/tests/phase7_rbtree_manifest.json`",
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
        "`zigux/tests/phase7_build.zig`",
    }) |needle| {
        try expectContains(tests_readme, needle);
    }
    try expectContains(
        tests_readme,
        "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor",
    );

    try expectContains(string_helpers_slice, "`PHASE7_STATUS=starter_landed`");
    try expectContains(string_helpers_slice, "`PHASE7_SLICE=string-helpers-runtime-leaf`");
    try expectContains(string_helpers_slice, "`lib/string_helpers.zig`");
    try expectContains(string_helpers_slice, "`zigux/tests/phase7_string_helpers.zig`");
    try expectContains(string_helpers_slice, "`zigux/tests/phase7_string_helpers_survey.zig`");
    try expectContains(string_helpers_slice, "`zigux/tests/phase7_string_helpers_manifest.json`");
    try expectContains(string_helpers_slice, "`zigux/tests/phase7_string_helpers_sample_boundary.zig`");
    try expectContains(string_helpers_slice, "do not count `scripts/zigux/validate-phase7.py`");
    try expectContains(string_helpers_slice, "do not count `zigux/tests/phase7_build.zig`");
    try expectContains(string_helpers_slice, "unless a fresh same-family reread proves those broader shared-control reminders are directly readable again on current `master`.");
    try expectNotContains(string_helpers_slice, "`python3 scripts/zigux/validate-phase7.py`");

    try expectContains(string_helpers_test, "kasprintfStrarray");
    try expectContains(string_helpers_test, "kstrdupQuotable");
    try expectContains(string_helpers_test, "phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent");

    try expectContains(
        string_helpers_survey,
        "phase 7 string helpers survey keeps the expanded starter packet truthful",
    );
    try expectContains(
        string_helpers_survey,
        "phase 7 string helper boundary stays on sample-boundary surfaces only",
    );
    try expectContains(
        string_helpers_survey,
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    );

    try expectContains(string_helpers_manifest, "\"current_master_state\": \"expanded_starter_packet\"");
    try expectContains(string_helpers_manifest, "\"kstrdupQuotable\"");
    try expectContains(
        string_helpers_manifest,
        "\"next_bounded_step\": \"Leave the current quotable helper packet parked unless a fresh reread finds helper-local drift across the slice note, helper-local manifest, dedicated survey, or dedicated no-string-sample boundary replay; if that packet stays aligned, the next same-lane reopen can decide whether `kstrdup_quotable_cmdline()` belongs in the same helper-local packet without widening into shared-control or file-path semantics.\"",
    );
}
