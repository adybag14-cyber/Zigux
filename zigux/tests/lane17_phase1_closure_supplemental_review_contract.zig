const std = @import("std");

const closure_note_path = "Documentation/zigux/phase1-closure.md";

const partial_xor_marker = "`PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay owned by the shared Phase 1 parity fixture and replay; current fixture pins partial_xor_nbits = 4 and partial_xor_masked_values = [14] as a single-word packet, while the broader multiword-tail clamp guarantee remains helper-local review evidence so caller-selected bit windows cannot silently leak tail bits beyond nbits`";
const complement_tail_marker = "`PHASE1_BITMAP_COMPLEMENT_TAIL_REVIEW=helper-local complement-tail masking stays explicit through the direct bitmap tests because the shared Phase 1 replay still does not carry a dedicated complement-tail fixture field, so partial-tail masking and zero-sized caller-view no-op behavior remain review-visible at the helper surface`";
const find_bit_alias_tail_marker = "`PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=helper-local Linux-style find_next_or_bit tail and past-end alias proof plus find_*clump8 tail-byte and exhausted-caller-byte alias proof stay explicit through the direct find_bit tests, so this closure packet parks them as helper-local alias evidence until a dedicated shared fixture key lands`";
const next_safe_step_marker = "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`";

fn loadClosureNote(allocator: std.mem.Allocator) ![]const u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, closure_note_path, allocator, .limited(1024 * 1024));
}

fn expectOnce(closure_note: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, closure_note, needle));
}

fn expectContains(closure_note: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, closure_note, needle) != null);
}

fn markerIndex(closure_note: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, closure_note, needle) orelse error.MissingMarker;
}

test "phase1 closure keeps supplemental bitmap review markers exact" {
    const closure_note = try loadClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    try expectOnce(closure_note, partial_xor_marker);
    try expectOnce(closure_note, complement_tail_marker);
    try expectContains(closure_note, "partial_xor_nbits = 4");
    try expectContains(closure_note, "partial_xor_masked_values = [14]");
    try expectContains(closure_note, "single-word packet");
    try expectContains(closure_note, "zero-sized caller-view no-op behavior");
}

test "phase1 closure keeps supplemental find_bit alias tail marker exact" {
    const closure_note = try loadClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    try expectOnce(closure_note, find_bit_alias_tail_marker);
    try expectContains(closure_note, "Linux-style find_next_or_bit tail and past-end alias proof");
    try expectContains(closure_note, "find_*clump8 tail-byte and exhausted-caller-byte alias proof");
    try expectContains(closure_note, "dedicated shared fixture key lands");
}

test "phase1 supplemental review markers stay before the next safe step" {
    const closure_note = try loadClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    const partial_xor_index = try markerIndex(closure_note, partial_xor_marker);
    const complement_tail_index = try markerIndex(closure_note, complement_tail_marker);
    const find_bit_alias_tail_index = try markerIndex(closure_note, find_bit_alias_tail_marker);
    const next_safe_step_index = try markerIndex(closure_note, next_safe_step_marker);

    try std.testing.expect(partial_xor_index < complement_tail_index);
    try std.testing.expect(complement_tail_index < find_bit_alias_tail_index);
    try std.testing.expect(find_bit_alias_tail_index < next_safe_step_index);
}
