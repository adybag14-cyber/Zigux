const std = @import("std");
const build_options = @import("build_options");

const helper_paths = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const direct_anchor_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(8 * 1024 * 1024));
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "closure note keeps manifest-backed Phase 1 authority visible" {
    const allocator = std.testing.allocator;
    const closure_text = try readRepoFile(allocator, build_options.closure_note_path);
    defer allocator.free(closure_text);

    try expectContains(closure_text, "`PHASE1_STATUS=parked`");
    try expectContains(closure_text, "`PHASE1_HELPER_COUNT=13`");
    try expectContains(closure_text, "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`");
    try expectContains(closure_text, "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`");
    try expectContains(closure_text, "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(closure_text, "helper-specific next_safe_step_note entries in the committed manifest");
    try expectNotContains(closure_text, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
}

test "validator and manifest agree on the closed thirteen-helper roster" {
    const allocator = std.testing.allocator;
    const validator_text = try readRepoFile(allocator, build_options.validator_path);
    defer allocator.free(validator_text);
    const manifest_text = try readRepoFile(allocator, build_options.manifest_path);
    defer allocator.free(manifest_text);

    try expectContains(validator_text, "EXPECTED_HELPERS = [");
    try expectContains(validator_text, "manifest.get(\"helper_count\"), len(EXPECTED_HELPERS)");
    try expectContains(validator_text, "manifest.get(\"helpers\"), EXPECTED_HELPERS");
    try expectContains(manifest_text, "\"phase\": \"Phase 1\"");
    try expectContains(manifest_text, "\"status\": \"closed\"");
    try expectContains(manifest_text, "\"helper_count\": 13");

    for (helper_paths) |path| {
        try expectContains(validator_text, path);
        try expectContains(manifest_text, path);
    }
}

test "validator keeps the direct-anchor helper subset separate from shared replay parked helpers" {
    const allocator = std.testing.allocator;
    const validator_text = try readRepoFile(allocator, build_options.validator_path);
    defer allocator.free(validator_text);
    const manifest_text = try readRepoFile(allocator, build_options.manifest_path);
    defer allocator.free(manifest_text);

    try expectContains(validator_text, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    try expectContains(validator_text, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    try expectContains(validator_text, "shared_replay_parked_helpers");
    try expectContains(validator_text, "direct_anchor_followup_helpers");
    try expectContains(validator_text, "anti_overlap_rule");
    try expectContains(manifest_text, "\"shared_replay_parked_helpers\"");
    try expectContains(manifest_text, "\"direct_anchor_followup_helpers\"");
    try expectContains(manifest_text, "\"anti_overlap_rule\"");

    for (direct_anchor_helpers) |path| {
        try expectContains(validator_text, path);
        try expectContains(manifest_text, path);
    }

    try expectOrdered(
        validator_text,
        "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [",
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
    );
}
