const std = @import("std");

const PairShard = struct {
    path: []const u8,
    route: []const u8,
    companion: []const u8,
};

const abi_pair_shards = [_]PairShard{
    .{
        .path = "zigux/tests/phase3_abi_allocator_policy_pair_build.zig",
        .route = "phase3-abi-allocator-policy-pair-test",
        .companion = "zigux/helpers/allocator_policy.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_atomic_pair_build.zig",
        .route = "phase3-abi-atomic-pair-test",
        .companion = "zigux/helpers/atomic.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_barrier_pair_build.zig",
        .route = "phase3-abi-barrier-pair-test",
        .companion = "zigux/helpers/barrier.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_bitmap_view_pair_build.zig",
        .route = "phase3-abi-bitmap-view-pair-test",
        .companion = "zigux/helpers/bitmap_view.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_cpumask_view_pair_build.zig",
        .route = "phase3-abi-cpumask-view-pair-test",
        .companion = "zigux/helpers/cpumask_view.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_dev_t_pair_build.zig",
        .route = "phase3-abi-dev-t-pair-test",
        .companion = "zigux/uapi/dev_t.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_dev_t_binding_pair_build.zig",
        .route = "phase3-abi-dev-t-binding-pair-test",
        .companion = "zigux/bindings/dev_t.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_dump_current_pair_build.zig",
        .route = "phase3-abi-dump-current-pair-test",
        .companion = "zigux/tests/phase3_abi_dump_current.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_export_shim_pair_build.zig",
        .route = "phase3-abi-export-shim-pair-test",
        .companion = "zigux/kernel/export_shim.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_header_family_pair_build.zig",
        .route = "phase3-abi-header-family-pair-test",
        .companion = "zigux/bindings/header_family.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_layout_assert_pair_build.zig",
        .route = "phase3-abi-layout-assert-pair-test",
        .companion = "zigux/helpers/layout_assert.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_mmio_pair_build.zig",
        .route = "phase3-abi-mmio-pair-test",
        .companion = "zigux/helpers/mmio.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_notifier_abi_pair_build.zig",
        .route = "phase3-abi-notifier-abi-pair-test",
        .companion = "zigux/bindings/notifier_abi.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_panic_policy_pair_build.zig",
        .route = "phase3-abi-panic-policy-pair-test",
        .companion = "zigux/helpers/panic_policy.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_unsafe_narrow_pair_build.zig",
        .route = "phase3-abi-unsafe-narrow-pair-test",
        .companion = "zigux/unsafe/narrow.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_unsafe_policy_pair_build.zig",
        .route = "phase3-abi-unsafe-policy-pair-test",
        .companion = "zigux/helpers/unsafe_policy.zig",
    },
    .{
        .path = "zigux/tests/phase3_abi_version_pair_build.zig",
        .route = "phase3-abi-version-pair-test",
        .companion = "zigux/uapi/version.zig",
    },
};

fn hasCompanion(comptime companion: []const u8) bool {
    for (abi_pair_shards) |shard| {
        if (std.mem.eql(u8, shard.companion, companion)) return true;
    }
    return false;
}

test "phase3 ABI pair-build inventory keeps the landed shard count explicit" {
    try std.testing.expectEqual(@as(usize, 17), abi_pair_shards.len);
}

test "phase3 ABI pair-build inventory uses stable tests-root paths and routes" {
    for (abi_pair_shards) |shard| {
        try std.testing.expect(std.mem.startsWith(u8, shard.path, "zigux/tests/phase3_abi_"));
        try std.testing.expect(std.mem.endsWith(u8, shard.path, "_pair_build.zig"));
        try std.testing.expect(std.mem.startsWith(u8, shard.route, "phase3-abi-"));
        try std.testing.expect(std.mem.endsWith(u8, shard.route, "-pair-test"));
    }
}

test "phase3 ABI pair-build inventory has no duplicate paths or routes" {
    for (abi_pair_shards, 0..) |left, left_index| {
        for (abi_pair_shards[(left_index + 1)..]) |right| {
            try std.testing.expect(!std.mem.eql(u8, left.path, right.path));
            try std.testing.expect(!std.mem.eql(u8, left.route, right.route));
        }
    }
}

test "phase3 ABI pair-build inventory covers the ABI substrate companion surface" {
    try std.testing.expect(hasCompanion("zigux/bindings/dev_t.zig"));
    try std.testing.expect(hasCompanion("zigux/bindings/header_family.zig"));
    try std.testing.expect(hasCompanion("zigux/bindings/notifier_abi.zig"));
    try std.testing.expect(hasCompanion("zigux/helpers/allocator_policy.zig"));
    try std.testing.expect(hasCompanion("zigux/helpers/atomic.zig"));
    try std.testing.expect(hasCompanion("zigux/helpers/barrier.zig"));
    try std.testing.expect(hasCompanion("zigux/helpers/layout_assert.zig"));
    try std.testing.expect(hasCompanion("zigux/helpers/mmio.zig"));
    try std.testing.expect(hasCompanion("zigux/helpers/panic_policy.zig"));
    try std.testing.expect(hasCompanion("zigux/helpers/unsafe_policy.zig"));
    try std.testing.expect(hasCompanion("zigux/kernel/export_shim.zig"));
    try std.testing.expect(hasCompanion("zigux/uapi/dev_t.zig"));
    try std.testing.expect(hasCompanion("zigux/uapi/version.zig"));
    try std.testing.expect(hasCompanion("zigux/unsafe/narrow.zig"));
}
