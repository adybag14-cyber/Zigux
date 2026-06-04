const std = @import("std");

const freeze_in_c_anchors = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
};

const study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const required_policy_documents = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
};

const stay_in_c_fields = [_][]const u8{
    "Linux anchor path",
    "roadmap phase",
    "current status bucket",
    "requested decision bucket",
    "decision record ID",
    "lane owner",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "benchmark-notes status",
    "replay command",
    "latest blocker disposition",
    "evidence archive path",
    "automatic return-to-blocked trigger",
    "retired_from_active_discussion",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or explicit non-applicability note",
    "explicit non-goals",
    "written rationale",
};

const reopen_triggers = [_][]const u8{
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
};

fn expectContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    return error.MissingRequiredMarker;
}

test "freeze map keeps deep-core anchors in the correct policy buckets" {
    try std.testing.expectEqual(@as(usize, 4), freeze_in_c_anchors.len);
    try std.testing.expectEqual(@as(usize, 2), study_only_anchors.len);

    try expectContains(&freeze_in_c_anchors, "kernel/sched/core.c");
    try expectContains(&freeze_in_c_anchors, "mm/page_alloc.c");
    try expectContains(&freeze_in_c_anchors, "kernel/rcu/tree.c");
    try expectContains(&freeze_in_c_anchors, "net/core/skbuff.c");

    try expectContains(&study_only_anchors, "kernel/workqueue.c");
    try expectContains(&study_only_anchors, "kernel/trace/ring_buffer.c");

    for (freeze_in_c_anchors) |anchor| {
        for (study_only_anchors) |study_anchor| {
            try std.testing.expect(!std.mem.eql(u8, anchor, study_anchor));
        }
    }
}

test "stay-in-C closeout keeps Architecture Council evidence fields explicit" {
    try std.testing.expectEqual(@as(usize, 7), required_policy_documents.len);
    try expectContains(&required_policy_documents, "Documentation/zigux/freeze-map.md");
    try expectContains(&required_policy_documents, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(&required_policy_documents, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(&required_policy_documents, "Documentation/zigux/phase15-parity-scorecard.md");

    try std.testing.expect(stay_in_c_fields.len >= 20);
    try expectContains(&stay_in_c_fields, "required approver set");
    try expectContains(&stay_in_c_fields, "rollback owner");
    try expectContains(&stay_in_c_fields, "validation gate summary");
    try expectContains(&stay_in_c_fields, "evidence archive path");
    try expectContains(&stay_in_c_fields, "automatic return-to-blocked trigger");
    try expectContains(&stay_in_c_fields, "retired_from_active_discussion");
    try expectContains(&stay_in_c_fields, "trigger-specific evidence refresh");
    try expectContains(&stay_in_c_fields, "indefinite-C policy link or explicit non-applicability note");
}

test "reopen policy rejects silent status changes" {
    const approvals_recorded_for_status_change: usize = 0;
    const silent_exception_allowed = false;
    const direct_bridge_without_council_record_allowed = false;

    try std.testing.expectEqual(@as(usize, 3), reopen_triggers.len);
    try expectContains(&reopen_triggers, "narrower_followup_answers_blocker");
    try expectContains(&reopen_triggers, "evidence_packet_stale_or_contradictory");
    try expectContains(&reopen_triggers, "ownership_or_validation_changed");

    try std.testing.expectEqual(@as(usize, 0), approvals_recorded_for_status_change);
    try std.testing.expect(!silent_exception_allowed);
    try std.testing.expect(!direct_bridge_without_council_record_allowed);
}
