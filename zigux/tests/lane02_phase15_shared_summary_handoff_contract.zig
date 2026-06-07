const std = @import("std");

const max_doc_bytes = 512 * 1024;

fn readText(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_doc_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "docs root, handoff, and shared gap agree on materialized Phase 15 governance packet" {
    const allocator = std.testing.allocator;

    const docs_readme = try readText(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_readme);
    const handoff = try readText(allocator, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    defer allocator.free(handoff);
    const shared_gap = try readText(allocator, "Documentation/zigux/phase15-shared-summary-gap.md");
    defer allocator.free(shared_gap);

    try expectContains(docs_readme, "Phase 15 notes");
    try expectContains(docs_readme, "`Documentation/zigux/phase15-shared-summary-gap.md`");
    try expectContains(docs_readme, "`Documentation/zigux/phase15-handoff-next-steps-survey.md`");
    try expectContains(docs_readme, "`scripts/zigux/check-phase15-docs-readme-alignment.py`");
    try expectContains(docs_readme, "`scripts/zigux/check-phase15-architecture-council-packet.py`");
    try expectContains(docs_readme, "`scripts/zigux/validate-phase15.py`");

    try expectContains(handoff, "## Current handed-off packet on current master");
    try expectContains(handoff, "`zigux/tests/phase15_build.zig`");
    try expectContains(handoff, "`zigux/tests/phase15_handoff_next_steps.zig`");
    try expectContains(handoff, "`zigux/tests/phase15_readiness_gap_matrix.json`");
    try expectContains(handoff, "`scripts/zigux/check-phase15-blocked-route-recovery.py`");

    try expectContains(shared_gap, "## Materialized Phase 15 governance assets");
    try expectContains(shared_gap, "## Materialized focused companions on current master");
    try expectContains(shared_gap, "`zigux/tests/phase15_build.zig`");
    try expectContains(shared_gap, "`scripts/zigux/check-phase15-architecture-council-packet.py`");
    try expectContains(shared_gap, "`scripts/zigux/validate-phase15.py`");
}

test "freeze map and review checklist keep study-only anchors routed through Phase 15 accounting" {
    const allocator = std.testing.allocator;

    const freeze_map = try readText(allocator, "Documentation/zigux/freeze-map.md");
    defer allocator.free(freeze_map);
    const review_checklist = try readText(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(review_checklist);
    const docs_readme = try readText(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_readme);

    try expectContains(freeze_map, "## Freeze In C Initially");
    try expectContains(freeze_map, "`kernel/sched/core.c`");
    try expectContains(freeze_map, "`mm/page_alloc.c`");
    try expectContains(freeze_map, "`kernel/rcu/tree.c`");
    try expectContains(freeze_map, "`net/core/skbuff.c`");
    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectContains(freeze_map, "`kernel/workqueue.c`");
    try expectContains(freeze_map, "`kernel/trace/ring_buffer.c`");
    try expectContains(freeze_map, "shared reminder surfaces that summarize freeze posture");
    try expectContains(freeze_map, "`Documentation/zigux/phase15-study-only-anchor-accounting.md`");

    try expectContains(review_checklist, "if a shared reminder surface summarizes the study-only freeze-map anchors");
    try expectContains(review_checklist, "`Documentation/zigux/freeze-map.md`");
    try expectContains(review_checklist, "`Documentation/zigux/phase15-study-only-anchor-accounting.md`");
    try expectContains(review_checklist, "`kernel/workqueue.c`");
    try expectContains(review_checklist, "`kernel/trace/ring_buffer.c`");

    try expectContains(docs_readme, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(docs_readme, "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors");
}

test "broader Phase 15 make and shared CI routes remain gap-tracked instead of shipped" {
    const allocator = std.testing.allocator;

    const handoff = try readText(allocator, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    defer allocator.free(handoff);
    const shared_gap = try readText(allocator, "Documentation/zigux/phase15-shared-summary-gap.md");
    defer allocator.free(shared_gap);
    const makefile = try readText(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    const workflow = try readText(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectContains(handoff, "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`");
    try expectContains(handoff, "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`");
    try expectContains(shared_gap, "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`");
    try expectContains(shared_gap, "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`");

    try expectNotContains(makefile, "\nphase15-validate:");
    try expectNotContains(makefile, "\nphase15-test:");
    try expectNotContains(makefile, "\nphase15:");
    try expectNotContains(workflow, "phase15-validate");
    try expectNotContains(workflow, "phase15-test");
}
