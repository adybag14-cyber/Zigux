const std = @import("std");
const bpf_type_names = @import("bpf_type_names");

const DenseTableEntry = struct {
    token: []const u8,
    name: []const u8,
};

fn readWorkspaceFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

fn trimInlineBlockComment(line: []const u8) []const u8 {
    return line[0 .. std.mem.indexOf(u8, line, "/*") orelse line.len];
}

fn trimAscii(line: []const u8) []const u8 {
    return std.mem.trim(u8, line, " \t\r");
}

fn enumBody(header_text: []const u8, enum_marker: []const u8) ![]const u8 {
    const enum_start = std.mem.indexOf(u8, header_text, enum_marker) orelse return error.MissingEnum;
    const body_start_rel = std.mem.indexOfScalar(u8, header_text[enum_start..], '{') orelse return error.MissingEnumBody;
    const body_start = enum_start + body_start_rel + 1;
    const body_end_rel = std.mem.indexOf(u8, header_text[body_start..], "};") orelse return error.MissingEnumBodyEnd;
    return header_text[body_start .. body_start + body_end_rel];
}

fn parseEnumAssignment(header_text: []const u8, enum_marker: []const u8, value_text: []const u8) anyerror!usize {
    if (std.ascii.isAlphabetic(value_text[0]) or value_text[0] == '_') {
        return parseEnumOrdinal(header_text, enum_marker, value_text);
    }

    return std.fmt.parseInt(usize, value_text, 0) catch error.UnsupportedEnumAssignment;
}

fn parseEnumOrdinal(header_text: []const u8, enum_marker: []const u8, token: []const u8) anyerror!usize {
    const body = try enumBody(header_text, enum_marker);
    var next_ordinal: usize = 0;
    var saw_entry = false;
    var lines = std.mem.splitScalar(u8, body, '\n');
    while (lines.next()) |raw_line| {
        const trimmed = trimAscii(trimInlineBlockComment(raw_line));
        if (trimmed.len == 0) continue;

        const comma = std.mem.indexOfScalar(u8, trimmed, ',') orelse continue;
        const item = trimAscii(trimmed[0..comma]);
        if (item.len == 0) continue;

        var current_ordinal = next_ordinal;
        var item_token = item;
        if (std.mem.indexOfScalar(u8, item, '=')) |equals| {
            item_token = trimAscii(item[0..equals]);
            const value_text = trimAscii(item[equals + 1 ..]);
            if (value_text.len == 0) return error.InvalidEnumAssignment;
            current_ordinal = try parseEnumAssignment(header_text, enum_marker, value_text);
        } else if (!saw_entry) {
            current_ordinal = 0;
        }

        if (std.mem.eql(u8, item_token, token)) {
            return current_ordinal;
        }

        next_ordinal = current_ordinal + 1;
        saw_entry = true;
    }

    return error.MissingEnumToken;
}

fn denseTableBody(table_text: []const u8, table_marker: []const u8) ![]const u8 {
    const table_start = std.mem.indexOf(u8, table_text, table_marker) orelse return error.MissingTable;
    const body_start_rel = std.mem.indexOfScalar(u8, table_text[table_start..], '{') orelse return error.MissingTableBody;
    const body_start = table_start + body_start_rel + 1;
    const body_end_rel = std.mem.indexOf(u8, table_text[body_start..], "};") orelse return error.MissingTableBodyEnd;
    return table_text[body_start .. body_start + body_end_rel];
}

fn parseDenseTableEntry(raw_line: []const u8) ?DenseTableEntry {
    const trimmed = trimAscii(trimInlineBlockComment(raw_line));
    const token_start = std.mem.indexOfScalar(u8, trimmed, '[') orelse return null;
    const token_end = std.mem.indexOfScalarPos(u8, trimmed, token_start + 1, ']') orelse return null;
    const quote_start = std.mem.indexOfScalar(u8, trimmed, '"') orelse return null;
    const quote_end = std.mem.indexOfScalarPos(u8, trimmed, quote_start + 1, '"') orelse return null;
    return .{
        .token = trimAscii(trimmed[token_start + 1 .. token_end]),
        .name = trimmed[quote_start + 1 .. quote_end],
    };
}

fn validateDenseTable(
    header_text: []const u8,
    table_text: []const u8,
    table_marker: []const u8,
    enum_marker: []const u8,
    expected_len: usize,
    helper: *const fn (i32) ?[]const u8,
) !void {
    const body = try denseTableBody(table_text, table_marker);
    var lines = std.mem.splitScalar(u8, body, '\n');
    var entry_count: usize = 0;
    var max_ordinal: usize = 0;

    while (lines.next()) |raw_line| {
        const entry = parseDenseTableEntry(raw_line) orelse continue;
        const ordinal = try parseEnumOrdinal(header_text, enum_marker, entry.token);
        const resolved = helper(@intCast(ordinal)) orelse return error.MissingResolvedName;
        try std.testing.expectEqualStrings(entry.name, resolved);
        entry_count += 1;
        max_ordinal = @max(max_ordinal, ordinal);
    }

    try std.testing.expectEqual(expected_len, entry_count);
    try std.testing.expectEqual(expected_len, max_ordinal + 1);
    try std.testing.expectEqual(@as(?[]const u8, null), helper(-1));
    try std.testing.expectEqual(@as(?[]const u8, null), helper(@intCast(expected_len)));
}

test "phase 8 bpf type-name segment imports cleanly" {
    _ = bpf_type_names;
}

test "phase 8 bpf type-name segment keeps live libbpf tables aligned with current UAPI ordinals" {
    const uapi_bpf_h = try readWorkspaceFile(
        std.testing.allocator,
        "tools/include/uapi/linux/bpf.h",
        512 * 1024,
    );
    defer std.testing.allocator.free(uapi_bpf_h);

    const libbpf_c = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/libbpf.c",
        1024 * 1024,
    );
    defer std.testing.allocator.free(libbpf_c);

    try validateDenseTable(
        uapi_bpf_h,
        libbpf_c,
        "static const char * const attach_type_name[] = {",
        "enum bpf_attach_type {",
        bpf_type_names.attach_type_names.len,
        bpf_type_names.libbpfBpfAttachTypeStr,
    );
    try validateDenseTable(
        uapi_bpf_h,
        libbpf_c,
        "static const char * const link_type_name[] = {",
        "enum bpf_link_type {",
        bpf_type_names.link_type_names.len,
        bpf_type_names.libbpfBpfLinkTypeStr,
    );
    try validateDenseTable(
        uapi_bpf_h,
        libbpf_c,
        "static const char * const map_type_name[] = {",
        "enum bpf_map_type {",
        bpf_type_names.map_type_names.len,
        bpf_type_names.libbpfBpfMapTypeStr,
    );
    try validateDenseTable(
        uapi_bpf_h,
        libbpf_c,
        "static const char * const prog_type_name[] = {",
        "enum bpf_prog_type {",
        bpf_type_names.prog_type_names.len,
        bpf_type_names.libbpfBpfProgTypeStr,
    );
}

test "phase 8 bpf type-name segment still exposes the current live enum ceilings" {
    try std.testing.expectEqualStrings(
        "trace_fsession",
        bpf_type_names.libbpfBpfAttachTypeStr(@intCast(bpf_type_names.attach_type_names.len - 1)).?,
    );
    try std.testing.expectEqualStrings(
        "sockmap",
        bpf_type_names.libbpfBpfLinkTypeStr(@intCast(bpf_type_names.link_type_names.len - 1)).?,
    );
    try std.testing.expectEqualStrings(
        "insn_array",
        bpf_type_names.libbpfBpfMapTypeStr(@intCast(bpf_type_names.map_type_names.len - 1)).?,
    );
    try std.testing.expectEqualStrings(
        "netfilter",
        bpf_type_names.libbpfBpfProgTypeStr(@intCast(bpf_type_names.prog_type_names.len - 1)).?,
    );
}
