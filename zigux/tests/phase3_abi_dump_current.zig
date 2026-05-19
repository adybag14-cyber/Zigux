const std = @import("std");
const abi = @import("abi_bindings");

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = std.Io.File.stdout().writer(io, &stdout_buffer);
    const stdout = &stdout_writer.interface;

    const default_header = abi.defaultHeader(0);
    const policy = abi.defaultInteropPolicy();
    const header_is_canonical = abi.headerIsCanonical(default_header);

    try stdout.writeAll("{\n");
    try stdout.print("  \"abi_version\": {},\n", .{abi.ABI_VERSION});
    try stdout.print(
        "  \"boundary_header\": {{\n    \"size\": {},\n    \"align\": {},\n    \"fields\": {{\n      \"size_offset\": {},\n      \"abi_version_offset\": {},\n      \"flags_offset\": {}\n    }},\n    \"default\": {{\n      \"size\": {},\n      \"abi_version\": {},\n      \"flags\": {}\n    }},\n    \"compatibility\": {{\n      \"canonical\": {},\n      \"size_matches\": {},\n      \"version_matches\": {}\n    }}\n  }},\n",
        .{
            @sizeOf(abi.BoundaryHeader),
            @alignOf(abi.BoundaryHeader),
            @offsetOf(abi.BoundaryHeader, "size"),
            @offsetOf(abi.BoundaryHeader, "abi_version"),
            @offsetOf(abi.BoundaryHeader, "flags"),
            default_header.size,
            default_header.abi_version,
            default_header.flags,
            header_is_canonical,
            default_header.size == @sizeOf(abi.BoundaryHeader),
            default_header.abi_version == abi.ABI_VERSION,
        },
    );
    try stdout.print(
        "  \"export_status\": {{\n    \"size\": {},\n    \"align\": {},\n    \"fields\": {{\n      \"code_offset\": {},\n      \"facility_offset\": {},\n      \"flags_offset\": {}\n    }},\n    \"error_flag\": {}\n  }},\n",
        .{
            @sizeOf(abi.ExportStatus),
            @alignOf(abi.ExportStatus),
            @offsetOf(abi.ExportStatus, "code"),
            @offsetOf(abi.ExportStatus, "facility"),
            @offsetOf(abi.ExportStatus, "flags"),
            abi.STATUS_FLAG_ERROR,
        },
    );
    try stdout.print(
        "  \"chrdev_budget_window\": {{\n    \"status_skipped\": {},\n    \"budget_flag_budget_applied\": {},\n    \"budget_window_flag_window_applied\": {},\n    \"budget_window_status_skipped\": {},\n    \"view\": {{\n      \"size\": {},\n      \"align\": {},\n      \"fields\": {{\n        \"ack_window_offset\": {},\n        \"delivery_window_offset\": {},\n        \"status_offset\": {}\n      }}\n    }},\n    \"summary\": {{\n      \"size\": {},\n      \"align\": {},\n      \"fields\": {{\n        \"applied_offset\": {},\n        \"skipped_offset\": {},\n        \"delivered_offset\": {}\n      }}\n    }},\n    \"budget_view\": {{\n      \"size\": {},\n      \"align\": {},\n      \"fields\": {{\n        \"budget_offset\": {},\n        \"window_offset\": {},\n        \"flags_offset\": {}\n      }}\n    }},\n    \"budget_summary\": {{\n      \"size\": {},\n      \"align\": {},\n      \"fields\": {{\n        \"attempted_offset\": {},\n        \"applied_offset\": {},\n        \"skipped_offset\": {}\n      }}\n    }}\n  }},\n",
        .{
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
            @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
            @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window"),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window"),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status"),
            @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
            @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied"),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped"),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered"),
            @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
            @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget"),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window"),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags"),
            @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
            @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted"),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied"),
            @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped"),
        },
    );
    try stdout.print(
        "  \"interop_policy\": {{\n    \"size\": {},\n    \"align\": {},\n    \"fields\": {{\n      \"panic_mode_offset\": {},\n      \"allocator_mode_offset\": {},\n      \"unsafe_scope_offset\": {},\n      \"reserved_offset\": {}\n    }},\n    \"default\": {{\n      \"panic_mode\": {},\n      \"allocator_mode\": {},\n      \"unsafe_scope\": {},\n      \"reserved\": {}\n    }}\n  }},\n",
        .{
            @sizeOf(abi.InteropPolicy),
            @alignOf(abi.InteropPolicy),
            @offsetOf(abi.InteropPolicy, "panic_mode"),
            @offsetOf(abi.InteropPolicy, "allocator_mode"),
            @offsetOf(abi.InteropPolicy, "unsafe_scope"),
            @offsetOf(abi.InteropPolicy, "reserved"),
            policy.panic_mode,
            policy.allocator_mode,
            policy.unsafe_scope,
            policy.reserved,
        },
    );
    try stdout.print(
        "  \"panic_mode\": {{\n    \"abort\": {},\n    \"bug\": {},\n    \"warn\": {}\n  }},\n",
        .{
            @intFromEnum(abi.PanicMode.abort),
            @intFromEnum(abi.PanicMode.bug),
            @intFromEnum(abi.PanicMode.warn),
        },
    );
    try stdout.print(
        "  \"allocator_mode\": {{\n    \"caller_provided\": {},\n    \"kernel_heap\": {},\n    \"arena\": {}\n  }},\n",
        .{
            @intFromEnum(abi.AllocatorMode.caller_provided),
            @intFromEnum(abi.AllocatorMode.kernel_heap),
            @intFromEnum(abi.AllocatorMode.arena),
        },
    );
    try stdout.print(
        "  \"unsafe_scope\": {{\n    \"none\": {},\n    \"volatile_mmio\": {},\n    \"raw_pointer_bridge\": {}\n  }},\n",
        .{
            @intFromEnum(abi.UnsafeScope.none),
            @intFromEnum(abi.UnsafeScope.volatile_mmio),
            @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        },
    );
    try stdout.print(
        "  \"facility\": {{\n    \"kernel\": {},\n    \"helpers\": {},\n    \"drivers\": {}\n  }},\n",
        .{
            @intFromEnum(abi.Facility.kernel),
            @intFromEnum(abi.Facility.helpers),
            @intFromEnum(abi.Facility.drivers),
        },
    );
    try stdout.print(
        "  \"notifier\": {{\n    \"done\": {},\n    \"ok\": {},\n    \"stop\": {},\n    \"block_size\": {},\n    \"block_align\": {},\n    \"fields\": {{\n      \"notifier_call_offset\": {},\n      \"next_offset\": {},\n      \"priority_offset\": {}\n    }}\n  }}\n}}\n",
        .{
            abi.NOTIFIER_DONE,
            abi.NOTIFIER_OK,
            abi.NOTIFIER_STOP,
            @sizeOf(abi.NotifierBlock),
            @alignOf(abi.NotifierBlock),
            @offsetOf(abi.NotifierBlock, "notifier_call"),
            @offsetOf(abi.NotifierBlock, "next"),
            @offsetOf(abi.NotifierBlock, "priority"),
        },
    );
    try stdout.flush();
}
