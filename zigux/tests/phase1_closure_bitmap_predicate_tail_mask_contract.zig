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

fn readClosureNote() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        "Documentation/zigux/phase1-closure.md",
        testing.allocator,
        .limited(128 * 1024),
    );
}

test "closure note keeps bitmap predicate tail masking parked in Phase 1 closure" {
    const closure_note = try readClosureNote();
    defer testing.allocator.free(closure_note);

    try expectAnyContains(closure_note, &.{
        "PHASE1_BITMAP_PREDICATE_TAIL_MASK_REVIEW",
        "tail-masked predicate behavior",
    });
    try expectAnyContains(closure_note, &.{
        "equal, intersects, and subset ignore out-of-range tail bits",
        "tail-masked predicate behavior",
    });
    try expectAnyContains(closure_note, &.{
        "PHASE1_BITMAP_DIRECT_REVIEW",
        "PHASE1_BITMAP_PREDICATE_TAIL_MASK_REVIEW",
    });
    try expectContains(closure_note, "helper-local bitmap");
    try expectContains(closure_note, "shared Phase 1 replay");
}

test "manifest names predicate tail masking as helper-local review evidence" {
    try expectContains(helper_manifest, "\"predicate_tail_mask_anchor\"");
    try expectAnyContains(helper_manifest, &.{
        "test \\\"bitmap tail-masked helpers ignore out-of-range differences\\\"",
        "test \\\"bitmap predicates ignore out-of-range tail bits\\\"",
    });
    try expectAnyContains(helper_manifest, &.{
        "tail-masked predicate behavior",
        "predicates ignore out-of-range tail bits",
    });
    try expectNotContains(helper_manifest, "\"predicate_tail_mask_values\"");
    try expectNotContains(helper_manifest, "\"tail_masked_predicate_values\"");
}

test "shared fixture owns logical predicate outcomes but not a predicate-tail field" {
    try expectContains(helper_fixture, "\"equal\"");
    try expectContains(helper_fixture, "\"intersects\"");
    try expectContains(helper_fixture, "\"subset\"");
    try expectContains(helper_fixture, "\"and_result\"");
    try expectContains(helper_fixture, "\"andnot_result\"");
    try expectNotContains(helper_fixture, "\"predicate_tail_mask_values\"");
    try expectNotContains(helper_fixture, "\"tail_masked_predicate_values\"");
}
