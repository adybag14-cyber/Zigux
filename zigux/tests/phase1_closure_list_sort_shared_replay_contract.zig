const std = @import("std");

const read_limit = 512 * 1024;

const list_sort_path = "tools/lib/list_sort.zig";
const shared_replay_helpers = "tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig";
const direct_anchor_helpers = "tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig";

const list_sort_review_summary = "keep list_sort parked in the shared-replay helper family for fixture ownership, but reread the helper-local proof packet before reopening the lane: current master already names direct witnesses for comparator-context ordering, repeat-sort circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, and empty-or-singleton handling beside the committed parity keys";
const list_sort_next_safe_step = "If this helper lane reopens, keep list_sort parked unless a fresh reread finds drift in the committed `tri_sorted_*` or `bool_sorted_*` fixture keys, or in the current helper-local anchors for comparator-context ordering, repeat-sort circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, or empty-or-singleton handling; do not widen into the missing shared replay stack by default.";

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(read_limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "lane note keeps list_sort in the shared replay parked helper family" {
    const lane_note = try readFile("Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer std.testing.allocator.free(lane_note);

    try expectContains(lane_note, "PHASE1_SHARED_REPLAY_PARKED_HELPERS=" ++ shared_replay_helpers);
    try expectContains(lane_note, "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=" ++ direct_anchor_helpers);
    try expectContains(lane_note, "`tools/lib/list_sort.zig` stays in the shared-replay parked family");
    try expectContains(lane_note, "PHASE1_LIST_SORT_NEXT_SAFE_STEP=list_sort reopens only for shared replay or reminder-surface drift in the committed tri_sorted_* or bool_sorted_* fixture keys");
    try expectNotContains(lane_note, "PHASE1_LIST_SORT_DIRECT_OWNER=");
}

test "manifest keeps list_sort fixture keys and helper-local anchors aligned" {
    const manifest = try readFile("zigux/tests/fixtures/phase1_helper_manifest.json");
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"" ++ list_sort_path ++ "\": {");
    try expectContains(manifest, "\"parity_fixture_keys\": [");
    try expectContains(manifest, "\"tri_sorted_keys\"");
    try expectContains(manifest, "\"tri_sorted_ordinals\"");
    try expectContains(manifest, "\"bool_sorted_keys\"");
    try expectContains(manifest, "\"bool_sorted_ordinals\"");
    try expectContains(manifest, "\"comparator_context_anchor\": \"test \\\"list sort honors comparator context\\\"\"");
    try expectContains(manifest, "\"repeat_sort_anchor\": \"test \\\"list sort can reorder the same circular list twice\\\"\"");
    try expectContains(manifest, "\"reverse_link_anchor\": \"test \\\"list sort keeps reverse links aligned after reordering\\\"\"");
    try expectContains(manifest, "\"sorted_input_anchor\": \"test \\\"list sort preserves sorted unique input\\\"\"");
    try expectContains(manifest, "\"parity_bucket_anchor\": \"test \\\"list sort preserves stable bucket order across parity groups\\\"\"");
    try expectContains(manifest, "\"modulo_bucket_anchor\": \"test \\\"list sort preserves stable modulo bucket order across a longer merge path\\\"\"");
    try expectContains(manifest, "\"all_ties_anchor\": \"test \\\"list sort preserves input order when every comparison ties\\\"\"");
    try expectContains(manifest, "\"empty_singleton_anchor\": \"test \\\"list sort handles empty and singleton lists\\\"\"");
    try expectContains(manifest, "\"review_packet_summary\": \"" ++ list_sort_review_summary ++ "\"");
    try expectContains(manifest, "\"next_safe_step_note\": \"" ++ list_sort_next_safe_step ++ "\"");
}

test "closure validator treats list_sort as shared replay parked, not direct anchor follow-up" {
    const validator = try readFile("scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    try expectContains(validator, "\"tools/lib/list_sort.zig\",");
    try expectContains(validator, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    try expectContains(validator, "\"tools/lib/bitmap.zig\",");
    try expectContains(validator, "\"tools/lib/find_bit.zig\",");
    try expectContains(validator, "\"tools/lib/rbtree.zig\",");
    try expectContains(validator, "\"tools/lib/string.zig\",");
    try expectNotContains(validator, "\"direct_anchor_followup_helpers\": [\n    \"tools/lib/list_sort.zig\"");
}

test "closure note keeps the next-safe-step contract tied to manifest notes" {
    const closure = try readFile("Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.");
    try expectContains(closure, "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`");
    try expectContains(closure, "the committed helper manifest, this closure note, the narrow closure validator");
    try expectNotContains(closure, "PHASE1_LIST_SORT_DIRECT_OWNER=");
}
