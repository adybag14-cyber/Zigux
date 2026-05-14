const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const notifier_abi = @import("notifier_abi");

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

fn writeDevT(writer: anytype) !void {
    const minor_bits: u5 = 20;
    const minor_mask: u32 = 1_048_575;
    const max_major: u32 = 4_095;
    const sample_major: u32 = 42;
    const sample_minor: u32 = 7;
    const range_first_minor: u32 = 7;
    const range_count: u32 = 4;
    const sample_encoded: u32 = (sample_major << minor_bits) | sample_minor;
    const range_last_encoded: u32 = (sample_major << minor_bits) | (range_first_minor + range_count - 1);

    try writeQuoted(writer, "dev_t");
    try writer.writeAll(":{\"minor_bits\":");
    try writer.print("{d}", .{minor_bits});
    try writer.writeAll(",\"minor_mask\":");
    try writer.print("{d}", .{minor_mask});
    try writer.writeAll(",\"max_major\":");
    try writer.print("{d}", .{max_major});
    try writer.writeAll(",\"sample_major\":");
    try writer.print("{d}", .{sample_major});
    try writer.writeAll(",\"sample_minor\":");
    try writer.print("{d}", .{sample_minor});
    try writer.writeAll(",\"sample_encoded\":");
    try writer.print("{d}", .{sample_encoded});
    try writer.writeAll(",\"range_first_minor\":");
    try writer.print("{d}", .{range_first_minor});
    try writer.writeAll(",\"range_count\":");
    try writer.print("{d}", .{range_count});
    try writer.writeAll(",\"range_fits\":");
    try writer.print("{d}", .{@intFromBool(range_first_minor + range_count - 1 <= minor_mask)});
    try writer.writeAll(",\"range_last_encoded\":");
    try writer.print("{d}", .{range_last_encoded});
    try writer.writeByte('}');
}

fn writeNotifierChain(writer: anytype) !void {
    const single = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const descending_third = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = -4,
    };
    const descending_second = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&descending_third),
        .priority = 8,
    };
    const descending_first = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&descending_second),
        .priority = 8,
    };
    const rising_second = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 5,
    };
    const rising_first = notifier_abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_second),
        .priority = 3,
    };

    try writeQuoted(writer, "notifier_chain");
    try writer.writeAll(":{\"empty_ok\":");
    try writer.print("{d}", .{@intFromBool(notifier_abi.chainHasNonincreasingPriority(null))});
    try writer.writeAll(",\"single_ok\":");
    try writer.print("{d}", .{@intFromBool(notifier_abi.chainHasNonincreasingPriority(&single))});
    try writer.writeAll(",\"descending_ok\":");
    try writer.print("{d}", .{@intFromBool(notifier_abi.chainHasNonincreasingPriority(&descending_first))});
    try writer.writeAll(",\"rising_ok\":");
    try writer.print("{d}", .{@intFromBool(notifier_abi.chainHasNonincreasingPriority(&rising_first))});
    try writer.writeByte('}');
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
        "\"facility_kernel\":{d},\"facility_helpers\":{d},\"facility_drivers\":{d},\"status_flag_error\":{d},\"panic_abort\":{d},\"panic_bug\":{d},\"panic_warn\":{d},\"allocator_caller_provided\":{d},\"allocator_kernel_heap\":{d},\"allocator_arena\":{d},\"unsafe_scope_none\":{d},\"unsafe_scope_volatile_mmio\":{d},\"unsafe_scope_raw_pointer_bridge\":{d},\"chrdev_notify_ack_window_policy_budget_window_delivery_window_status_skipped\":{d},\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_flag_budget_applied\":{d},\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_flag_window_applied\":{d},\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_status_skipped\":{d},\"notifier_done\":{d},\"notifier_ok\":{d},\"notifier_stop\":{d}",
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
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
            @intFromEnum(notifier_abi.NotifierResult.done),
            @intFromEnum(notifier_abi.NotifierResult.ok),
            @intFromEnum(notifier_abi.NotifierResult.stop),
        },
    );

    try writer.writeAll("},");
    try writeDevT(writer);
    try writer.writeByte(',');
    try writeNotifierChain(writer);
    try writer.writeAll(",\"structs\":{");
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
    try writer.writeByte(',');
    try writeStruct(writer, "notifier_block", notifier_abi.NotifierBlock);
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
