const std = @import("std");

const max_file_size = 1024 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try expectContains(haystack, needle);
    }
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "phase1 direct-anchor manifest gate keeps fail-closed status surface" {
    const allocator = std.testing.allocator;
    const gate = try readRepoFile(allocator, "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py");
    defer allocator.free(gate);

    try expectContainsAll(gate, &.{
        "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass",
        "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass",
        "PHASE1_DIRECT_ANCHOR_HELPER_COUNT",
        "PHASE1_DIRECT_ANCHOR_REVIEW_FIELD_COUNT",
    });

    if (contains(gate, "DuplicateTrackingDict")) {
        try expectContainsAll(gate, &.{
            "MANIFEST_REL",
            "zigux/tests/fixtures/phase1_helper_manifest.json",
            "duplicate_json_key",
            "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail",
            "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_START",
            "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_END",
        });
    }
}

test "phase1 direct-anchor manifest gate pins the direct helper family split" {
    const allocator = std.testing.allocator;
    const gate = try readRepoFile(allocator, "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py");
    defer allocator.free(gate);

    try expectContainsAll(gate, &.{
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
        "review_anchors",
    });

    if (contains(gate, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS")) {
        try expectContainsAll(gate, &.{
            "tools/lib/argv_split.zig",
            "tools/lib/cmdline.zig",
            "tools/lib/ctype.zig",
            "tools/lib/hweight.zig",
            "tools/lib/list_sort.zig",
            "tools/lib/slab.zig",
            "tools/lib/str_error_r.zig",
            "tools/lib/vsprintf.zig",
            "tools/lib/zalloc.zig",
            "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS",
            "EXPECTED_ANTI_OVERLAP_RULE",
            "direct_anchor_followup_helpers",
            "shared_replay_parked_helpers",
        });
    } else {
        try expectContainsAll(gate, &.{
            "EXPECTED_HELPERS",
            "EXPECTED_REVIEW_ANCHORS",
            "manifest:review_anchor_value",
        });
    }
}

test "phase1 direct-anchor manifest gate delegates helper-specific closure checks" {
    const allocator = std.testing.allocator;
    const gate = try readRepoFile(allocator, "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py");
    defer allocator.free(gate);

    if (contains(gate, "DELEGATED_CHECKERS")) {
        try expectContainsAll(gate, &.{
            "scripts/zigux/check-phase1-bitmap-direct-anchors.py",
            "scripts/zigux/check-phase1-find-bit-review-packet.py",
            "scripts/zigux/check-phase1-rbtree-direct-anchors.py",
            "scripts/zigux/check-phase1-rbtree-review-packet.py",
            "scripts/zigux/check-phase1-string-review-packet.py",
            "PHASE1_BITMAP_DIRECT_ANCHOR_CHECKER=pass",
            "PHASE1_FIND_BIT_REVIEW_CHECKER=pass",
            "PHASE1_RBTREE_DIRECT_ANCHOR_CHECKER=pass",
            "PHASE1_RBTREE_REVIEW_CHECKER=pass",
            "PHASE1_STRING_REVIEW_CHECKER=pass",
            "missing_success_stdout",
        });
    } else {
        try expectContainsAll(gate, &.{
            "EXPECTED_REVIEW_ANCHORS",
            "manifest:missing_review_anchor_field",
            "manifest:review_anchor_value",
            "tail_clamp_fixture_keys",
            "shared_replace_char_cstr_review_summary",
        });
    }
}

test "phase1 closure notes keep direct-anchor gate as a closure-validation surface" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure);
    const lane = try readRepoFile(allocator, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer allocator.free(lane);

    try expectContainsAll(lane, &.{
        "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig",
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        "PHASE1_BITMAP_NEXT_SAFE_STEP",
        "PHASE1_FIND_BIT_NEXT_SAFE_STEP",
        "PHASE1_RBTREE_NEXT_SAFE_STEP",
        "PHASE1_STRING_NEXT_SAFE_STEP",
    });

    if (contains(closure, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE")) {
        try expectContainsAll(closure, &.{
            "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
            "exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string",
        });
    } else {
        try expectContainsAll(closure, &.{
            "scripts/zigux/validate-phase1-closure.py",
            "PHASE1_CLOSURE_GATE",
        });
    }
}
