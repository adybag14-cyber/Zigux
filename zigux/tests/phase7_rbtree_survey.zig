const std = @import("std");

const active_lane_key = "P7-L13";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 7 rbtree survey keeps the direct anchor note aligned with repo reality" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const direct_anchor_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-rbtree-direct-anchor-note.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(direct_anchor_note);

    const string_helpers_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-string-helpers-slice.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(string_helpers_slice);

    const string_helpers_test = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_string_helpers.zig",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(string_helpers_test);

    try std.testing.expectEqualStrings("P7-L13", active_lane_key);
    try expectContains(
        direct_anchor_note,
        "Current direct-readback Phase 7 rbtree anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    );
    try expectContains(
        direct_anchor_note,
        "Current directly readable same-lane Phase 7 sibling evidence also includes:",
    );

    for ([_][]const u8{
        "`Documentation/zigux/phase7-string-helpers-slice.md`",
        "`lib/string_helpers.zig`",
        "`zigux/tests/phase7_string_helpers.zig`",
    }) |needle| {
        try expectContains(direct_anchor_note, needle);
    }

    try expectContains(
        direct_anchor_note,
        "Repo-reality warning for the broader Phase 7 rbtree packet:",
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
        try expectContains(direct_anchor_note, needle);
    }

    try expectContains(
        direct_anchor_note,
        "`string_helpers` stays the only directly readable helper implementation packet in this lane today",
    );
    try expectContains(
        direct_anchor_note,
        "`cmdline` stays reviewable through the parked Phase 1 helper packet",
    );
    try expectContains(
        direct_anchor_note,
        "do not present `argv_split` or the broader `rbtree` helper-local slice, checker, manifest, fixture, or shared build-route files as directly readable again until a fresh same-lane reread or republish materializes them on current `master`",
    );
    try expectContains(
        direct_anchor_note,
        "Do not widen this note into broader validator, checker, manifest, fixture, or make-wrapper claims without a fresh same-lane reread of those sibling review surfaces.",
    );

    try expectContains(string_helpers_slice, "`PHASE7_STATUS=starter_landed`");
    try expectContains(string_helpers_slice, "`lib/string_helpers.zig`");
    try expectContains(string_helpers_slice, "`zigux/tests/phase7_string_helpers.zig`");
    try expectContains(string_helpers_slice, "`python3 scripts/zigux/validate-phase7.py`");

    try expectContains(string_helpers_test, "kasprintfStrarray");
    try expectContains(string_helpers_test, "kstrdupQuotable");
}