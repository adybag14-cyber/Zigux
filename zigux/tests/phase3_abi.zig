const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const dev_t = @import("dev_t_binding");
const export_shim = @import("export_shim");
const narrow_unsafe = @import("narrow_unsafe");
const panic_policy = @import("panic_policy");
const unsafe_policy = @import("unsafe_policy");
const version = @import("version_binding");

test "phase3 abi keeps boundary header and status layout explicit" {
    const header = export_shim.canonicalHeader(0x41);
    const ok = export_shim.okStatus(.helpers);
    const err = export_shim.errorStatus(-12, .kernel);

    try testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), header.size);
    try testing.expectEqual(@as(u16, abi.ABI_VERSION), header.abi_version);
    try testing.expectEqual(@as(u16, 0x41), header.flags);

    try testing.expectEqual(@as(usize, 8), @sizeOf(abi.BoundaryHeader));
    try testing.expectEqual(@as(usize, 4), @alignOf(abi.BoundaryHeader));
    try testing.expectEqual(@as(usize, 0), @offsetOf(abi.BoundaryHeader, "size"));
    try testing.expectEqual(@as(usize, 4), @offsetOf(abi.BoundaryHeader, "abi_version"));
    try testing.expectEqual(@as(usize, 6), @offsetOf(abi.BoundaryHeader, "flags"));

    try testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));
    try testing.expectEqual(@as(usize, 4), @alignOf(abi.ExportStatus));
    try testing.expectEqual(@as(usize, 0), @offsetOf(abi.ExportStatus, "code"));
    try testing.expectEqual(@as(usize, 4), @offsetOf(abi.ExportStatus, "facility"));
    try testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));

    try testing.expectEqual(@as(i32, 0), ok.code);
    try testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.helpers)), ok.facility);
    try testing.expectEqual(@as(u16, 0), ok.flags);

    try testing.expectEqual(@as(i32, -12), err.code);
    try testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), err.facility);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), err.flags);
}

test "phase3 abi keeps default header and interop policy reviewable" {
    const header = abi.defaultHeader(0);
    const policy = abi.defaultInteropPolicy();

    try testing.expect(abi.headerIsCanonical(header));
    try testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), header.size);
    try testing.expectEqual(@as(u16, abi.ABI_VERSION), header.abi_version);
    try testing.expectEqual(@as(u16, 0), header.flags);

    try testing.expectEqual(@as(u8, @intFromEnum(abi.PanicMode.abort)), policy.panic_mode);
    try testing.expectEqual(@as(u8, @intFromEnum(abi.AllocatorMode.caller_provided)), policy.allocator_mode);
    try testing.expectEqual(@as(u8, @intFromEnum(abi.UnsafeScope.none)), policy.unsafe_scope);
    try testing.expectEqual(@as(u8, 0), policy.reserved);

    try testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(policy));
    try testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(policy));
    try testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.modeFromInteropPolicy(policy));
    try testing.expectEqual(@as(?narrow_unsafe.UnsafeScopeTag, .none), narrow_unsafe.scopeFromInteropPolicy(policy));

    try testing.expect(panic_policy.causesImmediateHaltInteropPolicy(policy));
    try testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(policy));
    try testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(policy));
    try testing.expect(unsafe_policy.permitsNoUnsafeInteropPolicy(policy));
    try testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(policy));
    try testing.expect(!unsafe_policy.permitsRawPointerBridgeInteropPolicy(policy));
    try testing.expect(narrow_unsafe.permitsNoUnsafeInteropPolicy(policy));
    try testing.expect(!narrow_unsafe.requiresDedicatedAuditInteropPolicy(policy));
}

test "phase3 abi keeps version and dev_t starter helpers aligned" {
    const current = export_shim.currentVersion();
    const fields = export_shim.makeDevTFields(11, 29);
    const same = export_shim.makeDevTFields(11, 29);
    const different = export_shim.makeDevTFields(11, 30);

    try testing.expectEqual(@as(u32, version.abi_major), current.abi_major);
    try testing.expectEqual(@as(u32, version.abi_minor), current.abi_minor);
    try testing.expectEqual(@as(u32, version.header_family_revision), current.header_family_revision);
    try testing.expect(version.eql(version.current(), current));

    try testing.expectEqual(@as(usize, 8), @sizeOf(export_shim.DevTFields));
    try testing.expectEqual(@as(usize, 4), @alignOf(export_shim.DevTFields));
    try testing.expectEqual(@as(u32, 11), fields.major);
    try testing.expectEqual(@as(u32, 29), fields.minor);
    try testing.expect(dev_t.eql(fields, same));
    try testing.expect(!dev_t.eql(fields, different));
}

test "phase3 abi keeps policy helpers decoding the same interop bytes" {
    const safe_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
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

    try testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(safe_policy));
    try testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromInteropPolicy(mmio_policy));
    try testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(raw_policy));
    try testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));

    try testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(safe_policy));
    try testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(mmio_policy));
    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(raw_policy));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved_policy));

    try testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.modeFromInteropPolicy(safe_policy));
    try testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), unsafe_policy.modeFromInteropPolicy(mmio_policy));
    try testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.modeFromInteropPolicy(raw_policy));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.modeFromInteropPolicy(reserved_policy));

    try testing.expectEqual(@as(?narrow_unsafe.UnsafeScopeTag, .none), narrow_unsafe.scopeFromInteropPolicy(safe_policy));
    try testing.expectEqual(@as(?narrow_unsafe.UnsafeScopeTag, .volatile_mmio), narrow_unsafe.scopeFromInteropPolicy(mmio_policy));
    try testing.expectEqual(@as(?narrow_unsafe.UnsafeScopeTag, .raw_pointer_bridge), narrow_unsafe.scopeFromInteropPolicy(raw_policy));
    try testing.expectEqual(@as(?narrow_unsafe.UnsafeScopeTag, null), narrow_unsafe.scopeFromInteropPolicy(reserved_policy));

    try testing.expect(panic_policy.causesImmediateHaltInteropPolicy(safe_policy));
    try testing.expect(panic_policy.emitsKernelBugInteropPolicy(mmio_policy));
    try testing.expect(panic_policy.permitsWarningOnlyContinuationInteropPolicy(raw_policy));

    try testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(safe_policy));
    try testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(mmio_policy));
    try testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(raw_policy));

    try testing.expect(unsafe_policy.permitsNoUnsafeInteropPolicy(safe_policy));
    try testing.expect(unsafe_policy.permitsVolatileMmioInteropPolicy(mmio_policy));
    try testing.expect(unsafe_policy.permitsRawPointerBridgeInteropPolicy(raw_policy));
    try testing.expect(!unsafe_policy.recognizesInteropPolicy(reserved_policy));

    try testing.expect(!narrow_unsafe.requiresDedicatedAuditInteropPolicy(safe_policy));
    try testing.expect(narrow_unsafe.allowsVolatileMmioInteropPolicy(mmio_policy));
    try testing.expect(narrow_unsafe.allowsRawPointerBridgeInteropPolicy(raw_policy));
    try testing.expect(!narrow_unsafe.recognizesInteropPolicy(reserved_policy));
}

test "phase3 abi keeps notifier and shared constants reviewable" {
    const tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 3,
    };
    const middle = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 5,
    };
    const head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&middle),
        .priority = 5,
    };

    try testing.expectEqual(@as(u16, 1), abi.FACILITY_KERNEL);
    try testing.expectEqual(@as(u16, 2), abi.FACILITY_HELPERS);
    try testing.expectEqual(@as(u16, 3), abi.FACILITY_DRIVERS);
    try testing.expectEqual(@as(u16, 1), abi.STATUS_FLAG_ERROR);
    try testing.expectEqual(@as(u8, 0), abi.PANIC_ABORT);
    try testing.expectEqual(@as(u8, 2), abi.ALLOC_ARENA);
    try testing.expectEqual(@as(u8, 2), abi.UNSAFE_RAW_POINTER_BRIDGE);
    try testing.expectEqual(@as(u32, 1), abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED);
    try testing.expectEqual(@as(u32, 1), abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED);
    try testing.expectEqual(@as(u32, 1), abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED);
    try testing.expectEqual(@as(u32, 1), abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED);

    try testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(abi.NotifierBlock));
    try testing.expectEqual(@as(usize, 0), @offsetOf(abi.NotifierBlock, "notifier_call"));
    try testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(abi.NotifierBlock, "next"));
    try testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(abi.NotifierBlock, "priority"));

    try testing.expect(abi.chainHasNonincreasingPriority(&head));
}