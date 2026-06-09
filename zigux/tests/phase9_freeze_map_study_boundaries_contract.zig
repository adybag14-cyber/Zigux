const std = @import("std");
const testing = std.testing;

const root_markers = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "study-only anchors",
    "not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence",
    "blocked publication, install-root, or module-metadata surfaces are complete",
};

const freeze_map_markers = [_][]const u8{
    "# Zigux Freeze Map",
    "## Study / Boundary Only",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "shared Phase 9 runtime-pilot freeze-boundary packet",
    "`scripts/zigux/check-phase9-freeze-map-study-boundaries.py`",
    "The shared Phase 9 freeze-boundary packet is governance evidence only",
    "must not be cited as proof that `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, blocked publication paths, install-root paths, or deeper runtime-loader substrate work became delivery-ready",
};

const checklist_markers = [_][]const u8{
    "# Zigux Review Checklist",
    "Phase 9 reviewer prompt:",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    "kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
    "returned shared runtime-loader allocator/init-flow packet",
    "returned family-local runtime kretprobe packet",
    "blocked publication, install-root, or depmod surfaces are complete",
};

const checker_markers = [_][]const u8{
    "FREEZE_MAP_PATH = \"Documentation/zigux/freeze-map.md\"",
    "STUDY_ONLY_ACCOUNTING_PATH = \"Documentation/zigux/phase15-study-only-anchor-accounting.md\"",
    "LANE_SEQUENCING_PATH = \"Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md\"",
    "ROADMAP_STUDY_ONLY_ANCHORS = (",
    "\"kernel/workqueue.c\"",
    "\"kernel/trace/ring_buffer.c\"",
    "PHASE9_REQUIRED_PATH_COUNT",
    "PHASE9_FORBIDDEN_MAKE_ROUTE_COUNT",
    "phase9-runtime-loader-command-env-boundary-guard-test",
    "FORBIDDEN_PHASE9_MAKE_ROUTES = [",
    "\"phase9-validate\"",
};

const build_route_markers = [_][]const u8{
    "phase9-freeze-map-study-boundaries-contract",
    "phase9_freeze_map_study_boundaries_contract.zig",
    ".cwd = b.path(\"../..\")",
    "\"test\"",
};

test "docs root keeps Phase 9 study-only freeze boundary routed to owner notes" {
    const docs_root = try readFile("Documentation/zigux/README.md");
    defer testing.allocator.free(docs_root);

    try requireAll(docs_root, &root_markers);
    try testing.expect(std.mem.indexOf(u8, docs_root, "Phase 9 notes -") != null);
    try testing.expect(std.mem.indexOf(u8, docs_root, "runtime-pilot expansion evidence") != null);
}

test "freeze map and review checklist keep Phase 9 boundary as governance evidence" {
    const freeze_map = try readFile("Documentation/zigux/freeze-map.md");
    defer testing.allocator.free(freeze_map);
    const checklist = try readFile("Documentation/zigux/review-checklist.md");
    defer testing.allocator.free(checklist);

    try requireAll(freeze_map, &freeze_map_markers);
    try requireAll(checklist, &checklist_markers);
    try requireExactOccurrences(freeze_map, "`kernel/workqueue.c`", 3);
    try requireExactOccurrences(freeze_map, "`kernel/trace/ring_buffer.c`", 3);
}

test "checker contract and standalone build route stay explicit" {
    const checker = try readFile("scripts/zigux/check-phase9-freeze-map-study-boundaries.py");
    defer testing.allocator.free(checker);
    const build_file = try readFile("zigux/tests/phase9_freeze_map_study_boundaries_contract_build.zig");
    defer testing.allocator.free(build_file);

    try requireAll(checker, &checker_markers);
    try requireAll(build_file, &build_route_markers);
    try requireExactOccurrences(checker, "\"phase9\"", 1);
    try requireExactOccurrences(checker, "\"phase9-validate\"", 1);
}

fn readFile(comptime path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireAll(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
    }
}

fn requireExactOccurrences(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |found| {
        count += 1;
        offset += found + needle.len;
    }
    try testing.expectEqual(expected, count);
}
