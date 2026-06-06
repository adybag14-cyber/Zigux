const std = @import("std");
const testing = std.testing;

const export_shim = @import("export_shim_binding");

test "export shim accepts only coherent rbtree root view shapes" {
    const uncached = export_shim.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = 0,
    };
    const cached = export_shim.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = rbtreeCachedLeftmostFlags(),
    };
    const rootless = export_shim.RbtreeRootView{
        .root = 0,
        .cached_leftmost = 0,
        .flags = 0,
    };
    const leftmost_without_cached_flag = export_shim.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = leftmostFlag(),
    };
    const cached_without_leftmost_addr = export_shim.RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = rbtreeCachedLeftmostFlags(),
    };

    try testing.expect(export_shim.rbtreeRootViewIsValid(uncached));
    try testing.expect(!export_shim.rbtreeRootViewIsCached(uncached));
    try testing.expect(!export_shim.rbtreeRootViewHasLeftmost(uncached));

    try testing.expect(export_shim.rbtreeRootViewIsValid(cached));
    try testing.expect(export_shim.rbtreeRootViewIsCached(cached));
    try testing.expect(export_shim.rbtreeRootViewHasLeftmost(cached));

    try testing.expect(!export_shim.rbtreeRootViewIsValid(rootless));
    try testing.expect(!export_shim.rbtreeRootViewIsValid(leftmost_without_cached_flag));
    try testing.expect(!export_shim.rbtreeRootViewIsValid(cached_without_leftmost_addr));
}

test "export shim canonicalizes malformed cached-leftmost state before validation" {
    const stale_cached_flag = export_shim.RbtreeRootView{
        .root = 0x2000,
        .cached_leftmost = 0,
        .flags = cachedFlag(),
    };
    const stale_leftmost_pointer = export_shim.RbtreeRootView{
        .root = 0x2000,
        .cached_leftmost = 0x1000,
        .flags = 0,
    };
    const rootless = export_shim.RbtreeRootView{
        .root = 0,
        .cached_leftmost = 0x1000,
        .flags = rbtreeCachedLeftmostFlags(),
    };

    const canonical_uncached = export_shim.canonicalizeRbtreeRootView(stale_cached_flag);
    try testing.expect(export_shim.rbtreeRootViewIsValid(canonical_uncached));
    try testing.expectEqual(@as(usize, 0x2000), canonical_uncached.root);
    try testing.expectEqual(@as(usize, 0), canonical_uncached.cached_leftmost);
    try testing.expectEqual(@as(u32, 0), canonical_uncached.flags);

    const canonical_cached = export_shim.canonicalizeRbtreeRootView(stale_leftmost_pointer);
    try testing.expect(export_shim.rbtreeRootViewIsValid(canonical_cached));
    try testing.expectEqual(@as(usize, 0x2000), canonical_cached.root);
    try testing.expectEqual(@as(usize, 0x1000), canonical_cached.cached_leftmost);
    try testing.expectEqual(rbtreeCachedLeftmostFlags(), canonical_cached.flags);

    const canonical_rootless = export_shim.canonicalizeRbtreeRootView(rootless);
    try testing.expect(!export_shim.rbtreeRootViewIsValid(canonical_rootless));
    try testing.expectEqual(@as(usize, 0), canonical_rootless.root);
    try testing.expectEqual(@as(usize, 0), canonical_rootless.cached_leftmost);
    try testing.expectEqual(@as(u32, 0), canonical_rootless.flags);
}

test "export shim reports rbtree root validation through kernel status helpers" {
    const valid = export_shim.RbtreeRootView{
        .root = 0x4000,
        .cached_leftmost = 0x3000,
        .flags = rbtreeCachedLeftmostFlags(),
    };
    const invalid = export_shim.RbtreeRootView{
        .root = 0x4000,
        .cached_leftmost = 0,
        .flags = rbtreeCachedLeftmostFlags(),
    };

    const valid_status = export_shim.validateRbtreeRootView(valid);
    const invalid_status = export_shim.validateRbtreeRootView(invalid);

    try testing.expect(export_shim.statusIsOk(valid_status));
    try testing.expect(!export_shim.statusIsOk(invalid_status));
    try testing.expect(export_shim.statusHasKnownFacility(valid_status));
    try testing.expect(export_shim.statusHasKnownFacility(invalid_status));
    try testing.expectEqual(@as(i32, 0), valid_status.code);
    try testing.expectEqual(@as(i32, -22), invalid_status.code);
    try testing.expectEqual(@intFromEnum(export_shim.Facility.kernel), valid_status.facility);
    try testing.expectEqual(@intFromEnum(export_shim.Facility.kernel), invalid_status.facility);
    try testing.expectEqual(@as(u16, 0), valid_status.flags);
    try testing.expectEqual(@as(u16, 1), invalid_status.flags);
}

fn cachedFlag() u32 {
    return 1;
}

fn leftmostFlag() u32 {
    return 2;
}

fn rbtreeCachedLeftmostFlags() u32 {
    return cachedFlag() | leftmostFlag();
}
