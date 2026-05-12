const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 governance lane sequencing note keeps the lane family split explicit" {
    const note = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md", 32 * 1024);
    defer std.testing.allocator.free(note);

    try expectContains(note, "PHASE15_STATUS=lane_sequencing_note_landed");
    try expectContains(note, "PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-11");
    try expectContains(note, "freeze-map-governance");
    try expectContains(note, "review-process");
    try expectContains(note, "readiness-gate");
    try expectContains(note, "handoff-next-steps");
    try expectContains(note, "shared-summaries");
    try expectContains(note, "Documentation/zigux/phase15-readiness-gate-survey.md");
    try expectContains(note, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    try expectContains(note, "Documentation/zigux/phase15-governance-lane-sequencing.md");
    try expectContains(note, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectContains(note, "zigux/tests/phase15_readiness_gate_manifest.json");
    try expectContains(note, "zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectContains(note, "zigux/tests/phase15_readiness_gate.zig");
    try expectContains(note, "zigux/tests/phase15_parity_scorecard.zig");
    try expectContains(note, "make -C zigux phase15-validate");
    try expectContains(note, "make -C zigux phase15-test");
    try expectContains(note, "make -C zigux phase15");
}

test "phase 15 governance lane sequencing note matches the shared summary follow-up surfaces" {
    const docs_readme = try readRepoFile("Documentation/zigux/README.md", 64 * 1024);
    defer std.testing.allocator.free(docs_readme);

    const review_checklist = try readRepoFile("Documentation/zigux/review-checklist.md", 64 * 1024);
    defer std.testing.allocator.free(review_checklist);

    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 64 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    const tests_readme = try readRepoFile("zigux/tests/README.md", 64 * 1024);
    defer std.testing.allocator.free(tests_readme);

    try expectContains(docs_readme, "Phase 15 notes");
    try expectContains(review_checklist, "Documentation/zigux/phase15-governance-lane-sequencing.md");
    try expectContains(review_checklist, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectContains(review_checklist, "zigux/tests/phase15_readiness_gate_manifest.json");
    try expectContains(scripts_readme, "check-phase15-review-process-handoff.py");
    try expectContains(scripts_readme, "make -C zigux phase15-validate");
    try expectContains(tests_readme, "zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectContains(tests_readme, "zigux/tests/phase15_readiness_gate.zig");
    try expectContains(tests_readme, "make -C zigux phase15-test");
}
