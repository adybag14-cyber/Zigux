const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn writeSummary(writer: anytype, summary: abi.XaSlotSummary) !void {
    try writer.writeAll("{\"scanned_count\":");
    try writer.print("{d}", .{summary.scanned_count});
    try writer.writeAll(",\"null_count\":");
    try writer.print("{d}", .{summary.null_count});
    try writer.writeAll(",\"value_count\":");
    try writer.print("{d}", .{summary.value_count});
    try writer.writeAll(",\"error_count\":");
    try writer.print("{d}", .{summary.error_count});
    try writer.writeAll(",\"plain_count\":");
    try writer.print("{d}", .{summary.plain_count});
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
    const truncated_view = xarray_slot_view.viewFromEntries(slots[0..], 5);
    const full_view = xarray_slot_view.viewFromEntries(slots[0..], 6);
    const empty_view = abi.XaSlotView{ .slots_addr = 0, .slot_count = 0, .max_scan = 0 };

    try writer.writeAll("{\"constants\":{\"xa_slot_flag_truncated\":");
    try writer.print("{d}", .{abi.XA_SLOT_FLAG_TRUNCATED});
    try writer.writeAll("},\"truncated\":{\"entry_3\":");
    try writer.print("{d}", .{xarray_slot_view.entryAt(truncated_view, 3)});
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, xarray_slot_view.summarize(truncated_view));
    try writer.writeAll("},\"full\":{\"entry_5\":");
    try writer.print("{d}", .{xarray_slot_view.entryAt(full_view, 5)});
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, xarray_slot_view.summarize(full_view));
    try writer.writeAll("},\"empty\":{\"is_valid\":");
    try writer.writeAll(if (xarray_slot_view.isValid(empty_view)) "true" else "false");
    try writer.writeAll(",\"summary\":");
    try writeSummary(writer, xarray_slot_view.summarize(empty_view));
    try writer.writeAll("}}\n");

    try stdout_writer.interface.flush();
}
