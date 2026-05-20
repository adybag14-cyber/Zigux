const std = @import("std");
const helper = @import("rbtree_root_view");
const rbtree = @import("rbtree_bindings");

test "phase3 rbtree root view survey keeps the helper-local contract aligned with the dedicated binding" {
    const empty_view = helper.empty();
    const cached_view = helper.cached(0x2000, 0x1800);
    const uncached_view = helper.uncached(0x2400);

    try std.testing.expectEqual(rbtree.KNOWN_FLAG_MASK, helper.KNOWN_FLAG_MASK);
    try std.testing.expectEqual(rbtree.ROOT_FLAG_LEFTMOST_VALID, helper.ROOT_FLAG_LEFTMOST_VALID);

    try std.testing.expect(helper.isCanonical(empty_view));
    try std.testing.expect(helper.isCanonical(cached_view));
    try std.testing.expect(helper.isCanonical(uncached_view));

    try std.testing.expectEqual(empty_view, helper.canonicalize(rbtree.empty()).?);
    try std.testing.expectEqual(cached_view, helper.canonicalize(rbtree.cached(0x2000, 0x1800)).?);
    try std.testing.expectEqual(uncached_view, helper.canonicalize(rbtree.uncached(0x2400)).?);
}
