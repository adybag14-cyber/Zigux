const std = @import("std");
const Io = std.Io;

const EntryKind = enum {
    tristate,
    string,
    int,
    hex,
    value,
    unset,

    pub fn text(self: EntryKind) []const u8 {
        return switch (self) {
            .tristate => "tristate",
            .string => "string",
            .int => "int",
            .hex => "hex",
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

fn decrementCounts(kind: EntryKind, set_count: *usize, unset_count: *usize) void {
    switch (kind) {
        .unset => unset_count.* -= 1,
        else => set_count.* -= 1,
    }
}

fn incrementCounts(kind: EntryKind, set_count: *usize, unset_count: *usize) void {
    switch (kind) {
        .unset => unset_count.* += 1,
        else => set_count.* += 1,
    }
}

fn findEntryIndex(entries: []const Entry, name: []const u8) ?usize {
    for (entries, 0..) |entry, index| {
        if (std.mem.eql(u8, entry.name, name)) return index;
    }
    return null;
}

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |c| switch (c) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\x08' => try writer.writeAll("\\b"),
        '\x0c' => try writer.writeAll("\\f"),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        else => {
            if (c < 0x20) {
                try writer.print("\\u00{x:0>2}", .{c});
            } else {
                try writer.writeByte(c);
            }
        },
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
                const escaped = switch (inner[index]) {
                    'b' => '\x08',
                    'f' => '\x0c',
                    'n' => '\n',
                    'r' => '\r',
                    't' => '\t',
                    else => inner[index],
                };
                try decoded.append(allocator, escaped);
            }
            continue;
        }
        try decoded.append(allocator, byte);
    }

    return decoded.toOwnedSlice(allocator);
}

fn isDecimalValue(raw_value: []const u8) bool {
    if (raw_value.len == 0) return false;

    const digits = if (raw_value[0] == '-' or raw_value[0] == '+') raw_value[1..] else raw_value;
    if (digits.len == 0) return false;

    for (digits) |byte| {
        if (!std.ascii.isDigit(byte)) return false;
    }
    return true;
}

fn isHexValue(raw_value: []const u8) bool {
    if (raw_value.len < 3) return false;

    const digits = if (raw_value[0] == '-' or raw_value[0] == '+') raw_value[1..] else raw_value;
    if (digits.len < 3) return false;
    if (digits[0] != '0' or (digits[1] != 'x' and digits[1] != 'X')) return false;

    for (digits[2..]) |byte| {
        if (!std.ascii.isHex(byte)) return false;
    }
    return true;
}

fn isMalformedQuotedString(raw_value: []const u8) bool {
    if (raw_value.len == 0) return false;
    return (raw_value[0] == '"') != (raw_value[raw_value.len - 1] == '"');
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

        if (std.mem.startsWith(u8, line, "# CONFIG_") and std.mem.endsWith(u8, line, " is not set")) {
            const name = line[2 .. line.len - " is not set".len];
            if (findEntryIndex(entries.items, name)) |index| {
                decrementCounts(entries.items[index].kind, &set_count, &unset_count);
                allocator.free(entries.items[index].value);
                entries.items[index].kind = .unset;
                entries.items[index].value = try allocator.dupe(u8, "n");
            } else {
                try entries.append(allocator, .{
                    .name = try allocator.dupe(u8, name),
                    .kind = .unset,
                    .value = try allocator.dupe(u8, "n"),
                });
            }
            incrementCounts(.unset, &set_count, &unset_count);
            continue;
        }

        if (!std.mem.startsWith(u8, line, "CONFIG_")) continue;

        const eq_index = std.mem.indexOfScalar(u8, line, '=') orelse continue;
        const name = line[0..eq_index];
        const raw_value = line[eq_index + 1 ..];

        // Match upstream confdata's invalid-string handling closely enough for the
        // bounded bridge: a one-sided quoted string is treated as malformed and skipped.
        if (isMalformedQuotedString(raw_value)) continue;

        const kind: EntryKind = if (std.mem.eql(u8, raw_value, "y") or std.mem.eql(u8, raw_value, "m") or std.mem.eql(u8, raw_value, "n"))
            .tristate
        else if (raw_value.len >= 2 and raw_value[0] == '"' and raw_value[raw_value.len - 1] == '"')
            .string
        else if (isHexValue(raw_value))
            .hex
        else if (isDecimalValue(raw_value))
            .int
        else
            .value;

        const cooked_value = if (kind == .string)
            try decodeQuotedString(allocator, raw_value)
        else
            try allocator.dupe(u8, raw_value);

        if (findEntryIndex(entries.items, name)) |index| {
            decrementCounts(entries.items[index].kind, &set_count, &unset_count);
            allocator.free(entries.items[index].value);
            entries.items[index].kind = kind;
            entries.items[index].value = cooked_value;
        } else {
            try entries.append(allocator, .{
                .name = try allocator.dupe(u8, name),
                .kind = kind,
                .value = cooked_value,
            });
        }
        incrementCounts(kind, &set_count, &unset_count);
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
        \\CONFIG_NAME="zigux"
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 4), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 5), summary.entries.len);
    try std.testing.expectEqual(EntryKind.int, summary.entries[2].kind);
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

test "confdata bridge escapes low control bytes in emitted json" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 192), .allocator = allocator };
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

    try runConfdataBridge(
        std.testing.allocator,
        "CONFIG_CTRL=\"a\\bb\\fc\x1dd\"\n",
        &capture,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\b") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\f") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\\u00") != null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x08') == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x0c') == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x1d') == null);
}

test "confdata bridge decodes escaped quoted strings" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_BANNER=\"zigux \\\"bridge\\\"\"\n" ++
            "CONFIG_PATH=\"drivers\\\\zigux\"\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqual(EntryKind.string, summary.entries[0].kind);
    try std.testing.expectEqualStrings("zigux \"bridge\"", summary.entries[0].value);
    try std.testing.expectEqualStrings("drivers\\zigux", summary.entries[1].value);
}

test "confdata bridge decodes escaped control sequences in quoted strings" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_BANNER=\"line1\\nline2\"\n" ++
            "CONFIG_NOTE=\"zigux\\bbridge\"\n" ++
            "CONFIG_TITLE=\"zigux\\tbridge\"\n" ++
            "CONFIG_STATUS=\"ready\\rok\"\n" ++
            "CONFIG_FORM=\"line1\\fline2\"\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 5), summary.entries.len);
    try std.testing.expectEqualStrings("line1\nline2", summary.entries[0].value);
    try std.testing.expectEqualStrings("zigux\x08bridge", summary.entries[1].value);
    try std.testing.expectEqualStrings("zigux\tbridge", summary.entries[2].value);
    try std.testing.expectEqualStrings("ready\rok", summary.entries[3].value);
    try std.testing.expectEqualStrings("line1\x0cline2", summary.entries[4].value);
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

test "confdata bridge keeps empty quoted strings as string values" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_EMPTY=""
        \\CONFIG_LABEL="zigux"
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqual(EntryKind.string, summary.entries[0].kind);
    try std.testing.expectEqualStrings("", summary.entries[0].value);
    try std.testing.expectEqualStrings("zigux", summary.entries[1].value);
}

test "confdata bridge skips malformed quoted strings" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_BROKEN="zigux
        \\CONFIG_LABEL="ok"
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_LABEL", summary.entries[0].name);
    try std.testing.expectEqual(EntryKind.string, summary.entries[0].kind);
    try std.testing.expectEqualStrings("ok", summary.entries[0].value);
}

test "confdata bridge ignores non-CONFIG lines" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ALPHA=y
        \\BROKEN_ALPHA=y
        \\# BROKEN_BETA is not set
        \\CONFIG_NAME="zigux"
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("CONFIG_NAME", summary.entries[1].name);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
}

test "confdata bridge distinguishes integer, hex, and fallback scalar values" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_DECIMAL=42
        \\CONFIG_SIGNED=-7
        \\CONFIG_HEX=0x2A
        \\CONFIG_UPPER_HEX=0XFF
        \\CONFIG_RAW=alpha_beta
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 5), summary.entries.len);
    try std.testing.expectEqual(EntryKind.int, summary.entries[0].kind);
    try std.testing.expectEqual(EntryKind.int, summary.entries[1].kind);
    try std.testing.expectEqual(EntryKind.hex, summary.entries[2].kind);
    try std.testing.expectEqual(EntryKind.hex, summary.entries[3].kind);
    try std.testing.expectEqual(EntryKind.value, summary.entries[4].kind);
}

test "confdata bridge keeps the last assignment for duplicate symbols" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ALPHA=y
        \\CONFIG_ALPHA=m
        \\# CONFIG_BETA is not set
        \\CONFIG_BETA=y
        \\CONFIG_COUNT=7
        \\# CONFIG_COUNT is not set
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[0].kind);
    try std.testing.expectEqualStrings("m", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[1].kind);
    try std.testing.expectEqualStrings("y", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_COUNT", summary.entries[2].name);
    try std.testing.expectEqual(EntryKind.unset, summary.entries[2].kind);
    try std.testing.expectEqualStrings("n", summary.entries[2].value);
}

test "confdata bridge recognizes explicit plus-signed integers and hex values" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_POSITIVE_DECIMAL=+42
        \\CONFIG_POSITIVE_HEX=+0x2A
        \\CONFIG_POSITIVE_UPPER_HEX=+0XFF
        \\CONFIG_RAW=plus_alpha
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 4), summary.entries.len);
    try std.testing.expectEqual(EntryKind.int, summary.entries[0].kind);
    try std.testing.expectEqualStrings("+42", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.hex, summary.entries[1].kind);
    try std.testing.expectEqualStrings("+0x2A", summary.entries[1].value);
    try std.testing.expectEqual(EntryKind.hex, summary.entries[2].kind);
    try std.testing.expectEqualStrings("+0XFF", summary.entries[2].value);
    try std.testing.expectEqual(EntryKind.value, summary.entries[3].kind);
}
