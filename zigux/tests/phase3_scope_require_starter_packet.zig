const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");
const scope_require = @import("scope_require");
const unsafe_policy = @import("unsafe_policy");

fn expectRequireNoUnsafe(unsafe_scope: u8, reserved: u8, expected_ok: bool) !void {
    if (expected_ok) {
        try scope_require.requireNoUnsafePolicyBytes(unsafe_scope, reserved);
        try narrow.requireNoUnsafePolicyBytes(unsafe_scope, reserved);
    } else {
        try testing.expectError(
            error.UnsafeScopeDenied,
            scope_require.requireNoUnsafePolicyBytes(unsafe_scope, reserved),
        );
        try testing.expectError(
            error.UnsafeScopeDenied,
            narrow.requireNoUnsafePolicyBytes(unsafe_scope, reserved),
        );
    }
}

fn expectRequireVolatileMmio(unsafe_scope: u8, reserved: u8, expected_ok: bool) !void {
    if (expected_ok) {
        try scope_require.requireVolatileMmioPolicyBytes(unsafe_scope, reserved);
        try narrow.requireVolatileMmioPolicyBytes(unsafe_scope, reserved);
    } else {
        try testing.expectError(
            error.UnsafeScopeDenied,
            scope_require.requireVolatileMmioPolicyBytes(unsafe_scope, reserved),
        );
        try testing.expectError(
            error.UnsafeScopeDenied,
            narrow.requireVolatileMmioPolicyBytes(unsafe_scope, reserved),
        );
    }
}

fn expectRequireRawPointerBridge(unsafe_scope: u8, reserved: u8, expected_ok: bool) !void {
    if (expected_ok) {
        try scope_require.requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
        try narrow.requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    } else {
        try testing.expectError(
            error.UnsafeScopeDenied,
            scope_require.requireRawPointerBridgePolicyBytes(unsafe_scope, reserved),
        );
        try testing.expectError(
            error.UnsafeScopeDenied,
            narrow.requireRawPointerBridgePolicyBytes(unsafe_scope, reserved),
        );
    }
}

test "phase3 scope require starter packet keeps typed scope gates aligned" {
    const cases = [_]struct {
        scope: abi.UnsafeScope,
        allow_no_unsafe: bool,
        allow_volatile_mmio: bool,
        allow_raw_pointer_bridge: bool,
    }{
        .{ .scope = .none, .allow_no_unsafe = true, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = false },
        .{ .scope = .volatile_mmio, .allow_no_unsafe = false, .allow_volatile_mmio = true, .allow_raw_pointer_bridge = false },
        .{ .scope = .raw_pointer_bridge, .allow_no_unsafe = false, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = true },
    };

    for (cases) |case| {
        try testing.expectEqual(case.allow_no_unsafe, narrow.permitsNoUnsafe(case.scope));
        try testing.expectEqual(case.allow_volatile_mmio, narrow.permitsVolatileMmio(case.scope));
        try testing.expectEqual(case.allow_raw_pointer_bridge, narrow.permitsRawPointerBridge(case.scope));
        try testing.expectEqual(case.allow_no_unsafe, unsafe_policy.permitsNoUnsafe(case.scope));
        try testing.expectEqual(case.allow_volatile_mmio, unsafe_policy.permitsVolatileMmio(case.scope));
        try testing.expectEqual(case.allow_raw_pointer_bridge, unsafe_policy.permitsRawPointerBridge(case.scope));

        if (case.allow_no_unsafe) {
            try scope_require.requireNoUnsafe(case.scope);
        } else {
            try testing.expectError(error.UnsafeScopeDenied, scope_require.requireNoUnsafe(case.scope));
        }

        if (case.allow_volatile_mmio) {
            try scope_require.requireVolatileMmio(case.scope);
        } else {
            try testing.expectError(error.UnsafeScopeDenied, scope_require.requireVolatileMmio(case.scope));
        }

        if (case.allow_raw_pointer_bridge) {
            try scope_require.requireRawPointerBridge(case.scope);
        } else {
            try testing.expectError(error.UnsafeScopeDenied, scope_require.requireRawPointerBridge(case.scope));
        }
    }
}

test "phase3 scope require starter packet keeps policy-byte gates aligned" {
    const cases = [_]struct {
        unsafe_scope: u8,
        reserved: u8,
        allow_no_unsafe: bool,
        allow_volatile_mmio: bool,
        allow_raw_pointer_bridge: bool,
    }{
        .{ .unsafe_scope = 0, .reserved = 0, .allow_no_unsafe = true, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = false },
        .{ .unsafe_scope = 1, .reserved = 0, .allow_no_unsafe = false, .allow_volatile_mmio = true, .allow_raw_pointer_bridge = false },
        .{ .unsafe_scope = 2, .reserved = 0, .allow_no_unsafe = false, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = true },
        .{ .unsafe_scope = 9, .reserved = 0, .allow_no_unsafe = false, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = false },
        .{ .unsafe_scope = 2, .reserved = 1, .allow_no_unsafe = false, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = false },
    };

    for (cases) |case| {
        try testing.expectEqual(
            case.allow_no_unsafe,
            unsafe_policy.permitsNoUnsafePolicyBytes(case.unsafe_scope, case.reserved),
        );
        try testing.expectEqual(
            case.allow_volatile_mmio,
            unsafe_policy.permitsVolatileMmioPolicyBytes(case.unsafe_scope, case.reserved),
        );
        try testing.expectEqual(
            case.allow_raw_pointer_bridge,
            unsafe_policy.permitsRawPointerBridgePolicyBytes(case.unsafe_scope, case.reserved),
        );

        try expectRequireNoUnsafe(case.unsafe_scope, case.reserved, case.allow_no_unsafe);
        try expectRequireVolatileMmio(case.unsafe_scope, case.reserved, case.allow_volatile_mmio);
        try expectRequireRawPointerBridge(
            case.unsafe_scope,
            case.reserved,
            case.allow_raw_pointer_bridge,
        );
    }
}

test "phase3 scope require starter packet keeps byte shorthand entry points aligned" {
    const cases = [_]struct {
        unsafe_scope: u8,
        allow_no_unsafe: bool,
        allow_volatile_mmio: bool,
        allow_raw_pointer_bridge: bool,
    }{
        .{ .unsafe_scope = 0, .allow_no_unsafe = true, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = false },
        .{ .unsafe_scope = 1, .allow_no_unsafe = false, .allow_volatile_mmio = true, .allow_raw_pointer_bridge = false },
        .{ .unsafe_scope = 2, .allow_no_unsafe = false, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = true },
        .{ .unsafe_scope = 9, .allow_no_unsafe = false, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = false },
    };

    for (cases) |case| {
        try testing.expectEqual(case.allow_no_unsafe, unsafe_policy.permitsNoUnsafeByte(case.unsafe_scope));
        try testing.expectEqual(case.allow_no_unsafe, narrow.permitsNoUnsafeByte(case.unsafe_scope));
        try testing.expectEqual(case.allow_volatile_mmio, unsafe_policy.permitsVolatileMmioByte(case.unsafe_scope));
        try testing.expectEqual(case.allow_volatile_mmio, narrow.permitsVolatileMmioByte(case.unsafe_scope));
        try testing.expectEqual(case.allow_raw_pointer_bridge, unsafe_policy.permitsRawPointerBridgeByte(case.unsafe_scope));
        try testing.expectEqual(case.allow_raw_pointer_bridge, narrow.permitsRawPointerBridgeByte(case.unsafe_scope));

        if (case.allow_no_unsafe) {
            try scope_require.requireNoUnsafeByte(case.unsafe_scope);
            try narrow.requireNoUnsafeByte(case.unsafe_scope);
        } else {
            try testing.expectError(
                error.UnsafeScopeDenied,
                scope_require.requireNoUnsafeByte(case.unsafe_scope),
            );
            try testing.expectError(
                error.UnsafeScopeDenied,
                narrow.requireNoUnsafeByte(case.unsafe_scope),
            );
        }

        if (case.allow_volatile_mmio) {
            try scope_require.requireVolatileMmioByte(case.unsafe_scope);
            try narrow.requireVolatileMmioByte(case.unsafe_scope);
        } else {
            try testing.expectError(
                error.UnsafeScopeDenied,
                scope_require.requireVolatileMmioByte(case.unsafe_scope),
            );
            try testing.expectError(
                error.UnsafeScopeDenied,
                narrow.requireVolatileMmioByte(case.unsafe_scope),
            );
        }

        if (case.allow_raw_pointer_bridge) {
            try scope_require.requireRawPointerBridgeByte(case.unsafe_scope);
            try narrow.requireRawPointerBridgeByte(case.unsafe_scope);
        } else {
            try testing.expectError(
                error.UnsafeScopeDenied,
                scope_require.requireRawPointerBridgeByte(case.unsafe_scope),
            );
            try testing.expectError(
                error.UnsafeScopeDenied,
                narrow.requireRawPointerBridgeByte(case.unsafe_scope),
            );
        }
    }
}

test "phase3 scope require starter packet keeps typed interop-policy relays explicit" {
    const cases = [_]struct {
        policy: abi.InteropPolicy,
        allow_no_unsafe: bool,
        allow_volatile_mmio: bool,
        allow_raw_pointer_bridge: bool,
    }{
        .{ .policy = .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 }, .allow_no_unsafe = true, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = false },
        .{ .policy = .{ .panic_mode = 1, .allocator_mode = 1, .unsafe_scope = 1, .reserved = 0 }, .allow_no_unsafe = false, .allow_volatile_mmio = true, .allow_raw_pointer_bridge = false },
        .{ .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 0 }, .allow_no_unsafe = false, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = true },
        .{ .policy = .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 9, .reserved = 0 }, .allow_no_unsafe = false, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = false },
        .{ .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 1 }, .allow_no_unsafe = false, .allow_volatile_mmio = false, .allow_raw_pointer_bridge = false },
    };

    for (cases) |case| {
        try testing.expectEqual(case.allow_no_unsafe, unsafe_policy.permitsNoUnsafeInteropPolicy(case.policy));
        try testing.expectEqual(case.allow_volatile_mmio, unsafe_policy.permitsVolatileMmioInteropPolicy(case.policy));
        try testing.expectEqual(case.allow_raw_pointer_bridge, unsafe_policy.permitsRawPointerBridgeInteropPolicy(case.policy));

        if (case.allow_no_unsafe) {
            try scope_require.requireNoUnsafeInteropPolicy(case.policy);
            try narrow.requireNoUnsafeInteropPolicy(case.policy);
        } else {
            try testing.expectError(
                error.UnsafeScopeDenied,
                scope_require.requireNoUnsafeInteropPolicy(case.policy),
            );
            try testing.expectError(
                error.UnsafeScopeDenied,
                narrow.requireNoUnsafeInteropPolicy(case.policy),
            );
        }

        if (case.allow_volatile_mmio) {
            try scope_require.requireVolatileMmioInteropPolicy(case.policy);
            try narrow.requireVolatileMmioInteropPolicy(case.policy);
        } else {
            try testing.expectError(
                error.UnsafeScopeDenied,
                scope_require.requireVolatileMmioInteropPolicy(case.policy),
            );
            try testing.expectError(
                error.UnsafeScopeDenied,
                narrow.requireVolatileMmioInteropPolicy(case.policy),
            );
        }

        if (case.allow_raw_pointer_bridge) {
            try scope_require.requireRawPointerBridgeInteropPolicy(case.policy);
            try narrow.requireRawPointerBridgeInteropPolicy(case.policy);
        } else {
            try testing.expectError(
                error.UnsafeScopeDenied,
                scope_require.requireRawPointerBridgeInteropPolicy(case.policy),
            );
            try testing.expectError(
                error.UnsafeScopeDenied,
                narrow.requireRawPointerBridgeInteropPolicy(case.policy),
            );
        }
    }
}
