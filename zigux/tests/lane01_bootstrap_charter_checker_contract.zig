const std = @import("std");

fn readFileAlloc(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.ExpectedBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.ExpectedAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

test "checker owns all three Lane 01 charter source files" {
    const checker = try readFileAlloc("scripts/zigux/check-lane01-bootstrap-charter-alignment.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "README_PATH = Path(\"zigux-alpha/README.md\")");
    try expectContains(checker, "ROADMAP_PATH = Path(\"zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md\")");
    try expectContains(checker, "LEDGER_PATH = Path(\"zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md\")");
    try expectOrdered(checker, "readme = (root / README_PATH).read_text", "roadmap = (root / ROADMAP_PATH).read_text");
    try expectOrdered(checker, "roadmap = (root / ROADMAP_PATH).read_text", "ledger = (root / LEDGER_PATH).read_text");
}

test "checker keeps README roadmap and ledger marker rosters explicit" {
    const checker = try readFileAlloc("scripts/zigux/check-lane01-bootstrap-charter-alignment.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "README_MARKERS = (");
    try expectContains(checker, "ROADMAP_MARKERS = (");
    try expectContains(checker, "LEDGER_MARKERS = (");
    try expectContains(checker, "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard");
    try expectContains(checker, "confirm later-lane state in the live product docs, current repo tree, and active lane notes");
    try expectContains(checker, "## Bootstrap Status Note");
    try expectContains(checker, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(checker, "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes");
}

test "checker self-test covers each charter drift family" {
    const checker = try readFileAlloc("scripts/zigux/check-lane01-bootstrap-charter-alignment.py");
    defer std.testing.allocator.free(checker);

    try std.testing.expect(countOccurrences(checker, "unexpected missing markers for") >= 8);
    try expectContains(checker, "README rule case");
    try expectContains(checker, "README ledger-scope case");
    try expectContains(checker, "README guard case");
    try expectContains(checker, "README link case");
    try expectContains(checker, "roadmap heading case");
    try expectContains(checker, "roadmap status note case");
    try expectContains(checker, "ledger heading case");
    try expectContains(checker, "ledger follow-through case");
    try expectContains(checker, "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_SELF_TEST=pass");
}

test "checker CLI exposes live-root and synthetic self-test modes" {
    const checker = try readFileAlloc("scripts/zigux/check-lane01-bootstrap-charter-alignment.py");
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "Verify that the landed Lane 01 zigux-alpha charter packet remains aligned.");
    try expectContains(checker, "\"--root\"");
    try expectContains(checker, "\"--self-test\"");
    try expectContains(checker, "missing = collect_missing_markers(args.root)");
    try expectContains(checker, "print(f\"ERROR: {item}\")");
    try expectContains(checker, "Lane 01 bootstrap charter alignment check passed.");
}
