const std = @import("std");

const active_lane_key = "P7-Y05";

const SurveySummary = struct {
    rbtree_c_lines: usize,
    preexisting_phase7_test_files: usize,
    preexisting_phase7_build_present: bool,
    preexisting_phase7_doc_present: bool,
    preexisting_phase7_helper_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 7 rbtree survey manifest records the landed runtime leaf surface and committed parity fixture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_rbtree_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-rbtree-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const validate_phase7 = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/validate-phase7.py",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(validate_phase7);

    const helper_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_rbtree.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(helper_tests);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings(active_lane_key, manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("7361ac51374149a96b7a7a2c6ea3c995d8cc1231", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.survey_summary.rbtree_c_lines >= 600);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expect(manifest.gaps.len >= 6);

    var starter_landed_count: usize = 0;
    var saw_helper = false;
    var saw_survey_gate = false;
    var saw_parity_fixture = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-helper")) {
            saw_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/rbtree.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase7_rbtree_survey.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-parity-fixture-layer")) {
            saw_parity_fixture = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/fixtures/phase7_rbtree.json", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try expectContains(slice_note, "PHASE7_LANE_KEY=P7-Y05");
    try expectContains(slice_note, "erase-and-detach ownership reset via `eraseInit()`");
    try expectContains(slice_note, "detached-node clearing semantics");
    try expectContains(validate_phase7, "\"scripts/zigux/check-phase7-rbtree-parity.py\",");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_rbtree.zig\",");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_rbtree_survey.zig\",");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_rbtree_manifest.json\",");
    try expectContains(validate_phase7, "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test");
    try expectContains(validate_phase7, "python3 scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(helper_tests, "phase 7 rbtree eraseInit detaches erased nodes and keeps traversal stable");
    try expectContains(helper_tests, "phase 7 rbtree detached nodes stay non-empty until callers clear them");
    try expectContains(helper_tests, "phase 7 rbtree clearNode marks detached nodes as empty");

    try std.testing.expectEqual(manifest.gaps.len, starter_landed_count);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_parity_fixture);
}
