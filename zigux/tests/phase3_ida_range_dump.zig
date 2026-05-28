const std = @import("std");
const ida_bitmap_view = @import("ida_bitmap_view");
const ida_range_view = @import("ida_range_view");

const SelectionDump = struct {
    id: u32,
    relative_bit: u32,
};

const WindowDump = struct {
    first_id: u32,
    last_id: u32,
    first_relative_bit: u32,
    last_relative_bit: u32,
    span_len: u32,
};

const SummaryDump = struct {
    window: WindowDump,
    allocated_bits: u32,
    first_allocated: ?SelectionDump,
    first_free: ?SelectionDump,
    fully_allocated: bool,
    fully_free: bool,
};

const CaseDump = struct {
    name: []const u8,
    summary: ?SummaryDump,
};

fn selectionDump(selection: ?ida_range_view.Selection) ?SelectionDump {
    const concrete = selection orelse return null;
    return .{
        .id = concrete.id,
        .relative_bit = concrete.relative_bit,
    };
}

fn summaryDump(view: ida_range_view.RangeView, alloc_range: ida_range_view.AllocationRange) ?SummaryDump {
    const summary = view.summarize(alloc_range) orelse return null;
    return .{
        .window = .{
            .first_id = summary.window.first_id,
            .last_id = summary.window.last_id,
            .first_relative_bit = summary.window.first_relative_bit,
            .last_relative_bit = summary.window.last_relative_bit,
            .span_len = summary.window.spanLen(),
        },
        .allocated_bits = summary.allocated_bits,
        .first_allocated = selectionDump(summary.first_allocated),
        .first_free = selectionDump(summary.first_free),
        .fully_allocated = summary.isFullyAllocated(),
        .fully_free = summary.isFullyFree(),
    };
}

pub fn main() !void {
    var floor_words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    floor_words[0] |= (@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 3);
    const floor_view = ida_range_view.fromWords(&floor_words, 1024);

    var ceiling_words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const high_a: u32 = ida_bitmap_view.bitmap_bits - 2;
    const high_b: u32 = ida_bitmap_view.bitmap_bits - 1;
    ceiling_words[high_a / ida_bitmap_view.word_bits] |= @as(usize, 1) << @intCast(high_a % ida_bitmap_view.word_bits);
    ceiling_words[high_b / ida_bitmap_view.word_bits] |= @as(usize, 1) << @intCast(high_b % ida_bitmap_view.word_bits);
    const ceiling_view = ida_range_view.fromWords(&ceiling_words, 2048);

    const clear_words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const clear_view = ida_range_view.fromWords(&clear_words, 0);

    const cases = [_]CaseDump{
        .{
            .name = "clamped_floor_partial",
            .summary = summaryDump(floor_view, ida_range_view.range(1000, 1027)),
        },
        .{
            .name = "clamped_ceiling_full",
            .summary = summaryDump(ceiling_view, ida_range_view.range(3070, 4096)),
        },
        .{
            .name = "clear_middle_window",
            .summary = summaryDump(clear_view, ida_range_view.range(8, 11)),
        },
        .{
            .name = "disjoint_window",
            .summary = summaryDump(clear_view, ida_range_view.range(2048, 2050)),
        },
        .{
            .name = "unordered_window",
            .summary = summaryDump(clear_view, ida_range_view.range(17, 12)),
        },
    };

    std.debug.print("{f}\n", .{std.json.fmt(cases, .{ .whitespace = .indent_2 })});
}
