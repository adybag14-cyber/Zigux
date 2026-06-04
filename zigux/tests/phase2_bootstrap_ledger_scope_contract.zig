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

test "bootstrap ledger keeps item 25 as the broadened Phase 2 tranche boundary" {
    const ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 128 * 1024);
    defer std.testing.allocator.free(ledger);

    try expectContains(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(ledger, "- `Documentation/zigux/phase2-closure.md`");
    try expectContains(ledger, "- `Documentation/zigux/artifact-diff.md`");
    try expectContains(ledger, "- `scripts/zigux/README.md`");
    try expectContains(ledger, "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try expectContains(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(ledger, "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.");
    try expectContains(ledger, "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.");
}

test "ledger redirects later release planning away from synthetic bootstrap history" {
    const ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 128 * 1024);
    defer std.testing.allocator.free(ledger);

    try expectContains(ledger, "## Release-Planning Continuation");
    try expectContains(ledger, "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.");
    try expectContains(ledger, "Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.");
    try expectContains(ledger, "For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:");
    try expectContains(ledger, "- `Documentation/zigux/README.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase12-release-sequencing.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase12-release-readiness-survey.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase12-release-closure-checklist.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase12-release-coordination-matrix.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase14-release-boundary-survey.md`");
}

test "ledger keeps Phase 5 sample continuation as a handoff, not a new train entry" {
    const ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 128 * 1024);
    defer std.testing.allocator.free(ledger);

    try expectContains(ledger, "For the active Phase 5 non-runtime sample tranche, treat the landed closure note as the ledger-side handoff instead of inventing synthetic later-train commit entries:");
    try expectContains(ledger, "- `Documentation/zigux/phase5-closure.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase5-sample-lane-sequencing.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase5-sample-review-guide.md`");
    try expectContains(ledger, "use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train");
    try expectContains(ledger, "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`");
    try expectContains(ledger, "use the Phase 5 closure note plus its two shared reminder companions when the question is which active non-runtime sample tranche evidence currently governs the bounded Phase 5 lane on `master`");
    try expectContains(ledger, "This keeps the ledger truthful about the early train while making the live release packet explicit for later scheduled PMO runs and the active Phase 5 closure packet explicit for sample-lane runs.");
}
