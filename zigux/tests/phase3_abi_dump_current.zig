const std = @import("std");
const abi = @import("abi_bindings");

fn dumpNotifierSection(stdout: anytype) !void {
    try stdout.writeAll("  \"notifier\": {\n");
    try stdout.print("    \"done\": {},\n", .{abi.NOTIFIER_DONE});
    try stdout.print("    \"ok\": {},\n", .{abi.NOTIFIER_OK});
    try stdout.print("    \"stop\": {},\n", .{abi.NOTIFIER_STOP});
    try stdout.print("    \"block_size\": {},\n", .{@sizeOf(abi.NotifierBlock)});
    try stdout.print("    \"block_align\": {},\n", .{@alignOf(abi.NotifierBlock)});
    try stdout.writeAll("    \"fields\": {\n");
    try stdout.print("      \"notifier_call_offset\": {},\n", .{@offsetOf(abi.NotifierBlock, "notifier_call")});
    try stdout.print("      \"next_offset\": {},\n", .{@offsetOf(abi.NotifierBlock, "next")});
    try stdout.print("      \"priority_offset\": {}\n", .{@offsetOf(abi.NotifierBlock, "priority")});
    try stdout.writeAll("    },\n");
    try stdout.writeAll("    \"priority_increase\": {\n");
    try stdout.print("      \"size\": {},\n", .{@sizeOf(abi.NotifierChainPriorityIncrease)});
    try stdout.print("      \"align\": {},\n", .{@alignOf(abi.NotifierChainPriorityIncrease)});
    try stdout.writeAll("      \"fields\": {\n");
    try stdout.print("        \"previous_index_offset\": {},\n", .{@offsetOf(abi.NotifierChainPriorityIncrease, "previous_index")});
    try stdout.print("        \"current_index_offset\": {},\n", .{@offsetOf(abi.NotifierChainPriorityIncrease, "current_index")});
    try stdout.print("        \"previous_priority_offset\": {},\n", .{@offsetOf(abi.NotifierChainPriorityIncrease, "previous_priority")});
    try stdout.print("        \"current_priority_offset\": {}\n", .{@offsetOf(abi.NotifierChainPriorityIncrease, "current_priority")});
    try stdout.writeAll("      }\n    },\n");
    try stdout.writeAll("    \"list_head\": {\n");
    try stdout.print("      \"size\": {},\n", .{@sizeOf(abi.ListHead)});
    try stdout.print("      \"align\": {},\n", .{@alignOf(abi.ListHead)});
    try stdout.writeAll("      \"fields\": {\n");
    try stdout.print("        \"next_offset\": {},\n", .{@offsetOf(abi.ListHead, "next")});
    try stdout.print("        \"prev_offset\": {}\n", .{@offsetOf(abi.ListHead, "prev")});
    try stdout.writeAll("      }\n    },\n");
    try stdout.writeAll("    \"hlist_head\": {\n");
    try stdout.print("      \"size\": {},\n", .{@sizeOf(abi.HListHead)});
    try stdout.print("      \"align\": {},\n", .{@alignOf(abi.HListHead)});
    try stdout.writeAll("      \"fields\": {\n");
    try stdout.print("        \"first_offset\": {}\n", .{@offsetOf(abi.HListHead, "first")});
    try stdout.writeAll("      }\n    },\n");
    try stdout.writeAll("    \"hlist_node\": {\n");
    try stdout.print("      \"size\": {},\n", .{@sizeOf(abi.HListNode)});
    try stdout.print("      \"align\": {},\n", .{@alignOf(abi.HListNode)});
    try stdout.writeAll("      \"fields\": {\n");
    try stdout.print("        \"next_offset\": {},\n", .{@offsetOf(abi.HListNode, "next")});
    try stdout.print("        \"pprev_offset\": {}\n", .{@offsetOf(abi.HListNode, "pprev")});
    try stdout.writeAll("      }\n    },\n");
    try stdout.writeAll("    \"list_break\": {\n");
    try stdout.print("      \"size\": {},\n", .{@sizeOf(abi.ListBackLinkBreak)});
    try stdout.print("      \"align\": {},\n", .{@alignOf(abi.ListBackLinkBreak)});
    try stdout.writeAll("      \"fields\": {\n");
    try stdout.print("        \"current_index_offset\": {},\n", .{@offsetOf(abi.ListBackLinkBreak, "current_index")});
    try stdout.print("        \"expected_prev_offset\": {},\n", .{@offsetOf(abi.ListBackLinkBreak, "expected_prev")});
    try stdout.print("        \"actual_prev_offset\": {}\n", .{@offsetOf(abi.ListBackLinkBreak, "actual_prev")});
    try stdout.writeAll("      }\n    },\n");
    try stdout.writeAll("    \"hlist_break\": {\n");
    try stdout.print("      \"size\": {},\n", .{@sizeOf(abi.HListPrevLinkBreak)});
    try stdout.print("      \"align\": {},\n", .{@alignOf(abi.HListPrevLinkBreak)});
    try stdout.writeAll("      \"fields\": {\n");
    try stdout.print("        \"current_index_offset\": {},\n", .{@offsetOf(abi.HListPrevLinkBreak, "current_index")});
    try stdout.print("        \"expected_pprev_offset\": {},\n", .{@offsetOf(abi.HListPrevLinkBreak, "expected_pprev")});
    try stdout.print("        \"actual_pprev_offset\": {}\n", .{@offsetOf(abi.HListPrevLinkBreak, "actual_pprev")});
    try stdout.writeAll("      }\n    }\n  }\n}\n");
}

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
        "  \"chrdev_budget_window\": {{\n    \"delivery_flag_applied\": {},\n    \"status_skipped\": {},\n    \"budget_flag_budget_applied\": {},\n    \"budget_window_flag_window_applied\": {},\n    \"budget_window_status_skipped\": {},\n    \"view\": {{\n      \"size\": {},\n      \"align\": {},\n      \"fields\": {{\n        \"ack_window_offset\": {},\n        \"delivery_window_offset\": {},\n        \"status_offset\": {}\n      }}\n    }},\n    \"summary\": {{\n      \"size\": {},\n      \"align\": {},\n      \"fields\": {{\n        \"applied_offset\": {},\n        \"skipped_offset\": {},\n        \"delivered_offset\": {}\n      }}\n    }},\n    \"budget_view\": {{\n      \"size\": {},\n      \"align\": {},\n      \"fields\": {{\n        \"budget_offset\": {},\n        \"window_offset\": {},\n        \"flags_offset\": {}\n      }}\n    }},\n    \"budget_summary\": {{\n      \"size\": {},\n      \"align\": {},\n      \"fields\": {{\n        \"attempted_offset\": {},\n        \"applied_offset\": {},\n        \"skipped_offset\": {}\n      }}\n    }}\n  }},\n",
        .{
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
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
    try dumpNotifierSection(stdout);
    try stdout.flush();
}
