const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");
const narrow = @import("narrow_unsafe");

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    var empty_list_head = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    const empty_list_head_addr = narrow.addressOf(&empty_list_head);
    empty_list_head.next_addr = empty_list_head_addr;
    empty_list_head.prev_addr = empty_list_head_addr;

    var single_list_head = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    var single_list_node = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    const single_list_head_addr = narrow.addressOf(&single_list_head);
    const single_list_node_addr = narrow.addressOf(&single_list_node);
    single_list_head.next_addr = single_list_node_addr;
    single_list_head.prev_addr = single_list_node_addr;
    single_list_node.next_addr = single_list_head_addr;
    single_list_node.prev_addr = single_list_head_addr;

    var triple_list_head = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    var triple_list_a = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    var triple_list_b = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    var triple_list_c = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    const triple_list_head_addr = narrow.addressOf(&triple_list_head);
    const triple_list_a_addr = narrow.addressOf(&triple_list_a);
    const triple_list_b_addr = narrow.addressOf(&triple_list_b);
    const triple_list_c_addr = narrow.addressOf(&triple_list_c);
    triple_list_head.next_addr = triple_list_a_addr;
    triple_list_head.prev_addr = triple_list_c_addr;
    triple_list_a.next_addr = triple_list_b_addr;
    triple_list_a.prev_addr = triple_list_head_addr;
    triple_list_b.next_addr = triple_list_c_addr;
    triple_list_b.prev_addr = triple_list_a_addr;
    triple_list_c.next_addr = triple_list_head_addr;
    triple_list_c.prev_addr = triple_list_b_addr;

    const empty_list = list_view.viewFromHead(&empty_list_head, 8);
    const single_list = list_view.viewFromHead(&single_list_head, 8);
    const triple_list = list_view.viewFromHead(&triple_list_head, 8);
    const truncated_list = list_view.viewFromHead(&triple_list_head, 2);

    var empty_hlist_head = abi.HListHeadRef{ .first_addr = 0 };

    var single_hlist_head = abi.HListHeadRef{ .first_addr = undefined };
    var single_hlist_node = abi.HListNodeRef{ .next_addr = undefined, .pprev_addr = undefined };
    const single_hlist_node_addr = narrow.addressOf(&single_hlist_node);
    single_hlist_head.first_addr = single_hlist_node_addr;
    single_hlist_node.next_addr = 0;
    single_hlist_node.pprev_addr = narrow.addressOf(&single_hlist_head.first_addr);

    var triple_hlist_head = abi.HListHeadRef{ .first_addr = undefined };
    var triple_hlist_a = abi.HListNodeRef{ .next_addr = undefined, .pprev_addr = undefined };
    var triple_hlist_b = abi.HListNodeRef{ .next_addr = undefined, .pprev_addr = undefined };
    var triple_hlist_c = abi.HListNodeRef{ .next_addr = undefined, .pprev_addr = undefined };
    const triple_hlist_a_addr = narrow.addressOf(&triple_hlist_a);
    const triple_hlist_b_addr = narrow.addressOf(&triple_hlist_b);
    const triple_hlist_c_addr = narrow.addressOf(&triple_hlist_c);
    triple_hlist_head.first_addr = triple_hlist_a_addr;
    triple_hlist_a.next_addr = triple_hlist_b_addr;
    triple_hlist_a.pprev_addr = narrow.addressOf(&triple_hlist_head.first_addr);
    triple_hlist_b.next_addr = triple_hlist_c_addr;
    triple_hlist_b.pprev_addr = narrow.addressOf(&triple_hlist_a.next_addr);
    triple_hlist_c.next_addr = 0;
    triple_hlist_c.pprev_addr = narrow.addressOf(&triple_hlist_b.next_addr);

    const empty_hlist = hlist_view.viewFromHead(&empty_hlist_head, 8);
    const single_hlist = hlist_view.viewFromHead(&single_hlist_head, 8);
    const triple_hlist = hlist_view.viewFromHead(&triple_hlist_head, 8);
    const truncated_hlist = hlist_view.viewFromHead(&triple_hlist_head, 2);

    try writer.writeAll("{\"constants\":{\"list_empty\":");
    try writer.print("{d}", .{abi.LIST_FLAG_EMPTY});
    try writer.writeAll(",\"list_singular\":");
    try writer.print("{d}", .{abi.LIST_FLAG_SINGULAR});
    try writer.writeAll(",\"list_circular\":");
    try writer.print("{d}", .{abi.LIST_FLAG_CIRCULAR});
    try writer.writeAll(",\"list_truncated\":");
    try writer.print("{d}", .{abi.LIST_FLAG_TRUNCATED});
    try writer.writeAll(",\"hlist_empty\":");
    try writer.print("{d}", .{abi.HLIST_FLAG_EMPTY});
    try writer.writeAll(",\"hlist_singular\":");
    try writer.print("{d}", .{abi.HLIST_FLAG_SINGULAR});
    try writer.writeAll(",\"hlist_terminated\":");
    try writer.print("{d}", .{abi.HLIST_FLAG_TERMINATED});
    try writer.writeAll(",\"hlist_truncated\":");
    try writer.print("{d}", .{abi.HLIST_FLAG_TRUNCATED});
    try writer.writeAll("},\"list\":{");

    try writer.writeAll("\"empty\":{\"valid\":");
    try writer.writeAll(if (list_view.isValid(empty_list)) "true" else "false");
    try writer.writeAll(",\"empty\":");
    try writer.writeAll(if (list_view.isEmpty(empty_list)) "true" else "false");
    try writer.writeAll(",\"singular\":");
    try writer.writeAll(if (list_view.isSingular(empty_list)) "true" else "false");
    try writer.writeAll(",\"summary\":{\"length\":");
    try writer.print("{d}", .{list_view.summarize(empty_list).length});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{list_view.summarize(empty_list).flags});
    try writer.writeAll("}},");

    try writer.writeAll("\"single\":{\"length\":");
    try writer.print("{d}", .{list_view.length(single_list)});
    try writer.writeAll(",\"empty\":");
    try writer.writeAll(if (list_view.isEmpty(single_list)) "true" else "false");
    try writer.writeAll(",\"singular\":");
    try writer.writeAll(if (list_view.isSingular(single_list)) "true" else "false");
    try writer.writeAll(",\"summary\":{\"length\":");
    try writer.print("{d}", .{list_view.summarize(single_list).length});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{list_view.summarize(single_list).flags});
    try writer.writeAll("}},");

    try writer.writeAll("\"triple\":{\"length\":");
    try writer.print("{d}", .{list_view.length(triple_list)});
    try writer.writeAll(",\"summary\":{\"length\":");
    try writer.print("{d}", .{list_view.summarize(triple_list).length});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{list_view.summarize(triple_list).flags});
    try writer.writeAll("}},");

    try writer.writeAll("\"truncated\":{\"length\":");
    try writer.print("{d}", .{list_view.length(truncated_list)});
    try writer.writeAll(",\"summary\":{\"length\":");
    try writer.print("{d}", .{list_view.summarize(truncated_list).length});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{list_view.summarize(truncated_list).flags});
    try writer.writeAll("}}},\"hlist\":{");

    try writer.writeAll("\"empty\":{\"valid\":");
    try writer.writeAll(if (hlist_view.isValid(empty_hlist)) "true" else "false");
    try writer.writeAll(",\"empty\":");
    try writer.writeAll(if (hlist_view.isEmpty(empty_hlist)) "true" else "false");
    try writer.writeAll(",\"singular\":");
    try writer.writeAll(if (hlist_view.isSingular(empty_hlist)) "true" else "false");
    try writer.writeAll(",\"summary\":{\"length\":");
    try writer.print("{d}", .{hlist_view.summarize(empty_hlist).length});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{hlist_view.summarize(empty_hlist).flags});
    try writer.writeAll("}},");

    try writer.writeAll("\"single\":{\"length\":");
    try writer.print("{d}", .{hlist_view.length(single_hlist)});
    try writer.writeAll(",\"empty\":");
    try writer.writeAll(if (hlist_view.isEmpty(single_hlist)) "true" else "false");
    try writer.writeAll(",\"singular\":");
    try writer.writeAll(if (hlist_view.isSingular(single_hlist)) "true" else "false");
    try writer.writeAll(",\"summary\":{\"length\":");
    try writer.print("{d}", .{hlist_view.summarize(single_hlist).length});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{hlist_view.summarize(single_hlist).flags});
    try writer.writeAll("}},");

    try writer.writeAll("\"triple\":{\"length\":");
    try writer.print("{d}", .{hlist_view.length(triple_hlist)});
    try writer.writeAll(",\"summary\":{\"length\":");
    try writer.print("{d}", .{hlist_view.summarize(triple_hlist).length});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{hlist_view.summarize(triple_hlist).flags});
    try writer.writeAll("}},");

    try writer.writeAll("\"truncated\":{\"length\":");
    try writer.print("{d}", .{hlist_view.length(truncated_hlist)});
    try writer.writeAll(",\"summary\":{\"length\":");
    try writer.print("{d}", .{hlist_view.summarize(truncated_hlist).length});
    try writer.writeAll(",\"flags\":");
    try writer.print("{d}", .{hlist_view.summarize(truncated_hlist).flags});
    try writer.writeAll("}}}}\n");

    try stdout_writer.interface.flush();
}
