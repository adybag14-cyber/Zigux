const std = @import("std");

const active_lane_key = "P7-L13";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 rbtree survey keeps the direct anchor packet aligned with repo reality" {
    const allocator = std.testing.allocator;

    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    const direct_anchor_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    defer allocator.free(direct_anchor_note);

    const string_helpers_slice = try readRepoFile(allocator, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(string_helpers_slice);

    const string_helpers_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(string_helpers_tests);

    const argv_split_helper = try readRepoFile(allocator, "lib/argv_split.zig");
    defer allocator.free(argv_split_helper);

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
        "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone",
    );
    try expectContains(
        tests_readme,
        "leave `cmdline` and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond the directly readable string_helpers packet and the surviving rbtree survey anchor",
    );

    try expectContains(
        direct_anchor_note,
        "Current direct-readback Phase 7 rbtree anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    );
    try expectContains(
        direct_anchor_note,
        "Repo-reality warning for the broader Phase 7 rbtree packet:",
    );
    try expectContains(
        direct_anchor_note,
        "`string_helpers` stays the only directly readable full helper-local Phase 7 packet in this lane today",
    );
    try expectContains(
        direct_anchor_note,
        "`cmdline` stays reviewable through the parked Phase 1 helper packet",
    );
    try expectContains(
        direct_anchor_note,
        "`lib/argv_split.zig` is directly readable again on current `master`, but the dedicated Phase 7 `argv_split` slice, survey, manifest, and shared build-route packet still need a fresh same-lane reread or republish before they can count as a full helper-local review surface",
    );
    try expectContains(
        direct_anchor_note,
        "do not present the broader `argv_split` review packet or the broader `rbtree` helper-local slice, checker, manifest, fixture, or shared build-route files as directly readable again until a fresh same-lane reread or republish materializes them on current `master`",
    );

    try expectContains(argv_split_helper, "pub const ArgvSplitResult = struct");
    try expectContains(argv_split_helper, "pub fn argvSplit");

    try expectContains(string_helpers_slice, "PHASE7_STATUS=starter_landed");
    try expectContains(string_helpers_slice, "`lib/string_helpers.zig`");
    try expectContains(string_helpers_slice, "`zigux/tests/phase7_string_helpers.zig`");
    try expectContains(string_helpers_slice, "expanded starter packet");
    try expectContains(string_helpers_slice, "quoted cmdline duplication that collapses trailing NULs, replaces inter-argument NULs with spaces");

    try expectContains(
        string_helpers_tests,
        "phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly",
    );
    try expectContains(
        string_helpers_tests,
        "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators",
    );
}
