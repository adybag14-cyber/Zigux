const std = @import("std");
const abi = @import("abi_bindings");
const unsafe_policy = @import("unsafe_policy");

fn rawPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
}

fn safePolicy() abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_ABORT,
        .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
        .unsafe_scope = abi.UNSAFE_NONE,
        .reserved = 0,
    };
}

test "raw pointer window creation requires raw bridge scope and clear reserved byte" {
    var words = [_]u32{ 11, 22, 33 };
    const base_addr = @intFromPtr(&words[0]);
    const byte_len = @sizeOf(@TypeOf(words));

    const from_policy = try unsafe_policy.windowInteropPolicy(base_addr, byte_len, rawPolicy());
    const from_bytes = try unsafe_policy.windowInteropPolicyBytes(
        base_addr,
        byte_len,
        abi.UNSAFE_RAW_POINTER_BRIDGE,
        0,
    );
    const from_byte = try unsafe_policy.windowByte(base_addr, byte_len, abi.UNSAFE_RAW_POINTER_BRIDGE);

    try std.testing.expectEqual(base_addr, from_policy.base_addr);
    try std.testing.expectEqual(byte_len, from_policy.byte_len);
    try std.testing.expectEqual(from_policy, from_bytes);
    try std.testing.expectEqual(from_policy, from_byte);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        unsafe_policy.windowInteropPolicy(base_addr, byte_len, safePolicy()),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        unsafe_policy.windowInteropPolicyBytes(
            base_addr,
            byte_len,
            abi.UNSAFE_RAW_POINTER_BRIDGE,
            1,
        ),
    );
    try std.testing.expectError(
        error.AddressOverflow,
        unsafe_policy.windowByte(std.math.maxInt(usize), 1, abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
}

test "raw pointer window keeps pointer, slice, read, write, and exchange bounded" {
    var words = [_]u32{ 11, 22, 33, 44 };
    const window = try unsafe_policy.windowInteropPolicy(
        @intFromPtr(&words[0]),
        @sizeOf(@TypeOf(words)),
        rawPolicy(),
    );

    const second = try unsafe_policy.pointerAtWindow(u32, window, @sizeOf(u32));
    try std.testing.expectEqual(@as(u32, 22), second.*);

    const tail = try unsafe_policy.constPointerAtWindow(u32, window, @sizeOf(u32) * 3);
    try std.testing.expectEqual(@as(u32, 44), tail.*);

    const middle = try unsafe_policy.sliceAtWindow(u32, window, @sizeOf(u32), 2);
    try std.testing.expectEqual(@as(usize, 2), middle.len);
    middle[0] = 55;
    middle[1] = 66;
    try std.testing.expectEqual(@as(u32, 55), words[1]);
    try std.testing.expectEqual(@as(u32, 66), words[2]);

    const replay = try unsafe_policy.constSliceAtWindow(u32, window, 0, words.len);
    try std.testing.expectEqual(@as(u32, 11), replay[0]);
    try std.testing.expectEqual(@as(u32, 66), replay[2]);

    try std.testing.expectEqual(
        @as(u32, 66),
        try unsafe_policy.readValueAtWindow(u32, window, @sizeOf(u32) * 2),
    );
    try unsafe_policy.writeValueAtWindow(u32, window, @sizeOf(u32) * 2, 77);
    try std.testing.expectEqual(@as(u32, 77), words[2]);
    try std.testing.expectEqual(
        @as(u32, 77),
        try unsafe_policy.exchangeValueAtWindow(u32, window, @sizeOf(u32) * 2, 88),
    );
    try std.testing.expectEqual(@as(u32, 88), words[2]);

    try std.testing.expectError(error.AccessOutsideWindow, unsafe_policy.pointerAtWindow(u32, window, @sizeOf(@TypeOf(words))));
    try std.testing.expectError(error.AccessOutsideWindow, unsafe_policy.constPointerAtWindow(u32, window, @sizeOf(@TypeOf(words))));
    try std.testing.expectError(error.AccessOutsideWindow, unsafe_policy.sliceAtWindow(u32, window, @sizeOf(u32) * 3, 2));
    try std.testing.expectError(error.OffsetOverflow, unsafe_policy.readValueAtWindow(u32, window, std.math.maxInt(usize)));
    try std.testing.expectError(error.LengthOverflow, unsafe_policy.sliceAtWindow(u32, window, 0, std.math.maxInt(usize)));
}

test "raw pointer window rejected offsets leave storage unchanged" {
    var words = [_]u32{ 101, 202 };
    const window = try unsafe_policy.windowByte(
        @intFromPtr(&words[0]),
        @sizeOf(@TypeOf(words)),
        abi.UNSAFE_RAW_POINTER_BRIDGE,
    );

    try std.testing.expectError(
        error.AccessOutsideWindow,
        unsafe_policy.writeValueAtWindow(u32, window, @sizeOf(@TypeOf(words)), 303),
    );
    try std.testing.expectError(
        error.AccessOutsideWindow,
        unsafe_policy.exchangeValueAtWindow(u32, window, @sizeOf(u32) + 1, 404),
    );

    try std.testing.expectEqual(@as(u32, 101), words[0]);
    try std.testing.expectEqual(@as(u32, 202), words[1]);
}
