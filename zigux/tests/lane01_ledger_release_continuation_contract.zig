const std = @import("std");
const testing = std.testing;

const max_doc_size = 512 * 1024;

fn readDoc(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_doc_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, first: []const u8, second: []const u8, third: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    const third_index = std.mem.indexOf(u8, haystack, third) orelse return error.MissingThirdMarker;

    try testing.expect(first_index < second_index);
    try testing.expect(second_index < third_index);
}

test "bootstrap ledger release continuation delegates later PMO state" {
    const allocator = testing.allocator;
    const ledger = try readDoc(allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer allocator.free(ledger);

    try expectContains(ledger, "## Release-Planning Continuation");
    try expectContains(ledger, "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.");
    try expectContains(ledger, "Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.");
    try expectContains(ledger, "For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:");
    try expectContains(ledger, "`Documentation/zigux/phase12-release-sequencing.md`");
    try expectContains(ledger, "`Documentation/zigux/phase12-release-readiness-survey.md`");
    try expectContains(ledger, "`Documentation/zigux/phase12-release-closure-checklist.md`");
    try expectContains(ledger, "`Documentation/zigux/phase12-release-coordination-matrix.md`");
    try expectContains(ledger, "`Documentation/zigux/phase14-release-boundary-survey.md`");
    try expectOrder(
        ledger,
        "## Scope Note",
        "## Release-Planning Continuation",
        "- Practical rule:",
    );
}

test "bootstrap ledger keeps Phase 5 handoff separate from synthetic later train" {
    const allocator = testing.allocator;
    const ledger = try readDoc(allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer allocator.free(ledger);

    try expectContains(ledger, "For the active Phase 5 non-runtime sample tranche, treat the landed closure note as the ledger-side handoff instead of inventing synthetic later-train commit entries:");
    try expectContains(ledger, "`Documentation/zigux/phase5-closure.md`");
    try expectContains(ledger, "`Documentation/zigux/phase5-sample-lane-sequencing.md`");
    try expectContains(ledger, "`Documentation/zigux/phase5-sample-review-guide.md`");
    try expectContains(ledger, "use the Phase 5 closure note plus its two shared reminder companions when the question is which active non-runtime sample tranche evidence currently governs the bounded Phase 5 lane on `master`");
    try expectContains(ledger, "This keeps the ledger truthful about the early train while making the live release packet explicit for later scheduled PMO runs and the active Phase 5 closure packet explicit for sample-lane runs.");
}

test "release continuation paths materialize in docs root" {
    const required_paths = [_][]const u8{
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase12-release-sequencing.md",
        "Documentation/zigux/phase12-release-readiness-survey.md",
        "Documentation/zigux/phase12-release-closure-checklist.md",
        "Documentation/zigux/phase12-release-coordination-matrix.md",
        "Documentation/zigux/phase14-release-boundary-survey.md",
        "Documentation/zigux/phase5-closure.md",
        "Documentation/zigux/phase5-sample-lane-sequencing.md",
        "Documentation/zigux/phase5-sample-review-guide.md",
    };

    for (required_paths) |path| {
        var io_instance: std.Io.Threaded = .init(testing.allocator, .{});
        defer io_instance.deinit();

        var file = try std.Io.Dir.cwd().openFile(io_instance.io(), path, .{});
        file.close(io_instance.io());
    }
}

test "alpha README and roadmap keep the ledger as a bounded bootstrap source" {
    const allocator = testing.allocator;
    const readme = try readDoc(allocator, "zigux-alpha/README.md");
    defer allocator.free(readme);
    const roadmap = try readDoc(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(readme, "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.");
    try expectContains(readme, "[Live Product Docs](../Documentation/zigux/README.md)");
    try expectContains(roadmap, "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.");
    try expectContains(roadmap, "keep `zigux-alpha/` as the control-plane for startup planning only");
}
