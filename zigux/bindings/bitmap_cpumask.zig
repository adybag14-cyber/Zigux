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
