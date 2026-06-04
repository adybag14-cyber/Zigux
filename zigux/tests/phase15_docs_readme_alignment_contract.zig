const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "docs README keeps the landed Phase 15 reminder roster aligned with its checker" {
    const docs_readme = try readRepoFile("Documentation/zigux/README.md", 128 * 1024);
    defer std.testing.allocator.free(docs_readme);

    const checker = try readRepoFile("scripts/zigux/check-phase15-docs-readme-alignment.py", 24 * 1024);
    defer std.testing.allocator.free(checker);

    const required_markers = [_][]const u8{
        "Phase 15 notes",
        "`Documentation/zigux/freeze-map.md`",
        "`Documentation/zigux/phase15-freeze-map-governance.md`",
        "`Documentation/zigux/phase15-architecture-council-review-process.md`",
        "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
        "`Documentation/zigux/phase15-indefinite-c-policy.md`",
        "`Documentation/zigux/phase15-parity-scorecard.md`",
        "`Documentation/zigux/phase15-readiness-gate-survey.md`",
        "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
        "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
        "`Documentation/zigux/phase15-shared-summary-gap.md`",
        "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
        "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
        "`scripts/zigux/check-phase15-architecture-council-packet.py`",
        "`scripts/zigux/validate-phase15.py`",
    };

    for (required_markers) |marker| {
        try expectContains(docs_readme, marker);
        try expectContains(checker, marker);
    }

    try expectContains(checker, "LANDED_DOCS_REQUIRED_MARKERS");
    try expectContains(checker, "PARKED_DOCS_FORBIDDEN_MARKERS");
    try expectContains(checker, "missing_landed_marker");
}

test "handoff and shared-gap notes describe README as landed alignment follow-through" {
    const handoff_note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 64 * 1024);
    defer std.testing.allocator.free(handoff_note);

    const shared_gap_note = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md", 64 * 1024);
    defer std.testing.allocator.free(shared_gap_note);

    const landed_handoff_marker =
        "`Documentation/zigux/README.md`, which now carries a dedicated Phase 15 reminder packet and should be reread with `scripts/zigux/check-phase15-docs-readme-alignment.py` whenever that shared docs-root wording drifts away from the directly materialized governance packet";
    const landed_shared_gap_marker =
        "`Documentation/zigux/README.md` now keeps a dedicated Phase 15 reminder packet explicit, so reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py` whenever that shared docs-root wording drifts away from the directly materialized governance packet";

    try expectContains(handoff_note, landed_handoff_marker);
    try expectContains(shared_gap_note, landed_shared_gap_marker);
    try expectContains(shared_gap_note, "fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims");

    try expectNotContains(handoff_note, "still stops at Phase 14 on current `master`");
}

test "lane sequencing keeps shared README/checklist/scripts/tests surfaces non-owning" {
    const lane_seq_note = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md", 48 * 1024);
    defer std.testing.allocator.free(lane_seq_note);

    const checker = try readRepoFile("scripts/zigux/check-phase15-docs-readme-alignment.py", 24 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(lane_seq_note, "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves");
    try expectContains(lane_seq_note, "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`");
    try expectContains(lane_seq_note, ".github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`");

    try expectContains(checker, "PHASE15_DOCS_README_ALIGNMENT_SELF_TEST=pass");
    try expectContains(checker, "PHASE15_DOCS_README_ALIGNMENT_SELF_TEST_CASES=");
    try expectContains(checker, "docs_readme:unexpected_phase15_marker");
}
