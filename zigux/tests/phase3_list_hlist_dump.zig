const std = @import("std");
const Io = std.Io;
const list_hlist = @import("list_hlist_bindings");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn asListViewHead(head: *const list_hlist.ListHead) *const list_view.ListHead {
    return @ptrCast(head);
}

fn asHListViewHead(head: *const list_hlist.HListHead) *const hlist_view.HListHead {
    return @ptrCast(head);
}

fn writeQuoted(writer: anytype, text: []const u8) !void {
    try writer.writeByte('"');
    try writer.writeAll(text);
    try writer.writeByte('"');
}

fn listIsCircular(head: *const list_hlist.ListHead) bool {
    const head_addr = @intFromPtr(head);
    if (head.next == 0 or head.prev == 0) return false;
    if (head.next == head_addr and head.prev == head_addr) return true;

    const first = @as(*const list_hlist.ListHead, @ptrFromInt(head.next));
    var current = first;
    var steps: usize = 0;

    while (true) {
        steps += 1;
        if (steps > 1024) return false;

        if (current.next == 0 or current.prev == 0) return false;
        const next = @as(*const list_hlist.ListHead, @ptrFromInt(current.next));
        const prev = @as(*const list_hlist.ListHead, @ptrFromInt(current.prev));
        if (next.prev != @intFromPtr(current)) return false;
        if (prev.next != @intFromPtr(current)) return false;
        if (next == head) {
            return head.prev == @intFromPtr(current) and head.next == @intFromPtr(first);
        }
        current = next;
    }
}

fn writeListScenario(writer: anytype, comptime name: []const u8, head: *const list_hlist.ListHead) !void {
    const view = list_view.ListView.init(asListViewHead(head));
    try writeQuoted(writer, name);
    try writer.writeAll(":{\"empty\":");
    try writer.writeAll(if (view.isEmpty()) "true" else "false");
    try writer.writeAll(",\"len\":");
    try writer.print("{d}", .{view.len()});
    try writer.writeAll(",\"circular\":");
    try writer.writeAll(if (listIsCircular(head)) "true" else "false");
    try writer.writeAll(",\"head_links_match\":");
    try writer.writeAll(if ((view.first() == null and view.last() == null) or (head.next == @intFromPtr(view.first().?) and head.prev == @intFromPtr(view.last().?))) "true" else "false");
    try writer.writeByte('}');
}

fn writeHListScenario(writer: anytype, comptime name: []const u8, head: *const list_hlist.HListHead) !void {
    const view = hlist_view.HListView.init(asHListViewHead(head));
    try writeQuoted(writer, name);
    try writer.writeAll(":{\"empty\":");
    try writer.writeAll(if (view.isEmpty()) "true" else "false");
    try writer.writeAll(",\"len\":");
    try writer.print("{d}", .{view.len()});
    try writer.writeAll(",\"head_links_match\":");
    try writer.writeAll(if (view.firstPprevMatchesHead() and view.hasConsistentPrevLinks()) "true" else "false");
    try writer.writeAll(",\"tail_next_null\":");
    try writer.writeAll(if (view.tailNextIsNull()) "true" else "false");
    try writer.writeByte('}');
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [2048]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    var empty_list_head = list_hlist.emptyListHead();
    empty_list_head.next = @intFromPtr(&empty_list_head);
    empty_list_head.prev = @intFromPtr(&empty_list_head);

    var list_head = list_hlist.emptyListHead();
    var list_first = list_hlist.emptyListHead();
    var list_second = list_hlist.emptyListHead();
    list_head.next = @intFromPtr(&list_first);
    list_head.prev = @intFromPtr(&list_second);
    list_first.next = @intFromPtr(&list_second);
    list_first.prev = @intFromPtr(&list_head);
    list_second.next = @intFromPtr(&list_head);
    list_second.prev = @intFromPtr(&list_first);

    const empty_hlist_head = list_hlist.emptyHListHead();
    var hlist_head = list_hlist.emptyHListHead();
    var hlist_first = list_hlist.emptyHListNode();
    var hlist_second = list_hlist.emptyHListNode();
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