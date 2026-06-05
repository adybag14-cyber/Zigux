const std = @import("std");

const abi = @import("abi_bindings");
const export_shim = @import("export_shim");

const invalid_argument: i32 = -22;

fn expectKernelOk(status: abi.ExportStatus) !void {
    try std.testing.expect(export_shim.statusIsOk(status));
    try std.testing.expect(abi.statusIsOk(status));
    try std.testing.expect(export_shim.statusHasKnownFacility(status));
    try std.testing.expectEqual(@as(i32, 0), status.code);
    try std.testing.expectEqual(@as(u16, abi.FACILITY_KERNEL), status.facility);
    try std.testing.expectEqual(@as(u16, 0), status.flags);
}

fn expectKernelInvalid(status: abi.ExportStatus) !void {
    try std.testing.expect(!export_shim.statusIsOk(status));
    try std.testing.expect(!abi.statusIsOk(status));
    try std.testing.expect(export_shim.statusHasKnownFacility(status));
    try std.testing.expectEqual(@as(i32, invalid_argument), status.code);
    try std.testing.expectEqual(@as(u16, abi.FACILITY_KERNEL), status.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), status.flags);
}

test "export shim validates recognized interop policies through kernel status" {
    const safe = export_shim.defaultInteropPolicy();
    const mmio = abi.InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const raw = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };

    try std.testing.expect(std.meta.eql(abi.defaultInteropPolicy(), safe));
    try std.testing.expect(export_shim.interopPolicyIsRecognized(safe));
    try std.testing.expect(export_shim.interopPolicyIsRecognized(mmio));
    try std.testing.expect(export_shim.interopPolicyIsRecognized(raw));

    try expectKernelOk(export_shim.validateInteropPolicy(safe));
    try expectKernelOk(export_shim.validateInteropPolicy(mmio));
    try expectKernelOk(export_shim.validateInteropPolicy(raw));

    try std.testing.expect(std.meta.eql(abi.okStatus(.kernel), export_shim.validateInteropPolicy(safe)));
    try std.testing.expect(std.meta.eql(abi.okStatus(.kernel), export_shim.validateInteropPolicy(mmio)));
    try std.testing.expect(std.meta.eql(abi.okStatus(.kernel), export_shim.validateInteropPolicy(raw)));
}

test "export shim rejects reserved interop policy bytes before mode decoding" {
    const reserved = abi.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };

    try std.testing.expect(!abi.interopPolicyIsRecognized(reserved));
    try std.testing.expect(!export_shim.interopPolicyIsRecognized(reserved));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), export_shim.panicModeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), export_shim.allocatorModeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), export_shim.unsafeScopeFromInteropPolicy(reserved));

    const status = export_shim.validateInteropPolicy(reserved);
    try expectKernelInvalid(status);
    try std.testing.expect(std.meta.eql(abi.makeStatus(invalid_argument, .kernel), status));
}

test "export shim rejects unknown interop policy mode bytes consistently" {
    const unknown_panic = abi.InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const unknown_allocator = abi.InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = 9,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const unknown_scope = abi.InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = 9,
        .reserved = 0,
    };

    try std.testing.expect(!export_shim.interopPolicyIsRecognized(unknown_panic));
    try std.testing.expect(!export_shim.interopPolicyIsRecognized(unknown_allocator));
    try std.testing.expect(!export_shim.interopPolicyIsRecognized(unknown_scope));

    try expectKernelInvalid(export_shim.validateInteropPolicy(unknown_panic));
    try expectKernelInvalid(export_shim.validateInteropPolicy(unknown_allocator));
    try expectKernelInvalid(export_shim.validateInteropPolicy(unknown_scope));

    try std.testing.expectEqual(abi.panicModeFromInteropPolicy(unknown_panic), export_shim.panicModeFromInteropPolicy(unknown_panic));
    try std.testing.expectEqual(abi.allocatorModeFromInteropPolicy(unknown_allocator), export_shim.allocatorModeFromInteropPolicy(unknown_allocator));
    try std.testing.expectEqual(abi.unsafeScopeFromInteropPolicy(unknown_scope), export_shim.unsafeScopeFromInteropPolicy(unknown_scope));
}

test "export shim status helpers preserve facility recognition boundary" {
    const ok = export_shim.okStatus(.kernel);
    const invalid = export_shim.errorStatus(invalid_argument, .kernel);
    const unknown_facility = abi.ExportStatus{
        .code = 0,
        .facility = 9,
        .flags = 0,
    };

    try expectKernelOk(ok);
    try expectKernelInvalid(invalid);

    try std.testing.expectEqual(@as(?abi.Facility, .kernel), export_shim.facilityFromInt(ok.facility));
    try std.testing.expect(export_shim.facilityIsKnown(ok.facility));
    try std.testing.expect(export_shim.statusHasKnownFacility(ok));
    try std.testing.expectEqual(@as(?abi.Facility, null), export_shim.facilityFromInt(unknown_facility.facility));
    try std.testing.expect(!export_shim.facilityIsKnown(unknown_facility.facility));
    try std.testing.expect(!export_shim.statusHasKnownFacility(unknown_facility));
}
