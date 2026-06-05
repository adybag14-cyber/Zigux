const std = @import("std");

const manifest = @embedFile("fixtures/phase1_helper_manifest.json");
const fixture = @embedFile("fixtures/phase1_helpers.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "closure note keeps bitmap complement-tail review helper-local" {
    const closure_note = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "Documentation/zigux/phase1-closure.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE1_BITMAP_DIRECT_REVIEW=");
    try expectContains(closure_note, "PHASE1_BITMAP_UNIT_REVIEW=");
    try expectContains(closure_note, "PHASE1_BITMAP_EMPTY_UNIT_REVIEW=");
    try expectContains(closure_note, "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=");
    try expectContains(closure_note, "helper-local bitmap final partial-word proof stays explicit");
    try expectContains(closure_note, "bitmap multiword-tail xorBits behavior still lets callers clamp");
    try expectContains(closure_note, "empty-bitmap caller-buffer preservation");
    try expectContains(closure_note, "complement tail clamping");
    try expectContains(closure_note, "complement-tail masking");
    try expectContains(closure_note, "partial-tail masking and zero-sized caller-view no-op behavior remain review-visible at the helper surface");
}

test "bitmap helper still carries the direct complement-tail proof" {
    const bitmap_helper = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "tools/lib/bitmap.zig",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(bitmap_helper);

    try expectContains(bitmap_helper, "pub fn complement(");
    try expectContains(bitmap_helper, "pub fn bitmap_complement(");
    try expectContains(bitmap_helper, "test \"bitmap complement");
    try expectContains(bitmap_helper, "lastWordMask(nbits)");
    try expectContains(bitmap_helper, "zero_dst[0..0]");
    try expectContains(bitmap_helper, "try std.testing.expectEqualSlices(Word, &direct, &alias)");
}

test "manifest names the complement-tail anchor and keeps it out of shared fixture keys" {
    try expectContains(manifest, "\"complement_tail_anchor\": \"test \\\"bitmap complement clamps partial tails and leaves zero-sized caller views untouched\\\"\"");
    try expectContains(manifest, "\"complement_tail_review_summary\": \"helper-local complement-tail masking stays explicit");
    try expectContains(manifest, "\"parity_fixture_keys\"");
    try expectContains(manifest, "\"complement_values\"");
    try expectContains(manifest, "\"partial_xor_review_fields\"");
    try expectContains(manifest, "\"partial_xor_nbits\"");
    try expectContains(manifest, "\"partial_xor_masked_values\"");
    try expectNotContains(manifest, "\"complement_tail_values\"");
    try expectNotContains(manifest, "\"complement_tail_masked_values\"");
}

test "committed fixture carries complement values but no dedicated complement-tail field" {
    try expectContains(fixture, "\"complement_values\"");
    try expectContains(fixture, "\"partial_xor_nbits\"");
    try expectContains(fixture, "\"partial_xor_masked_values\"");
    try expectNotContains(fixture, "\"complement_tail_values\"");
    try expectNotContains(fixture, "\"complement_tail_masked_values\"");
}
