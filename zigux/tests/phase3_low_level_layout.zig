const std = @import("std");
const layout_assert = @import("layout_assert");
const mmio = @import("mmio");
const narrow = @import("narrow");

test "phase3 low-level wrappers keep interop-policy layout bytes explicit for MMIO and raw-pointer bridges" {
    try layout_assert.assertInteropPolicyLayout();

    const InteropPolicy = @typeInfo(@TypeOf(mmio.readInteropPolicy)).@"fn".params[1].type.?;
    try std.testing.expectEqual(@as(usize, 4), @sizeOf(InteropPolicy));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(InteropPolicy, "panic_mode"));
    try std.testing.expectEqual(@as(usize, 1), @offsetOf(InteropPolicy, "allocator_mode"));
    try std.testing.expectEqual(@as(usize, 2), @offsetOf(InteropPolicy, "unsafe_scope"));
    try std.testing.expectEqual(@as(usize, 3), @offsetOf(InteropPolicy, "reserved"));

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

    try std.testing.expect(mmio.allowsInteropPolicy(mmio_policy));
    try std.testing.expect(!mmio.allowsInteropPolicy(raw_policy));
    try std.testing.expect(!mmio.allowsInteropPolicy(reserved_policy));
    try std.testing.expectEqual(
        @as(?narrow.UnsafeScopeTag, .volatile_mmio),
        narrow.scopeFromInteropPolicy(mmio_policy),
    );
    try std.testing.expectEqual(
        @as(?narrow.UnsafeScopeTag, .raw_pointer_bridge),
        narrow.scopeFromInteropPolicy(raw_policy),
    );
    try std.testing.expectEqual(
        @as(?narrow.UnsafeScopeTag, null),
        narrow.scopeFromInteropPolicy(reserved_policy),
    );
    try std.testing.expect(!narrow.permitsRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(narrow.permitsRawPointerBridgeInteropPolicy(raw_policy));
}
