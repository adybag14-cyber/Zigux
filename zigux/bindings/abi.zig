const std = @import("std");

pub const ABI_VERSION: u16 = 1;
pub const STATUS_FLAG_ERROR: u16 = 1;
pub const LIST_FLAG_EMPTY: u32 = 1;
pub const LIST_FLAG_SINGULAR: u32 = 2;
pub const LIST_FLAG_CIRCULAR: u32 = 4;
pub const LIST_FLAG_TRUNCATED: u32 = 8;
pub const HLIST_FLAG_EMPTY: u32 = 1;
pub const HLIST_FLAG_SINGULAR: u32 = 2;
pub const HLIST_FLAG_TERMINATED: u32 = 4;
pub const HLIST_FLAG_TRUNCATED: u32 = 8;
pub const ERR_PTR_FLAG_ERROR: u16 = 1;
pub const ERR_PTR_FLAG_NULL: u16 = 2;
pub const XA_VALUE_FLAG_VALUE: u32 = 1;
pub const XA_VALUE_FLAG_PLAIN: u32 = 2;

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

pub const BitmapSummary = extern struct {
    first_set: u32,
    first_zero: u32,
    weight: u32,
    reserved: u32,
};

pub const CpuMaskSummary = extern struct {
    first_cpu: u32,
    next_cpu: u32,
    weight: u32,
    reserved: u32,
};

pub const ListHeadRef = extern struct {
    next_addr: usize,
    prev_addr: usize,
};

pub const ListView = extern struct {
    head_addr: usize,
    max_nodes: u32,
    reserved: u32,
};

pub const ListSummary = extern struct {
    length: u32,
    flags: u32,
};

pub const HListHeadRef = extern struct {
    first_addr: usize,
};

pub const HListNodeRef = extern struct {
    next_addr: usize,
    pprev_addr: usize,
};

pub const HListView = extern struct {
    head_addr: usize,
    max_nodes: u32,
    reserved: u32,
};

pub const HListSummary = extern struct {
    length: u32,
    flags: u32,
};

pub const ErrPtrSummary = extern struct {
    errno_code: i32,
    flags: u16,
    reserved: u16,
};

pub const XaValueSummary = extern struct {
    raw_addr: usize,
    decoded_value: u32,
    flags: u32,
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
    try std.testing.expectEqual(@as(u32, 4), LIST_FLAG_CIRCULAR);
    try std.testing.expectEqual(@as(u32, 4), HLIST_FLAG_TERMINATED);
    try std.testing.expectEqual(@as(u16, 1), ERR_PTR_FLAG_ERROR);
    try std.testing.expectEqual(@as(u32, 1), XA_VALUE_FLAG_VALUE);
}

test "phase3 abi layouts stay stable" {
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(ExportStatus));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(BitmapView));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(CpuMaskView));
    try std.testing.expectEqual(@as(usize, 16), @sizeOf(BitmapSummary));
    try std.testing.expectEqual(@as(usize, 16), @sizeOf(CpuMaskSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(ListHeadRef));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(ListView));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(ListSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @sizeOf(HListHeadRef));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(HListNodeRef));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(HListView));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(HListSummary));
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(ErrPtrSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(XaValueSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(MmioRange));
    try std.testing.expectEqual(@as(usize, 4), @sizeOf(InteropPolicy));
}
