const std = @import("std");
const Io = std.Io;

const config_prefix = "CONFIG_";

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

fn deinitEntries(allocator: std.mem.Allocator, entries: []Entry) void {
    for (entries) |entry| {
        allocator.free(entry.name);
        allocator.free(entry.value);
    }
}

fn writeHexLower(writer: anytype, value: u8) !void {
    const digits = "0123456789abcdef";
    try writer.writeByte(digits[value >> 4]);
    try writer.writeByte(digits[value & 0x0f]);
}

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |c| switch (c) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        '\x08' => try writer.writeAll("\\b"),
        '\x0c' => try writer.writeAll("\\f"),
        0...0x07, 0x0b, 0x0e...0x1f => {
            try writer.writeAll("\\u00");
            try writeHexLower(writer, c);
        },
        else => try writer.writeByte(c),
    };
}

fn trimTrailingCarriageReturn(text: []const u8) []const u8 {
    if (text.len > 0 and text[text.len - 1] == '\r') {
        return text[0 .. text.len - 1];
    }
    return text;
}

fn trimLeadingUtf8Bom(text: []const u8, is_first_line: bool) []const u8 {
    if (is_first_line and std.mem.startsWith(u8, text, "\xef\xbb\xbf")) {
        return text[3..];
    }
    return text;
}

fn truncateAtFirstNull(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

fn nextConfigLine(input: []const u8, cursor: *usize) ?[]const u8 {
    if (cursor.* >= input.len) return null;
    const line_start = cursor.*;
    const remaining = input[line_start..];
    if (std.mem.indexOfScalar(u8, remaining, '\n')) |newline_index| {
        cursor.* += newline_index + 1;
        return truncateAtFirstNull(trimLeadingUtf8Bom(trimTrailingCarriageReturn(remaining[0..newline_index]), line_start == 0));
    }

    cursor.* = input.len;
    return truncateAtFirstNull(trimLeadingUtf8Bom(remaining, line_start == 0));
}

fn findClosingQuote(raw_value: []const u8) ?usize {
    if (raw_value.len < 2 or raw_value[0] != '"') return null;

    var index: usize = 1;
    while (index < raw_value.len) : (index += 1) {
        if (raw_value[index] == '\\') {
            if (index + 1 < raw_value.len) {
                index += 1;
            }
            continue;
        }
        if (raw_value[index] == '"') {
            return index;
        }
    }

    return null;
}

fn decodeQuotedString(allocator: std.mem.Allocator, raw_value: []const u8, closing_quote_index: usize) ![]u8 {
    const inner = raw_value[1..closing_quote_index];
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
    if (raw_value.len == 0) return false;
    return switch (std.ascii.toLower(raw_value[0])) {
        'y', 'm', 'n' => true,
        else => false,
    };
}

fn dupCanonicalTristateValue(allocator: std.mem.Allocator, raw_value: []const u8) ![]u8 {
    const owned = try allocator.alloc(u8, 1);
    owned[0] = std.ascii.toLower(raw_value[0]);
    return owned;
}

fn isConfigSymbol(name: []const u8) bool {
    if (!std.mem.startsWith(u8, name, config_prefix) or name.len <= config_prefix.len) {
        return false;
    }

    for (name[config_prefix.len..]) |char| {
        if (!(std.ascii.isAlphanumeric(char) or char == '_')) return false;
    }
    return true;
}

fn parseUnsetSymbol(line: []const u8) ?[]const u8 {
    if (!std.mem.startsWith(u8, line, "# ")) return null;

    const body = line[2..];
    if (!std.mem.startsWith(u8, body, config_prefix)) return null;

    const separator_index = std.mem.indexOfScalar(u8, body, ' ') orelse return null;
    const name = body[0..separator_index];
    if (!isConfigSymbol(name)) return null;
    if (!std.mem.eql(u8, body[separator_index + 1 ..], "is not set")) return null;

    return name;
}

pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {
    var entries = std.ArrayList(Entry).empty;
    var entry_indexes = std.StringHashMap(usize).init(allocator);
    defer entry_indexes.deinit();
    errdefer {
        deinitEntries(allocator, entries.items);
        entries.deinit(allocator);
    }

    var set_count: usize = 0;
    var unset_count: usize = 0;
    var cursor: usize = 0;

    while (nextConfigLine(input, &cursor)) |line| {
        if (line.len == 0) continue;

        if (parseUnsetSymbol(line)) |name| {
            if (entry_indexes.get(name)) |existing_index| {
                const existing = &entries.items[existing_index];
                if (existing.kind == .unset) {
                    unset_count -= 1;
                } else {
                    set_count -= 1;
                }
                const owned_unset_value = try allocator.dupe(u8, "n");
                allocator.free(existing.value);
                existing.kind = .unset;
                existing.value = owned_unset_value;
            } else {
                const owned_name = try allocator.dupe(u8, name);
                var ownership_transferred = false;
                errdefer if (!ownership_transferred) allocator.free(owned_name);
                const owned_value = try allocator.dupe(u8, "n");
                errdefer if (!ownership_transferred) allocator.free(owned_value);

                try entries.append(allocator, .{
                    .name = owned_name,
                    .kind = .unset,
                    .value = owned_value,
                });
                ownership_transferred = true;
                errdefer if (ownership_transferred) {
                    const removed = entries.pop().?;
                    allocator.free(removed.name);
                    allocator.free(removed.value);
                };

                try entry_indexes.put(owned_name, entries.items.len - 1);
            }
            unset_count += 1;
            continue;
        }

        const eq_index = std.mem.indexOfScalar(u8, line, '=') orelse continue;
        const name = line[0..eq_index];
        if (!isConfigSymbol(name)) continue;
        const raw_value = line[eq_index + 1 ..];

        const closing_quote_index = findClosingQuote(raw_value);
        const malformed_quoted_value = raw_value.len > 0 and raw_value[0] == '"' and closing_quote_index == null;
        if (malformed_quoted_value) continue;
        const kind: EntryKind = if (isTristateValue(raw_value))
            .tristate
        else if (closing_quote_index != null)
            .string
        else
            .value;

        const cooked_value = if (kind == .tristate)
            try dupCanonicalTristateValue(allocator, raw_value)
        else if (closing_quote_index) |index|
            try decodeQuotedString(allocator, raw_value, index)
        else
            try allocator.dupe(u8, raw_value);

        if (entry_indexes.get(name)) |existing_index| {
            const existing = &entries.items[existing_index];
            if (existing.kind == .unset) {
                unset_count -= 1;
            } else {
                set_count -= 1;
            }
            allocator.free(existing.value);
            existing.kind = kind;
            existing.value = cooked_value;
        } else {
            var ownership_transferred = false;
            errdefer if (!ownership_transferred) allocator.free(cooked_value);
            const owned_name = try allocator.dupe(u8, name);
            errdefer if (!ownership_transferred) allocator.free(owned_name);

            try entries.append(allocator, .{
                .name = owned_name,
                .kind = kind,
                .value = cooked_value,
            });
            ownership_transferred = true;
            errdefer if (ownership_transferred) {
                const removed = entries.pop().?;
                allocator.free(removed.name);
                allocator.free(removed.value);
            };

            try entry_indexes.put(owned_name, entries.items.len - 1);
        }
        set_count += 1;
    }

    return .{
        .entries = try entries.toOwnedSlice(allocator),
        .set_count = set_count,
        .unset_count = unset_count,
    };
}

pub fn deinitSummary(allocator: std.mem.Allocator, summary: *Summary) void {
    deinitEntries(allocator, summary.entries);
    allocator.free(summary.entries);
}

pub fn runConfdataBridge(allocator: std.mem.Allocator, input: []const u8, writer: anytype) !void {
    var summary = try parseConfig(allocator, input);
    defer deinitSummary(allocator, &summary);

    try writer.writeAll("{\"counts\":{\"set\":");
    try writer.print("{}", .{summary.set_count});
    try writer.writeAll(",\"unset\":");
    try writer.print("{}", .{summary.unset_count});
    try writer.writeAll("},\"entries\":[");
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
    var summary = try parseConfig(
        allocator,
        "\xef\xbb\xbfCONFIG_ALPHA=y\n" ++
            "CONFIG_BETA=m\n" ++
            "CONFIG_COUNT=7\n" ++
            "CONFIG_NAME=\"zigux\"\n" ++
            "# CONFIG_DEBUG is not set\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 4), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 5), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqual(EntryKind.tristate, summary.entries[0].kind);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
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

test "confdata bridge keeps explicit empty assignments distinct from quoted empty strings" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(
        allocator,
        "CONFIG_EMPTY=\n" ++
            "CONFIG_QUOTED_EMPTY=\"\"\n",
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_EMPTY", summary.entries[0].name);
    try std.testing.expectEqual(EntryKind.value, summary.entries[0].kind);
    try std.testing.expectEqualStrings("", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_QUOTED_EMPTY", summary.entries[1].name);
    try std.testing.expectEqual(EntryKind.string, summary.entries[1].kind);
    try std.testing.expectEqualStrings("", summary.entries[1].value);
}
