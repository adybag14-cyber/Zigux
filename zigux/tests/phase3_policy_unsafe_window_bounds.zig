const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const unsafe_policy = @import("unsafe_policy");

fn rawPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
}

fn reservedRawPolicy() abi.InteropPolicy {
    var policy = rawPolicy();
    policy.reserved = 1;
    return policy;
}

test "phase3 raw-pointer windows keep exact-end accesses bounded" {
    var words = [_]u32{ 0x1020_3040, 0x5060_7080, 0x90a0_b0c0 };
    const base_addr = @intFromPtr(&words[0]);
    const byte_len = @sizeOf(@TypeOf(words));
    const last_word_offset = byte_len - @sizeOf(u32);

    const window = try unsafe_policy.windowInteropPolicy(base_addr, byte_len, rawPolicy());

    const last = try unsafe_policy.pointerAtWindow(u32, window, last_word_offset);
    try testing.expectEqual(@as(u32, 0x90a0_b0c0), last.*);

    try testing.expectError(
        error.AccessOutsideWindow,
        unsafe_policy.pointerAtWindow(u32, window, last_word_offset + 1),
    );
    try testing.expectError(
        error.AccessOutsideWindow,
        unsafe_policy.constSliceAtWindow(u32, window, @sizeOf(u32), words.len),
    );
}

test "phase3 raw-pointer windows reject policy and address overflow before pointer formation" {
    try testing.expectError(
        error.UnsafeScopeDenied,
        unsafe_policy.windowInteropPolicy(0x1000, @sizeOf(u32), reservedRawPolicy()),
    );

    try testing.expectError(
        error.AddressOverflow,
        unsafe_policy.windowByte(std.math.maxInt(usize), 1, abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
}

test "phase3 raw-pointer windows allow empty slices without widening non-empty access" {
    var byte: u8 = 0xaa;
    const base_addr = @intFromPtr(&byte);
    const empty = try unsafe_policy.windowByte(base_addr, 0, abi.UNSAFE_RAW_POINTER_BRIDGE);

    const empty_slice = try unsafe_policy.constSliceAtWindow(u8, empty, 0, 0);
    try testing.expectEqual(@as(usize, 0), empty_slice.len);

    try testing.expectError(error.AccessOutsideWindow, unsafe_policy.pointerAtWindow(u8, empty, 0));
    try testing.expectError(error.AccessOutsideWindow, unsafe_policy.readValueAtWindow(u8, empty, 0));
}
