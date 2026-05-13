const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const export_shim = @import("export_shim");
const layout_assert = @import("layout_assert");
const narrow_unsafe = @import("narrow_unsafe");
const panic_policy = @import("panic_policy");

test "phase3 abi keeps shared layout assertions wired into the abi replay" {
    try layout_assert.assertBoundaryHeaderLayout();
    try layout_assert.assertExportStatusLayout();
    try layout_assert.assertInteropPolicyLayout();
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout();
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout();
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout();
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout();
    layout_assert.assertInteropPolicyModeValues();
}

test "phase3 abi keeps exported status helpers and compatibility rules reviewable" {
    const canonical = export_shim.boundaryHeader(0x41);
    const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 16, 0x41);
    const version_mismatch = export_shim.versionedHeader(
        export_shim.header_size,
        export_shim.abi_version + 1,
        0x41,
    );

    const ok_status = export_shim.compatibilityStatus(canonical, -22, .kernel);
    try std.testing.expect(export_shim.isOk(ok_status));
    try std.testing.expectEqual(@as(i32, 0), ok_status.code);
    try std.testing.expectEqual(@as(u16, 0), ok_status.flags);

    const future_status = export_shim.compatibilityStatus(future_compatible, -75, .helpers);
    try std.testing.expect(export_shim.isOk(future_status));
    try std.testing.expectEqual(@as(i32, 0), future_status.code);

    const rejected = export_shim.compatibilityStatus(version_mismatch, -71, .drivers);
    try std.testing.expect(!export_shim.isOk(rejected));
    try std.testing.expectEqual(@as(i32, -71), rejected.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), rejected.flags);
}

test "phase3 abi keeps exported constants and family markers present" {
    try std.testing.expectEqual(@as(u16, 1), abi.FACILITY_KERNEL);
    try std.testing.expectEqual(@as(u16, 2), abi.FACILITY_HELPERS);
    try std.testing.expectEqual(@as(u16, 3), abi.FACILITY_DRIVERS);
    try std.testing.expectEqual(@as(u16, 1), abi.STATUS_FLAG_ERROR);
    try std.testing.expectEqual(@as(u8, 0), abi.PANIC_ABORT);
    try std.testing.expectEqual(@as(u8, 2), abi.ALLOC_ARENA);
    try std.testing.expectEqual(@as(u8, 2), abi.UNSAFE_RAW_POINTER_BRIDGE);

    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    );
}

test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {
    const caller_abort_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const heap_bug_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const arena_raw_policy = abi.InteropPolicy{
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

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(caller_abort_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromInteropPolicy(heap_bug_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(arena_raw_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, .abort_now), panic_policy.actionForInteropPolicy(caller_abort_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, .bug_check), panic_policy.actionForInteropPolicy(heap_bug_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, .warn_and_return), panic_policy.actionForInteropPolicy(arena_raw_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(caller_abort_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(heap_bug_policy));
    try std.testing.expect(panic_policy.canReturnInteropPolicy(arena_raw_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(reserved_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(unknown_policy));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(caller_abort_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(heap_bug_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(arena_raw_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(caller_abort_policy));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(heap_bug_policy));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(arena_raw_policy));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(reserved_policy));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(caller_abort_policy));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(heap_bug_policy));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(arena_raw_policy));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(reserved_policy));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(unknown_policy));

    try std.testing.expect(narrow_unsafe.permitsNoUnsafeInteropPolicy(caller_abort_policy));
    try std.testing.expect(!narrow_unsafe.permitsNoUnsafeInteropPolicy(heap_bug_policy));
    try std.testing.expect(!narrow_unsafe.permitsNoUnsafeInteropPolicy(arena_raw_policy));
    try std.testing.expect(!narrow_unsafe.permitsNoUnsafeInteropPolicy(reserved_policy));
    try std.testing.expect(narrow_unsafe.permitsVolatileMmioInteropPolicy(heap_bug_policy));
    try std.testing.expect(!narrow_unsafe.permitsVolatileMmioInteropPolicy(caller_abort_policy));
    try std.testing.expect(!narrow_unsafe.permitsVolatileMmioInteropPolicy(arena_raw_policy));
    try std.testing.expect(!narrow_unsafe.permitsVolatileMmioInteropPolicy(reserved_policy));
    try std.testing.expect(narrow_unsafe.permitsRawPointerBridgeInteropPolicy(arena_raw_policy));
    try std.testing.expect(!narrow_unsafe.permitsRawPointerBridgeInteropPolicy(caller_abort_policy));
    try std.testing.expect(!narrow_unsafe.permitsRawPointerBridgeInteropPolicy(heap_bug_policy));
    try std.testing.expect(!narrow_unsafe.permitsRawPointerBridgeInteropPolicy(reserved_policy));
    try std.testing.expect(!narrow_unsafe.recognizesInteropPolicy(unknown_policy));
    try narrow_unsafe.requireNoUnsafeInteropPolicy(caller_abort_policy);
    try narrow_unsafe.requireVolatileMmioInteropPolicy(heap_bug_policy);
    try narrow_unsafe.requireRawPointerBridgeInteropPolicy(arena_raw_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireNoUnsafeInteropPolicy(arena_raw_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireVolatileMmioInteropPolicy(caller_abort_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireRawPointerBridgeInteropPolicy(caller_abort_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireRawPointerBridgeInteropPolicy(reserved_policy));
}

test "phase3 abi keeps dev_t sample encoding and kernel relay status explicit" {
    const minor_bits: u5 = 20;
    const minor_mask: u32 = 1_048_575;
    const max_major: u32 = 4_095;
    const sample_major: u32 = 42;
    const sample_minor: u32 = 7;
    const range_count: u32 = 4;

    const encoded = export_shim.encodeDeviceNumber(sample_major, sample_minor, .kernel);
    try std.testing.expect(export_shim.isOk(encoded.status));
    try std.testing.expectEqual(@as(u32, 44_040_199), encoded.value);
    try std.testing.expectEqual(@as(u32, sample_major), encoded.value >> minor_bits);
    try std.testing.expectEqual(@as(u32, sample_minor), encoded.value & minor_mask);

    const range_last = export_shim.lastDeviceNumberInRange(sample_major, sample_minor, range_count, .helpers);
    try std.testing.expect(export_shim.isOk(range_last.status));
    try std.testing.expect(sample_minor + range_count - 1 <= minor_mask);
    try std.testing.expectEqual(@as(u32, 44_040_202), range_last.value);

    const bad_major = export_shim.encodeDeviceNumber(max_major + 1, sample_minor, .drivers);
    try std.testing.expect(!export_shim.isOk(bad_major.status));
    try std.testing.expectEqual(@as(i32, -22), bad_major.status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), bad_major.status.flags);

    const bad_range = export_shim.lastDeviceNumberInRange(sample_major, minor_mask - 1, 3, .helpers);
    try std.testing.expect(!export_shim.isOk(bad_range.status));
    try std.testing.expectEqual(@as(i32, -34), bad_range.status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), bad_range.status.flags);
}
