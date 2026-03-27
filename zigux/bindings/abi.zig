const std = @import("std");

pub const ABI_VERSION: u16 = 1;
pub const STATUS_FLAG_ERROR: u16 = 1;

pub const Facility = enum(u16) {
    kernel = 1,
    helpers = 2,
    drivers = 3,
};

pub const PanicMode = enum(u8) {
    abort = 0,
    bug = 1,
    warn = 2,
};

pub const AllocatorMode = enum(u8) {
    caller_provided = 0,
    kernel_heap = 1,
    arena = 2,
};

pub const UnsafeScope = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

pub const BoundaryHeader = extern struct {
    size: u32,
    abi_version: u16,
    flags: u16,
};

pub const ExportStatus = extern struct {
    code: i32,
    facility: u16,
    flags: u16,
};

pub const BitmapView = extern struct {
    words_addr: usize,
    nbits: u32,
    word_count: u32,
};

pub const CpuMaskView = extern struct {
    bits_addr: usize,
    nr_cpu_ids: u32,
    reserved: u32,
};

pub const MmioRange = extern struct {
    base_addr: usize,
    length: u32,
    stride: u32,
};

pub const InteropPolicy = extern struct {
    panic_mode: u8,
    allocator_mode: u8,
    unsafe_scope: u8,
    reserved: u8,
};

pub fn defaultHeader(flags: u16) BoundaryHeader {
    return .{
        .size = @sizeOf(BoundaryHeader),
        .abi_version = ABI_VERSION,
        .flags = flags,
    };
}

test "phase3 abi constants stay stable" {
    try std.testing.expectEqual(@as(u16, 1), ABI_VERSION);
    try std.testing.expectEqual(@as(u16, 1), @intFromEnum(Facility.kernel));
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(PanicMode.abort));
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(AllocatorMode.caller_provided));
    try std.testing.expectEqual(@as(u8, 2), @intFromEnum(UnsafeScope.raw_pointer_bridge));
}

test "phase3 abi layouts stay stable" {
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(ExportStatus));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(BitmapView));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(CpuMaskView));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(MmioRange));
    try std.testing.expectEqual(@as(usize, 4), @sizeOf(InteropPolicy));
}
