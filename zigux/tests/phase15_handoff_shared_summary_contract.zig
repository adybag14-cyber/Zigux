const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase 15 handoff note and shared-summary gap keep materialized governance packet explicit" {
    const handoff = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 64 * 1024);
    defer std.testing.allocator.free(handoff);

    const shared_summary = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 48 * 1024);
    defer std.testing.allocator.free(shared_summary);

    try expectContains(handoff, "PHASE15_STATUS=handoff_next_steps_survey_landed");
    try expectContains(handoff, "PHASE15_LANE_KEY=P15-L12");
    try expectContains(handoff, "PHASE15_SLICE=existing_governance_packet_handoff_inventory");
    try expectContains(handoff, "current-master-readback-2026-05-29");
    try expectContains(handoff, "Current handed-off packet on current master");
    try expectContains(handoff, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectContains(handoff, "zigux/tests/phase15_handoff_next_steps.zig");
    try expectContains(handoff, "zigux/tests/phase15_readiness_gap_matrix.json");
    try expectContains(handoff, "zigux/tests/phase15_build.zig");
    try expectContains(handoff, "scripts/zigux/check-phase15-blocked-route-recovery.py");
    try expectContains(handoff, "scripts/zigux/validate-phase15.py");

    try expectContains(shared_summary, "PHASE15_STATUS=shared_summary_gap_recorded");
    try expectContains(shared_summary, "PHASE15_SLICE=materialized-governance-packet-truthfulness-refresh");
    try expectContains(shared_summary, "Materialized focused companions on current master");
    try expectContains(shared_summary, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectContains(shared_summary, "zigux/tests/phase15_handoff_next_steps.zig");
    try expectContains(shared_summary, "scripts/zigux/check-phase15-handoff-note-alignment.py");
    try expectContains(shared_summary, "scripts/zigux/check-phase15-shared-summary-gap.py");
    try expectContains(shared_summary, "zigux/tests/phase15_build.zig");

    try expectOrdered(handoff, "Current handed-off packet on current master", "Roadmap-backed open handoff gaps");
    try expectOrdered(shared_summary, "Materialized focused companions on current master", "Still-missing broader wrapper and shared-CI route companions on current master");
}

test "handoff and shared-summary surfaces keep blocked wrapper and CI routes gap-tracked" {
    const handoff = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 64 * 1024);
    defer std.testing.allocator.free(handoff);

    const shared_summary = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 48 * 1024);
    defer std.testing.allocator.free(shared_summary);

    const route_gap_markers = [_][]const u8{
        "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
        "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`",
        "no Architecture Council approval is currently recorded for a freeze-map status change",
    };

    for (route_gap_markers) |marker| {
        try expectContains(handoff, marker);
    }

    try expectContains(shared_summary, "Still-missing broader wrapper and shared-CI route companions on current master");
    try expectContains(shared_summary, "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`");
    try expectContains(shared_summary, "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`");
    try expectContains(shared_summary, "do not treat the parked make-route vocabulary or shared-CI route vocabulary as shipped evidence until direct current-tree reads recover them");
    try expectContains(shared_summary, "do not treat present focused companions as Architecture Council approval or direct deep-core delivery evidence by themselves");
}

test "docs root checklist and freeze map route shared handoff posture without changing anchor status" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 96 * 1024);
    defer std.testing.allocator.free(docs_root);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 80 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 48 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(docs_root, "Phase 15 notes");
    try expectContains(docs_root, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-shared-summary-gap.md");
    try expectContains(docs_root, "no Architecture Council approval claim posture");
    try expectContains(docs_root, "make -C zigux phase15-validate");
    try expectContains(docs_root, "remain blocked route vocabulary rather than shipped replay paths");

    try expectContains(review_checklist, "does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?");
    try expectContains(review_checklist, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(review_checklist, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(review_checklist, "Documentation/zigux/phase15-indefinite-c-policy.md");

    try expectContains(freeze_map, "Freeze In C Initially");
    try expectContains(freeze_map, "`kernel/sched/core.c`");
    try expectContains(freeze_map, "`mm/page_alloc.c`");
    try expectContains(freeze_map, "`kernel/rcu/tree.c`");
    try expectContains(freeze_map, "`net/core/skbuff.c`");
    try expectContains(freeze_map, "Study / Boundary Only");
    try expectContains(freeze_map, "`kernel/workqueue.c`");
    try expectContains(freeze_map, "`kernel/trace/ring_buffer.c`");
    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry");
}
