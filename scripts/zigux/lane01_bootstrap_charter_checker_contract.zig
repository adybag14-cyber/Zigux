const std = @import("std");

const max_file_size = 128 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "Lane 01 checker keeps the charter file roster and CLI surface explicit" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(
        allocator,
        "scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    );
    defer allocator.free(checker);

    try expectContains(checker, "README_PATH = Path(\"zigux-alpha/README.md\")");
    try expectContains(checker, "ROADMAP_PATH = Path(\"zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md\")");
    try expectContains(checker, "LEDGER_PATH = Path(\"zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md\")");
    try expectContains(checker, "description=\"Verify that the landed Lane 01 zigux-alpha charter packet remains aligned.\"");
    try expectContains(checker, "\"--root\"");
    try expectContains(checker, "\"--self-test\"");
    try expectContains(checker, "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_SELF_TEST=pass");
    try expectContains(checker, "Lane 01 bootstrap charter alignment check passed.");
}

test "Lane 01 checker guards truth-preserving scope notes instead of phase-completion claims" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(
        allocator,
        "scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    );
    defer allocator.free(checker);

    try expectContains(checker, "`zigux-alpha` is the Zigux bootstrap workspace.");
    try expectContains(checker, "planning-only `zigux-alpha/` packet");
    try expectContains(checker, "bounded early commit train through the broadened Phase 2 tranche");
    try expectContains(checker, "confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.");
    try expectContains(checker, "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.");
    try expectContains(checker, "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.");
}

test "Lane 01 checker keeps live product surface markers in its guarded roster" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(
        allocator,
        "scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    );
    defer allocator.free(checker);

    try expectContains(checker, "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.");
    try expectContains(checker, "`Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.");
    try expectContains(checker, "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)");
    try expectContains(checker, "## Bootstrap Status Note");
    try expectContains(checker, "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.");
    try expectContains(checker, "## Scope Note");
    try expectContains(checker, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
}
