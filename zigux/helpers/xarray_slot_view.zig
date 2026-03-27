const std = @import("std");
const abi = @import("abi_bindings");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const narrow = @import("narrow_unsafe");

pub fn viewFromEntries(entries: []const usize, max_scan: u32) abi.XaSlotView {
    return .{
        .slots_addr = if (entries.len == 0) 0 else narrow.addressOf(&entries[0]),
        .slot_count = @intCast(entries.len),
        .max_scan = max_scan,
    };
}

pub fn isValid(view: abi.XaSlotView) bool {
    if (view.slot_count == 0) return true;
    return view.slots_addr != 0 and view.max_scan != 0;
}

fn entriesPtr(view: abi.XaSlotView) [*]const usize {
    std.debug.assert(isValid(view));
    return narrow.constSliceAt(usize, view.slots_addr, view.slot_count).ptr;
}

pub fn entryAt(view: abi.XaSlotView, index: u32) usize {
    if (!isValid(view) or index >= view.slot_count) return 0;
    return entriesPtr(view)[index];
}

pub fn summarize(view: abi.XaSlotView) abi.XaSlotSummary {
    if (!isValid(view) or view.slot_count == 0) {
        return .{
            .scanned_count = 0,
            .null_count = 0,
            .value_count = 0,
            .error_count = 0,
            .plain_count = 0,
            .flags = 0,
        };
    }

    const scanned: u32 = @min(view.slot_count, view.max_scan);
    var summary = abi.XaSlotSummary{
        .scanned_count = scanned,
        .null_count = 0,
        .value_count = 0,
        .error_count = 0,
        .plain_count = 0,
        .flags = if (scanned < view.slot_count) abi.XA_SLOT_FLAG_TRUNCATED else 0,
    };

    const entries = entriesPtr(view);
    var index: u32 = 0;
    while (index < scanned) : (index += 1) {
        const raw_addr = entries[index];
        if (err_ptr.isNull(raw_addr)) {
            summary.null_count += 1;
        } else if (err_ptr.isErr(raw_addr)) {
            summary.error_count += 1;
        } else if (xa_value.isValue(raw_addr)) {
            summary.value_count += 1;
        } else {
            summary.plain_count += 1;
        }
    }

    return summary;
}

test "phase3 xarray slot helpers stay bounded and predictable" {
    const slots = [_]usize{ 0, 0x2000, xa_value.make(11), err_ptr.fromErrno(-2), xa_value.make(29), err_ptr.fromErrno(-12) };
    const view = viewFromEntries(slots[0..], 5);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(usize, slots[4]), entryAt(view, 4));
    try std.testing.expectEqual(@as(u32, 5), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 1), summary.null_count);
    try std.testing.expectEqual(@as(u32, 2), summary.value_count);
    try std.testing.expectEqual(@as(u32, 1), summary.error_count);
    try std.testing.expectEqual(@as(u32, 1), summary.plain_count);
    try std.testing.expectEqual(@as(u32, abi.XA_SLOT_FLAG_TRUNCATED), summary.flags);
}

test "phase3 xarray slot empty sentinel stays explicit" {
    const view = abi.XaSlotView{ .slots_addr = 0, .slot_count = 0, .max_scan = 0 };
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 0), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 0), summary.flags);
}
