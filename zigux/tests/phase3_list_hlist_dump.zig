const std = @import("std");
const Io = std.Io;
const abi = @import("list_hlist_binding");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn writeQuoted(writer: anytype, text: []const u8) !void {
    try writer.writeByte('"');
    try writer.writeAll(text);
    try writer.writeByte('"');
}

fn writeListScenario(writer: anytype, comptime name: []const u8, head: *const abi.ListHead) !void {
    const view = list_view.ListView.init(head);
    try writeQuoted(writer, name);
    try writer.writeAll(":{\"empty\":");
    try writer.writeAll(if (view.isEmpty()) "true" else "false");
    try writer.writeAll(",\"len\":");
    try writer.print("{d}", .{view.len()});
    try writer.writeAll(",\"circular\":");
    try writer.writeAll(if (view.isCircular()) "true" else "false");
    try writer.writeAll(",\"head_links_match\":");
    try writer.writeAll(if ((view.first() == null and view.last() == null) or (head.next == @intFromPtr(view.first().?) and head.prev == @intFromPtr(view.last().?))) "true" else "false");
    try writer.writeByte('}');
}

fn writeHListScenario(writer: anytype, comptime name: []const u8, head: *const abi.HListHead) !void {
    const view = hlist_view.HListView.init(head);
    try writeQuoted(writer, name);
    try writer.writeAll(":{\"empty\":");
    try writer.writeAll(if (view.isEmpty()) "true" else "false");
    try writer.writeAll(",\"len\":");
    try writer.print("{d}", .{view.len()});
    try writer.writeAll(",\"head_links_match\":");
    try writer.writeAll(if (view.firstPprevMatchesHead() and view.linksBackToPrevious()) "true" else "false");
    try writer.writeAll(",\"tail_next_null\":");
    try writer.writeAll(if (view.tailNextIsNull()) "true" else "false");
    try writer.writeByte('}');
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [2048]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    var empty_list_head = abi.ListHead{ .next = 0, .prev = 0 };
    empty_list_head.next = @intFromPtr(&empty_list_head);
    empty_list_head.prev = @intFromPtr(&empty_list_head);

    var list_head = abi.ListHead{ .next = 0, .prev = 0 };
    var list_first = abi.ListHead{ .next = 0, .prev = 0 };
    var list_second = abi.ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_first);

    const empty_hlist_head = abi.HListHead{ .first = 0 };
    var hlist_head = abi.HListHead{ .first = 0 };
    var hlist_first = abi.HListNode{ .next = 0, .pprev = 0 };
    var hlist_second = abi.HListNode{ .next = 0, .pprev = 0 };
    hlist_head.first = @intFromPtr(&hlist_first);
    hlist_first.next = @intFromPtr(&hlist_second);
    hlist_first.pprev = @intFromPtr(&hlist_head.first);
    hlist_second.next = 0;
    hlist_second.pprev = @intFromPtr(&hlist_first.next);

    try writer.writeAll("{");
    try writeListScenario(writer, "list_empty", &empty_list_head);
    try writer.writeByte(',');
    try writeListScenario(writer, "list_pair", &list_head);
    try writer.writeByte(',');
    try writeHListScenario(writer, "hlist_empty", &empty_hlist_head);
    try writer.writeByte(',');
    try writeHListScenario(writer, "hlist_pair", &hlist_head);
    try writer.writeAll("}\n");
    try stdout_writer.interface.flush();
}
