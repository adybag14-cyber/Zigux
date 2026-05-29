const std = @import("std");

const CharterDocs = struct {
    readme: []const u8,
    roadmap: []const u8,
    ledger: []const u8,
};

fn loadFile(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn loadDocs(io: std.Io) !CharterDocs {
    return .{
        .readme = try loadFile(io, "zigux-alpha/README.md", 32 * 1024),
        .roadmap = try loadFile(io, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 128 * 1024),
        .ledger = try loadFile(io, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 128 * 1024),
    };
}

fn freeDocs(docs: CharterDocs) void {
    std.testing.allocator.free(docs.readme);
    std.testing.allocator.free(docs.roadmap);
    std.testing.allocator.free(docs.ledger);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "Lane 01 README keeps zigux-alpha planning-only charter and live anchors" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs = try loadDocs(io_instance.io());
    defer freeDocs(docs);

    try expectContains(docs.readme, "`zigux-alpha` is the Zigux bootstrap workspace.");
    try expectContains(docs.readme, "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.");
    try expectContains(docs.readme, "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche");
    try expectContains(docs.readme, "confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.");
    try expectContains(docs.readme, "Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.");
    try expectContains(docs.readme, "Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.");
    try expectContains(docs.readme, "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.");
    try expectContains(docs.readme, "`Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.");
    try expectContains(docs.readme, "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.");
    try expectContains(docs.readme, "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)");
}

test "Lane 01 roadmap status note does not claim later packets are all materialized" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs = try loadDocs(io_instance.io());
    defer freeDocs(docs);

    try expectContains(docs.roadmap, "## Bootstrap Status Note");
    try expectContains(docs.roadmap, "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.");
    try expectContains(docs.roadmap, "For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");
    try expectContains(docs.roadmap, "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.");
    try expectContains(docs.roadmap, "starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.");
}

test "Lane 01 ledger scope stays bounded to early train with live continuation handoffs" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs = try loadDocs(io_instance.io());
    defer freeDocs(docs);

    try expectContains(docs.ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(docs.ledger, "## Scope Note");
    try expectContains(docs.ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(docs.ledger, "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.");
    try expectContains(docs.ledger, "## Release-Planning Continuation");
    try expectContains(docs.ledger, "Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.");
    try expectContains(docs.ledger, "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`");
    try expectContains(docs.ledger, "use the Phase 5 closure note plus its two shared reminder companions when the question is which active non-runtime sample tranche evidence currently governs the bounded Phase 5 lane on `master`");
    try expectNotContains(docs.ledger, "26. `docs(zigux): backfill later release-planning state`");
}
