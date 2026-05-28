const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const prefixes = [_][]const u8{ "", "../", "../../" };
    for (prefixes) |prefix| {
        const candidate = if (prefix.len == 0)
            path
        else
            try std.mem.concat(std.testing.allocator, u8, &.{ prefix, path });
        defer if (prefix.len != 0) std.testing.allocator.free(candidate);

        return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), candidate, std.testing.allocator, .limited(limit)) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        };
    }

    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "lane 01 bootstrap README keeps zigux-alpha as planning-only charter" {
    const readme = try readRepoFile("zigux-alpha/README.md", 16 * 1024);
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "`zigux-alpha` is the Zigux bootstrap workspace.");
    try expectContains(readme, "It does not exist to become a permanent parallel subsystem tree.");
    try expectContains(readme, "Keep product planning and bootstrap artifacts here first.");
    try expectContains(readme, "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.");
    try expectContains(readme, "Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.");
    try expectContains(readme, "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.");
    try expectContains(readme, "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.");
}

test "lane 01 roadmap and ledger preserve the bounded bootstrap handoff" {
    const roadmap = try readRepoFile("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", 96 * 1024);
    defer std.testing.allocator.free(roadmap);

    const ledger = try readRepoFile("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", 96 * 1024);
    defer std.testing.allocator.free(ledger);

    try expectContains(roadmap, "## Bootstrap Status Note");
    try expectContains(roadmap, "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.");
    try expectContains(roadmap, "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.");
    try expectContains(roadmap, "starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.");
    try expectContains(roadmap, "`zigux-alpha/` is not the final home for:");

    try expectContains(ledger, "1. `docs(zigux-alpha): establish roadmap and folder charter`");
    try expectContains(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(ledger, "## Scope Note");
    try expectContains(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(ledger, "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.");
    try expectContains(ledger, "Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.");
}

test "lane 01 shipped checker covers the same charter anchors" {
    const checker = try readRepoFile("scripts/zigux/check-lane01-bootstrap-charter-alignment.py", 32 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "README_PATH = Path(\"zigux-alpha/README.md\")");
    try expectContains(checker, "ROADMAP_PATH = Path(\"zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md\")");
    try expectContains(checker, "LEDGER_PATH = Path(\"zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md\")");
    try expectContains(checker, "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.");
    try expectContains(checker, "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.");
    try expectContains(checker, "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.");
    try expectContains(checker, "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_SELF_TEST=pass");
    try expectContains(checker, "Lane 01 bootstrap charter alignment check passed.");
}
