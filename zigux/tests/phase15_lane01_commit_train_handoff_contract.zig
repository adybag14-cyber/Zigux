const std = @import("std");

const CommitExpectation = struct {
    number: []const u8,
    roadmap_subject: []const u8,
    ledger_subject: []const u8,
    roadmap_marker: []const u8,
    ledger_marker: []const u8,
};

const early_commit_expectations = [_]CommitExpectation{
    .{
        .number = "1.",
        .roadmap_subject = "`docs(zigux-alpha): establish roadmap and folder charter`",
        .ledger_subject = "`docs(zigux-alpha): establish roadmap and folder charter`",
        .roadmap_marker = "add this roadmap",
        .ledger_marker = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    },
    .{
        .number = "2.",
        .roadmap_subject = "`docs(Documentation/zigux): add program charter and freeze map`",
        .ledger_subject = "`docs(zigux): add documentation root, review checklist, and freeze map`",
        .roadmap_marker = "Documentation/zigux/freeze-map.md",
        .ledger_marker = "Documentation/zigux/freeze-map.md",
    },
    .{
        .number = "3.",
        .roadmap_subject = "`build(scripts/zigux): add toolchain pinning and version checks`",
        .ledger_subject = "`build(scripts/zigux): add bootstrap validation and toolchain checks`",
        .roadmap_marker = "add deterministic version-check helper",
        .ledger_marker = "scripts/zigux/check-zig-toolchain.py",
    },
    .{
        .number = "4.",
        .roadmap_subject = "`test(zigux/tests): add differential harness scaffolding`",
        .ledger_subject = "`test(zigux): establish differential-test root`",
        .roadmap_marker = "add artifact-diff scaffolds for host-side tools",
        .ledger_marker = "zigux/tests/README.md",
    },
};

fn readAlphaFile(path: []const u8, max_size: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(max_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn markerIndex(haystack: []const u8, marker: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, marker) orelse error.MissingLane01Marker;
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    try std.testing.expect(try markerIndex(haystack, first) < try markerIndex(haystack, second));
}

test "lane 01 roadmap keeps the first commit train anchored before later phases" {
    const roadmap = try readAlphaFile("../../zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 96 * 1024);
    defer std.testing.allocator.free(roadmap);

    try expectContains(roadmap, "## First Commit and Push Sequence for Zigux");
    try expectContains(roadmap, "This is the recommended near-term commit train after this roadmap lands.");

    var previous_index = try markerIndex(roadmap, "### Bootstrap commits");
    for (early_commit_expectations) |expectation| {
        const commit_index = try markerIndex(roadmap, expectation.roadmap_subject);
        try std.testing.expect(commit_index > previous_index);
        try expectContains(roadmap, expectation.roadmap_marker);
        previous_index = commit_index;
    }

    try expectOrdered(roadmap, "### Bootstrap commits", "### Phase 1 commits");
    try expectOrdered(roadmap, "### Phase 1 commits", "### Phase 2 commits");
    try expectOrdered(roadmap, "### Phase 2 commits", "### Phase 3 and 4 commits");
    try expectOrdered(roadmap, "### Phase 3 and 4 commits", "### Phase 5 commits");
    try expectOrdered(roadmap, "### Phase 5 commits", "## Recommended Validation Gates");

    try expectContains(roadmap, "Do not schedule Phase 10+ commits until the earlier gates are actually green.");
}

test "lane 01 ledger preserves the materialized early train and handoff boundary" {
    const ledger = try readAlphaFile("../../zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 128 * 1024);
    defer std.testing.allocator.free(ledger);

    try expectContains(ledger, "# Zigux Alpha Bootstrap Commit Ledger");
    try expectContains(ledger, "This ledger turns the roadmap into the first product commit train.");
    try expectContains(ledger, "## Commit Train");

    var previous_index = try markerIndex(ledger, "## Commit Train");
    for (early_commit_expectations) |expectation| {
        const numbered_subject = try std.fmt.allocPrint(
            std.testing.allocator,
            "{s} {s}",
            .{ expectation.number, expectation.ledger_subject },
        );
        defer std.testing.allocator.free(numbered_subject);

        const commit_index = try markerIndex(ledger, numbered_subject);
        try std.testing.expect(commit_index > previous_index);
        try expectContains(ledger, expectation.ledger_marker);
        previous_index = commit_index;
    }

    try expectContains(ledger, "## Scope Note");
    try expectContains(ledger, "## Release-Planning Continuation");
    try expectOrdered(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`", "## Scope Note");
    try expectOrdered(ledger, "## Scope Note", "## Release-Planning Continuation");
}

test "lane 01 roadmap and ledger agree on the current handoff rule" {
    const roadmap = try readAlphaFile("../../zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 96 * 1024);
    defer std.testing.allocator.free(roadmap);
    const ledger = try readAlphaFile("../../zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 128 * 1024);
    defer std.testing.allocator.free(ledger);

    try expectContains(roadmap, "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.");
    try expectContains(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(ledger, "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.");
    try expectContains(ledger, "Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.");
    try expectContains(ledger, "use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train");
}
