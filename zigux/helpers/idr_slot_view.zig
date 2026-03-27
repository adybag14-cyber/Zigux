const std = @import("std");
const abi = @import("abi_bindings");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const narrow = @import("narrow_unsafe");

pub fn viewFromEntries(entries: []const usize, base_id: u32, max_scan: u32) abi.IdrSlotView {
    return .{
        .slots_addr = if (entries.len == 0) 0 else narrow.addressOf(&entries[0]),
        .base_id = base_id,
        .slot_count = @intCast(entries.len),
        .max_scan = max_scan,
        .reserved = 0,
    };
}

pub fn isValid(view: abi.IdrSlotView) bool {
    if (view.reserved != 0) return false;
    if (view.slot_count == 0) return true;
    return view.slots_addr != 0 and view.max_scan != 0;
}

fn entriesPtr(view: abi.IdrSlotView) [*]const usize {
    std.debug.assert(isValid(view));
    return narrow.constSliceAt(usize, view.slots_addr, view.slot_count).ptr;
}

pub fn entryAt(view: abi.IdrSlotView, index: u32) usize {
    if (!isValid(view) or index >= view.slot_count) return 0;
    return entriesPtr(view)[index];
}

pub fn summarize(view: abi.IdrSlotView) abi.IdrSlotSummary {
    if (!isValid(view)) {
        return .{ .scanned_count = 0, .present_count = 0, .value_count = 0, .error_count = 0, .plain_count = 0, .first_present_id = 0, .next_free_id = 0, .flags = 0 };
    }
    if (view.slot_count == 0) {
        return .{ .scanned_count = 0, .present_count = 0, .value_count = 0, .error_count = 0, .plain_count = 0, .first_present_id = view.base_id, .next_free_id = view.base_id, .flags = 0 };
    }

    const scanned: u32 = @min(view.slot_count, view.max_scan);
    var summary = abi.IdrSlotSummary{
        .scanned_count = scanned,
        .present_count = 0,
        .value_count = 0,
        .error_count = 0,
        .plain_count = 0,
        .first_present_id = view.base_id + scanned,
        .next_free_id = view.base_id + scanned,
        .flags = if (scanned < view.slot_count) abi.IDR_SLOT_FLAG_TRUNCATED else 0,
    };
    var have_first_present = false;
    var have_first_free = false;

    const entries = entriesPtr(view);
    var index: u32 = 0;
    while (index < scanned) : (index += 1) {
        const raw_addr = entries[index];
        const current_id = view.base_id + index;
        if (err_ptr.isNull(raw_addr)) {
            if (!have_first_free) {
                summary.next_free_id = current_id;
                have_first_free = true;
            }
            continue;
        }

        summary.present_count += 1;
        if (!have_first_present) {
            summary.first_present_id = current_id;
            have_first_present = true;
        }

        if (err_ptr.isErr(raw_addr)) {
            summary.error_count += 1;
        } else if (xa_value.isValue(raw_addr)) {
            summary.value_count += 1;
        } else {
            summary.plain_count += 1;
        }
    }
    return summary;
}

test "phase3 idr slot helpers stay bounded and predictable" {
    const slots = [_]usize{ 0, 0x2000, xa_value.make(11), err_ptr.fromErrno(-2), xa_value.make(29), err_ptr.fromErrno(-12) };
    const view = viewFromEntries(slots[0..], 64, 5);
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(usize, slots[2]), entryAt(view, 2));
    try std.testing.expectEqual(@as(u32, 5), summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 4), summary.present_count);
    try std.testing.expectEqual(@as(u32, 2), summary.value_count);
    try std.testing.expectEqual(@as(u32, 1), summary.error_count);
    try std.testing.expectEqual(@as(u32, 1), summary.plain_count);
    try std.testing.expectEqual(@as(u32, 65), summary.first_present_id);
    try std.testing.expectEqual(@as(u32, 64), summary.next_free_id);
    try std.testing.expectEqual(@as(u32, abi.IDR_SLOT_FLAG_TRUNCATED), summary.flags);
}

test "phase3 idr slot empty sentinel stays explicit" {
    const view = abi.IdrSlotView{ .slots_addr = 0, .base_id = 32, .slot_count = 0, .max_scan = 0, .reserved = 0 };
    const summary = summarize(view);
    try std.testing.expect(isValid(view));
    try std.testing.expectEqual(@as(u32, 32), summary.first_present_id);
    try std.testing.expectEqual(@as(u32, 32), summary.next_free_id);
    try std.testing.expectEqual(@as(u32, 0), summary.flags);
}
