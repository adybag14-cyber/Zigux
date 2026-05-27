const std = @import("std");
const companion = @import("phase5_rbtree_cached_leftmost_companion");

test "phase 5 rbtree companion keeps the cached-leftmost sample step reviewable through a focused test surface" {
    const summary = companion.referencePattern();

    try std.testing.expectEqualStrings("lib/rbtree.c", summary.anchor);
    try std.testing.expectEqualStrings("lib/rbtree.zig", summary.helper);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 5, 15 }, &summary.insert_keys);
    try std.testing.expectEqual(@as(i32, 10), summary.duplicate_key);
    try std.testing.expectEqual(@as(usize, 0), summary.duplicate_existing_slot);
    try std.testing.expectEqual(@as(i32, 5), summary.leftmost_before_cached_erase);
    try std.testing.expectEqual(@as(i32, 10), summary.promoted_leftmost_after_cached_erase);
    try std.testing.expectEqual(@as(i32, 15), summary.remaining_leftmost_after_erase_init);
    try std.testing.expect(!summary.requires_runtime_substrate);
    try std.testing.expect(summary.provides_selfcheck);
}

test "phase 5 rbtree companion keeps the ordered helper cues visible without widening into a broad sample family" {
    const summary = companion.referencePattern();

    try std.testing.expectEqual(companion.ReviewFocus.ordered_insertion, summary.checked_focus[0]);
    try std.testing.expectEqual(companion.ReviewFocus.cached_leftmost_promotion, summary.checked_focus[1]);
    try std.testing.expectEqual(companion.ReviewFocus.duplicate_rejection, summary.checked_focus[2]);
    try std.testing.expectEqual(companion.ReviewFocus.erase_init_detaches_node, summary.checked_focus[3]);
}
