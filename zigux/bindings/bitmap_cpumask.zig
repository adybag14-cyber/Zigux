const std = @import("std");
const uapi = @import("uapi_bitmap_cpumask");

pub const bitmap_view_abi_version = uapi.bitmap_view_abi_version;
pub const bitmap_summary_abi_version = uapi.bitmap_summary_abi_version;
pub const cpumask_view_abi_version = uapi.cpumask_view_abi_version;

pub const bitmap_view_size: usize = @sizeOf(uapi.BitmapView);
pub const bitmap_view_align: usize = @alignOf(uapi.BitmapView);
pub const bitmap_view_words_addr_offset: usize = @offsetOf(uapi.BitmapView, "words_addr");
pub const bitmap_view_nbits_offset: usize = @offsetOf(uapi.BitmapView, "nbits");
pub const bitmap_view_word_count_offset: usize = @offsetOf(uapi.BitmapView, "word_count");

pub const bitmap_summary_size: usize = @sizeOf(uapi.BitmapSummary);
pub const bitmap_summary_align: usize = @alignOf(uapi.BitmapSummary);
pub const bitmap_summary_first_set_offset: usize = @offsetOf(uapi.BitmapSummary, "first_set");
pub const bitmap_summary_first_zero_offset: usize = @offsetOf(uapi.BitmapSummary, "first_zero");
pub const bitmap_summary_weight_offset: usize = @offsetOf(uapi.BitmapSummary, "weight");
pub const bitmap_summary_reserved_offset: usize = @offsetOf(uapi.BitmapSummary, "reserved");

pub const cpumask_view_size: usize = @sizeOf(uapi.CpumaskView);
pub const cpumask_view_align: usize = @alignOf(uapi.CpumaskView);
pub const cpumask_view_words_addr_offset: usize = @offsetOf(uapi.CpumaskView, "words_addr");
pub const cpumask_view_nbits_offset: usize = @offsetOf(uapi.CpumaskView, "nbits");
pub const cpumask_view_word_count_offset: usize = @offsetOf(uapi.CpumaskView, "word_count");
pub const cpumask_view_nr_cpu_ids_offset: usize = @offsetOf(uapi.CpumaskView, "nr_cpu_ids");
pub const cpumask_view_reserved_offset: usize = @offsetOf(uapi.CpumaskView, "reserved");

pub const BitmapView = uapi.BitmapView;
pub const BitmapSummary = uapi.BitmapSummary;
pub const CpumaskView = uapi.CpumaskView;

pub fn initBitmapView(words_addr: usize, nbits: u32, word_count: u32) BitmapView {
    return uapi.initBitmapView(words_addr, nbits, word_count);
}

pub fn initBitmapSummary(first_set: u32, first_zero: u32, weight: u32) BitmapSummary {
    return uapi.initBitmapSummary(first_set, first_zero, weight);
}

pub fn initCpumaskView(
    words_addr: usize,
    nbits: u32,
    word_count: u32,
    nr_cpu_ids: u32,
) CpumaskView {
    return uapi.initCpumaskView(words_addr, nbits, word_count, nr_cpu_ids);
}

pub fn asBitmap(view: CpumaskView) BitmapView {
    return initBitmapView(view.words_addr, view.nbits, view.word_count);
}

comptime {
    std.debug.assert(bitmap_view_abi_version == 1);
    std.debug.assert(bitmap_summary_abi_version == 1);
    std.debug.assert(cpumask_view_abi_version == 1);

    std.debug.assert(bitmap_view_words_addr_offset == 0);
    std.debug.assert(bitmap_view_nbits_offset == @sizeOf(usize));
    std.debug.assert(bitmap_view_word_count_offset == @sizeOf(usize) + 4);

    std.debug.assert(bitmap_summary_first_set_offset == 0);
    std.debug.assert(bitmap_summary_first_zero_offset == 4);
    std.debug.assert(bitmap_summary_weight_offset == 8);
    std.debug.assert(bitmap_summary_reserved_offset == 12);

    std.debug.assert(cpumask_view_words_addr_offset == 0);
    std.debug.assert(cpumask_view_nbits_offset == @sizeOf(usize));
    std.debug.assert(cpumask_view_word_count_offset == @sizeOf(usize) + 4);
    std.debug.assert(cpumask_view_nr_cpu_ids_offset == @sizeOf(usize) + 8);
    std.debug.assert(cpumask_view_reserved_offset == @sizeOf(usize) + 12);
}

test "binding constants stay aligned with the exported uapi layout" {
    try std.testing.expectEqual(uapi.bitmap_view_abi_version, bitmap_view_abi_version);
    try std.testing.expectEqual(uapi.bitmap_summary_abi_version, bitmap_summary_abi_version);
    try std.testing.expectEqual(uapi.cpumask_view_abi_version, cpumask_view_abi_version);

    try std.testing.expectEqual(@sizeOf(uapi.BitmapView), bitmap_view_size);
    try std.testing.expectEqual(@alignOf(uapi.BitmapView), bitmap_view_align);
    try std.testing.expectEqual(@offsetOf(uapi.BitmapView, "words_addr"), bitmap_view_words_addr_offset);
    try std.testing.expectEqual(@offsetOf(uapi.BitmapView, "nbits"), bitmap_view_nbits_offset);
    try std.testing.expectEqual(@offsetOf(uapi.BitmapView, "word_count"), bitmap_view_word_count_offset);

    try std.testing.expectEqual(@sizeOf(uapi.BitmapSummary), bitmap_summary_size);
    try std.testing.expectEqual(@alignOf(uapi.BitmapSummary), bitmap_summary_align);
    try std.testing.expectEqual(@offsetOf(uapi.BitmapSummary, "first_set"), bitmap_summary_first_set_offset);
    try std.testing.expectEqual(@offsetOf(uapi.BitmapSummary, "first_zero"), bitmap_summary_first_zero_offset);
    try std.testing.expectEqual(@offsetOf(uapi.BitmapSummary, "weight"), bitmap_summary_weight_offset);
    try std.testing.expectEqual(@offsetOf(uapi.BitmapSummary, "reserved"), bitmap_summary_reserved_offset);

    try std.testing.expectEqual(@sizeOf(uapi.CpumaskView), cpumask_view_size);
    try std.testing.expectEqual(@alignOf(uapi.CpumaskView), cpumask_view_align);
    try std.testing.expectEqual(@offsetOf(uapi.CpumaskView, "words_addr"), cpumask_view_words_addr_offset);
    try std.testing.expectEqual(@offsetOf(uapi.CpumaskView, "nbits"), cpumask_view_nbits_offset);
    try std.testing.expectEqual(@offsetOf(uapi.CpumaskView, "word_count"), cpumask_view_word_count_offset);
    try std.testing.expectEqual(@offsetOf(uapi.CpumaskView, "nr_cpu_ids"), cpumask_view_nr_cpu_ids_offset);
    try std.testing.expectEqual(@offsetOf(uapi.CpumaskView, "reserved"), cpumask_view_reserved_offset);
}

test "binding constructors preserve fields and zero reserved state" {
    const bitmap = initBitmapView(0x1234, 73, 2);
    const summary = initBitmapSummary(5, 9, 12);
    const cpumask = initCpumaskView(0x5678, 96, 3, 96);

    try std.testing.expectEqual(@as(usize, 0x1234), bitmap.words_addr);
    try std.testing.expectEqual(@as(u32, 73), bitmap.nbits);
    try std.testing.expectEqual(@as(u32, 2), bitmap.word_count);

    try std.testing.expectEqual(@as(u32, 5), summary.first_set);
    try std.testing.expectEqual(@as(u32, 9), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 12), summary.weight);
    try std.testing.expectEqual(@as(u32, 0), summary.reserved);

    try std.testing.expectEqual(@as(usize, 0x5678), cpumask.words_addr);
    try std.testing.expectEqual(@as(u32, 96), cpumask.nbits);
    try std.testing.expectEqual(@as(u32, 3), cpumask.word_count);
    try std.testing.expectEqual(@as(u32, 96), cpumask.nr_cpu_ids);
    try std.testing.expectEqual(@as(u32, 0), cpumask.reserved);
}

test "binding cpumask projection keeps the bitmap-facing fields intact" {
    const cpumask = initCpumaskView(0x9abc, 41, 1, 41);
    const bitmap = asBitmap(cpumask);

    try std.testing.expectEqual(cpumask.words_addr, bitmap.words_addr);
    try std.testing.expectEqual(cpumask.nbits, bitmap.nbits);
    try std.testing.expectEqual(cpumask.word_count, bitmap.word_count);
}

test "binding cpumask projection keeps a drifted all-clear window explicit" {
    var cpumask = initCpumaskView(0x2468, 16, 1, 15);
    cpumask.reserved = 1;
    const bitmap = asBitmap(cpumask);
    const empty = initBitmapView(1, 0, 0);

    try std.testing.expectEqual(cpumask.words_addr, bitmap.words_addr);
    try std.testing.expectEqual(cpumask.nbits, bitmap.nbits);
    try std.testing.expectEqual(cpumask.word_count, bitmap.word_count);
    try std.testing.expectEqual(@as(usize, 0x2468), bitmap.words_addr);
    try std.testing.expectEqual(@as(u32, 16), bitmap.nbits);
    try std.testing.expectEqual(@as(u32, 1), bitmap.word_count);
    try std.testing.expect(bitmap.nbits != empty.nbits);
    try std.testing.expect(bitmap.word_count != empty.word_count);
}
