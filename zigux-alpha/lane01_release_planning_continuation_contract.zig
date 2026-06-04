const std = @import("std");

const ledger = @embedFile("BOOTSTRAP_COMMIT_LEDGER.md");

fn requireMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, ledger, marker) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, ledger, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, ledger, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "release planning continuation stays tied to docs-root PMO packet" {
    try requireMarker("## Release-Planning Continuation");
    try requireMarker("Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.");
    try requireMarker("Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.");
    try requireMarker("For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:");
    try requireMarker("`Documentation/zigux/README.md`");
    try requireMarker("`Documentation/zigux/phase12-release-sequencing.md`");
    try requireMarker("`Documentation/zigux/phase12-release-readiness-survey.md`");
    try requireMarker("`Documentation/zigux/phase12-release-closure-checklist.md`");
    try requireMarker("`Documentation/zigux/phase12-release-coordination-matrix.md`");
    try requireMarker("`Documentation/zigux/phase14-release-boundary-survey.md`");
    try requireOrdered("## Scope Note", "## Release-Planning Continuation");
}

test "phase5 non-runtime sample handoff remains explicit" {
    try requireMarker("For the active Phase 5 non-runtime sample tranche, treat the landed closure note as the ledger-side handoff instead of inventing synthetic later-train commit entries:");
    try requireMarker("`Documentation/zigux/phase5-closure.md`");
    try requireMarker("`Documentation/zigux/phase5-sample-lane-sequencing.md`");
    try requireMarker("`Documentation/zigux/phase5-sample-review-guide.md`");
    try requireMarker("use the Phase 5 closure note plus its two shared reminder companions when the question is which active non-runtime sample tranche evidence currently governs the bounded Phase 5 lane on `master`");
}

test "practical routing rule keeps bootstrap ledger truthful" {
    try requireMarker("use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train");
    try requireMarker("use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`");
    try requireMarker("This keeps the ledger truthful about the early train while making the live release packet explicit for later scheduled PMO runs and the active Phase 5 closure packet explicit for sample-lane runs.");
    try std.testing.expect(std.mem.indexOf(u8, ledger, "26. `") == null);
}
