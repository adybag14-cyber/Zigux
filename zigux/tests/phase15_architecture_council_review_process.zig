const std = @import("std");

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
    anchor: []const u8,
    trigger_conditions: []const []const u8,
    required_review_packet_fields: []const []const u8,
    decision_buckets: []const []const u8,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

test "phase 15 architecture council review-process manifest records the bounded governance slice" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L05", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("40aa574db33204bfbb0c972f1de37ad4cb396a77", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirement);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 4), manifest.trigger_conditions.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.required_review_packet_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.decision_buckets.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);

    try std.testing.expectEqualStrings("freeze-map list change", manifest.trigger_conditions[0]);
    try std.testing.expectEqualStrings("requested decision bucket", manifest.required_review_packet_fields[2]);
    try std.testing.expectEqualStrings("keep_in_c", manifest.decision_buckets[0]);
    try std.testing.expectEqualStrings("bounded_dual_implementation", manifest.decision_buckets[2]);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_doc = false;
    var saw_manifest = false;
    var saw_test = false;
    var saw_checklist = false;
    var saw_build = false;
    var saw_parity_followup = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase15-architecture-council-review-process-doc")) {
            saw_doc = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Architecture Council review process") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-architecture-council-review-process-manifest")) {
            saw_manifest = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_architecture_council_review_process_manifest.json", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-architecture-council-review-process-test")) {
            saw_test = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_architecture_council_review_process.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-review-checklist-hook")) {
            saw_checklist = true;
            try std.testing.expectEqualStrings("Documentation/zigux/review-checklist.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-build-gate-review-process")) {
            saw_build = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-parity-scorecard-template")) {
            saw_parity_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/parity-scorecard.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "parity-scorecard") != null or std.mem.indexOf(u8, gap.why_now, "parity scorecard") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 5), landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expect(saw_doc);
    try std.testing.expect(saw_manifest);
    try std.testing.expect(saw_test);
    try std.testing.expect(saw_checklist);
    try std.testing.expect(saw_build);
    try std.testing.expect(saw_parity_followup);
}

test "phase 15 architecture council review-process doc records the required process language" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "## Trigger Conditions") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "## Required Review Packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "## Decision Buckets") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "written rationale") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "parity scorecard link, or an explicit blocker record") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`keep_in_c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`study_only_followup`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`bounded_dual_implementation`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`defer_or_reject`") != null);
}

test "phase 15 review checklist stays aligned with the council review-process hook" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "Architecture Council decision") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "parity scorecard evidence or blocker state explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "Architecture Council review record linked") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "requested decision bucket explicit") != null);
}
