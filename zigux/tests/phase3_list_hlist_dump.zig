const std = @import("std");
const Io = std.Io;
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");

fn writeOptionalIndex(writer: anytype, value: ?usize) !void {
    if (value) |index| {
        try writer.print("{}", .{index});
        return;
    }
    try writer.writeAll("null");
}

fn writeLabel(writer: anytype, label: []const u8) !void {
    try writer.print("\"{s}\"", .{label});
}

fn writeOptionalLabel(writer: anytype, label: ?[]const u8) !void {
    if (label) |value| {
        try writeLabel(writer, value);
        return;
    }
    try writer.writeAll("null");
}

fn listNodeLabel(head: *const list_view.ListHead, first: *const list_view.ListHead, second: *const list_view.ListHead, raw: usize) []const u8 {
    if (raw == 0) return "null";
    if (raw == @intFromPtr(head)) return "head";
    if (raw == @intFromPtr(first)) return "node0";
    if (raw == @intFromPtr(second)) return "node1";
    return "unknown";
}

fn listIndexFromNode(head: *const list_view.ListHead, first: *const list_view.ListHead, second: *const list_view.ListHead, node: ?*const list_view.ListHead) ?usize {
    const actual = node orelse return null;
    if (actual == head) return null;
    if (actual == first) return 0;
    if (actual == second) return 1;
    return null;
}

fn hlistNodeLabel(head: *const hlist_view.HListHead, first: *const hlist_view.HListNode, second: *const hlist_view.HListNode, raw: usize) []const u8 {
    if (raw == 0) return "null";
    if (raw == @intFromPtr(&head.first)) return "head.first";
    if (raw == @intFromPtr(&first.next)) return "node0.next";
    if (raw == @intFromPtr(first)) return "node0";
    if (raw == @intFromPtr(second)) return "node1";
    return "unknown";
}

fn hlistIndexFromNode(first: *const hlist_view.HListNode, second: *const hlist_view.HListNode, node: ?*const hlist_view.HListNode) ?usize {
    const actual = node orelse return null;
    if (actual == first) return 0;
    if (actual == second) return 1;
    return null;
}

fn writeListCase(writer: anytype, name: []const u8, head: *const list_view.ListHead, first: *const list_view.ListHead, second: *const list_view.ListHead, trailing_comma: bool) !void {
    const view = list_view.ListView.init(head);
    const breakage = view.firstBrokenBacklink();

    try writer.print(
        "    {{\n" ++
            "      \"name\": \"{s}\",\n" ++
            "      \"is_empty\": {s},\n" ++
            "      \"len\": {},\n" ++
            "      \"first_index\": ",
        .{
            name,
            if (view.isEmpty()) "true" else "false",
            view.len(),
        },
    );
    try writeOptionalIndex(writer, listIndexFromNode(head, first, second, view.first()));
    try writer.writeAll(",\n      \"last_index\": ");
    try writeOptionalIndex(writer, listIndexFromNode(head, first, second, view.last()));
    try writer.print(
        ",\n" ++
            "      \"backlinks_consistent\": {s},\n" ++
            "      \"first_broken_index\": ",
        .{if (view.hasConsistentBacklinks()) "true" else "false"},
    );
    try writeOptionalIndex(writer, if (breakage) |it| it.current_index else null);
    try writer.writeAll(",\n      \"expected_prev_label\": ");
    try writeOptionalLabel(writer, if (breakage) |it| listNodeLabel(head, first, second, it.expected_prev) else null);
    try writer.writeAll(",\n      \"actual_prev_label\": ");
    try writeOptionalLabel(writer, if (breakage) |it| listNodeLabel(head, first, second, it.actual_prev) else null);
    try writer.writeAll("\n    }");
    if (trailing_comma) try writer.writeAll(",");
    try writer.writeAll("\n");
}

fn writeHListCase(writer: anytype, name: []const u8, head: *const hlist_view.HListHead, first: *const hlist_view.HListNode, second: *const hlist_view.HListNode, trailing_comma: bool) !void {
    const view = hlist_view.HListView.init(head);
    const breakage = view.firstBrokenPrevLink();

    try writer.print(
        "    {{\n" ++
            "      \"name\": \"{s}\",\n" ++
            "      \"is_empty\": {s},\n" ++
            "      \"len\": {},\n" ++
            "      \"first_index\": ",
        .{
            name,
            if (view.isEmpty()) "true" else "false",
            view.len(),
        },
    );
    try writeOptionalIndex(writer, hlistIndexFromNode(first, second, view.first()));
    try writer.print(
        ",\n" ++
            "      \"first_pprev_matches_head\": {s},\n" ++
            "      \"prev_links_consistent\": {s},\n" ++
            "      \"tail_next_is_null\": {s},\n" ++
            "      \"first_broken_index\": ",
        .{
            if (view.firstPprevMatchesHead()) "true" else "false",
            if (view.hasConsistentPrevLinks()) "true" else "false",
            if (view.tailNextIsNull()) "true" else "false",
        },
    );
    try writeOptionalIndex(writer, if (breakage) |it| it.current_index else null);
    try writer.writeAll(",\n      \"expected_pprev_label\": ");
    try writeOptionalLabel(writer, if (breakage) |it| hlistNodeLabel(head, first, second, it.expected_pprev) else null);
    try writer.writeAll(",\n      \"actual_pprev_label\": ");
    try writeOptionalLabel(writer, if (breakage) |it| hlistNodeLabel(head, first, second, it.actual_pprev) else null);
    try writer.writeAll("\n    }");
    if (trailing_comma) try writer.writeAll(",");
    try writer.writeAll("\n");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    var list_empty_head = list_view.ListHead{ .next = 0, .prev = 0 };
    list_empty_head.next = @intFromPtr(&list_empty_head);
    list_empty_head.prev = @intFromPtr(&list_empty_head);

    var list_ordered_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_ordered_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_ordered_second = list_view.ListHead{ .next = 0, .prev = 0 };
    list_ordered_head.next = @intFromPtr(&list_ordered_first);
    list_ordered_head.prev = @intFromPtr(&list_ordered_second);
    list_ordered_first.next = @intFromPtr(&list_ordered_second);
    list_ordered_first.prev = @intFromPtr(&list_ordered_head);
    list_ordered_second.next = @intFromPtr(&list_ordered_head);
    list_ordered_second.prev = @intFromPtr(&list_ordered_first);

    var list_broken_head = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_broken_first = list_view.ListHead{ .next = 0, .prev = 0 };
    var list_broken_second = list_view.ListHead{ .next = 0, .prev = 0 };
    list_broken_head.next = @intFromPtr(&list_broken_first);
    list_broken_head.prev = @intFromPtr(&list_broken_second);
    list_broken_first.next = @intFromPtr(&list_broken_second);
    list_broken_first.prev = @intFromPtr(&list_broken_head);
    list_broken_second.next = @intFromPtr(&list_broken_head);
    list_broken_second.prev = @intFromPtr(&list_broken_head);

    const hlist_empty_head = hlist_view.HListHead{ .first = 0 };

    var hlist_ordered_head = hlist_view.HListHead{ .first = 0 };
    var hlist_ordered_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_ordered_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    hlist_ordered_head.first = @intFromPtr(&hlist_ordered_first);
    hlist_ordered_first.next = @intFromPtr(&hlist_ordered_second);
    hlist_ordered_first.pprev = @intFromPtr(&hlist_ordered_head.first);
    hlist_ordered_second.next = 0;
    hlist_ordered_second.pprev = @intFromPtr(&hlist_ordered_first.next);

    var hlist_broken_head = hlist_view.HListHead{ .first = 0 };
    var hlist_broken_first = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    var hlist_broken_second = hlist_view.HListNode{ .next = 0, .pprev = 0 };
    hlist_broken_head.first = @intFromPtr(&hlist_broken_first);
    hlist_broken_first.next = @intFromPtr(&hlist_broken_second);
    hlist_broken_first.pprev = @intFromPtr(&hlist_broken_head.first);
    hlist_broken_second.next = 0;
    hlist_broken_second.pprev = @intFromPtr(&hlist_broken_head.first);

    try writer.print(
        "{{\n" ++
            "  \"word_bits\": {},\n" ++
            "  \"list_cases\": [\n",
        .{@bitSizeOf(usize)},
    );
    try writeListCase(writer, "empty", &list_empty_head, &list_empty_head, &list_empty_head, true);
    try writeListCase(writer, "ordered_two", &list_ordered_head, &list_ordered_first, &list_ordered_second, true);
    try writeListCase(writer, "broken_backlink", &list_broken_head, &list_broken_first, &list_broken_second, false);
    try writer.writeAll("  ],\n  \"hlist_cases\": [\n");
    try writeHListCase(writer, "empty", &hlist_empty_head, &hlist_ordered_first, &hlist_ordered_second, true);
    try writeHListCase(writer, "ordered_two", &hlist_ordered_head, &hlist_ordered_first, &hlist_ordered_second, true);
    try writeHListCase(writer, "broken_prev_link", &hlist_broken_head, &hlist_broken_first, &hlist_broken_second, false);
    try writer.writeAll("  ]\n}\n");
    try stdout_writer.interface.flush();
}
