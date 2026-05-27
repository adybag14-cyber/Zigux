const std = @import("std");

pub const linux_anchor = "lib/rbtree.c";
pub const helper_path = "lib/rbtree.zig";

pub const ReviewFocus = enum {
    ordered_insertion,
    cached_leftmost_promotion,
    duplicate_rejection,
    erase_init_detaches_node,
};

pub const CompanionSummary = struct {
    anchor: []const u8,
    helper: []const u8,
    insert_keys: [3]i32,
    duplicate_key: i32,
    duplicate_existing_slot: usize,
    leftmost_before_cached_erase: i32,
    promoted_leftmost_after_cached_erase: i32,
    remaining_leftmost_after_erase_init: i32,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
    checked_focus: [4]ReviewFocus,
};

pub fn referencePattern() CompanionSummary {
    return .{
        .anchor = linux_anchor,
        .helper = helper_path,
        .insert_keys = .{ 10, 5, 15 },
        .duplicate_key = 10,
        .duplicate_existing_slot = 0,
        .leftmost_before_cached_erase = 5,
        .promoted_leftmost_after_cached_erase = 10,
        .remaining_leftmost_after_erase_init = 15,
        .requires_runtime_substrate = false,
        .provides_selfcheck = true,
        .checked_focus = .{
            .ordered_insertion,
            .cached_leftmost_promotion,
            .duplicate_rejection,
            .erase_init_detaches_node,
        },
    };
}

test "rbtree companion keeps the bounded cached-leftmost review packet explicit" {
    const summary = referencePattern();

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

test "rbtree companion keeps the focused helper cues ordered and reviewable" {
    const summary = referencePattern();

    try std.testing.expectEqual(ReviewFocus.ordered_insertion, summary.checked_focus[0]);
    try std.testing.expectEqual(ReviewFocus.cached_leftmost_promotion, summary.checked_focus[1]);
    try std.testing.expectEqual(ReviewFocus.duplicate_rejection, summary.checked_focus[2]);
    try std.testing.expectEqual(ReviewFocus.erase_init_detaches_node, summary.checked_focus[3]);
}
