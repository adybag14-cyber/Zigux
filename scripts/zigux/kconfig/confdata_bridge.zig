const std = @import("std");
const Io = std.Io;

const EntryKind = enum {
    tristate,
    string,
    value,
    unset,

    pub fn text(self: EntryKind) []const u8 {
        return switch (self) {
            .tristate => "tristate",
            .string => "string",
            .value => "value",
            .unset => "unset",
        };
    }
};

pub const Entry = struct {
    name: []const u8,
    kind: EntryKind,
    value: []const u8,
};

pub const Summary = struct {
    entries: []Entry,
    set_count: usize,
    unset_count: usize,
};

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |c| switch (c) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        else => try writer.writeByte(c),
    };
}

fn trimTrailingCarriageReturn(text: []const u8) []const u8 {
    if (text.len > 0 and text[text.len - 1] == '\r') {
        return text[0 .. text.len - 1];
    }
    return text;
}

fn decodeQuotedString(allocator: std.mem.Allocator, raw_value: []const u8) ![]u8 {
    const inner = raw_value[1 .. raw_value.len - 1];
    var decoded = std.ArrayList(u8).empty;
    errdefer decoded.deinit(allocator);

    var index: usize = 0;
    while (index < inner.len) : (index += 1) {
        const byte = inner[index];
        if (byte == '\\') {
            if (index + 1 < inner.len) {
                index += 1;
                try decoded.append(allocator, inner[index]);
            }
            continue;
        }
        try decoded.append(allocator, byte);
    }

    return decoded.toOwnedSlice(allocator);
}

fn isTristateValue(raw_value: []const u8) bool {
    return std.ascii.eqlIgnoreCase(raw_value, "y") or
        std.ascii.eqlIgnoreCase(raw_value, "m") or
        std.ascii.eqlIgnoreCase(raw_value, "n");
}

pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {
    var entries = std.ArrayList(Entry).empty;
    errdefer entries.deinit(allocator);

    var set_count: usize = 0;
    var unset_count: usize = 0;

    var it = std.mem.splitScalar(u8, input, '\n');
    while (it.next()) |raw_line| {
        const line = trimTrailingCarriageReturn(raw_line);
        if (line.len == 0) continue;

        if (std.mem.startsWith(u8, line, "# ") and std.mem.endsWith(u8, line, " is not set")) {
            const name = line[2 .. line.len - " is not set".len];
            try entries.append(allocator, .{
                .name = try allocator.dupe(u8, name),
                .kind = .unset,
                .value = try allocator.dupe(u8, "n"),
            });
            unset_count += 1;
            continue;
        }

        const eq_index = std.mem.indexOfScalar(u8, line, '=') orelse continue;
        const name = line[0..eq_index];
        const raw_value = line[eq_index + 1 ..];

        const kind: EntryKind = if (isTristateValue(raw_value))
            .tristate
        else if (raw_value.len >= 2 and raw_value[0] == '"' and raw_value[raw_value.len - 1] == '"')
            .string
        else
            .value;

        const cooked_value = if (kind == .string)
            try decodeQuotedString(allocator, raw_value)
        else
            try allocator.dupe(u8, raw_value);

        try entries.append(allocator, .{
            .name = try allocator.dupe(u8, name),
            .kind = kind,
            .value = cooked_value,
        });
        set_count += 1;
    }

    return .{
        .entries = try entries.toOwnedSlice(allocator),
        .set_count = set_count,
        .unset_count = unset_count,
    };
}

pub fn deinitSummary(allocator: std.mem.Allocator, summary: *Summary) void {
    for (summary.entries) |entry| {
        allocator.free(entry.name);
        allocator.free(entry.value);
    }
    allocator.free(summary.entries);
}

pub fn runConfdataBridge(allocator: std.mem.Allocator, input: []const u8, writer: anytype) !void {
    var summary = try parseConfig(allocator, input);
    defer deinitSummary(allocator, &summary);

    try writer.print("{{\"counts\":{{\"set\":{},\"unset\":{}}},\"entries\":[", .{ summary.set_count, summary.unset_count });
    for (summary.entries, 0..) |entry, index| {
        if (index != 0) try writer.writeByte(',');
        try writer.writeAll("{\"name\":\"");
        try writeJsonEscaped(writer, entry.name);
        try writer.writeAll("\",\"kind\":\"");
        try writer.writeAll(entry.kind.text());
        try writer.writeAll("\",\"value\":\"");
        try writeJsonEscaped(writer, entry.value);
        try writer.writeAll("\"}");
    }
    try writer.writeAll("]}\n");
}

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);

    if (args.len != 2) {
        var stderr_buffer: [160]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("Usage: confdata_bridge <config>\n");
        try stderr_writer.interface.flush();
        std.process.exit(1);
    }

    const input = try Io.Dir.cwd().readFileAlloc(io, args[1], arena, .limited(1024 * 1024));
    var stdout_buffer: [2048]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    try runConfdataBridge(arena, input, &stdout_writer.interface);
    try stdout_writer.interface.flush();
}

test "confdata bridge parses bounded config states" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ALPHA=y
        \\CONFIG_BETA=m
        \\CONFIG_COUNT=7
        \\CONFIG_NAME=\"zigux\"
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 4), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 5), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_NAME", summary.entries[3].name);
    try std.testing.expectEqual(EntryKind.string, summary.entries[3].kind);
    try std.testing.expectEqualStrings("zigux", summary.entries[3].value);
    try std.testing.expectEqual(EntryKind.unset, summary.entries[4].kind);
}

test "confdata bridge emits bounded json output" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 160), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA=y
        \\# CONFIG_DEBUG is not set
        \\
    , &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"CONFIG_DEBUG\"") != null);
}

test "confdata bridge decodes escaped quoted strings" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_BANNER=\"zigux \\\"bridge\\\"\"
        \\CONFIG_PATH=\"drivers\\\\zigux\"
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqual(EntryKind.string, summary.entries[0].kind);
    try std.testing.expectEqualStrings("zigux \"bridge\"", summary.entries[0].value);
    try std.testing.expectEqualStrings("drivers\\zigux", summary.entries[1].value);
}

test "confdata bridge accepts CRLF config lines" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_ALPHA=y\r\n" ++
            "CONFIG_NAME=\"zigux\"\r\n" ++
            "# CONFIG_DEBUG is not set\r\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("zigux", summary.entries[1].value);
    try std.testing.expectEqual(EntryKind.unset, summary.entries[2].kind);
}

test "confdata bridge trims trailing carriage return from final value line" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator, "CONFIG_DECIMAL=7\r");
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqual(EntryKind.value, summary.entries[0].kind);
    try std.testing.expectEqualStrings("CONFIG_DECIMAL", summary.entries[0].name);
    try std.testing.expectEqualStrings("7", summary.entries[0].value);
}

test "confdata bridge accepts unterminated unset comment with trailing carriage return" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_ALPHA=y\n" ++
            "# CONFIG_DEBUG is not set\r",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[0].kind);
    try std.testing.expectEqual(EntryKind.unset, summary.entries[1].kind);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[1].name);
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
}

test "confdata bridge keeps explicit n assignments as tristate values" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ALPHA=n
        \\CONFIG_BETA=y
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[0].kind);
    try std.testing.expectEqualStrings("n", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[1].kind);
}

test "confdata bridge recognizes uppercase tristate assignments" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ALPHA=Y
        \\CONFIG_BETA=M
        \\CONFIG_DEBUG=N
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[0].kind);
    try std.testing.expectEqualStrings("Y", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[1].kind);
    try std.testing.expectEqualStrings("M", summary.entries[1].value);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[2].kind);
    try std.testing.expectEqualStrings("N", summary.entries[2].value);
}
