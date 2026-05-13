const std = @import("std");

pub const DirectoryEntry = struct {
    name: []const u8,
    is_executable: bool,
};

pub const CmdName = struct {
    name: []u8,
};

pub const CmdNames = struct {
    allocator: std.mem.Allocator,
    names: std.ArrayList(CmdName),

    pub fn init(allocator: std.mem.Allocator) CmdNames {
        return .{
            .allocator = allocator,
            .names = .empty,
        };
    }

    pub fn deinit(self: *CmdNames) void {
        for (self.names.items) |entry| {
            self.allocator.free(entry.name);
        }
        self.names.deinit(self.allocator);
        self.* = undefined;
    }

    pub fn count(self: CmdNames) usize {
        return self.names.items.len;
    }

    pub fn longestNameLen(self: CmdNames) usize {
        var longest: usize = 0;
        for (self.names.items) |entry| {
            longest = @max(longest, entry.name.len);
        }
        return longest;
    }

    pub fn addCmdName(self: *CmdNames, name: []const u8, len: usize) !void {
        const clipped = name[0..@min(name.len, len)];
        const owned = try self.allocator.dupe(u8, clipped);
        errdefer self.allocator.free(owned);
        try self.names.append(self.allocator, .{ .name = owned });
    }

    pub fn sort(self: *CmdNames) void {
        var i: usize = 1;
        while (i < self.names.items.len) : (i += 1) {
            var j = i;
            while (j > 0 and std.mem.order(u8, self.names.items[j - 1].name, self.names.items[j].name) == .gt) : (j -= 1) {
                std.mem.swap(CmdName, &self.names.items[j - 1], &self.names.items[j]);
            }
        }
    }

    pub fn uniq(self: *CmdNames) void {
        if (self.names.items.len <= 1) return;

        var write_index: usize = 1;
        var read_index: usize = 1;
        while (read_index < self.names.items.len) : (read_index += 1) {
            if (std.mem.eql(u8, self.names.items[write_index - 1].name, self.names.items[read_index].name)) {
                self.allocator.free(self.names.items[read_index].name);
                continue;
            }

            if (write_index != read_index) {
                self.names.items[write_index] = self.names.items[read_index];
            }
            write_index += 1;
        }

        self.names.items.len = write_index;
    }

    pub fn isInCmdList(self: CmdNames, name: []const u8) bool {
        for (self.names.items) |entry| {
            if (std.mem.eql(u8, entry.name, name)) return true;
        }
        return false;
    }

    pub fn excludeCmds(self: *CmdNames, excludes: CmdNames) void {
        var write_index: usize = 0;
        for (self.names.items, 0..) |entry, read_index| {
            if (excludes.isInCmdList(entry.name)) {
                self.allocator.free(entry.name);
                continue;
            }

            if (write_index != read_index) {
                self.names.items[write_index] = self.names.items[read_index];
            }
            write_index += 1;
        }
        self.names.items.len = write_index;
    }
};

pub const PathEntries = struct {
    allocator: std.mem.Allocator,
    entries: std.ArrayList([]u8),

    pub fn init(allocator: std.mem.Allocator) PathEntries {
        return .{
            .allocator = allocator,
            .entries = .empty,
        };
    }

    pub fn deinit(self: *PathEntries) void {
        for (self.entries.items) |entry| {
            self.allocator.free(entry);
        }
        self.entries.deinit(self.allocator);
        self.* = undefined;
    }

    pub fn count(self: PathEntries) usize {
        return self.entries.items.len;
    }
};

pub const TerminalDimensions = struct {
    rows: usize,
    cols: usize,
};

pub const PrettyPrintLayout = struct {
    cols: usize,
    rows: usize,
    spacing: usize,
};

const default_prefix = "perf-";
const default_terminal = TerminalDimensions{ .rows = 25, .cols = 80 };

pub fn commandNameFromEntry(entry_name: []const u8, prefix: []const u8) ?[]const u8 {
    if (!std.mem.startsWith(u8, entry_name, prefix)) return null;

    var name = entry_name[prefix.len..];
    if (std.mem.endsWith(u8, name, ".exe")) {
        name = name[0 .. name.len - 4];
    }
    return name;
}

pub fn addExecutableEntry(
    cmds: *CmdNames,
    entry_name: []const u8,
    prefix: []const u8,
    is_executable: bool,
) !bool {
    if (!is_executable) return false;
    const command_name = commandNameFromEntry(entry_name, prefix) orelse return false;
    try cmds.addCmdName(command_name, command_name.len);
    return true;
}

pub fn addExecutableEntries(cmds: *CmdNames, entries: []const DirectoryEntry, prefix: []const u8) !void {
    for (entries) |entry| {
        _ = try addExecutableEntry(cmds, entry.name, prefix, entry.is_executable);
    }
}

pub fn splitPathEntries(allocator: std.mem.Allocator, raw_path: []const u8) !PathEntries {
    var result = PathEntries.init(allocator);
    errdefer result.deinit();

    var start: usize = 0;
    var index: usize = 0;
    while (index <= raw_path.len) : (index += 1) {
        if (index != raw_path.len and raw_path[index] != ':') continue;

        const entry = try allocator.dupe(u8, raw_path[start..index]);
        errdefer allocator.free(entry);
        try result.entries.append(allocator, entry);
        start = index + 1;
    }

    if (raw_path.len == 0) {
        return result;
    }

    return result;
}

fn seenEarlierPath(paths: []const []const u8, upto: usize, candidate: []const u8) bool {
    var index: usize = 0;
    while (index < upto) : (index += 1) {
        if (std.mem.eql(u8, paths[index], candidate)) return true;
    }
    return false;
}

pub fn loadCommandListsFromSource(
    prefix: ?[]const u8,
    exec_path: ?[]const u8,
    path_entries: []const []const u8,
    main_cmds: *CmdNames,
    other_cmds: *CmdNames,
    source: anytype,
    comptime populateFn: anytype,
) !void {
    const chosen_prefix = prefix orelse default_prefix;

    if (exec_path) |path| {
        try populateFn(source, main_cmds, path, chosen_prefix);
    }

    for (path_entries, 0..) |path, index| {
        if (exec_path) |primary| {
            if (std.mem.eql(u8, path, primary)) continue;
        }
        if (seenEarlierPath(path_entries, index, path)) continue;
        try populateFn(source, other_cmds, path, chosen_prefix);
    }

    main_cmds.sort();
    main_cmds.uniq();
    other_cmds.sort();
    other_cmds.uniq();
    other_cmds.excludeCmds(main_cmds.*);
}

pub fn loadCommandListsFromEnvPath(
    allocator: std.mem.Allocator,
    prefix: ?[]const u8,
    exec_path: ?[]const u8,
    raw_path: []const u8,
    main_cmds: *CmdNames,
    other_cmds: *CmdNames,
    source: anytype,
    comptime populateFn: anytype,
) !void {
    var split_entries = try splitPathEntries(allocator, raw_path);
    defer split_entries.deinit();

    var borrowed = try allocator.alloc([]const u8, split_entries.entries.items.len);
    defer allocator.free(borrowed);
    for (split_entries.entries.items, 0..) |entry, index| {
        borrowed[index] = entry;
    }

    try loadCommandListsFromSource(
        prefix,
        exec_path,
        borrowed,
        main_cmds,
        other_cmds,
        source,
        populateFn,
    );
}

fn parsePositiveDimension(text: ?[]const u8) ?usize {
    const raw = text orelse return null;
    const trimmed = std.mem.trim(u8, raw, " \t\r\n");
    if (trimmed.len == 0) return null;

    var index: usize = 0;
    if (trimmed[index] == '+') index += 1;

    const start = index;
    while (index < trimmed.len and std.ascii.isDigit(trimmed[index])) : (index += 1) {}
    if (index == start) return null;

    const value = std.fmt.parseInt(usize, trimmed[start..index], 10) catch return null;
    if (value == 0) return null;
    return value;
}

pub fn resolveTerminalDimensions(
    lines_text: ?[]const u8,
    columns_text: ?[]const u8,
    fallback: ?TerminalDimensions,
) TerminalDimensions {
    const rows = parsePositiveDimension(lines_text);
    const cols = parsePositiveDimension(columns_text);
    if (rows != null and cols != null) {
        return .{ .rows = rows.?, .cols = cols.? };
    }
    return fallback orelse default_terminal;
}

pub fn planPrettyPrint(count: usize, longest_name_len: usize, terminal_cols: usize) PrettyPrintLayout {
    const safe_spacing = @max(@as(usize, 1), longest_name_len + 1);
    const max_cols = terminal_cols -| 1;

    var cols: usize = 1;
    if (safe_spacing < max_cols) {
        cols = @max(@as(usize, 1), max_cols / safe_spacing);
    }

    const rows = if (count == 0) 0 else std.math.divCeil(usize, count, cols) catch count;
    return .{
        .cols = cols,
        .rows = rows,
        .spacing = safe_spacing,
    };
}

pub fn planPrettyPrintForTerminal(
    count: usize,
    longest_name_len: usize,
    lines_text: ?[]const u8,
    columns_text: ?[]const u8,
    fallback: ?TerminalDimensions,
) PrettyPrintLayout {
    const terminal = resolveTerminalDimensions(lines_text, columns_text, fallback);
    _ = terminal.rows;
    return planPrettyPrint(count, longest_name_len, terminal.cols);
}

pub fn writePrettyPrintStringListForTerminal(
    writer: anytype,
    cmds: CmdNames,
    longest_name_len: usize,
    lines_text: ?[]const u8,
    columns_text: ?[]const u8,
    fallback: ?TerminalDimensions,
) !void {
    if (cmds.count() == 0) return;

    const layout = planPrettyPrintForTerminal(
        cmds.count(),
        longest_name_len,
        lines_text,
        columns_text,
        fallback,
    );

    var row: usize = 0;
    while (row < layout.rows) : (row += 1) {
        try writer.writeByte(' ');

        var col: usize = 0;
        while (col < layout.cols) : (col += 1) {
            const index = row + (col * layout.rows);
            if (index >= cmds.count()) break;

            const cell_width = if (col == layout.cols - 1 or index + layout.rows >= cmds.count()) 1 else layout.spacing;
            const name = cmds.names.items[index].name;
            try writer.writeAll(name);

            var padding = cell_width;
            while (padding > name.len) : (padding -= 1) {
                try writer.writeByte(' ');
            }
        }

        try writer.writeByte('\n');
    }
}

fn writeRule(writer: anytype, width: usize) !void {
    var index: usize = 0;
    while (index < width) : (index += 1) {
        try writer.writeByte('-');
    }
    try writer.writeByte('\n');
}

fn writeSection(
    writer: anytype,
    heading: []const u8,
    cmds: CmdNames,
    lines_text: ?[]const u8,
    columns_text: ?[]const u8,
    fallback: ?TerminalDimensions,
) !void {
    if (cmds.count() == 0) return;

    try writer.writeAll(heading);
    try writer.writeByte('\n');
    try writeRule(writer, heading.len);
    try writePrettyPrintStringListForTerminal(
        writer,
        cmds,
        cmds.longestNameLen(),
        lines_text,
        columns_text,
        fallback,
    );
    try writer.writeByte('\n');
}

pub fn writeCommandSectionsForTerminal(
    writer: anytype,
    exec_name: []const u8,
    exec_path_display: []const u8,
    main_cmds: CmdNames,
    other_cmds: CmdNames,
    lines_text: ?[]const u8,
    columns_text: ?[]const u8,
    fallback: ?TerminalDimensions,
) !void {
    if (main_cmds.count() != 0) {
        var header_buffer: [256]u8 = undefined;
        const heading = try std.fmt.bufPrint(
            &header_buffer,
            "available {s} in '{s}'",
            .{ exec_name, exec_path_display },
        );
        try writeSection(writer, heading, main_cmds, lines_text, columns_text, fallback);
    }

    if (other_cmds.count() != 0) {
        var header_buffer: [256]u8 = undefined;
        const heading = try std.fmt.bufPrint(
            &header_buffer,
            "{s} available from elsewhere on your $PATH",
            .{exec_name},
        );
        try writeSection(writer, heading, other_cmds, lines_text, columns_text, fallback);
    }
}

test "commandNameFromEntry strips the perf prefix and optional exe suffix" {
    try std.testing.expectEqualStrings("record", commandNameFromEntry("perf-record.exe", "perf-").?);
    try std.testing.expectEqualStrings("", commandNameFromEntry("perf-.exe", "perf-").?);
    try std.testing.expectEqual(@as(?[]const u8, null), commandNameFromEntry("record", "perf-"));
}

test "splitPathEntries preserves empty segments" {
    var entries = try splitPathEntries(std.testing.allocator, ":/opt/perf/bin::/usr/bin:");
    defer entries.deinit();

    try std.testing.expectEqual(@as(usize, 5), entries.count());
    try std.testing.expectEqualStrings("", entries.entries.items[0]);
    try std.testing.expectEqualStrings("/opt/perf/bin", entries.entries.items[1]);
    try std.testing.expectEqualStrings("", entries.entries.items[2]);
    try std.testing.expectEqualStrings("/usr/bin", entries.entries.items[3]);
    try std.testing.expectEqualStrings("", entries.entries.items[4]);
}

test "resolveTerminalDimensions requires a full non-zero pair before overriding fallback" {
    try std.testing.expectEqualDeep(
        TerminalDimensions{ .rows = 31, .cols = 37 },
        resolveTerminalDimensions(" +31rows", "+37cols", .{ .rows = 20, .cols = 60 }),
    );
    try std.testing.expectEqualDeep(
        TerminalDimensions{ .rows = 20, .cols = 60 },
        resolveTerminalDimensions("31", null, .{ .rows = 20, .cols = 60 }),
    );
    try std.testing.expectEqualDeep(
        TerminalDimensions{ .rows = 25, .cols = 80 },
        resolveTerminalDimensions(null, null, null),
    );
}

test "planPrettyPrint keeps one-column fallback when a second column would hit the edge" {
    const layout = planPrettyPrint(4, 8, 18);
    try std.testing.expectEqual(@as(usize, 1), layout.cols);
    try std.testing.expectEqual(@as(usize, 4), layout.rows);
    try std.testing.expectEqual(@as(usize, 9), layout.spacing);
}

test "writePrettyPrintStringListForTerminal renders column-major output" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();
    try cmds.addCmdName("annotate", 8);
    try cmds.addCmdName("bench", 5);
    try cmds.addCmdName("diff", 4);
    try cmds.addCmdName("report", 6);
    try cmds.addCmdName("stat", 4);
    cmds.sort();

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try writePrettyPrintStringListForTerminal(
        &rendered.writer,
        cmds,
        cmds.longestNameLen(),
        "31",
        "24",
        .{ .rows = 25, .cols = 80 },
    );

    try std.testing.expectEqualStrings(
        " annotate report\n" ++
            " bench    stat\n" ++
            " diff\n",
        rendered.writer.buffered(),
    );
}

test "loadCommandListsFromSource keeps exec-path priority and removes duplicates from PATH lists" {
    const FixtureDir = struct {
        path: []const u8,
        entries: []const DirectoryEntry,
    };

    const FixtureSource = struct {
        dirs: []const FixtureDir,

        fn populate(self: *@This(), cmds: *CmdNames, path: []const u8, prefix: []const u8) !void {
            for (self.dirs) |dir| {
                if (std.mem.eql(u8, dir.path, path)) {
                    try addExecutableEntries(cmds, dir.entries, prefix);
                    return;
                }
            }
        }
    };

    const exec_entries = [_]DirectoryEntry{
        .{ .name = "perf-stat", .is_executable = true },
        .{ .name = "perf-report.exe", .is_executable = true },
        .{ .name = "perf-stat", .is_executable = true },
    };
    const path_entries = [_]DirectoryEntry{
        .{ .name = "perf-report.exe", .is_executable = true },
        .{ .name = "perf-trace", .is_executable = true },
        .{ .name = "trace", .is_executable = true },
    };

    var source = FixtureSource{
        .dirs = &.{
            .{ .path = "/opt/perf/bin", .entries = &exec_entries },
            .{ .path = "/usr/bin", .entries = &path_entries },
        },
    };

    var main_cmds = CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    var other_cmds = CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    try loadCommandListsFromSource(
        null,
        "/opt/perf/bin",
        &.{ "/opt/perf/bin", "/usr/bin", "/usr/bin" },
        &main_cmds,
        &other_cmds,
        &source,
        FixtureSource.populate,
    );

    try std.testing.expectEqual(@as(usize, 2), main_cmds.count());
    try std.testing.expectEqualStrings("report", main_cmds.names.items[0].name);
    try std.testing.expectEqualStrings("stat", main_cmds.names.items[1].name);
    try std.testing.expectEqual(@as(usize, 1), other_cmds.count());
    try std.testing.expectEqualStrings("trace", other_cmds.names.items[0].name);
}

test "writeCommandSectionsForTerminal keeps main and PATH headings stable" {
    var main_cmds = CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.addCmdName("stat", 4);
    try main_cmds.addCmdName("top", 3);
    main_cmds.sort();

    var other_cmds = CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.addCmdName("annotate", 8);
    other_cmds.sort();

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try writeCommandSectionsForTerminal(
        &rendered.writer,
        "tools",
        "/opt/perf/bin",
        main_cmds,
        other_cmds,
        "25",
        "20",
        null,
    );

    try std.testing.expectEqualStrings(
        "available tools in '/opt/perf/bin'\n" ++
            "----------------------------------\n" ++
            " stat top\n" ++
            "\n" ++
            "tools available from elsewhere on your $PATH\n" ++
            "--------------------------------------------\n" ++
            " annotate\n" ++
            "\n",
        rendered.writer.buffered(),
    );
}
