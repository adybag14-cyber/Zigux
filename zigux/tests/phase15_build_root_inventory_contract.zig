const std = @import("std");

const Phase15BuildTarget = struct {
    step_name: []const u8,
    root_source_file: []const u8,
    governance_surface: []const u8,
};

const expected_targets = [_]Phase15BuildTarget{
    .{
        .step_name = "phase15-freeze-map-governance",
        .root_source_file = "phase15_freeze_map_governance.zig",
        .governance_surface = "Documentation/zigux/freeze-map.md",
    },
    .{
        .step_name = "phase15-architecture-council-review-process",
        .root_source_file = "phase15_architecture_council_review_process.zig",
        .governance_surface = "Documentation/zigux/review-checklist.md",
    },
    .{
        .step_name = "phase15-architecture-council-decision-index",
        .root_source_file = "phase15_architecture_council_decision_index.zig",
        .governance_surface = "Documentation/zigux/phase15-architecture-council-decision-index.md",
    },
    .{
        .step_name = "phase15-governance-lane-sequencing",
        .root_source_file = "phase15_governance_lane_sequencing.zig",
        .governance_surface = "Documentation/zigux/phase15-governance-lane-sequencing.md",
    },
    .{
        .step_name = "phase15-parity-scorecard",
        .root_source_file = "phase15_parity_scorecard.zig",
        .governance_surface = "Documentation/zigux/phase15-parity-scorecard.md",
    },
    .{
        .step_name = "phase15-indefinite-c-policy",
        .root_source_file = "phase15_indefinite_c_policy.zig",
        .governance_surface = "Documentation/zigux/phase15-indefinite-c-policy.md",
    },
    .{
        .step_name = "phase15-handoff-next-steps",
        .root_source_file = "phase15_handoff_next_steps.zig",
        .governance_surface = "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    },
    .{
        .step_name = "phase15-indefinite-c-lane-owner-alignment",
        .root_source_file = "phase15_indefinite_c_lane_owner_alignment.zig",
        .governance_surface = "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    },
    .{
        .step_name = "phase15-readiness-gate",
        .root_source_file = "phase15_readiness_gate.zig",
        .governance_surface = "Documentation/zigux/phase15-readiness-gate-survey.md",
    },
};

const blocked_shared_routes = [_][]const u8{
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
};

fn readBuildRoot() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |found| {
        count += 1;
        offset += found + needle.len;
    }
    return count;
}

test "phase 15 build root keeps the shared governance roster explicit" {
    const build_root = try readBuildRoot();
    defer std.testing.allocator.free(build_root);

    try expectContains(build_root, "const phase15_targets = [_]Phase15Target{");
    try expectContains(build_root, "Run the shared Phase 15 governance test packet");

    for (expected_targets) |target| {
        try expectContains(build_root, target.step_name);
        try expectContains(build_root, target.root_source_file);
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(build_root, target.step_name));
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(build_root, target.root_source_file));
    }

    try std.testing.expectEqual(@as(usize, expected_targets.len), countOccurrences(build_root, ".step_name = \"phase15-"));
    try std.testing.expectEqual(@as(usize, expected_targets.len), countOccurrences(build_root, ".root_source_file = \"phase15_"));
}

test "phase 15 build inventory names the docs checklist and freeze-map surfaces" {
    try std.testing.expectEqual(@as(usize, 9), expected_targets.len);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", expected_targets[0].governance_surface);
    try std.testing.expectEqualStrings("Documentation/zigux/review-checklist.md", expected_targets[1].governance_surface);

    var saw_freeze_map = false;
    var saw_review_checklist = false;
    var saw_study_only_accounting = false;
    var saw_readiness = false;

    for (expected_targets) |target| {
        saw_freeze_map = saw_freeze_map or std.mem.eql(u8, target.governance_surface, "Documentation/zigux/freeze-map.md");
        saw_review_checklist = saw_review_checklist or std.mem.eql(u8, target.governance_surface, "Documentation/zigux/review-checklist.md");
        saw_study_only_accounting = saw_study_only_accounting or std.mem.eql(u8, target.governance_surface, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
        saw_readiness = saw_readiness or std.mem.eql(u8, target.governance_surface, "Documentation/zigux/phase15-readiness-gate-survey.md");
    }

    try std.testing.expect(saw_freeze_map);
    try std.testing.expect(saw_review_checklist);
    try std.testing.expect(saw_study_only_accounting);
    try std.testing.expect(saw_readiness);
}

test "phase 15 build-root inventory does not promote blocked shared wrapper routes" {
    const build_root = try readBuildRoot();
    defer std.testing.allocator.free(build_root);

    for (blocked_shared_routes) |route| {
        try std.testing.expect(std.mem.indexOf(u8, build_root, route) == null);
    }

    try expectContains(build_root, "phase15-readiness-gate");
    try expectContains(build_root, "phase15_indefinite_c_lane_owner_alignment.zig");
}
