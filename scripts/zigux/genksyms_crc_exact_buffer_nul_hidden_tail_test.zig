const std = @import("std");
const testing = std.testing;

const gen = @import("./genksyms_crc.zig");

const c_line_payload_len = 4095;

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) Capture {
        return .{
            .list = .empty,
            .allocator = allocator,
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "exact-buffer chunk hides bytes after NUL and still resumes on next visible record" {
    const visible = "visible_prefix_before_nul";
    const hidden = "hidden_tail_should_not_escape";
    const next = "next_visible_record";

    var input = try std.ArrayList(u8).initCapacity(testing.allocator, c_line_payload_len + 1 + next.len + 1);
    defer input.deinit(testing.allocator);

    try input.appendSlice(testing.allocator, visible);
    try input.append(testing.allocator, 0);
    while (input.items.len + hidden.len <= c_line_payload_len) {
        try input.appendSlice(testing.allocator, hidden);
    }
    try input.appendNTimes(testing.allocator, 'z', c_line_payload_len - input.items.len);
    try testing.expectEqual(@as(usize, c_line_payload_len), input.items.len);
    try input.append(testing.allocator, '\n');
    try input.appendSlice(testing.allocator, next);
    try input.append(testing.allocator, '\n');

    var output = Capture.init(testing.allocator);
    defer output.deinit();
    try gen.runGenksymsCrc(input.items, &output);

    const visible_crc = try std.fmt.allocPrint(testing.allocator, "0x{x:0>8}", .{gen.crc32(visible)});
    defer testing.allocator.free(visible_crc);
    const hidden_crc = try std.fmt.allocPrint(testing.allocator, "0x{x:0>8}", .{gen.crc32(hidden)});
    defer testing.allocator.free(hidden_crc);
    const next_crc = try std.fmt.allocPrint(testing.allocator, "0x{x:0>8}", .{gen.crc32(next)});
    defer testing.allocator.free(next_crc);

    try expectContains(output.list.items, "\"input\":\"visible_prefix_before_nul\"");
    try expectContains(output.list.items, visible_crc);
    try expectContains(output.list.items, "\"input\":\"next_visible_record\"");
    try expectContains(output.list.items, next_crc);
    try expectAbsent(output.list.items, "hidden_tail_should_not_escape");
    try expectAbsent(output.list.items, hidden_crc);
    try testing.expectEqual(@as(usize, 2), std.mem.count(u8, output.list.items, "crc_hex"));
    try testing.expectEqualStrings("]}\n", output.list.items[output.list.items.len - 3 ..]);
}
