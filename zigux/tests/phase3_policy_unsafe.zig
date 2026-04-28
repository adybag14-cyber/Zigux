const std = @import("std");
const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const narrow = @import("narrow_unsafe");

test "phase3 policy helpers stay aligned with canonical abi bindings" {
    comptime {
        layout_assert.assertSize(abi.BoundaryHeader, 8);
        layout_assert.assertAlign(abi.BoundaryHeader, 4);
        layout_assert.assertOffset(abi.BoundaryHeader, "abi_version", 4);
        layout_assert.assertOffset(abi.InteropPolicy, "panic_mode", 0);
        layout_assert.assertOffset(abi.InteropPolicy, "allocator_mode", 1);
        layout_assert.assertOffset(abi.InteropPolicy, "unsafe_scope", 2);
        layout_assert.assertOffset(abi.InteropPolicy, "reserved", 3);
    }
}

test "phase3 panic and allocator policies stay explicit" {
    try std.testing.expectEqual(panic_policy.Action.abort_now, panic_policy.actionFor(.abort));
    try std.testing.expectEqual(panic_policy.Action.bug_check, panic_policy.actionFor(.bug));
    try std.testing.expectEqual(panic_policy.Action.warn_and_return, panic_policy.actionFor(.warn));
    try std.testing.expect(!panic_policy.canReturn(.abort));
    try std.testing.expect(!panic_policy.canReturn(.bug));
    try std.testing.expect(panic_policy.canReturn(.warn));

    try std.testing.expectEqual(
        allocator_policy.InitFlow.caller_prepared,
        allocator_policy.initFlowFor(.caller_provided),
    );
    try std.testing.expectEqual(
        allocator_policy.InitFlow.helper_owned,
        allocator_policy.initFlowFor(.kernel_heap),
    );
    try std.testing.expectEqual(
        allocator_policy.InitFlow.helper_owned_with_reset,
        allocator_policy.initFlowFor(.arena),
    );
    try std.testing.expect(allocator_policy.requiresExplicitCaller(.caller_provided));
    try std.testing.expect(!allocator_policy.permitsGlobalFallback(.caller_provided));
    try std.testing.expect(!allocator_policy.initializesOwnedState(.caller_provided));
    try std.testing.expect(!allocator_policy.requiresResetOnInit(.kernel_heap));
    try std.testing.expect(allocator_policy.requiresResetOnInit(.arena));
}

test "phase3 narrow unsafe scope stays paired to abi policy" {
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.none), @intFromEnum(narrow.UnsafeScopeTag.none));
    try std.testing.expectEqual(
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio),
    );
    try std.testing.expectEqual(
        @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge),
    );

    var values = [_]u32{ 7, 11 };
    const base = narrow.addressOf(&values[0]);
    const volatile_ptr = narrow.pointerAt(u32, base, @sizeOf(u32));
    try std.testing.expectEqual(@as(u32, 11), volatile_ptr.*);
    const view = narrow.constSliceAt(u32, base, values.len);
    try std.testing.expectEqualSlices(u32, values[0..], view);
    const const_ptr = narrow.constPointerAt(u32, base);
    try std.testing.expectEqual(@as(u32, 7), const_ptr.*);

    try std.testing.expect(!narrow.permitsVolatileMmio(.none));
    try std.testing.expect(narrow.permitsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!narrow.permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expect(narrow.permitsRawPointerBridge(.raw_pointer_bridge));
}
