const std = @import("std");

pub const bitmap_view_abi_version: u32 = 1;
pub const bitmap_summary_abi_version: u32 = 1;
pub const cpumask_view_abi_version: u32 = 1;

pub const BitmapView = extern struct {
    words_addr: usize,
    nbits: u32,
    word_count: u32,
};

pub const BitmapSummary = extern struct {
    first_set: u32,
    first_zero: u32,
    weight: u32,
    reserved: u32,
};

pub const CpumaskView = extern struct {
    words_addr: usize,
    nbits: u32,
    word_count: u32,
    nr_cpu_ids: u32,
    reserved: u32,
};

pub fn initBitmapView(words_addr: usize, nbits: u32, word_count: u32) BitmapView {
    return .{
        .words_addr = words_addr,
        .nbits = nbits,
        .word_count = word_count,
    };
}

pub fn initBitmapSummary(first_set: u32, first_zero: u32, weight: u32) BitmapSummary {
    return .{
        .first_set = first_set,
        .first_zero = first_zero,
        .weight = weight,
        .reserved = 0,
    };
}

pub fn initCpumaskView(
    words_addr: usize,
    nbits: u32,
    word_count: u32,
    nr_cpu_ids: u32,
) CpumaskView {
    return .{
        .words_addr = words_addr,
        .nbits = nbits,
        .word_count = word_count,
        .nr_cpu_ids = nr_cpu_ids,
        .reserved = 0,
    };
}

comptime {
    std.debug.assert(@sizeOf(BitmapView) == @sizeOf(usize) + 8);
    std.debug.assert(@alignOf(BitmapView) == @alignOf(usize));
    std.debug.assert(@offsetOf(BitmapView, "words_addr") == 0);
    std.debug.assert(@offsetOf(BitmapView, "nbits") == @sizeOf(usize));
    std.debug.assert(@offsetOf(BitmapView, "word_count") == @sizeOf(usize) + 4);

    std.debug.assert(@sizeOf(BitmapSummary) == 16);
    std.debug.assert(@alignOf(BitmapSummary) == 4);
    std.debug.assert(@offsetOf(BitmapSummary, "first_set") == 0);
    std.debug.assert(@offsetOf(BitmapSummary, "first_zero") == 4);
    std.debug.assert(@offsetOf(BitmapSummary, "weight") == 8);
    std.debug.assert(@offsetOf(BitmapSummary, "reserved") == 12);

    std.debug.assert(@sizeOf(CpumaskView) == @sizeOf(usize) + 16);
    std.debug.assert(@alignOf(CpumaskView) == @alignOf(usize));
    std.debug.assert(@offsetOf(CpumaskView, "words_addr") == 0);
    std.debug.assert(@offsetOf(CpumaskView, "nbits") == @sizeOf(usize));
    std.debug.assert(@offsetOf(CpumaskView, "word_count") == @sizeOf(usize) + 4);
    std.debug.assert(@offsetOf(CpumaskView, "nr_cpu_ids") == @sizeOf(usize) + 8);
    std.debug.assert(@offsetOf(CpumaskView, "reserved") == @sizeOf(usize) + 12);
}
