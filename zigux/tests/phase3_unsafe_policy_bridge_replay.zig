const std = @import("std");

const abi = @import("abi_bindings");
const narrow = @import("narrow");
const unsafe_policy = @import("unsafe_policy");

test "phase3 unsafe-policy bridge replay keeps helper-local raw-pointer gates explicit" {
    const raw_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const safe_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };

    var bridge_words = [_]u32{ 0x1122_3344, 0x5566_7788, 0x99AA_BBCC };
    const first_addr = @intFromPtr(&bridge_words[0]);
    const second_addr = @intFromPtr(&bridge_words[1]);
    const third_addr = @intFromPtr(&bridge_words[2]);

    const ptr = try unsafe_policy.pointerAtInteropPolicy(u32, first_addr, @sizeOf(u32), raw_policy);
    try std.testing.expectEqual(@as(u32, 0x1122_3344), ptr.*);

    const const_ptr = try unsafe_policy.constPointerAtByte(u32, second_addr, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge));
    try std.testing.expectEqual(@as(u32, 0x5566_7788), const_ptr.*);

    const slice = try unsafe_policy.sliceAtInteropPolicy(u32, first_addr, bridge_words.len, raw_policy);
    try std.testing.expectEqual(@as(usize, bridge_words.len), slice.len);
    slice[0] = 0xAABB_CCDD;
    try std.testing.expectEqual(@as(u32, 0xAABB_CCDD), bridge_words[0]);

    const const_slice = try unsafe_policy.constSliceAtByte(
        u32,
        first_addr,
        bridge_words.len,
        @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
    );
    try std.testing.expectEqual(@as(u32, 0x5566_7788), const_slice[1]);

    try unsafe_policy.writeValueAtInteropPolicy(u32, third_addr, 0xDEAD_BEEF, raw_policy);
    try std.testing.expectEqual(@as(u32, 0xDEAD_BEEF), bridge_words[2]);

    try std.testing.expectEqual(
        @as(u32, 0x5566_7788),
        try narrow.readValueAtInteropPolicyBytes(
            u32,
            second_addr,
            @sizeOf(u32),
            raw_policy.unsafe_scope,
            raw_policy.reserved,
        ),
    );
    try std.testing.expectEqual(
        @as(u32, 0xDEAD_BEEF),
        try narrow.exchangeValueAtByte(
            u32,
            third_addr,
            @sizeOf(u32),
            0xFACE_CAFE,
            @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        ),
    );
    try std.testing.expectEqual(@as(u32, 0xFACE_CAFE), bridge_words[2]);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        unsafe_policy.pointerAtInteropPolicy(u32, first_addr, @sizeOf(u32), safe_policy),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        unsafe_policy.constSliceAtInteropPolicy(u32, first_addr, bridge_words.len, reserved_policy),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.readValueAtInteropPolicyBytes(u32, first_addr, @sizeOf(u32), safe_policy.unsafe_scope, safe_policy.reserved),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.exchangeValueAtInteropPolicy(
            u32,
            second_addr,
            @sizeOf(u32),
            0,
            reserved_policy,
        ),
    );
}
