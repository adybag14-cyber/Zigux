const std = @import("std");
const mmio = @import("mmio");
const narrow = @import("narrow");

test "phase3 low-level wrappers keep MMIO range overflow boundaries explicit" {
    const InteropPolicy = @typeInfo(@TypeOf(mmio.readInteropPolicy)).@"fn".params[1].type.?;
    const mmio_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio),
        .reserved = 0,
    };
    const raw_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio),
        .reserved = 1,
    };
    const mmio_scope = @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio);
    const near_end = std.math.maxInt(usize) - 3;

    const typed_range = try mmio.rangeScoped(near_end, 4, 1, .volatile_mmio);
    try std.testing.expectEqual(near_end, typed_range.base_addr);
    try std.testing.expectEqual(@as(u32, 4), typed_range.length);
    try std.testing.expectEqual(@as(u32, 1), typed_range.stride);

    const policy_range = try mmio.rangeInteropPolicy(near_end, 4, 1, mmio_policy);
    try std.testing.expectEqual(typed_range.base_addr, policy_range.base_addr);
    try std.testing.expectEqual(typed_range.length, policy_range.length);
    try std.testing.expectEqual(typed_range.stride, policy_range.stride);

    const bytes_range = try mmio.rangeInteropPolicyBytes(near_end, 4, 1, mmio_scope, 0);
    try std.testing.expectEqual(policy_range.base_addr, bytes_range.base_addr);
    try std.testing.expectEqual(policy_range.length, bytes_range.length);
    try std.testing.expectEqual(policy_range.stride, bytes_range.stride);

    const byte_range = try mmio.rangeInteropPolicyByte(near_end, 4, 1, mmio_scope);
    try std.testing.expectEqual(policy_range.base_addr, byte_range.base_addr);
    try std.testing.expectEqual(policy_range.length, byte_range.length);
    try std.testing.expectEqual(policy_range.stride, byte_range.stride);

    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeScoped(near_end, 5, 1, .volatile_mmio));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicy(near_end, 5, 1, mmio_policy));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicyBytes(near_end, 5, 1, mmio_scope, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicyByte(near_end, 5, 1, mmio_scope));

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicy(near_end, 4, 1, raw_policy));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicy(near_end, 4, 1, reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicyBytes(near_end, 4, 1, @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge), 0));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicyBytes(near_end, 4, 1, mmio_scope, 1));

    const empty = try mmio.rangeInteropPolicyByte(std.math.maxInt(usize), 0, 0, mmio_scope);
    try std.testing.expectEqual(std.math.maxInt(usize), empty.base_addr);
    try std.testing.expectEqual(@as(u32, 0), empty.length);
    try std.testing.expectEqual(@as(u32, 0), empty.stride);
}
