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
pub const XA_SLOT_FLAG_TRUNCATED: u32 = 1;
pub const IDR_SLOT_FLAG_TRUNCATED: u32 = 1;
pub const IDA_BITMAP_FLAG_TRUNCATED: u32 = 1;
pub const IDA_BITMAP_FLAG_EXHAUSTED: u32 = 2;
pub const IDA_ALLOC_FLAG_TRUNCATED: u32 = 1;
pub const IDA_ALLOC_FLAG_FOUND: u32 = 2;
pub const IDA_ALLOC_FLAG_EXHAUSTED: u32 = 4;
pub const IDA_RANGE_FLAG_TRUNCATED: u32 = 1;
pub const IDA_RANGE_FLAG_FOUND: u32 = 2;
pub const IDA_RANGE_FLAG_EXHAUSTED: u32 = 4;
pub const IDA_RANGE_SET_FLAG_TRUNCATED: u32 = 1;
pub const IDA_RANGE_SET_FLAG_FOUND: u32 = 2;
pub const IDA_RANGE_SET_FLAG_EXHAUSTED: u32 = 4;
pub const IDA_RANGE_SET_FLAG_SELECTED: u32 = 8;
pub const IDA_POLICY_FIRST_FIT: u32 = 1;
pub const IDA_POLICY_LAST_FIT: u32 = 2;
pub const IDA_POLICY_FLAG_TRUNCATED: u32 = 1;
pub const IDA_POLICY_FLAG_FOUND: u32 = 2;
pub const IDA_POLICY_FLAG_EXHAUSTED: u32 = 4;

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

pub const XaSlotView = extern struct {
    slots_addr: usize,
    slot_count: u32,
    max_scan: u32,
};

pub const XaSlotSummary = extern struct {
    scanned_count: u32,
    null_count: u32,
    value_count: u32,
    error_count: u32,
    plain_count: u32,
    flags: u32,
};

pub const IdrSlotView = extern struct {
    slots_addr: usize,
    base_id: u32,
    slot_count: u32,
    max_scan: u32,
    reserved: u32,
};

pub const IdrSlotSummary = extern struct {
    scanned_count: u32,
    present_count: u32,
    value_count: u32,
    error_count: u32,
    plain_count: u32,
    first_present_id: u32,
    next_free_id: u32,
    flags: u32,
};

pub const IdaBitmapView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    reserved: u32,
};

pub const IdaBitmapSummary = extern struct {
    scanned_count: u32,
    allocated_count: u32,
    first_allocated_id: u32,
    first_free_id: u32,
    flags: u32,
    reserved: u32,
};

pub const IdaAllocView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    request_count: u32,
    reserved: u32,
};

pub const IdaAllocSummary = extern struct {
    scanned_count: u32,
    request_count: u32,
    first_fit_id: u32,
    longest_free_run: u32,
    flags: u32,
    reserved: u32,
};

pub const IdaRangeView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    request_count: u32,
    max_ranges: u32,
    reserved: u32,
};

pub const IdaRangeSummary = extern struct {
    scanned_count: u32,
    request_count: u32,
    candidate_range_count: u32,
    first_range_id: u32,
    last_range_id: u32,
    flags: u32,
};

pub const IdaRangeSetView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    request_count: u32,
    max_ranges: u32,
    max_selected: u32,
    reserved: u32,
};

pub const IdaRangeSetSummary = extern struct {
    scanned_count: u32,
    request_count: u32,
    candidate_range_count: u32,
    selected_range_count: u32,
    first_selected_id: u32,
    last_selected_id: u32,
    flags: u32,
    reserved: u32,
};

pub const IdaPolicyView = extern struct {
    bits_addr: usize,
    base_id: u32,
    nbits: u32,
    max_scan: u32,
    request_count: u32,
    policy: u32,
    reserved: u32,
};

pub const IdaPolicySummary = extern struct {
    scanned_count: u32,
    request_count: u32,
    selected_fit_id: u32,
    alternate_fit_id: u32,
    longest_free_run: u32,
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
    try std.testing.expectEqual(@as(u32, 1), XA_SLOT_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 1), IDR_SLOT_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 1), IDA_BITMAP_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_BITMAP_FLAG_EXHAUSTED);
    try std.testing.expectEqual(@as(u32, 1), IDA_ALLOC_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_ALLOC_FLAG_FOUND);
    try std.testing.expectEqual(@as(u32, 4), IDA_ALLOC_FLAG_EXHAUSTED);
    try std.testing.expectEqual(@as(u32, 1), IDA_RANGE_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_RANGE_FLAG_FOUND);
    try std.testing.expectEqual(@as(u32, 4), IDA_RANGE_FLAG_EXHAUSTED);
    try std.testing.expectEqual(@as(u32, 1), IDA_RANGE_SET_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_RANGE_SET_FLAG_FOUND);
    try std.testing.expectEqual(@as(u32, 4), IDA_RANGE_SET_FLAG_EXHAUSTED);
    try std.testing.expectEqual(@as(u32, 8), IDA_RANGE_SET_FLAG_SELECTED);
    try std.testing.expectEqual(@as(u32, 1), IDA_POLICY_FIRST_FIT);
    try std.testing.expectEqual(@as(u32, 2), IDA_POLICY_LAST_FIT);
    try std.testing.expectEqual(@as(u32, 1), IDA_POLICY_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), IDA_POLICY_FLAG_FOUND);
    try std.testing.expectEqual(@as(u32, 4), IDA_POLICY_FLAG_EXHAUSTED);
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
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(XaSlotView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(XaSlotSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 16), @sizeOf(IdrSlotView));
    try std.testing.expectEqual(@as(usize, 32), @sizeOf(IdrSlotSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 16), @sizeOf(IdaBitmapView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(IdaBitmapSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 24), @sizeOf(IdaAllocView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(IdaAllocSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 24), @sizeOf(IdaRangeView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(IdaRangeSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 32), @sizeOf(IdaRangeSetView));
    try std.testing.expectEqual(@as(usize, 32), @sizeOf(IdaRangeSetSummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 24), @sizeOf(IdaPolicyView));
    try std.testing.expectEqual(@as(usize, 24), @sizeOf(IdaPolicySummary));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) + 8), @sizeOf(MmioRange));
    try std.testing.expectEqual(@as(usize, 4), @sizeOf(InteropPolicy));
}
