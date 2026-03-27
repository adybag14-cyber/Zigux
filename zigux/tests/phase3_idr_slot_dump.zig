const std = @import("std");
const Io = std.Io;
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const idr_slot_view = @import("idr_slot_view");
const abi = @import("abi_bindings");

fn writeSummary(writer: anytype, summary: abi.IdrSlotSummary) !void {
    try writer.writeAll("{\"scanned_count\":");
    try writer.print("{d}", .{summary.scanned_count});
    try writer.writeAll(",\"present_count\":");
    try writer.print("{d}", .{summary.present_count});
    try writer.writeAll(",\"value_count\":");
    try writer.print("{d}", .{summary.value_count});
    try writer.writeAll(",\"error_count\":");
    try writer.print("{d}", .{summary.error_count});
    try writer.writeAll(",\"plain_count\":");
    try writer.print("{d}", .{summary.plain_count});
    try writer.writeAll(",\"first_present_id\":");
    try writer.print("{d}", .{summary.first_present_id});
    try writer.writeAll(",\"next_free_id\":");
    try writer.print("{d}", .{summary.next_free_id});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{summary.flags});
    try writer.writeAll("}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    const slots = [_]usize{ 0, 0x2000, xa_value.make(11), err_ptr.fromErrno(-2), xa_value.make(29), err_ptr.fromErrno(-12) };
    const truncated_view = idr_slot_view.viewFromEntries(slots[0..], 64, 5);
    const full_view = idr_slot_view.viewFromEntries(slots[0..], 64, 6);
    const empty_view = abi.IdrSlotView{ .slots_addr = 0, .base_id = 32, .slot_count = 0, .max_scan = 0, .reserved = 0 };

    try writer.writeAll("{\"constants\":{\"idr_slot_flag_truncated\":");
    try writer.print("{d}", .{abi.IDR_SLOT_FLAG_TRUNCATED});
    try writer.writeAll("},\"truncated\":{\"entry_2\":");
    try writer.print("{d}", .{idr_slot_view.entryAt(truncated_view, 2)});
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, idr_slot_view.summarize(truncated_view));
    try writer.writeAll("},\"full\":{\"entry_5\":");
    try writer.print("{d}", .{idr_slot_view.entryAt(full_view, 5)});
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, idr_slot_view.summarize(full_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (idr_slot_view.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, idr_slot_view.summarize(empty_view));
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
