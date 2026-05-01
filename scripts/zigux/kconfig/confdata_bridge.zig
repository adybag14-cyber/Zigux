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

    var digits = raw_value;
    if (raw_value[0] == '-') {
        digits = raw_value[1..];
    } else if (raw_value[0] == '+') {
        return false;
    }

    if (digits.len == 0) return false;
    if (digits.len > 1 and digits[0] == '0') return false;

    for (digits) |byte| {
        if (!std.ascii.isDigit(byte)) return false;
    }
    return true;
}

fn isHexValue(raw_value: []const u8) bool {
    if (raw_value.len < 3) return false;
    if (raw_value[0] == '+' or raw_value[0] == '-') return false;
    if (raw_value[0] != '0' or (raw_value[1] != 'x' and raw_value[1] != 'X')) return false;

    for (raw_value[2..]) |byte| {
        if (!std.ascii.isHex(byte)) return false;
    }
    return true;
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

    var it = std.mem.splitScalar(u8, input, '\n');
    while (it.next()) |raw_line| {
        const line = trimTrailingCarriageReturn(raw_line);
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
