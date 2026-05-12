const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");

fn writeQuoted(writer: anytype, text: []const u8) !void {
    try writer.writeByte('"');
    try writer.writeAll(text);
    try writer.writeByte('"');
}

fn writeStruct(writer: anytype, comptime name: []const u8, comptime T: type) !void {
    try writeQuoted(writer, name);
    try writer.writeAll(":{\"size\":");
    try writer.print("{d}", .{@sizeOf(T)});
    try writer.writeAll(",\"align\":");
    try writer.print("{d}", .{@alignOf(T)});
    try writer.writeAll(",\"offsets\":{");
    inline for (std.meta.fields(T), 0..) |field, index| {
        if (index != 0) try writer.writeByte(',');
        try writeQuoted(writer, field.name);
        try writer.writeByte(':');
        try writer.print("{d}", .{@offsetOf(T, field.name)});
    }
    try writer.writeAll("}}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    try writer.writeAll("{\"abi_version\":");
    try writer.print("{d}", .{abi.ABI_VERSION});

    try writer.writeAll(",\"constants\":{");
    try writer.print(
        "\"facility_kernel\":{d},\"facility_helpers\":{d},\"facility_drivers\":{d},\"status_flag_error\":{d},\"panic_abort\":{d},\"panic_bug\":{d},\"panic_warn\":{d},\"allocator_caller_provided\":{d},\"allocator_kernel_heap\":{d},\"allocator_arena\":{d},\"unsafe_scope_none\":{d},\"unsafe_scope_volatile_mmio\":{d},\"unsafe_scope_raw_pointer_bridge\":{d}",
        .{
            abi.FACILITY_KERNEL,
            abi.FACILITY_HELPERS,
            abi.FACILITY_DRIVERS,
            abi.STATUS_FLAG_ERROR,
            abi.PANIC_ABORT,
            abi.PANIC_BUG,
            abi.PANIC_WARN,
            abi.ALLOC_CALLER_PROVIDED,
            abi.ALLOC_KERNEL_HEAP,
            abi.ALLOC_ARENA,
            abi.UNSAFE_NONE,
            abi.UNSAFE_VOLATILE_MMIO,
            abi.UNSAFE_RAW_POINTER_BRIDGE,
        },
    );

    try writer.writeAll("},\"structs\":{");
    try writeStruct(writer, "boundary_header", abi.BoundaryHeader);
    try writer.writeByte(',');
    try writeStruct(writer, "export_status", abi.ExportStatus);
    try writer.writeByte(',');
    try writeStruct(writer, "interop_policy", abi.InteropPolicy);
    try writer.writeByte(',');
    try writeStruct(
        writer,
        "chrdev_notify_ack_window_policy_budget_window_delivery_window_view",
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView,
    );
    try writer.writeByte(',');
    try writeStruct(
        writer,
        "chrdev_notify_ack_window_policy_budget_window_delivery_window_summary",
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary,
    );
    try writer.writeByte(',');
    try writeStruct(
        writer,
        "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view",
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView,
    );
    try writer.writeByte(',');
    try writeStruct(
        writer,
        "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary",
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary,
    );
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
