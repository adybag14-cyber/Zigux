const std = @import("std");

const Requirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
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
    roadmap_requirement: []const u8,
    anchors: []const []const u8,
    supporting_artifacts: []const []const u8,
    indefinite_c_requirements: []const Requirement,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

fn expectContains(io: std.Io, path: []const u8, snippets: []const []const u8) !void {
    const contents = try std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(contents);

    for (snippets) |snippet| {
        try std.testing.expect(std.mem.indexOf(u8, contents, snippet) != null);
    }
}

test "phase 15 indefinite-C policy manifest records current policy, exception, and blocker evidence" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_indefinite_c_policy.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L15", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("cf59271229b54757ec5e60f73b4ea56ac27f5f9c", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.anchors[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", manifest.supporting_artifacts[3]);

    var saw_source_of_truth = false;
    var saw_recordkeeping = false;
    var saw_allowed_work = false;
    var saw_exception_path = false;
    var saw_reopen_gate = false;
    var saw_reopen_trigger_catalog = false;

    for (manifest.indefinite_c_requirements, 0..) |requirement, i| {
        try std.testing.expect(requirement.id.len > 0);
        try std.testing.expect(requirement.summary.len > 0);
        try std.testing.expect(requirement.required_terms.len >= 2);

        if (std.mem.eql(u8, requirement.id, "indefinite-c-source-of-truth")) {
            saw_source_of_truth = true;
            try std.testing.expectEqualStrings("product source of truth", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("remains in C indefinitely", requirement.required_terms[1]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-recordkeeping")) {
            saw_recordkeeping = true;
            try std.testing.expectEqualStrings("current status bucket", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("requested decision bucket", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("decision record ID", requirement.required_terms[2]);
            try std.testing.expectEqualStrings("owner", requirement.required_terms[3]);
            try std.testing.expectEqualStrings("rollback owner", requirement.required_terms[4]);
            try std.testing.expectEqualStrings("validation gate summary", requirement.required_terms[5]);
            try std.testing.expectEqualStrings("latest blocker disposition", requirement.required_terms[6]);
            try std.testing.expectEqualStrings("evidence archive path", requirement.required_terms[7]);
            try std.testing.expectEqualStrings("retained discussion state", requirement.required_terms[8]);
            try std.testing.expectEqualStrings("parity scorecard link or blocker record", requirement.required_terms[9]);
            try std.testing.expectEqualStrings("explicit non-goals", requirement.required_terms[10]);
            try std.testing.expectEqualStrings("written rationale", requirement.required_terms[11]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-allowed-work")) {
            saw_allowed_work = true;
            try std.testing.expectEqualStrings("explicit stay-in-C outcome", requirement.required_terms[1]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-exception-path")) {
            saw_exception_path = true;
            try std.testing.expectEqualStrings("no silent exception path", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("Architecture Council reopen request", requirement.require