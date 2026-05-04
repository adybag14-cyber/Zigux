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

const ValidateConfigPathError = error{
    EmptyConfigPath,
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

fn truncateAtFirstNull(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

fn nextConfigLine(input: []const u8, cursor: *usize) ?[]const u8 {
    if (cursor.* >= input.len) return null;

    const remaining = input[cursor.*..];
    if (std.mem.indexOfScalar(u8, remaining, '\n')) |newline_offset| {
        const line = truncateAtFirstNull(trimTrailingCarriageReturn(remaining[0..newline_offset]));
        cursor.* += newline_offset + 1;
        return line;
    }

    cursor.* = input.len;
    return truncateAtFirstNull(trimTrailingCarriageReturn(remaining));
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
                // Match confdata.c's bounded string handling: drop the escape
                // marker itself, but keep the following byte literal unless it
                // is one of the quote or backslash bytes being unescaped.
                try decoded.append(allocator, inner[index]);
            }
            continue;
        }
        try decoded.append(allocator, byte);
    }

    return decoded.toOwnedSlice(allocator);
}

fn isDecimalValue(raw_value: []const u8) bool {
    if (raw_value.len == 0) return false;

    const digits = if (raw_value[0] == '-') raw_value[1..] else raw_value;
    if (digits.len == 0) return false;
    if (!std.ascii.isDigit(digits[0])) return false;
    if (digits[0] == '0' and digits.len > 1) return false;

    for (digits[1..]) |byte| {
        if (!std.ascii.isDigit(byte)) return false;
    }
    return true;
}

fn isHexValue(raw_value: []const u8) bool {
    if (raw_value.len == 0) return false;

    var digits = raw_value;
    const has_prefix = digits.len >= 2 and digits[0] == '0' and (digits[1] == 'x' or digits[1] == 'X');
    if (has_prefix) digits = digits[2..];
    if (digits.len == 0) return false;

    var saw_alpha_digit = false;
    for (digits) |byte| {
        if (!std.ascii.isHex(byte)) return false;
        if (std.ascii.isAlphabetic(byte)) saw_alpha_digit = true;
    }
    return has_prefix or saw_alpha_digit;
}

fn findQuotedStringEnd(raw_value: []const u8) ?usize {
    if (raw_value.len == 0 or raw_value[0] != '"') return null;

    var index: usize = 1;
    while (index < raw_value.len) : (index += 1) {
        if (raw_value[index] == '\\') {
            if (index + 1 < raw_value.len) index += 1;
            continue;
        }
        if (raw_value[index] == '"') return index;
    }

    return null;
}

fn isMalformedQuotedString(raw_value: []const u8) bool {
    if (raw_value.len == 0) return false;
    if (raw_value[0] == '"') return findQuotedStringEnd(raw_value) == null;
    return raw_value[raw_value.len - 1] == '"';
}

fn hasEmptyConfigSymbolName(name: []const u8) bool {
    return name.len == "CONFIG_".len;
}

pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {
    var entries = std.ArrayList(Entry).empty;
    errdefer entries.deinit(allocator);

    var set_count: usize = 0;
    var unset_count: usize = 0;

    var cursor: usize = 0;
    while (nextConfigLine(input, &cursor)) |line| {
        if (line.len == 0) continue;

        if (std.mem.startsWith(u8, line, "# CONFIG_") and std.mem.endsWith(u8, line, " is not set")) {
            const name = line[2 .. line.len - " is not set".len];
            if (hasEmptyConfigSymbolName(name)) continue;
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
        if (hasEmptyConfigSymbolName(name)) continue;
        const raw_value = line[eq_index + 1 ..];

        // Match upstream confdata's invalid-string handling closely enough for the
        // bounded bridge: a one-sided quoted string is treated as malformed and skipped.
        if (isMalformedQuotedString(raw_value)) continue;

        const quoted_string_end = findQuotedStringEnd(raw_value);

        const kind: EntryKind = if (std.mem.eql(u8, raw_value, "y") or std.mem.eql(u8, raw_value, "m") or std.mem.eql(u8, raw_value, "n"))
            .tristate
        else if (quoted_string_end != null)
            .string
        else if (isHexValue(raw_value))
            .hex
        else if (isDecimalValue(raw_value))
            .int
        else
            .value;

        const cooked_value = if (kind == .string)
            try decodeQuotedString(allocator, raw_value[0 .. quoted_string_end.? + 1])
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

fn validateConfigPath(config_path: []const u8) ValidateConfigPathError!void {
    if (config_path.len == 0) return error.EmptyConfigPath;
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

    validateConfigPath(args[1]) catch {
        var stderr_buffer: [160]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("Error: config path must not be empty\n");
        try stderr_writer.interface.flush();
        std.process.exit(1);
    };

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

test "confdata bridge rejects empty config path arguments" {
    try std.testing.expectError(error.EmptyConfigPath, validateConfigPath(""));
    try validateConfigPath("zigux/tests/fixtures/kconfig_bridge/sample.config");
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
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"value\":\"abbfc\\u001dd\"") != null);
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

test "confdata bridge keeps trailing escaped backslashes in quoted strings" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_PATH=\"drivers\\\\\"\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqual(EntryKind.string, summary.entries[0].kind);
    try std.testing.expectEqualStrings("drivers\\", summary.entries[0].value);
}

test "confdata bridge keeps escaped control letters literal in quoted strings" {
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
    try std.testing.expectEqualStrings("line1nline2", summary.entries[0].value);
    try std.testing.expectEqualStrings("ziguxbbridge", summary.entries[1].value);
    try std.testing.expectEqualStrings("ziguxtbridge", summary.entries[2].value);
    try std.testing.expectEqualStrings("readyrok", summary.entries[3].value);
    try std.testing.expectEqualStrings("line1fline2", summary.entries[4].value);
}

test "confdata bridge preserves literal low control bytes distinct from escaped letters" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_CTRL=\"a\\bb\\fc\x1dd\"\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqual(EntryKind.string, summary.entries[0].kind);
    try std.testing.expectEqualStrings("abbfc\x1dd", summary.entries[0].value);
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

test "confdata bridge normalizes a trailing carriage return on the final unterminated line" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_DECIMAL=7\r",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_DECIMAL", summary.entries[0].name);
    try std.testing.expectEqual(EntryKind.int, summary.entries[0].kind);
    try std.testing.expectEqualStrings("7", summary.entries[0].value);
}

test "confdata bridge recognizes a final unset comment without a terminating newline once trailing CR is normalized" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_ALPHA=y\n# CONFIG_DEBUG is not set\r",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[0].kind);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[1].name);
    try std.testing.expectEqual(EntryKind.unset, summary.entries[1].kind);
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
}

test "confdata bridge ignores suffix bytes after an embedded NUL" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_ALPHA=y\x00suffix_noise\n" ++
            "CONFIG_BETA=\"zigux\"\x00trailing_bytes\n" ++
            "CONFIG_COUNT=42\x00garbage\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[0].kind);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.string, summary.entries[1].kind);
    try std.testing.expectEqualStrings("zigux", summary.entries[1].value);
    try std.testing.expectEqual(EntryKind.int, summary.entries[2].kind);
    try std.testing.expectEqualStrings("42", summary.entries[2].value);
}

test "confdata bridge preserves carriage return before an embedded NUL on newline-terminated lines" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_COUNT=7\r\x00suffix_noise\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqual(EntryKind.value, summary.entries[0].kind);
    try std.testing.expectEqualStrings("7\r", summary.entries[0].value);
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
        \\CONFIG_EMPTY=\"\"
        \\CONFIG_LABEL=\"zigux\"
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
        \\CONFIG_BROKEN=\"zigux
        \\CONFIG_LABEL=\"ok\"
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

test "confdata bridge keeps quoted payloads before trailing suffix bytes" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_BANNER=\"zigux\"suffix_noise
        \\CONFIG_STATE=y
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqual(EntryKind.string, summary.entries[0].kind);
    try std.testing.expectEqualStrings("zigux", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[1].kind);
    try std.testing.expectEqualStrings("y", summary.entries[1].value);
    try std.testing.expectEqual(EntryKind.unset, summary.entries[2].kind);
}

test "confdata bridge keeps escaped quoted payloads before trailing suffix bytes" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_BANNER=\"zigux \\\"bridge\\\"\"suffix_noise\n" ++
            "CONFIG_PATH=\"drivers\\\\zigux\"tail\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqual(EntryKind.string, summary.entries[0].kind);
    try std.testing.expectEqualStrings("zigux \"bridge\"", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.string, summary.entries[1].kind);
    try std.testing.expectEqualStrings("drivers\\zigux", summary.entries[1].value);
}

test "confdata bridge ignores non-CONFIG lines" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ALPHA=y
        \\BROKEN_ALPHA=y
        \\# BROKEN_BETA is not set
        \\CONFIG_NAME=\"zigux\"
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

test "confdata bridge skips entries with empty symbol names" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_=y
        \\# CONFIG_ is not set
        \\CONFIG_VALID=m
        \\# CONFIG_OTHER is not set
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_VALID", summary.entries[0].name);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[0].kind);
    try std.testing.expectEqualStrings("m", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_OTHER", summary.entries[1].name);
    try std.testing.expectEqual(EntryKind.unset, summary.entries[1].kind);
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
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

test "confdata bridge recognizes bare alphabetic hex values" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_BARE_HEX=2A
        \\CONFIG_BARE_UPPER_HEX=FF
        \\CONFIG_BARE_LOWER_HEX=ff
        \\CONFIG_PREFIXED_HEX=0x10
        \\CONFIG_DECIMAL=10
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 5), summary.entries.len);
    try std.testing.expectEqual(EntryKind.hex, summary.entries[0].kind);
    try std.testing.expectEqualStrings("2A", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.hex, summary.entries[1].kind);
    try std.testing.expectEqualStrings("FF", summary.entries[1].value);
    try std.testing.expectEqual(EntryKind.hex, summary.entries[2].kind);
    try std.testing.expectEqualStrings("ff", summary.entries[2].value);
    try std.testing.expectEqual(EntryKind.hex, summary.entries[3].kind);
    try std.testing.expectEqualStrings("0x10", summary.entries[3].value);
    try std.testing.expectEqual(EntryKind.int, summary.entries[4].kind);
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

test "confdata bridge keeps plus-signed numerics as fallback scalar values" {
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
    try std.testing.expectEqual(EntryKind.value, summary.entries[0].kind);
    try std.testing.expectEqualStrings("+42", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.value, summary.entries[1].kind);
    try std.testing.expectEqualStrings("+0x2A", summary.entries[1].value);
    try std.testing.expectEqual(EntryKind.value, summary.entries[2].kind);
    try std.testing.expectEqualStrings("+0XFF", summary.entries[2].value);
    try std.testing.expectEqual(EntryKind.value, summary.entries[3].kind);
}

test "confdata bridge keeps minus-signed hex values as fallback scalar values" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_NEGATIVE_HEX=-0x2A
        \\CONFIG_NEGATIVE_UPPER_HEX=-0XFF
        \\CONFIG_RAW=minus_alpha
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqual(EntryKind.value, summary.entries[0].kind);
    try std.testing.expectEqualStrings("-0x2A", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.value, summary.entries[1].kind);
    try std.testing.expectEqualStrings("-0XFF", summary.entries[1].value);
    try std.testing.expectEqual(EntryKind.value, summary.entries[2].kind);
}

test "confdata bridge keeps plus-signed and leading-zero decimals as fallback scalar values" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_PLUS_DECIMAL=+7
        \\CONFIG_PADDED_DECIMAL=042
        \\CONFIG_ZERO=0
        \\CONFIG_NEGATIVE=-9
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 4), summary.entries.len);
    try std.testing.expectEqual(EntryKind.value, summary.entries[0].kind);
    try std.testing.expectEqualStrings("+7", summary.entries[0].value);
    try std.testing.expectEqual(EntryKind.value, summary.entries[1].kind);
    try std.testing.expectEqualStrings("042", summary.entries[1].value);
    try std.testing.expectEqual(EntryKind.int, summary.entries[2].kind);
    try std.testing.expectEqualStrings("0", summary.entries[2].value);
    try std.testing.expectEqual(EntryKind.int, summary.entries[3].kind);
    try std.testing.expectEqualStrings("-9", summary.entries[3].value);
}

test "confdata bridge emits escaped quoted payloads before trailing suffix bytes" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 224), .allocator = allocator };
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
        "CONFIG_BANNER=\"zigux \\\"bridge\\\"\"suffix_noise\n" ++
            "CONFIG_PATH=\"drivers\\\\zigux\"tail\n",
        &capture,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":0") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "{\"name\":\"CONFIG_BANNER\",\"kind\":\"string\",\"value\":\"zigux \\\"bridge\\\"\"}") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "{\"name\":\"CONFIG_PATH\",\"kind\":\"string\",\"value\":\"drivers\\\\zigux\"}") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "suffix_noise") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "tail") == null);
}
