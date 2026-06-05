const std = @import("std");
const testing = std.testing;

const export_shim = @import("export_shim");

const RbtreeRootView = export_shim.RbtreeRootView;
const rbtree_cached_flag: u32 = 1;
const rbtree_leftmost_valid_flag: u32 = 2;
const status_flag_error: u16 = 1;

fn view(root: usize, leftmost: usize, flags: u32) RbtreeRootView {
    return .{
        .root = root,
        .cached_leftmost = leftmost,
        .flags = flags,
    };
}

fn expectKernelError(status: export_shim.ExportStatus) !void {
    try testing.expect(!export_shim.statusIsOk(status));
    try testing.expectEqual(@as(i32, -22), status.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), status.facility);
    try testing.expectEqual(status_flag_error, status.flags);
}

test "export shim rbtree relay accepts only root-backed symmetric cached-leftmost views" {
    const uncached = view(0x1000, 0, 0);
    const cached = view(
        0x1000,
        0x0800,
        rbtree_cached_flag | rbtree_leftmost_valid_flag,
    );
    const rootless = view(0, 0, 0);
    const cached_without_address = view(
        0x1000,
        0,
        rbtree_cached_flag | rbtree_leftmost_valid_flag,
    );
    const address_without_cached_flags = view(0x1000, 0x0800, 0);
    const cached_without_leftmost_flag = view(
        0x1000,
        0x0800,
        rbtree_cached_flag,
    );

    try testing.expect(export_shim.rbtreeRootViewIsValid(uncached));
    try testing.expect(!export_shim.rbtreeRootViewIsCached(uncached));
    try testing.expect(!export_shim.rbtreeRootViewHasLeftmost(uncached));

    try testing.expect(export_shim.rbtreeRootViewIsValid(cached));
    try testing.expect(export_shim.rbtreeRootViewIsCached(cached));
    try testing.expect(export_shim.rbtreeRootViewHasLeftmost(cached));

    try testing.expect(!export_shim.rbtreeRootViewIsValid(rootless));
    try testing.expect(!export_shim.rbtreeRootViewIsValid(cached_without_address));
    try testing.expect(!export_shim.rbtreeRootViewIsValid(address_without_cached_flags));
    try testing.expect(!export_shim.rbtreeRootViewIsValid(cached_without_leftmost_flag));
}

test "export shim rbtree canonicalization repairs cached-leftmost flag symmetry" {
    const uncached_with_cached_flag = view(
        0x1000,
        0,
        rbtree_cached_flag,
    );
    const cached_missing_flags = view(0x1000, 0x0800, 0);
    const rootless_with_leftmost = view(
        0,
        0x0800,
        rbtree_cached_flag | rbtree_leftmost_valid_flag,
    );

    const canonical_uncached = export_shim.canonicalizeRbtreeRootView(uncached_with_cached_flag);
    try testing.expectEqual(@as(usize, 0x1000), canonical_uncached.root);
    try testing.expectEqual(@as(usize, 0), canonical_uncached.cached_leftmost);
    try testing.expectEqual(@as(u32, 0), canonical_uncached.flags);
    try testing.expect(export_shim.rbtreeRootViewIsValid(canonical_uncached));

    const canonical_cached = export_shim.canonicalizeRbtreeRootView(cached_missing_flags);
    try testing.expectEqual(@as(usize, 0x1000), canonical_cached.root);
    try testing.expectEqual(@as(usize, 0x0800), canonical_cached.cached_leftmost);
    try testing.expectEqual(
        rbtree_cached_flag | rbtree_leftmost_valid_flag,
        canonical_cached.flags,
    );
    try testing.expect(export_shim.rbtreeRootViewIsValid(canonical_cached));

    const canonical_rootless = export_shim.canonicalizeRbtreeRootView(rootless_with_leftmost);
    try testing.expectEqual(@as(usize, 0), canonical_rootless.root);
    try testing.expectEqual(@as(usize, 0), canonical_rootless.cached_leftmost);
    try testing.expectEqual(@as(u32, 0), canonical_rootless.flags);
    try testing.expect(!export_shim.rbtreeRootViewIsValid(canonical_rootless));
}

test "export shim rbtree status helper keeps valid and malformed packets explicit" {
    const cached = view(
        0x2000,
        0x1800,
        rbtree_cached_flag | rbtree_leftmost_valid_flag,
    );
    const malformed = view(
        0x2000,
        0,
        rbtree_cached_flag | rbtree_leftmost_valid_flag,
    );
    const rootless = view(0, 0, 0);

    const valid_status = export_shim.validateRbtreeRootView(cached);
    try testing.expect(export_shim.statusIsOk(valid_status));
    try testing.expectEqual(@as(i32, 0), valid_status.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), valid_status.facility);
    try testing.expectEqual(@as(u16, 0), valid_status.flags);

    try expectKernelError(export_shim.validateRbtreeRootView(malformed));
    try expectKernelError(export_shim.validateRbtreeRootView(rootless));
}
