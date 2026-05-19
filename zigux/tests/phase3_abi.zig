const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const export_shim = @import("export_shim");
const layout_assert = @import("layout_assert");
const panic_policy = @import("panic_policy");
const unsafe_policy = @import("unsafe_policy");

test "phase3 abi keeps shared layout assertions wired into the replay" {
    try layout_assert.assertBoundaryHeaderLayout();
    try layout_assert.assertExportStatusLayout();
    try layout_assert.assertInteropPolicyLayout();
    try layout_assert.assertNotifierBlockLayout();
    try layout_assert.assertNotifierChainPriorityIncreaseLayout();
    layout_assert.assertInteropPolicyModeValues();
    layout_assert.assertNotifierResultValues();
}

test "phase3 abi keeps export shim compatibility and status helpers reviewable" {
    const canonical = export_shim.canonicalHeader(0x41);
    const expanded = abi.compatibleHeader(export_shim.header_size + 16, 0x41);
    const stale = export_shim.BoundaryHeader{
        .size = export_shim.header_size,
        .abi_version = export_shim.abi_version + 1,
        .flags = 0,
    };
    const canonicalized = export_shim.canonicalizeHeader(expanded);

    try std.testing.expect(export_shim.headerIsCanonical(canonical));
    try std.testing.expect(export_shim.headerIsCompatible(canonical));
    try std.testing.expect(!export_shim.extendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(canonical));

    try std.testing.expect(!export_shim.headerIsCanonical(expanded));
    try std.testing.expect(export_shim.headerIsCompatible(expanded));
    try std.testing.expect(export_shim.extendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 16), export_shim.requestedExtraBytes(expanded));

    try std.testing.expect(!export_shim.headerIsCanonical(stale));
    try std.testing.expect(!export_shim.headerIsCompatible(stale));
    try std.testing.expect(!export_shim.extendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, export_shim.header_size), canonicalized.size);
    try std.testing.expectEqual(@as(u16, export_shim.abi_version), canonicalized.abi_version);
    try std.testing.expectEqual(expanded.flags, canonicalized.flags);

    const ok = export_shim.okStatus(.helpers);
    const err = export_shim.errorStatus(-71, .drivers);
    const positive = export_shim.errorStatus(7, .kernel);
    const abi_ok = abi.okStatus(.helpers);
    const abi_err = abi.makeStatus(-71, .drivers);
    const abi_positive = abi.makeStatus(7, .kernel);

    try std.testing.expect(export_shim.statusIsOk(ok));
    try std.testing.expectEqual(@as(i32, 0), ok.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.helpers)), ok.facility);
    try std.testing.expectEqual(@as(u16, 0), ok.flags);
    try std.testing.expect(std.meta.eql(ok, abi_ok));

    try std.testing.expect(!export_shim.statusIsOk(err));
    try std.testing.expectEqual(@as(i32, -71), err.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.drivers)), err.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), err.flags);
    try std.testing.expect(std.meta.eql(err, abi_err));

    try std.testing.expect(export_shim.statusIsOk(positive));
    try std.testing.expectEqual(@as(i32, 7), positive.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), positive.facility);
    try std.testing.expectEqual(@as(u16, 0), positive.flags);
    try std.testing.expect(std.meta.eql(positive, abi_positive));
}

test "phase3 abi keeps version and dev_t relays explicit" {
    const current = export_shim.currentVersion();
    const fields = export_shim.makeDevTFields(42, 7);
    const valid = export_shim.validateDeviceNumber(42, 7);
    const invalid = export_shim.validateDeviceNumber(4_096, 0);
    const valid_range = export_shim.validateDeviceRange(
        export_shim.makeDevTFields(42, 7),
        export_shim.makeDevTFields(42, 9),
    );
    const invalid_range = export_shim.validateDeviceRange(
        export_shim.makeDevTFields(42, 9),
        export_shim.makeDevTFields(42, 7),
    );

    try std.testing.expectEqual(@as(u32, 0), current.abi_major);
    try std.testing.expectEqual(@as(u32, 1), current.abi_minor);
    try std.testing.expectEqual(@as(u32, 1), current.header_family_revision);

    try std.testing.expectEqual(@as(u32, 42), fields.major);
    try std.testing.expectEqual(@as(u32, 7), fields.minor);

    try std.testing.expect(export_shim.statusIsOk(valid));
    try std.testing.expect(!export_shim.statusIsOk(invalid));
    try std.testing.expectEqual(@as(i32, -22), invalid.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid.flags);

    try std.testing.expect(export_shim.statusIsOk(valid_range));
    try std.testing.expect(!export_shim.statusIsOk(invalid_range));
    try std.testing.expectEqual(@as(i32, -22), invalid_range.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_range.flags);
}

test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {
    const safe_policy = abi.defaultInteropPolicy();
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = 9,
        .unsafe_scope = 9,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .kernel_bug), panic_policy.escalationFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .warning_only), panic_policy.escalationFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expect(panic_policy.causesImmediateHaltInteropPolicy(safe_policy));
    try std.testing.expect(panic_policy.causesImmediateHaltInteropPolicy(mmio_policy));
    try std.testing.expect(!panic_policy.causesImmediateHaltInteropPolicy(raw_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved_policy));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(safe_policy));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(mmio_policy));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(mmio_policy));
    try std.testing.expect(allocator_policy.requiresResetOnInitInteropPolicy(raw_policy));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(reserved_policy));

    try std.testing.expect(unsafe_policy.permitsNoUnsafeInteropPolicy(safe_policy));
    try std.testing.expect(!unsafe_policy.permitsNoUnsafeInteropPolicy(mmio_policy));
    try std.testing.expect(unsafe_policy.permitsVolatileMmioInteropPolicy(mmio_policy));
    try std.testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(raw_policy));
    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(unsafe_policy.requiresDedicatedAuditInteropPolicy(raw_policy));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(unknown_policy));
}