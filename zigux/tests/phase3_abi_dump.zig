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

fn writeHeaderState(writer: anytype, header: abi.BoundaryHeader) !void {
    const current_abi = header.abi_version == abi.ABI_VERSION;
    const compatible_size = header.size >= @sizeOf(abi.BoundaryHeader);
    const canonical_size = header.size == @sizeOf(abi.BoundaryHeader);
    const compatible = current_abi and compatible_size;
    const canonical = current_abi and canonical_size;
    const extends_boundary = compatible and !canonical;
    const requested_extra_bytes: u32 = if (extends_boundary)
        header.size - @sizeOf(abi.BoundaryHeader)
    else
        0;

    try writer.writeByte('{');
    try writeQuoted(writer, "size");
    try writer.writeByte(':');
    try writer.print("{d}", .{header.size});
    try writer.writeAll(",\"abi_version\":");
    try writer.print("{d}", .{header.abi_version});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{header.flags});
    try writer.writeAll(",\"current_abi\":");
    try writer.print("{d}", .{@intFromBool(current_abi)});
    try writer.writeAll(",\"compatible_size\":");
    try writer.print("{d}", .{@intFromBool(compatible_size)});
    try writer.writeAll(",\"canonical_size\":");
    try writer.print("{d}", .{@intFromBool(canonical_size)});
    try writer.writeAll(",\"compatible\":");
    try writer.print("{d}", .{@intFromBool(compatible)});
    try writer.writeAll(",\"canonical\":");
    try writer.print("{d}", .{@intFromBool(canonical)});
    try writer.writeAll(",\"extends_boundary\":");
    try writer.print("{d}", .{@intFromBool(extends_boundary)});
    try writer.writeAll(",\"requested_extra_bytes\":");
    try writer.print("{d}", .{requested_extra_bytes});
    try writer.writeByte('}');
}

fn writeUapiBoundaryHeader(writer: anytype) !void {
    const flags: u16 = 0x22;
    const canonical_header = abi.defaultHeader(flags);
    var future_compatible = abi.defaultHeader(flags);
    future_compatible.size += 16;
    var mismatched_version = abi.defaultHeader(flags);
    mismatched_version.abi_version += 1;

    try writeQuoted(writer, "uapi_boundary_header");
    try writer.writeAll(":{\"header_size\":");
    try writer.print("{d}", .{@sizeOf(abi.BoundaryHeader)});
    try writer.writeAll(",\"abi_version\":");
    try writer.print("{d}", .{abi.ABI_VERSION});
    try writer.writeAll(",\"canonical_header\":");
    try writeHeaderState(writer, canonical_header);
    try writer.writeAll(",\"future_compatible\":");
    try writeHeaderState(writer, future_compatible);
    try writer.writeAll(",\"mismatched_version\":");
    try writeHeaderState(writer, mismatched_version);
    try writer.writeByte('}');
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
    const single = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const descending_third = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = -4,
    };
    const descending_second = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&descending_third),
        .priority = 8,
    };
    const descending_first = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&descending_second),
        .priority = 8,
    };
    const rising_second = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 5,
    };
    const rising_first = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_second),
        .priority = 3,
    };
    const zero_increase = abi.ChainPriorityIncrease{
        .previous_index = 0,
        .current_index = 0,
        .previous_priority = 0,
        .current_priority = 0,
    };
    const rising_increase = abi.firstChainPriorityIncrease(&rising_first);
    const increase = rising_increase orelse zero_increase;

    try writeQuoted(writer, "notifier_chain");
    try writer.writeAll(":{\"empty_ok\":");
    try writer.print("{d}", .{@intFromBool(abi.chainHasNonincreasingPriority(null))});
    try writer.writeAll(",\"single_ok\":");
    try writer.print("{d}", .{@intFromBool(abi.chainHasNonincreasingPriority(&single))});
    try writer.writeAll(",\"descending_ok\":");
    try writer.print("{d}", .{@intFromBool(abi.chainHasNonincreasingPriority(&descending_first))});
    try writer.writeAll(",\"rising_ok\":");
    try writer.print("{d}", .{@intFromBool(abi.chainHasNonincreasingPriority(&rising_first))});
    try writer.writeAll(",\"rising_first_increase\":{\"found\":");
    try writer.print("{d}", .{@intFromBool(rising_increase != null)});
    try writer.writeAll(",\"previous_index\":");
    try writer.print("{d}", .{increase.previous_index});
    try writer.writeAll(",\"current_index\":");
    try writer.print("{d}", .{increase.current_index});
    try writer.writeAll(",\"previous_priority\":");
    try writer.print("{d}", .{increase.previous_priority});
    try writer.writeAll(",\"current_priority\":");
    try writer.print("{d}", .{increase.current_priority});
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
            abi.NOTIFIER_DONE,
            abi.NOTIFIER_OK,
            abi.NOTIFIER_STOP,
        },
    );

    try writer.writeAll("},");
    try writeUapiBoundaryHeader(writer);
    try writer.writeByte(',');
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
    try writeStruct(writer, "notifier_chain_priority_increase", abi.ChainPriorityIncrease);
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
    try writeStruct(writer, "notifier_block", abi.NotifierBlock);
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
