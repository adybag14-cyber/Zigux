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

test "phase 15 indefinite-C policy manifest records the roadmap gap closure" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_indefinite_c_policy.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("5ef3897e33afaf014a686206f368ebd52c433b2c", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.anchors[0]);
    try std.testing.expectEqualStrings("mm/page_alloc.c", manifest.anchors[1]);
    try std.testing.expectEqualStrings("kernel/rcu/tree.c", manifest.anchors[2]);
    try std.testing.expectEqualStrings("net/core/skbuff.c", manifest.anchors[3]);

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_note = false;
    var saw_manifest = false;
    var saw_test = false;
    var saw_build = false;
    var saw_followup = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-policy-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remains in C indefinitely") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-policy-manifest")) {
            saw_manifest = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_indefinite_c_policy.json", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-policy-test")) {
            saw_test = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_indefinite_c_policy.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-build-gate-indefinite-c-policy")) {
            saw_build = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-field-sync-followup")) {
            saw_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase15-deep-core-status-change-blocker")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 4), landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_manifest);
    try std.testing.expect(saw_test);
    try std.testing.expect(saw_build);
    try std.testing.expect(saw_followup);
    try std.testing.expect(saw_blocker);
}

test "phase 15 indefinite-C policy doc records the current long-term C-owned posture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const policy_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(policy_doc);

    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "## When the indefinite-C policy applies") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "product source of truth") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "explicit stay-in-C outcome") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "## Reopen conditions") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "new bounded seam inventory") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "Architecture Council review request") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "decision record ID") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "latest blocker disposition") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "evidence archive path") != null);
    try std.testing.expect(std.mem.indexOf(u8, policy_doc, "replay command") != null);
}

test "phase 15 indefinite-C policy stays aligned with freeze-map, review-process, scorecard, and archive artifacts" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_indefinite_c_policy.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const policy_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(policy_doc);

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(freeze_map);

    const review_process = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(review_process);

    const scorecard = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-parity-scorecard.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(scorecard);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "product source of truth") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "keep the code in C and record the blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "if the council keeps the code in C") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "latest blocker disposition") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard, "explicit stay-in-C outcome") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard, "Documentation/zigux/phase15-evidence-archives/") != null);
    try std.testing.expect(std.mem.indexOf(u8, scorecard, "## Reserved Decision Record Templates") != null);

    for (parsed.value.supporting_artifacts) |artifact| {
        try std.testing.expect(std.mem.indexOf(u8, policy_doc, artifact) != null);
    }

    for (parsed.value.indefinite_c_requirements) |requirement| {
        try std.testing.expect(requirement.id.len > 0);
        try std.testing.expect(requirement.summary.len > 0);
        try std.testing.expect(requirement.required_terms.len > 0);

        for (requirement.required_terms) |term| {
            try std.testing.expect(std.mem.indexOf(u8, policy_doc, term) != null);
        }
    }
}
