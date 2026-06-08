const std = @import("std");

const required_files = [_][]const u8{
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-find-bit-review-packet.py",
    "scripts/zigux/check-phase1-rbtree-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/Makefile",
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const delegated_checker_labels = [_][]const u8{
    "phase1-string-review-packet",
    "phase1-find-bit-review-packet",
    "phase1-rbtree-review-packet",
    "phase1-direct-owner-markers",
    "phase1-direct-anchor-manifest-gate",
    "phase1-route-summary-counts",
    "phase1-find-bit-bench-anchors",
    "phase1-bitmap-direct-anchors",
    "phase1-shared-reminder-packet",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase 1 closure validator keeps the required file roster explicit" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 768 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "REQUIRED_FILES = (");
    try expectContains(validator, "PHASE1_CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")");
    try expectContains(validator, "STRING_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-string-review-packet.py\")");
    try expectContains(validator, "BITMAP_HELPER_REL = Path(\"tools/lib/bitmap.zig\")");
    try expectContains(validator, "STRING_HELPER_REL = Path(\"tools/lib/string.zig\")");

    for (required_files) |path| {
        const marker = try std.fmt.allocPrint(std.testing.allocator, "Path(\"{s}\")", .{path});
        defer std.testing.allocator.free(marker);
        try expectContains(validator, marker);
    }

    try expectBefore(validator, "PHASE1_CLOSURE_REL,", "PHASE1_LANE_NOTE_REL,");
    try expectBefore(validator, "BENCH_CHECKER_REL,", "FIND_BIT_BENCH_ANCHOR_CHECKER_REL,");
    try expectBefore(validator, "MANIFEST_REL,", "ZIGUX_MAKEFILE_REL,");
    try expectBefore(validator, "BITMAP_HELPER_REL,", "FIND_BIT_HELPER_REL,");
    try expectBefore(validator, "FIND_BIT_HELPER_REL,", "RBTREE_HELPER_REL,");
    try expectBefore(validator, "RBTREE_HELPER_REL,", "STRING_HELPER_REL,");
}

test "phase 1 closure validator fails before reading packets when files are missing" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 768 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "failures = [f\"missing_file:{path.as_posix()}\" for path in REQUIRED_FILES if not (root / path).is_file()]");
    try expectContains(validator, "if failures:\n        return failures");
    try expectBefore(validator, "if failures:\n        return failures", "closure_text = load_text(root, PHASE1_CLOSURE_REL)");
    try expectBefore(validator, "if failures:\n        return failures", "for script_rel, label in DELEGATED_CHECKERS:");
}

test "phase 1 closure validator self-test covers missing required owner files" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 768 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "for relative_path in REQUIRED_FILES:");
    try expectContains(validator, "write_text(root / relative_path, f\"fixture for {relative_path.as_posix()}\\n\")");
    try expectContains(validator, "(\"missing_string_checker\", lambda root: (root / STRING_REVIEW_CHECKER_REL).unlink())");
    try expectContains(validator, "(\"missing_find_bit_review_checker\", lambda root: (root / FIND_BIT_REVIEW_CHECKER_REL).unlink())");
    try expectContains(validator, "(\"missing_rbtree_review_checker\", lambda root: (root / RBTREE_REVIEW_CHECKER_REL).unlink())");
    try expectContains(validator, "(\"missing_direct_anchor_manifest_gate_checker\", lambda root: (root / DIRECT_ANCHOR_MANIFEST_GATE_REL).unlink())");
    try expectContains(validator, "(\"missing_bitmap_direct_anchor_checker\", lambda root: (root / BITMAP_DIRECT_ANCHOR_CHECKER_REL).unlink())");
}

test "phase 1 closure validator reports required-file failures without delegated prefixes" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 768 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "for failure in failures:\n            print(failure)");
    try expectContains(validator, "f\"missing_file:{path.as_posix()}\"");
    for (delegated_checker_labels) |label| {
        try expectContains(validator, label);
    }
    try expectBefore(validator, "if failures:\n        return failures", "for script_rel, label in DELEGATED_CHECKERS:");
}
