const std = @import("std");

pub const CmdName = struct {
    name: []u8,

    pub fn len(self: CmdName) usize {
        return self.name.len;
    }

    pub fn deinit(self: *CmdName, allocator: std.mem.Allocator) void {
        allocator.free(self.name);
        self.* = undefined;
    }
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
        for (self.names.items) |*entry| {
            entry.deinit(self.allocator);
        }
        self.names.deinit(self.allocator);
        self.* = undefined;
    }

    pub fn count(self: CmdNames) usize {
        return self.names.items.len;
    }

    pub fn addCmdName(self: *CmdNames, name: []const u8, len: usize) !void {
        if (len > name.len) {
            return error.InvalidCommandLength;
        }

        try self.names.append(self.allocator, .{
            .name = try self.allocator.dupe(u8, name[0..len]),
        });
    }

    pub fn sort(self: *CmdNames) void {
        std.mem.sort(CmdName, self.names.items, {}, lessThan);
    }

    pub fn uniq(self: *CmdNames) void {
        if (self.names.items.len == 0) {
            return;
        }

        var write_index: usize = 1;
        var read_index: usize = 1;
        while (read_index < self.names.items.len) : (read_index += 1) {
            const previous = &self.names.items[write_index - 1];
            const current = &self.names.items[read_index];
            if (std.mem.eql(u8, previous.name, current.name)) {
                current.deinit(self.allocator);
                continue;
            }

            if (write_index != read_index) {
                self.names.items[write_index] = current.*;
            }
            write_index += 1;
        }

        self.names.shrinkRetainingCapacity(write_index);
    }

    pub fn excludeCmds(self: *CmdNames, excludes: CmdNames) void {
        if (self.names.items.len == 0 or excludes.names.items.len == 0) {
            return;
        }

        var write_index: usize = 0;
        var read_index: usize = 0;
        var exclude_index: usize = 0;

        while (read_index < self.names.items.len and exclude_index < excludes.names.items.len) {
            const ordering = std.mem.order(u8, self.names.items[read_index].name, excludes.names.items[exclude_index].name);
            switch (ordering) {
                .lt => {
                    if (write_index != read_index) {
                        self.names.items[write_index] = self.names.items[read_index];
                    }
                    write_index += 1;
                    read_index += 1;
                },
                .eq => {
                    self.names.items[read_index].deinit(self.allocator);
                    read_index += 1;
                    exclude_index += 1;
                },
                .gt => exclude_index += 1,
            }
        }

        while (read_index < self.names.items.len) : (read_index += 1) {
            if (write_index != read_index) {
                self.names.items[write_index] = self.names.items[read_index];
            }
            write_index += 1;
        }

        self.names.shrinkRetainingCapacity(write_index);
    }

    pub fn isInCmdList(self: CmdNames, name: []const u8) bool {
        for (self.names.items) |entry| {
            if (std.mem.eql(u8, entry.name, name)) {
                return true;
            }
        }
        return false;
    }

    pub fn longestNameLen(self: CmdNames) usize {
        var longest: usize = 0;
        for (self.names.items) |entry| {
            longest = @max(longest, entry.len());
        }
        return longest;
    }
};

fn lessThan(_: void, lhs: CmdName, rhs: CmdName) bool {
    return std.mem.order(u8, lhs.name, rhs.name) == .lt;
}

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

pub const PrettyPrintLayout = struct {
    cols: usize,
    rows: usize,
    spacing: usize,
};

pub const TerminalDimensions = struct {
    rows: usize,
    cols: usize,
};

pub fn hasExtension(filename: []const u8, ext: []const u8) bool {
    return filename.len > ext.len and std.mem.eql(u8, filename[filename.len - ext.len ..], ext);
}

fn parseDimension(value: []const u8) usize {
    return std.fmt.parseInt(usize, value, 10) catch 0;
}

pub fn splitPathEntries(allocator: std.mem.Allocator, raw_path: []const u8) !PathEntries {
    var entries = PathEntries.init(allocator);
    errdefer entries.deinit();

    var start: usize = 0;
    while (true) {
        const maybe_colon = std.mem.indexOfScalarPos(u8, raw_path, start, ':');
        const end = maybe_colon orelse raw_path.len;
        try entries.entries.append(allocator, try allocator.dupe(u8, raw_path[start..end]));
        if (maybe_colon == null) {
            break;
        }
        start = end + 1;
    }

    return entries;
}

pub fn commandNameFromEntry(filename: []const u8, prefix: []const u8) ?[]const u8 {
    if (!std.mem.startsWith(u8, filename, prefix)) {
        return null;
    }

    var end = filename.len;
    if (hasExtension(filename, ".exe")) {
        end -= 4;
    }
    if (end <= prefix.len) {
        return null;
    }

    return filename[prefix.len..end];
}

pub fn addExecutableEntry(
    cmds: *CmdNames,
    filename: []const u8,
    prefix: []const u8,
    is_executable: bool,
) !bool {
    if (!is_executable) {
        return false;
    }

    const command_name = commandNameFromEntry(filename, prefix) orelse return false;
    try cmds.addCmdName(command_name, command_name.len);
    return true;
}

pub const DirectoryEntry = struct {
    name: []const u8,
    is_executable: bool,
};

pub fn addExecutableEntries(
    cmds: *CmdNames,
    entries: []const DirectoryEntry,
    prefix: ?[]const u8,
) !void {
    const actual_prefix = prefix orelse "perf-";
    for (entries) |entry| {
        _ = try addExecutableEntry(cmds, entry.name, actual_prefix, entry.is_executable);
    }
}

pub fn loadCommandListsFromSource(
    prefix: ?[]const u8,
    exec_path: ?[]const u8,
    path_entries: []const []const u8,
    main_cmds: *CmdNames,
    other_cmds: *CmdNames,
    source_context: anytype,
    comptime populate_dir: fn (@TypeOf(source_context), *CmdNames, []const u8, []const u8) anyerror!void,
) !void {
    const actual_prefix = prefix orelse "perf-";

    if (exec_path) |path| {
        try populate_dir(source_context, main_cmds, path, actual_prefix);
        main_cmds.sort();
        main_cmds.uniq();
    }

    for (path_entries) |path| {
        if (exec_path) |main_path| {
            if (std.mem.eql(u8, path, main_path)) {
                continue;
            }
        }

        try populate_dir(source_context, other_cmds, path, actual_prefix);
    }

    other_cmds.sort();
    other_cmds.uniq();
    other_cmds.excludeCmds(main_cmds.*);
}

pub fn loadCommandListsFromEnvPath(
    allocator: std.mem.Allocator,
    prefix: ?[]const u8,
    exec_path: ?[]const u8,
    env_path: ?[]const u8,
    main_cmds: *CmdNames,
    other_cmds: *CmdNames,
    source_context: anytype,
    comptime populate_dir: fn (@TypeOf(source_context), *CmdNames, []const u8, []const u8) anyerror!void,
) !void {
    var split_entries = PathEntries.init(allocator);
    defer split_entries.deinit();

    if (env_path) |raw_path| {
        split_entries = try splitPathEntries(allocator, raw_path);
    }

    const actual_prefix = prefix orelse "perf-";

    if (exec_path) |path| {
        try populate_dir(source_context, main_cmds, path, actual_prefix);
        main_cmds.sort();
        main_cmds.uniq();
    }

    for (split_entries.entries.items) |path| {
        if (exec_path) |main_path| {
            if (std.mem.eql(u8, path, main_path)) {
                continue;
            }
        }

        try populate_dir(source_context, other_cmds, path, actual_prefix);
    }

    other_cmds.sort();
    other_cmds.uniq();
    other_cmds.excludeCmds(main_cmds.*);
}

pub fn resolveTerminalDimensions(
    env_lines: ?[]const u8,
    env_columns: ?[]const u8,
    fallback: ?TerminalDimensions,
) TerminalDimensions {
    if (env_lines) |lines| {
        const rows = parseDimension(lines);
        if (env_columns) |columns| {
            const cols = parseDimension(columns);
            if (rows != 0 and cols != 0) {
                return .{
                    .rows = rows,
                    .cols = cols,
                };
            }
        }
    }

    if (fallback) |terminal| {
        if (terminal.rows != 0 and terminal.cols != 0) {
            return terminal;
        }
    }

    return .{
        .rows = 25,
        .cols = 80,
    };
}

pub fn planPrettyPrintForTerminal(
    count: usize,
    longest: usize,
    env_lines: ?[]const u8,
    env_columns: ?[]const u8,
    fallback: ?TerminalDimensions,
) PrettyPrintLayout {
    const terminal = resolveTerminalDimensions(env_lines, env_columns, fallback);
    return planPrettyPrint(count, longest, terminal.cols);
}

pub fn planPrettyPrint(count: usize, longest: usize, terminal_cols: usize) PrettyPrintLayout {
    const spacing = longest + 1;
    if (count == 0) {
        return .{
            .cols = 1,
            .rows = 0,
            .spacing = spacing,
        };
    }

    var cols: usize = 1;
    const max_cols = if (terminal_cols > 0) terminal_cols - 1 else 0;
    if (spacing < max_cols and spacing != 0) {
        cols = max_cols / spacing;
        if (cols == 0) {
            cols = 1;
        }
    }

    return .{
        .cols = cols,
        .rows = std.math.divCeil(usize, count, cols) catch unreachable,
        .spacing = spacing,
    };
}

pub fn writePrettyPrintWithLayout(
    writer: anytype,
    cmds: CmdNames,
    layout: PrettyPrintLayout,
) !void {
    var row: usize = 0;
    while (row < layout.rows) : (row += 1) {
        try writer.writeAll("  ");

        var col: usize = 0;
        while (col < layout.cols) : (col += 1) {
            const index = col * layout.rows + row;
            if (index >= cmds.count()) {
                break;
            }

            const entry = cmds.names.items[index].name;
            const is_last_column = col + 1 == layout.cols;
            const is_last_entry_in_row = index + layout.rows >= cmds.count();
            const padding = if (is_last_column or is_last_entry_in_row) 1 else layout.spacing;

            try writer.writeAll(entry);
            if (padding > entry.len) {
                try writer.splatByteAll(' ', padding - entry.len);
            }
        }

        try writer.writeByte('\n');
    }
}

pub fn writePrettyPrintStringList(
    writer: anytype,
    cmds: CmdNames,
    longest: usize,
    terminal_cols: usize,
) !void {
    const layout = planPrettyPrint(cmds.count(), longest, terminal_cols);
    try writePrettyPrintWithLayout(writer, cmds, layout);
}

pub fn writePrettyPrintStringListForTerminal(
    writer: anytype,
    cmds: CmdNames,
    longest: usize,
    env_lines: ?[]const u8,
    env_columns: ?[]const u8,
    fallback: ?TerminalDimensions,
) !void {
    const layout = planPrettyPrintForTerminal(cmds.count(), longest, env_lines, env_columns, fallback);
    try writePrettyPrintWithLayout(writer, cmds, layout);
}

test "addCmdName owns a copied slice and preserves the requested length" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();

    var backing = [_]u8{ 's', 't', 'a', 't', 'u', 's' };
    try cmds.addCmdName(&backing, 4);
    backing[0] = 'x';

    try std.testing.expectEqual(@as(usize, 1), cmds.count());
    try std.testing.expectEqualStrings("stat", cmds.names.items[0].name);
    try std.testing.expectEqual(@as(usize, 4), cmds.names.items[0].len());
}

test "uniq removes adjacent duplicates after sorting" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();

    try cmds.addCmdName("test", 4);
    try cmds.addCmdName("annotate", 8);
    try cmds.addCmdName("test", 4);
    try cmds.addCmdName("bench", 5);

    cmds.sort();
    cmds.