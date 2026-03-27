const std = @import("std");
const abi = @import("abi_bindings");
const bitmap_view = @import("bitmap_view");
const narrow = @import("narrow_unsafe");

pub const Word = usize;

pub fn viewFromBits(bits: []const Word, nr_cpu_ids: u32) abi.CpuMaskView {
    std.debug.assert(bits.len == bitmap_view.wordCount(nr_cpu_ids));
    return .{
        .bits_addr = if (bits.len == 0) 0 else narrow.addressOf(&bits[0]),
        .nr_cpu_ids = nr_cpu_ids,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.CpuMaskView) bool {
    if (view.reserved != 0) return false;
    return view.nr_cpu_ids == 0 or view.bits_addr != 0;
}

pub fn asBitmap(view: abi.CpuMaskView) abi.BitmapView {
    if (!isValid(view)) {
        return .{ .words_addr = 0, .nbits = 0, .word_count = 0 };
    }
    return .{
        .words_addr = view.bits_addr,
        .nbits = view.nr_cpu_ids,
        .word_count = bitmap_view.wordCount(view.nr_cpu_ids),
    };
}

pub fn testCpu(view: abi.CpuMaskView, cpu: u32) bool {
    return bitmap_view.testBit(asBitmap(view), cpu);
}

pub fn firstCpu(view: abi.CpuMaskView) u32 {
    if (!isValid(view)) return 0;
    return bitmap_view.firstSet(asBitmap(view));
}

pub fn nextCpu(view: abi.CpuMaskView, prev_cpu: u32) u32 {
    if (!isValid(view)) return 0;
    if (prev_cpu >= view.nr_cpu_ids) return view.nr_cpu_ids;

    const bitmap = asBitmap(view);
    var cpu = prev_cpu + 1;
    while (cpu < view.nr_cpu_ids) : (cpu += 1) {
        if (bitmap_view.testBit(bitmap, cpu)) return cpu;
    }
    return view.nr_cpu_ids;
}

pub fn weight(view: abi.CpuMaskView) u32 {
    if (!isValid(view)) return 0;
    return bitmap_view.weight(asBitmap(view));
}

pub fn summarize(view: abi.CpuMaskView) abi.CpuMaskSummary {
    if (!isValid(view)) return .{ .first_cpu = 0, .next_cpu = 0, .weight = 0, .reserved = 0 };

    const first = firstCpu(view);
    return .{
        .first_cpu = first,
        .next_cpu = if (first < view.nr_cpu_ids) nextCpu(view, first) else view.nr_cpu_ids,
        .weight = weight(view),
        .reserved = 0,
    };
}

test "phase3 cpumask view helpers stay bounded and predictable" {
    var bits = [_]Word{(@as(Word, 1) << 0) | (@as(Word, 1) << 2) | (@as(Word, 1) << 6) | (@as(Word, 1) << 9)};
    const view = viewFromBits(bits[0..], 12);
    const summary = summarize(view);

    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(view));
    try std.testing.expectEqual(@as(u32, 2), nextCpu(view, 0));
    try std.testing.expectEqual(@as(u32, 4), weight(view));
    try std.testing.expect(!testCpu(view, 3));
    try std.testing.expect(testCpu(view, 9));
    try std.testing.expectEqual(@as(u32, 0), summary.first_cpu);
    try std.testing.expectEqual(@as(u32, 2), summary.next_cpu);
    try std.testing.expectEqual(@as(u32, 4), summary.weight);
}

test "phase3 cpumask empty sentinel behavior stays explicit" {
    const empty = viewFromBits(&.{}, 0);
    const summary = summarize(empty);

    try std.testing.expect(isValid(empty));
    try std.testing.expectEqual(@as(u32, 0), firstCpu(empty));
    try std.testing.expectEqual(@as(u32, 0), nextCpu(empty, 0));
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
}
