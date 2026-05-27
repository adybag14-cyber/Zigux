const std = @import("std");
const Io = std.Io;

const config_prefix = "CONFIG_";
const max_config_bytes: usize = std.math.maxInt(usize);

pub const EntryKind = enum {
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

fn readConfigFile(allocator: std.mem.Allocator, io: std.Io, path: []const u8) ![]u8 {
    return try Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(max_config_bytes));
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
    if (raw_value.len != 1) return false;
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

    const input = try readConfigFile(arena, io, args[1]);
    var stdout_buffer: [2048]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    try runConfdataBridge(arena, input, &stdout_writer.interface);
    try stdout_writer.interface.flush();
}

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }

    fn print(self: *TestCapture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

fn expectEntry(summary: Summary, index: usize, name: []const u8, kind: EntryKind, value: []const u8) !void {
    try std.testing.expectEqualStrings(name, summary.entries[index].name);
    try std.testing.expectEqual(kind, summary.entries[index].kind);
    try std.testing.expectEqualStrings(value, summary.entries[index].value);
}

fn parseAndExpectSingleEntry(allocator: std.mem.Allocator, input: []const u8, name: []const u8, kind: EntryKind, value: []const u8) !void {
    var summary = try parseConfig(allocator, input);
    defer deinitSummary(allocator, &summary);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqual(@as(usize, if (kind == .unset) 0 else 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, if (kind == .unset) 1 else 0), summary.unset_count);
    try expectEntry(summary, 0, name, kind, value);
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
    try expectEntry(summary, 0, "CONFIG_ALPHA", .tristate, "y");
    try expectEntry(summary, 3, "CONFIG_NAME", .string, "zigux");
    try std.testing.expectEqual(EntryKind.unset, summary.entries[4].kind);
}

test "confdata bridge emits bounded json output" {
    var capture = try TestCapture.init(std.testing.allocator);
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
        \\CONFIG_MESSAGE="zigux\"bridge\\"
        \\
    );
    defer deinitSummary(allocator, &summary);

    try expectEntry(summary, 0, "CONFIG_MESSAGE", .string, "zigux\"bridge\\");
}

test "confdata bridge strips backslashes from escaped control sequences like upstream confdata" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ESCAPED="line\n\tend"
        \\
    );
    defer deinitSummary(allocator, &summary);

    try expectEntry(summary, 0, "CONFIG_ESCAPED", .string, "linentend");
}

test "confdata bridge escapes low control bytes in json output" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try writeJsonEscaped(&capture, "\x01\x08\x0c");
    try std.testing.expectEqualStrings("\\u0001\\b\\f", capture.list.items);
}

test "confdata bridge accepts CRLF config lines" {
    try parseAndExpectSingleEntry(std.testing.allocator, "CONFIG_ALPHA=y\r\n", "CONFIG_ALPHA", .tristate, "y");
}

test "confdata bridge preserves trailing carriage return on final unterminated value line" {
    try parseAndExpectSingleEntry(std.testing.allocator, "CONFIG_ALPHA=value\r", "CONFIG_ALPHA", .value, "value\r");
}

test "confdata bridge ignores unterminated unset comment with trailing carriage return" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator, "# CONFIG_DEBUG is not set\r");
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 0), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 0), summary.entries.len);
}

test "confdata bridge ignores suffix bytes after an embedded NUL" {
    try parseAndExpectSingleEntry(std.testing.allocator, "CONFIG_ALPHA=value\x00suffix\n", "CONFIG_ALPHA", .value, "value");
}

test "confdata bridge preserves carriage return before an embedded NUL on newline-terminated lines" {
    try parseAndExpectSingleEntry(std.testing.allocator, "CONFIG_ALPHA=value\r\x00suffix\n", "CONFIG_ALPHA", .value, "value\r");
}

test "confdata bridge keeps explicit n assignments as tristate values" {
    try parseAndExpectSingleEntry(std.testing.allocator, "CONFIG_ALPHA=n\n", "CONFIG_ALPHA", .tristate, "n");
}

test "confdata bridge recognizes uppercase tristate assignments" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_Y=Y
        \\CONFIG_M=M
        \\CONFIG_N=N
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try expectEntry(summary, 0, "CONFIG_Y", .tristate, "y");
    try expectEntry(summary, 1, "CONFIG_M", .tristate, "m");
    try expectEntry(summary, 2, "CONFIG_N", .tristate, "n");
}

test "confdata bridge ignores non-CONFIG lines like upstream confdata" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\source "Kconfig"
        \\NOT_CONFIG=y
        \\CONFIG_WORD=yes
        \\CONFIG_ALPHA=m
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try expectEntry(summary, 0, "CONFIG_WORD", .value, "yes");
    try expectEntry(summary, 1, "CONFIG_ALPHA", .tristate, "m");
}

test "confdata bridge ignores empty CONFIG symbol names" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator, "CONFIG_=y\n");
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 0), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 0), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
}

test "confdata bridge ignores malformed unset comments with extra tokens" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator, "# CONFIG_DEBUG is not set today\n");
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 0), summary.entries.len);
}

test "confdata bridge keeps trailing escaped backslashes in quoted strings" {
    try parseAndExpectSingleEntry(std.testing.allocator,
        \\CONFIG_PATH="drivers\\"
        \\
    , "CONFIG_PATH", .string, "drivers\\");
}

test "confdata bridge ignores trailing suffix bytes after a closing quote like upstream confdata" {
    try parseAndExpectSingleEntry(std.testing.allocator, "CONFIG_ALPHA=\"zigux\"suffix\n", "CONFIG_ALPHA", .string, "zigux");
}

test "confdata bridge ignores malformed quoted values like upstream confdata" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator, "CONFIG_ALPHA=\"zigux\n");
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 0), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 0), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
}

test "confdata bridge emits no entries for empty CONFIG symbol names" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfdataBridge(std.testing.allocator, "CONFIG_=y\n", &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"entries\":[]") != null);
}

test "confdata bridge keeps only the last assignment for duplicate symbols" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ALPHA=y
        \\CONFIG_ALPHA=m
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try expectEntry(summary, 0, "CONFIG_ALPHA", .tristate, "m");
}

test "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ALPHA="stable"
        \\CONFIG_ALPHA="broken
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try expectEntry(summary, 0, "CONFIG_ALPHA", .string, "stable");
}

test "confdata bridge emits the preserved duplicate state after later malformed quoted assignments" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA="stable"
        \\CONFIG_ALPHA="broken
        \\
    , &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"CONFIG_ALPHA\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"value\":\"stable\"") != null);
}

test "confdata bridge keeps only the last state across unset and set transitions" {
    const allocator = std.testing.allocator;
    var summary = try parseConfig(allocator,
        \\CONFIG_ALPHA=y
        \\# CONFIG_ALPHA is not set
        \\CONFIG_ALPHA=m
        \\
    );
    defer deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try expectEntry(summary, 0, "CONFIG_ALPHA", .tristate, "m");
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
    try expectEntry(summary, 0, "CONFIG_EMPTY", .value, "");
    try expectEntry(summary, 1, "CONFIG_QUOTED_EMPTY", .string, "");
}

test "confdata bridge emits explicit empty assignments distinctly in json output" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfdataBridge(std.testing.allocator,
        \\CONFIG_EMPTY=
        \\CONFIG_QUOTED_EMPTY=""
        \\
    , &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_QUOTED_EMPTY\",\"kind\":\"string\",\"value\":\"\"") != null);
}

test "confdata bridge escapes parsed string bytes in json output" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfdataBridge(std.testing.allocator,
        \\CONFIG_ALPHA="zigux\"bridge\\"
        \\
    , &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"value\":\"zigux\\\"bridge\\\\\"") != null);
}

test "confdata bridge file reader accepts config inputs beyond one mebibyte" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const header = "CONFIG_BIG=value\n# ";
    const padding_len = (1024 * 1024) + 64;
    var file_bytes = try std.ArrayList(u8).initCapacity(std.testing.allocator, header.len + padding_len + 1);
    defer file_bytes.deinit(std.testing.allocator);
    try file_bytes.appendSlice(std.testing.allocator, header);
    try file_bytes.appendNTimes(std.testing.allocator, 'a', padding_len);
    try file_bytes.append(std.testing.allocator, '\n');

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "large.config",
        .data = file_bytes.items,
    });

    const config_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/large.config",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(config_path);

    const input = try readConfigFile(std.testing.allocator, std.testing.io, config_path);
    defer std.testing.allocator.free(input);

    try std.testing.expect(input.len > 1024 * 1024);

    var summary = try parseConfig(std.testing.allocator, input);
    defer deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try expectEntry(summary, 0, "CONFIG_BIG", .value, "value");
}

test "confdata bridge releases appended entry ownership on index-allocation failure" {
    const Harness = struct {
        fn run(allocator: std.mem.Allocator) !void {
            var summary = try parseConfig(allocator,
                \\CONFIG_ALPHA=y
                \\
            );
            defer deinitSummary(allocator, &summary);
            try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
        }
    };

    try std.testing.checkAllAllocationFailures(std.testing.allocator, Harness.run, .{});
}

test "confdata bridge preserves duplicate unset ownership on allocation failure" {
    const Harness = struct {
        fn run(allocator: std.mem.Allocator) !void {
            var summary = try parseConfig(allocator,
                \\# CONFIG_DEBUG is not set
                \\# CONFIG_DEBUG is not set
                \\
            );
            defer deinitSummary(allocator, &summary);
            try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
            try expectEntry(summary, 0, "CONFIG_DEBUG", .unset, "n");
        }
    };

    try std.testing.checkAllAllocationFailures(std.testing.allocator, Harness.run, .{});
}
