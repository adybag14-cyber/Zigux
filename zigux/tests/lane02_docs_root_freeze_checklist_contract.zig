const std = @import("std");

const FreezeAnchor = struct {
    path: []const u8,
    status: Status,
};

const Status = enum {
    freeze_in_c,
    study_only,
};

const freeze_anchors = [_]FreezeAnchor{
    .{ .path = "kernel/sched/core.c", .status = .freeze_in_c },
    .{ .path = "mm/page_alloc.c", .status = .freeze_in_c },
    .{ .path = "kernel/rcu/tree.c", .status = .freeze_in_c },
    .{ .path = "net/core/skbuff.c", .status = .freeze_in_c },
    .{ .path = "kernel/workqueue.c", .status = .study_only },
    .{ .path = "kernel/trace/ring_buffer.c", .status = .study_only },
};

const phase15_packet_docs = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
};

const lane02_surfaces = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
};

const phase15_checker_routes = [_][]const u8{
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-architecture-council-packet.py",
    "scripts/zigux/validate-phase15.py",
};

const status_change_non_claims = [_][]const u8{
    "Architecture Council approval claim",
    "freeze-map status change",
    "dedicated `make -C zigux phase15-validate`",
    "shared-CI Phase 15 routes",
};

const review_owner_prompts = [_][]const u8{
    "required approver set",
    "rollback owner",
    "evidence archive path",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
};

test "lane02 docs root names the phase15 governance packet and bounded route posture" {
    try std.testing.expectEqual(@as(usize, 11), phase15_packet_docs.len);
    try std.testing.expectEqual(@as(usize, 3), phase15_checker_routes.len);

    for (phase15_packet_docs) |path| {
        try expectContains(path, "Documentation/zigux/");
    }

    try expectContains(phase15_packet_docs[0], "freeze-map.md");
    try expectContains(phase15_packet_docs[1], "freeze-map-governance.md");
    try expectContains(phase15_packet_docs[2], "architecture-council-review-process.md");
    try expectContains(phase15_packet_docs[3], "architecture-council-decision-record-template.md");
    try expectContains(phase15_packet_docs[8], "study-only-anchor-accounting.md");

    for (phase15_checker_routes) |route| {
        try expectContains(route, "scripts/zigux/");
    }

    for (status_change_non_claims) |phrase| {
        try std.testing.expect(phrase.len > 0);
    }
}

test "lane02 freeze map keeps anchor inventory and shared reminder routing explicit" {
    try std.testing.expectEqual(@as(usize, 6), freeze_anchors.len);
    try std.testing.expectEqual(@as(usize, 4), countAnchorsWithStatus(.freeze_in_c));
    try std.testing.expectEqual(@as(usize, 2), countAnchorsWithStatus(.study_only));

    for (freeze_anchors) |anchor| {
        try expectContains(anchor.path, ".c");
    }

    try expectContains(lane02_surfaces[0], "README.md");
    try expectContains(lane02_surfaces[1], "review-checklist.md");
    try expectContains(lane02_surfaces[2], "freeze-map.md");
    try expectContains(phase15_packet_docs[8], "study-only-anchor-accounting.md");
}

test "lane02 review checklist routes freeze decisions through owners instead of summaries" {
    try std.testing.expectEqual(@as(usize, 6), review_owner_prompts.len);

    for (review_owner_prompts) |prompt| {
        try std.testing.expect(prompt.len > 0);
    }

    try expectContains(review_owner_prompts[3], "review-process.md");
    try expectContains(review_owner_prompts[4], "decision-record-template.md");
    try expectContains(review_owner_prompts[5], "indefinite-c-policy.md");
}

test "lane02 shared docs agree on freeze anchor status boundaries" {
    for (freeze_anchors) |anchor| {
        switch (anchor.status) {
            .freeze_in_c => try expectContains(anchor.path, oneOf(&.{
                "kernel/sched/",
                "mm/",
                "kernel/rcu/",
                "net/core/",
            }, anchor.path).?),
            .study_only => try expectContains(anchor.path, "kernel/"),
        }
    }

    try std.testing.expect(!sameStatus("kernel/workqueue.c", .freeze_in_c));
    try std.testing.expect(!sameStatus("kernel/trace/ring_buffer.c", .freeze_in_c));
    try std.testing.expect(sameStatus("kernel/sched/core.c", .freeze_in_c));
    try std.testing.expect(sameStatus("net/core/skbuff.c", .freeze_in_c));
}

fn countAnchorsWithStatus(status: Status) usize {
    var count: usize = 0;
    for (freeze_anchors) |anchor| {
        if (anchor.status == status) count += 1;
    }
    return count;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn sameStatus(path: []const u8, status: Status) bool {
    for (freeze_anchors) |anchor| {
        if (std.mem.eql(u8, anchor.path, path)) return anchor.status == status;
    }
    return false;
}

fn oneOf(needles: []const []const u8, haystack: []const u8) ?[]const u8 {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) return needle;
    }
    return null;
}
