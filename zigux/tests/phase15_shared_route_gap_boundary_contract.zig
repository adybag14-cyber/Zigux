const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "docs root and freeze map keep Phase 15 route gaps distinct from governance evidence" {
    const docs_root = try readRepoFile("Documentation/zigux/README.md", 192 * 1024);
    defer std.testing.allocator.free(docs_root);

    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(docs_root, "Documentation/zigux/phase15-shared-summary-gap.md");
    try expectContains(docs_root, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(docs_root, "scripts/zigux/check-phase15-docs-readme-alignment.py");
    try expectContains(docs_root, "scripts/zigux/check-phase15-architecture-council-packet.py");
    try expectContains(docs_root, "scripts/zigux/validate-phase15.py");
    try expectContains(docs_root, "any claim that dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, or shared-CI Phase 15 routes are already shipped on current `master`");

    try expectContains(freeze_map, "shared Phase 15 handoff and gap notes");
    try expectContains(freeze_map, "landed governance evidence");
    try expectContains(freeze_map, "still-missing dedicated `phase15*` wrapper routes and shared-CI companions");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
}

test "shared summary and handoff notes preserve the missing-wrapper boundary" {
    const shared_summary_gap = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 96 * 1024);
    defer std.testing.allocator.free(shared_summary_gap);

    const handoff_note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 96 * 1024);
    defer std.testing.allocator.free(handoff_note);

    try expectContains(shared_summary_gap, "Materialized focused companions on current master");
    try expectContains(shared_summary_gap, "zigux/tests/phase15_build.zig");
    try expectContains(shared_summary_gap, "scripts/zigux/validate-phase15.py");
    try expectContains(shared_summary_gap, "Still-missing broader wrapper and shared-CI route companions on current master");
    try expectContains(shared_summary_gap, "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`");
    try expectContains(shared_summary_gap, "do not treat the parked make-route vocabulary or shared-CI route vocabulary as shipped evidence");
    try expectContains(shared_summary_gap, "an Architecture Council approval workflow implementation");
    try expectContains(shared_summary_gap, "a freeze-map status change for any deep-core anchor");

    try expectContains(handoff_note, "zigux/tests/phase15_build.zig");
    try expectContains(handoff_note, "The dedicated validator");
    try expectContains(handoff_note, "the broader wrapper-route and shared-CI follow-through should only reopen when fresh drift actually appears");
    try expectContains(handoff_note, "that the broader dedicated `phase15*` wrapper routes or shared-CI route are already shipped on current `master`");
}

test "review and scripts roots keep direct companions visible without approval claims" {
    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 192 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 128 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    try expectContains(review_checklist, "required approver set");
    try expectContains(review_checklist, "rollback owner");
    try expectContains(review_checklist, "evidence archive path");
    try expectContains(review_checklist, "trigger-specific evidence refresh");

    try expectContains(scripts_readme, "scripts/zigux/validate-phase15.py");
    try expectContains(scripts_readme, "zigux/tests/phase15_build.zig");
    try expectContains(scripts_readme, "the broader dedicated `phase15*` wrapper and shared-CI companions still stay blocked");
    try expectContains(scripts_readme, "it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`");
    try expectContains(scripts_readme, "no dedicated Phase 15 validate, test, or aggregate route");
    try expectContains(scripts_readme, "no Architecture Council approval is currently recorded for a freeze-map status change");
}
