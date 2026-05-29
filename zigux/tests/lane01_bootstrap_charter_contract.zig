const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "Lane 01 readme keeps zigux-alpha as a planning-only bootstrap workspace" {
    const allocator = std.testing.allocator;
    const readme = try readRepoFile(allocator, "zigux-alpha/README.md");
    defer allocator.free(readme);

    try expectContains(readme, "`zigux-alpha` is the Zigux bootstrap workspace.");
    try expectContains(readme, "It does not exist to become a permanent parallel subsystem tree.");
    try expectContains(readme, "Keep product planning and bootstrap artifacts here first.");
    try expectContains(readme, "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.");
    try expectContains(readme, "Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.");
    try expectContains(readme, "Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.");
    try expectContains(readme, "Treat ZAR as the research and proving repo and Zigux as the product repo.");
}

test "Lane 01 start-here packet points from bootstrap docs to live product docs" {
    const allocator = std.testing.allocator;
    const readme = try readRepoFile(allocator, "zigux-alpha/README.md");
    defer allocator.free(readme);

    try expectContains(readme, "[ZAR to Zigux Product Roadmap](./ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md)");
    try expectContains(readme, "[Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)");
    try expectContains(readme, "[Live Product Docs](../Documentation/zigux/README.md)");
    try expectContains(readme, "[Review Checklist](../Documentation/zigux/review-checklist.md)");
    try expectContains(readme, "[Freeze Map](../Documentation/zigux/freeze-map.md)");
    try expectContains(readme, "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)");
}

test "Lane 01 roadmap and ledger preserve current-state confirmation boundaries" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);
    const ledger = try readRepoFile(allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer allocator.free(ledger);

    try expectContains(roadmap, "## Bootstrap Status Note");
    try expectContains(roadmap, "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.");
    try expectContains(roadmap, "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.");
    try expectContains(roadmap, "starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.");

    try expectContains(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(ledger, "## Scope Note");
    try expectContains(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(ledger, "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.");
}

test "Lane 01 shipped Python guard names the same charter packet" {
    const allocator = std.testing.allocator;
    const guard = try readRepoFile(allocator, "scripts/zigux/check-lane01-bootstrap-charter-alignment.py");
    defer allocator.free(guard);

    try expectContains(guard, "README_PATH = Path(\"zigux-alpha/README.md\")");
    try expectContains(guard, "ROADMAP_PATH = Path(\"zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md\")");
    try expectContains(guard, "LEDGER_PATH = Path(\"zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md\")");
    try expectContains(guard, "README_MARKERS = (");
    try expectContains(guard, "ROADMAP_MARKERS = (");
    try expectContains(guard, "LEDGER_MARKERS = (");
    try expectContains(guard, "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_SELF_TEST=pass");
}
