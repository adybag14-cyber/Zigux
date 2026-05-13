const std = @import("std");
const Io = std.Io;
const abi = @import("notifier_abi_bindings");
const notifier_chain = @import("notifier_chain_view");

fn writeQuoted(writer: anytype, text: []const u8) !void {
    try writer.writeByte('"');
    try writer.writeAll(text);
    try writer.writeByte('"');
}

fn writeScenario(
    writer: anytype,
    comptime name: []const u8,
    head: ?*const abi.NotifierBlock,
) !void {
    const view = notifier_chain.ChainView.init(head);
    var priorities: [8]i32 = undefined;
    var count: usize = 0;
    var last_priority: ?i32 = null;
    var it = view.iterator();
    while (it.next()) |node| {
        priorities[count] = node.priority;
        count += 1;
        last_priority = node.priority;
    }

    try writeQuoted(writer, name);
    try writer.writeAll(":{\"len\":");
    try writer.print("{d}", .{view.len()});
    try writer.writeAll(",\"first_priority\":");
    if (view.first()) |first| {
        try writer.print("{d}", .{first.priority});
    } else {
        try writer.writeAll("null");
    }
    try writer.writeAll(",\"last_priority\":");
    if (last_priority) |value| {
        try writer.print("{d}", .{value});
    } else {
        try writer.writeAll("null");
    }
    try writer.writeAll(",\"nonincreasing\":");
    try writer.writeAll(if (view.hasNonincreasingPriority()) "true" else "false");
    try writer.writeAll(",\"priorities\":[");
    for (priorities[0..count], 0..) |priority, index| {
        if (index != 0) try writer.writeByte(',');
        try writer.print("{d}", .{priority});
    }
    try writer.writeAll("]}");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [2048]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    var ordered_tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = -4,
    };
    var ordered_middle = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&ordered_tail),
        .priority = 3,
    };
    var ordered_head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&ordered_middle),
        .priority = 12,
    };
    var unordered_tail = abi.NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    var unordered_head = abi.NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&unordered_tail),
        .priority = 1,
    };

    try writer.writeAll("{");
    try writeScenario(writer, "empty", null);
    try writer.writeByte(',');
    try writeScenario(writer, "ordered", &ordered_head);
    try writer.writeByte(',');
    try writeScenario(writer, "unordered", &unordered_head);
    try writer.writeAll(",\"results\":{");
    try writer.print(
        "\"done\":{d},\"ok\":{d},\"stop\":{d}",
        .{
            @intFromEnum(abi.NotifierResult.done),
            @intFromEnum(abi.NotifierResult.ok),
            @intFromEnum(abi.NotifierResult.stop),
        },
    );
    try writer.writeAll("}}\n");
    try stdout_writer.interface.flush();
}
