const std = @import("std");
const abi = @import("abi_bindings");
const mmio = @import("mmio");

pub const MmioRangeAdmissionKind = enum {
    empty_window,
    contiguous_window,
    strided_window,
    denied_scope,
    invalid_policy_or_window,
};

pub const MmioRangeAdmission = struct {
    kind: MmioRangeAdmissionKind,
    range: ?mmio.MmioRange = null,

    pub fn isAdmitted(self: MmioRangeAdmission) bool {
        return rangeIsAdmitted(self.kind);
    }
};

pub const MmioAccessAdmissionKind = enum {
    admitted,
    misaligned,
    stride_mismatch,
    outside_range,
    address_overflow,
};

pub const MmioAccessAdmission = struct {
    kind: MmioAccessAdmissionKind,
    byte_offset: usize,
    byte_len: usize,

    pub fn isAdmitted(self: MmioAccessAdmission) bool {
        return self.kind == .admitted;
    }
};

pub const RangeAdmissionError = mmio.PolicyError;

pub const AccessAdmissionError = error{
    MisalignedAccess,
    StrideMismatch,
    AccessOutsideRange,
    AddressOverflow,
};

fn admittedRangeKind(range: mmio.MmioRange) MmioRangeAdmissionKind {
    if (range.length == 0) return .empty_window;
    if (range.stride == 0) return .contiguous_window;
    return .strided_window;
}

fn rangeAdmissionFromResult(result: RangeAdmissionError!mmio.MmioRange) MmioRangeAdmission {
    const range = result catch |err| {
        return .{ .kind = switch (err) {
            error.UnsafeScopeDenied => .denied_scope,
            error.InvalidInteropPolicy => .invalid_policy_or_window,
        } };
    };

    return .{
        .kind = admittedRangeKind(range),
        .range = range,
    };
}

pub fn rangeIsAdmitted(kind: MmioRangeAdmissionKind) bool {
    return switch (kind) {
        .empty_window,
        .contiguous_window,
        .strided_window,
        => true,
        .denied_scope,
        .invalid_policy_or_window,
        => false,
    };
}

pub fn classifyRangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) MmioRangeAdmission {
    return rangeAdmissionFromResult(mmio.rangeScoped(base_addr, length, stride, scope));
}

pub fn classifyRangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) MmioRangeAdmission {
    return rangeAdmissionFromResult(mmio.rangeInteropPolicy(base_addr, length, stride, policy));
}

pub fn classifyRangeInteropPolicyBytes(
    base_addr: usize,
    length: u32,
    stride: u32,
    unsafe_scope: u8,
    reserved: u8,
) MmioRangeAdmission {
    return rangeAdmissionFromResult(mmio.rangeInteropPolicyBytes(base_addr, length, stride, unsafe_scope, reserved));
}

pub fn classifyRangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) MmioRangeAdmission {
    return classifyRangeInteropPolicyBytes(base_addr, length, stride, unsafe_scope, 0);
}

pub fn requireRangeScoped(base_addr: usize, length: u32, stride: u32, scope: abi.UnsafeScope) RangeAdmissionError!mmio.MmioRange {
    return mmio.rangeScoped(base_addr, length, stride, scope);
}

pub fn requireRangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) RangeAdmissionError!mmio.MmioRange {
    return mmio.rangeInteropPolicy(base_addr, length, stride, policy);
}

pub fn requireRangeInteropPolicyBytes(
    base_addr: usize,
    length: u32,
    stride: u32,
    unsafe_scope: u8,
    reserved: u8,
) RangeAdmissionError!mmio.MmioRange {
    return mmio.rangeInteropPolicyBytes(base_addr, length, stride, unsafe_scope, reserved);
}

pub fn requireRangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) RangeAdmissionError!mmio.MmioRange {
    return requireRangeInteropPolicyBytes(base_addr, length, stride, unsafe_scope, 0);
}

pub fn classifyAccess(comptime T: type, range: mmio.MmioRange, byte_offset: usize) MmioAccessAdmission {
    const byte_len = @sizeOf(T);
    const range_len: usize = @intCast(range.length);
    const stride: usize = @intCast(range.stride);

    if ((byte_offset % @alignOf(T)) != 0) {
        return .{ .kind = .misaligned, .byte_offset = byte_offset, .byte_len = byte_len };
    }

    if (stride != 0 and (byte_offset % stride) != 0) {
        return .{ .kind = .stride_mismatch, .byte_offset = byte_offset, .byte_len = byte_len };
    }

    const access_end = std.math.add(usize, byte_offset, byte_len) catch {
        return .{ .kind = .outside_range, .byte_offset = byte_offset, .byte_len = byte_len };
    };
    if (access_end > range_len) {
        return .{ .kind = .outside_range, .byte_offset = byte_offset, .byte_len = byte_len };
    }

    _ = std.math.add(usize, range.base_addr, byte_offset) catch {
        return .{ .kind = .address_overflow, .byte_offset = byte_offset, .byte_len = byte_len };
    };

    return .{ .kind = .admitted, .byte_offset = byte_offset, .byte_len = byte_len };
}

pub fn accessIsAdmitted(comptime T: type, range: mmio.MmioRange, byte_offset: usize) bool {
    return classifyAccess(T, range, byte_offset).isAdmitted();
}

pub fn requireAccess(comptime T: type, range: mmio.MmioRange, byte_offset: usize) AccessAdmissionError!void {
    return switch (classifyAccess(T, range, byte_offset).kind) {
        .admitted => {},
        .misaligned => error.MisalignedAccess,
        .stride_mismatch => error.StrideMismatch,
        .outside_range => error.AccessOutsideRange,
        .address_overflow => error.AddressOverflow,
    };
}

pub fn requireConstPointerAt(comptime T: type, range: mmio.MmioRange, byte_offset: usize) AccessAdmissionError!*const volatile T {
    try requireAccess(T, range, byte_offset);
    return mmio.constPointerAt(T, range, byte_offset) catch error.AddressOverflow;
}

pub fn requirePointerAt(comptime T: type, range: mmio.MmioRange, byte_offset: usize) AccessAdmissionError!*volatile T {
    try requireAccess(T, range, byte_offset);
    return mmio.pointerAt(T, range, byte_offset) catch error.AddressOverflow;
}

test "phase3 mmio guard classifies range admission without widening mmio helpers" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };
    const near_end = std.math.maxInt(usize) - 3;

    const empty = classifyRangeScoped(0x1000, 0, 0, .volatile_mmio);
    try std.testing.expect(empty.isAdmitted());
    try std.testing.expectEqual(MmioRangeAdmissionKind.empty_window, empty.kind);
    try std.testing.expectEqual(@as(u32, 0), empty.range.?.length);

    const contiguous = classifyRangeInteropPolicy(0x2000, 16, 0, mmio_policy);
    try std.testing.expect(contiguous.isAdmitted());
    try std.testing.expectEqual(MmioRangeAdmissionKind.contiguous_window, contiguous.kind);

    const strided = classifyRangeInteropPolicyByte(0x3000, 16, 4, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expect(strided.isAdmitted());
    try std.testing.expectEqual(MmioRangeAdmissionKind.strided_window, strided.kind);

    try std.testing.expect(!classifyRangeScoped(0x1000, 16, 0, .none).isAdmitted());
    try std.testing.expectEqual(MmioRangeAdmissionKind.denied_scope, classifyRangeScoped(0x1000, 16, 0, .raw_pointer_bridge).kind);
    try std.testing.expectEqual(
        MmioRangeAdmissionKind.invalid_policy_or_window,
        classifyRangeInteropPolicy(0x2000, 16, 0, reserved_policy).kind,
    );
    try std.testing.expectEqual(
        MmioRangeAdmissionKind.invalid_policy_or_window,
        classifyRangeInteropPolicyBytes(near_end, 5, 1, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0).kind,
    );
}

test "phase3 mmio guard require helpers return the blessed range record" {
    const mmio_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);
    const range = try requireRangeInteropPolicyByte(0x4000, 32, 8, mmio_scope);

    try std.testing.expectEqual(@as(usize, 0x4000), range.base_addr);
    try std.testing.expectEqual(@as(u32, 32), range.length);
    try std.testing.expectEqual(@as(u32, 8), range.stride);
    try std.testing.expectError(error.UnsafeScopeDenied, requireRangeInteropPolicyByte(0x4000, 32, 8, @intFromEnum(abi.UnsafeScope.none)));
}

test "phase3 mmio guard classifies typed access before pointer materialization" {
    const range = mmio.MmioRange{ .base_addr = 0x1000, .length = 16, .stride = 4 };
    const contiguous = mmio.MmioRange{ .base_addr = 0x1000, .length = 16, .stride = 0 };
    const overflowing_base = mmio.MmioRange{ .base_addr = std.math.maxInt(usize) - 1, .length = 4, .stride = 1 };

    try std.testing.expect(accessIsAdmitted(u32, range, 4));
    try std.testing.expectEqual(MmioAccessAdmissionKind.admitted, classifyAccess(u8, range, 8).kind);
    try std.testing.expectEqual(MmioAccessAdmissionKind.misaligned, classifyAccess(u32, range, 2).kind);
    try std.testing.expectEqual(MmioAccessAdmissionKind.stride_mismatch, classifyAccess(u8, range, 2).kind);
    try std.testing.expectEqual(MmioAccessAdmissionKind.outside_range, classifyAccess(u32, range, 16).kind);
    try std.testing.expectEqual(MmioAccessAdmissionKind.outside_range, classifyAccess(u8, contiguous, std.math.maxInt(usize)).kind);
    try std.testing.expectEqual(MmioAccessAdmissionKind.address_overflow, classifyAccess(u8, overflowing_base, 2).kind);

    try requireAccess(u32, range, 4);
    try std.testing.expectError(error.MisalignedAccess, requireAccess(u32, range, 2));
    try std.testing.expectError(error.StrideMismatch, requireAccess(u8, range, 2));
    try std.testing.expectError(error.AccessOutsideRange, requireAccess(u32, range, 16));
    try std.testing.expectError(error.AddressOverflow, requireAccess(u8, overflowing_base, 2));
}

test "phase3 mmio guard pointer requires delegate to the live mmio accessors" {
    var bytes: [16]u8 align(@alignOf(u32)) = @splat(0);
    const base_addr = @intFromPtr(&bytes[0]);
    const range = try requireRangeScoped(base_addr, 16, 4, .volatile_mmio);

    const ptr = try requirePointerAt(u32, range, 4);
    ptr.* = 0xCAFE_BABE;

    const const_ptr = try requireConstPointerAt(u32, range, 4);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), const_ptr.*);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try mmio.readAt(u32, range, 4));

    try std.testing.expectError(error.MisalignedAccess, requirePointerAt(u32, range, 2));
    try std.testing.expectError(error.StrideMismatch, requireConstPointerAt(u8, range, 2));
    try std.testing.expectError(error.AccessOutsideRange, requirePointerAt(u32, range, 16));
}
