const std = @import("std");

const testing = std.testing;

const helper_manifest = @embedFile("fixtures/phase1_helper_manifest.json");
const helper_fixture = @embedFile("fixtures/phase1_helpers.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectAnyContains(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) return;
    }

    try testing.expect(false);
}

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(256 * 1024),
    );
}

test "closure note keeps bitmap Linux alias review helper-local" {
    const closure_note = try readRepoFile("Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit");
    try expectContains(closure_note, "direct bitmap test anchor and the Phase 1 helper manifest");
    try expectContains(closure_note, "alloc/free, zero/fill, predicate, mutation, and render aliases");
    try expectContains(closure_note, "behaviorally locked to the primary helper surface");
    try expectNotContains(closure_note, "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=missing");
    try expectNotContains(closure_note, "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=validator-owned");
}

test "bitmap helper exposes Linux aliases and direct alias tests" {
    const bitmap_helper = try readRepoFile("tools/lib/bitmap.zig");
    defer testing.allocator.free(bitmap_helper);

    try expectContains(bitmap_helper, "pub fn bitmap_alloc");
    try expectContains(bitmap_helper, "pub fn bitmap_zalloc");
    try expectContains(bitmap_helper, "pub fn bitmap_free");
    try expectContains(bitmap_helper, "pub fn bitmap_zero");
    try expectContains(bitmap_helper, "pub fn bitmap_fill");
    try expectContains(bitmap_helper, "pub fn bitmap_empty");
    try expectContains(bitmap_helper, "pub fn bitmap_full");
    try expectContains(bitmap_helper, "pub fn bitmap_weight");
    try expectContains(bitmap_helper, "pub fn bitmap_or");
    try expectContains(bitmap_helper, "pub fn bitmap_xor");
    try expectContains(bitmap_helper, "pub fn bitmap_and");
    try expectContains(bitmap_helper, "pub fn bitmap_andnot");
    try expectContains(bitmap_helper, "pub fn bitmap_complement");
    try expectContains(bitmap_helper, "pub fn bitmap_equal");
    try expectContains(bitmap_helper, "pub fn bitmap_intersects");
    try expectContains(bitmap_helper, "pub fn bitmap_subset");
    try expectContains(bitmap_helper, "pub fn bitmap_set");
    try expectContains(bitmap_helper, "pub fn bitmap_clear");
    try expectContains(bitmap_helper, "pub fn bitmap_copy");
    try expectContains(bitmap_helper, "pub fn bitmap_copy_clear_tail");
    try expectContains(bitmap_helper, "pub fn bitmap_copy_and_extend");
    try expectContains(bitmap_helper, "pub fn bitmap_scnprintf");

    try expectAnyContains(bitmap_helper, &.{
        "test \"bitmap Linux-style aliases mirror copy logical range and format helpers\"",
        "test \"bitmap Linux-style aliases mirror the primary helper surface\"",
    });
    try expectAnyContains(bitmap_helper, &.{
        "test \"bitmap Linux-style aliases mirror size state and allocation helpers\"",
        "test \"bitmap Linux-style aliases keep zero-bit windows explicit no-ops\"",
    });
}

test "manifest keeps Linux alias ownership in the bitmap direct-anchor packet" {
    try expectAnyContains(helper_manifest, &.{
        "\"linux_alias_anchor\": \"test \\\"bitmap Linux-style aliases mirror copy logical range and format helpers\\\"\"",
        "\"linux_alias_anchor\": \"test \\\"bitmap Linux-style aliases mirror the primary helper surface\\\"\"",
    });
    try expectContains(helper_manifest, "\"parity_fixture_keys\"");
    try expectAnyContains(helper_manifest, &.{
        "\"shared_logical_fixture_keys\"",
        "logical operator outputs",
        "predicate tail-mask",
    });
    try expectAnyContains(helper_manifest, &.{
        "\"shared_range_fixture_keys\"",
        "\"range_after_set\"",
        "final-partial range boundary",
    });
    try expectAnyContains(helper_manifest, &.{
        "\"copy_values\"",
        "copy alias",
    });
    try expectAnyContains(helper_manifest, &.{
        "\"copy_clear_tail_values\"",
        "copy aliases preserve tail clearing",
    });
    try expectAnyContains(helper_manifest, &.{
        "\"copy_and_extend_values\"",
        "copy and extend handles zero and aligned counts",
    });
    try expectAnyContains(helper_manifest, &.{
        "\"or_values\"",
        "Linux-style alias behavior review-visible",
        "Linux-style alias mirror coverage",
    });
    try expectAnyContains(helper_manifest, &.{
        "\"range_after_set\"",
        "range boundary",
        "range set/clear/fill/zero outcomes",
    });
    try expectNotContains(helper_manifest, "\"linux_alias_values\"");
    try expectNotContains(helper_manifest, "\"bitmap_linux_alias_anchor\"");
}

test "shared fixture covers replay values without claiming a Linux alias fixture key" {
    try expectAnyContains(helper_fixture, &.{
        "\"copy_values\"",
        "\"partial_xor_masked_values\"",
    });
    try expectAnyContains(helper_fixture, &.{
        "\"copy_clear_tail_values\"",
        "\"complement_values\"",
        "\"andnot_values\"",
    });
    try expectAnyContains(helper_fixture, &.{
        "\"copy_and_extend_values\"",
        "\"zalloc_values\"",
    });
    try expectContains(helper_fixture, "\"or_values\"");
    try expectContains(helper_fixture, "\"xor_values\"");
    try expectContains(helper_fixture, "\"range_after_set\"");
    try expectContains(helper_fixture, "\"scnprintf\"");
    try expectContains(helper_fixture, "\"alloc_words\"");
    try expectContains(helper_fixture, "\"zalloc_values\"");
    try expectNotContains(helper_fixture, "\"linux_alias_values\"");
    try expectNotContains(helper_fixture, "\"bitmap_linux_alias_anchor\"");
}
