const std = @import("std");

const abi = @import("abi_bindings");
const export_shim = @import("export_shim");

const valid_panic_modes = [_]u8{
    abi.PANIC_ABORT,
    abi.PANIC_BUG,
    abi.PANIC_WARN,
};

const valid_allocator_modes = [_]u8{
    abi.ALLOC_CALLER_PROVIDED,
    abi.ALLOC_KERNEL_HEAP,
    abi.ALLOC_ARENA,
};

const valid_unsafe_scopes = [_]u8{
    abi.UNSAFE_NONE,
    abi.UNSAFE_VOLATILE_MMIO,
    abi.UNSAFE_RAW_POINTER_BRIDGE,
};

fn policy(panic_mode: u8, allocator_mode: u8, unsafe_scope: u8, reserved: u8) abi.InteropPolicy {
    return .{
        .panic_mode = panic_mode,
        .allocator_mode = allocator_mode,
        .unsafe_scope = unsafe_scope,
        .reserved = reserved,
    };
}

fn expectKernelOk(status: abi.ExportStatus) !void {
    try std.testing.expect(export_shim.statusIsOk(status));
    try std.testing.expectEqual(@as(i32, 0), status.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), status.facility);
    try std.testing.expectEqual(@as(u16, 0), status.flags);
}

fn expectKernelInvalid(status: abi.ExportStatus) !void {
    try std.testing.expect(!export_shim.statusIsOk(status));
    try std.testing.expectEqual(@as(i32, -22), status.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), status.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), status.flags);
}

test "phase3 abi recognizes every valid interop-policy mode combination" {
    var count: usize = 0;

    for (valid_panic_modes) |panic_mode| {
        for (valid_allocator_modes) |allocator_mode| {
            for (valid_unsafe_scopes) |unsafe_scope| {
                const candidate = policy(panic_mode, allocator_mode, unsafe_scope, 0);
                count += 1;

                try std.testing.expect(abi.interopPolicyReservedClear(candidate));
                try std.testing.expect(abi.interopPolicyIsRecognized(candidate));
                try std.testing.expect(export_shim.interopPolicyIsRecognized(candidate));
                try std.testing.expectEqual(abi.panicModeFromInteropPolicy(candidate), export_shim.panicModeFromInteropPolicy(candidate));
                try std.testing.expectEqual(abi.allocatorModeFromInteropPolicy(candidate), export_shim.allocatorModeFromInteropPolicy(candidate));
                try std.testing.expectEqual(abi.unsafeScopeFromInteropPolicy(candidate), export_shim.unsafeScopeFromInteropPolicy(candidate));
                try expectKernelOk(export_shim.validateInteropPolicy(candidate));
            }
        }
    }

    try std.testing.expectEqual(@as(usize, 27), count);
}

test "phase3 abi rejects reserved-byte drift for otherwise valid policies" {
    for (valid_panic_modes) |panic_mode| {
        for (valid_allocator_modes) |allocator_mode| {
            for (valid_unsafe_scopes) |unsafe_scope| {
                const candidate = policy(panic_mode, allocator_mode, unsafe_scope, 1);

                try std.testing.expect(!abi.interopPolicyReservedClear(candidate));
                try std.testing.expectEqual(@as(?abi.PanicMode, null), abi.panicModeFromInteropPolicy(candidate));
                try std.testing.expectEqual(@as(?abi.AllocatorMode, null), abi.allocatorModeFromInteropPolicy(candidate));
                try std.testing.expectEqual(@as(?abi.UnsafeScope, null), abi.unsafeScopeFromInteropPolicy(candidate));
                try std.testing.expect(!abi.interopPolicyIsRecognized(candidate));
                try std.testing.expect(!export_shim.interopPolicyIsRecognized(candidate));
                try expectKernelInvalid(export_shim.validateInteropPolicy(candidate));
            }
        }
    }
}

test "phase3 abi rejects a single unknown byte without masking other valid lanes" {
    const unknown_panic = policy(0xFF, abi.ALLOC_KERNEL_HEAP, abi.UNSAFE_VOLATILE_MMIO, 0);
    const unknown_allocator = policy(abi.PANIC_WARN, 0xFF, abi.UNSAFE_RAW_POINTER_BRIDGE, 0);
    const unknown_scope = policy(abi.PANIC_BUG, abi.ALLOC_ARENA, 0xFF, 0);

    try std.testing.expectEqual(@as(?abi.PanicMode, null), abi.panicModeFromInteropPolicy(unknown_panic));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), abi.allocatorModeFromInteropPolicy(unknown_panic));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), abi.unsafeScopeFromInteropPolicy(unknown_panic));

    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), abi.panicModeFromInteropPolicy(unknown_allocator));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), abi.allocatorModeFromInteropPolicy(unknown_allocator));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), abi.unsafeScopeFromInteropPolicy(unknown_allocator));

    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), abi.panicModeFromInteropPolicy(unknown_scope));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), abi.allocatorModeFromInteropPolicy(unknown_scope));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), abi.unsafeScopeFromInteropPolicy(unknown_scope));

    try std.testing.expect(!abi.interopPolicyIsRecognized(unknown_panic));
    try std.testing.expect(!abi.interopPolicyIsRecognized(unknown_allocator));
    try std.testing.expect(!abi.interopPolicyIsRecognized(unknown_scope));

    try expectKernelInvalid(export_shim.validateInteropPolicy(unknown_panic));
    try expectKernelInvalid(export_shim.validateInteropPolicy(unknown_allocator));
    try expectKernelInvalid(export_shim.validateInteropPolicy(unknown_scope));
}

test "phase3 abi default policy remains the first recognized matrix cell" {
    const default_policy = abi.defaultInteropPolicy();
    const first_cell = policy(
        valid_panic_modes[0],
        valid_allocator_modes[0],
        valid_unsafe_scopes[0],
        0,
    );

    try std.testing.expectEqual(first_cell, default_policy);
    try std.testing.expectEqual(default_policy, export_shim.defaultInteropPolicy());
    try std.testing.expect(abi.interopPolicyIsRecognized(default_policy));
    try std.testing.expect(export_shim.interopPolicyIsRecognized(default_policy));
    try expectKernelOk(export_shim.validateInteropPolicy(default_policy));
}
