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
    var index: usize = 0;
    while (index < value.len and std.ascii.isWhitespace(value[index])) : (index += 1) {}

    if (index == value.len) {
        return 0;
    }

    if (value[index] == '+') {
        index += 1;
    } else if (value[index] == '-') {
        return 0;
    }

    const digits_start = index;
    var result: usize = 0;

    while (index < value.len) : (index += 1) {
        const ch = value[index];
        if (ch < '0' or ch > '9') {
            break;
        }

        result = std.math.mul(usize, result, 10) catch return 0;
        result = std.math.add(usize, result, ch - '0') catch return 0;
    }

    if (index == digits_start) {
        return 0;
    }

    return result;
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

pub fn longestNameLenAcross(main_cmds: CmdNames, other_cmds: CmdNames) usize {
    return @max(main_cmds.longestNameLen(), other_cmds.longestNameLen());
}

fn writeRepeatedByte(writer: anytype, byte: u8, count: usize) !void {
    if (count == 0) {
        return;
    }
    try writer.splatByteAll(byte, count);
}

pub fn writeCommandSectionsForTerminal(
    writer: anytype,
    title: []const u8,
    exec_path: []const u8,
    main_cmds: CmdNames,
    other_cmds: CmdNames,
    env_lines: ?[]const u8,
    env_columns: ?[]const u8,
    fallback: ?TerminalDimensions,
) !void {
    const longest = longestNameLenAcross(main_cmds, other_cmds);

    if (main_cmds.count() != 0) {
        try writer.print("available {s} in '{s}'\n", .{ title, exec_path });
        try writer.writeAll("----------------");
        try writeRepeatedByte(writer, '-', title.len + exec_path.len);
        try writer.writeByte('\n');
        try writePrettyPrintStringListForTerminal(writer, main_cmds, longest, env_lines, env_columns, fallback);
        try writer.writeByte('\n');
    }

    if (other_cmds.count() != 0) {
        try writer.print("{s} available from elsewhere on your $PATH\n", .{title});
        try writer.writeAll("---------------------------------------");
        try writeRepeatedByte(writer, '-', title.len);
        try writer.writeByte('\n');
        try writePrettyPrintStringListForTerminal(writer, other_cmds, longest, env_lines, env_columns, fallback);
        try writer.writeByte('\n');
    }
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
    cmds.uniq();

    try std.testing.expectEqual(@as(usize, 3), cmds.count());
    try std.testing.expectEqualStrings("annotate", cmds.names.items[0].name);
    try std.testing.expectEqualStrings("bench", cmds.names.items[1].name);
    try std.testing.expectEqualStrings("test", cmds.names.items[2].name);
}

test "excludeCmds removes matches from a sorted command list" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();
    try cmds.addCmdName("annotate", 8);
    try cmds.addCmdName("bench", 5);
    try cmds.addCmdName("test", 4);
    cmds.sort();

    var excludes = CmdNames.init(std.testing.allocator);
    defer excludes.deinit();
    try excludes.addCmdName("bench", 5);
    try excludes.addCmdName("trace", 5);
    excludes.sort();

    cmds.excludeCmds(excludes);

    try std.testing.expectEqual(@as(usize, 2), cmds.count());
    try std.testing.expectEqualStrings("annotate", cmds.names.items[0].name);
    try std.testing.expectEqualStrings("test", cmds.names.items[1].name);
}

test "membership and longest-name helpers stay aligned with the stored list" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();
    try cmds.addCmdName("report", 6);
    try cmds.addCmdName("sched", 5);

    try std.testing.expect(cmds.isInCmdList("report"));
    try std.testing.expect(!cmds.isInCmdList("record"));
    try std.testing.expectEqual(@as(usize, 6), cmds.longestNameLen());
}

test "splitPathEntries preserves empty PATH segments and owns copied slices" {
    var backing = [_]u8{ ':', '/', 'u', 's', 'r', '/', 'b', 'i', 'n', ':', ':', '/', 'b', 'i', 'n', ':' };
    var entries = try splitPathEntries(std.testing.allocator, &backing);
    defer entries.deinit();
    backing[1] = 'x';

    try std.testing.expectEqual(@as(usize, 5), entries.count());
    try std.testing.expectEqualStrings("", entries.entries.items[0]);
    try std.testing.expectEqualStrings("/usr/bin", entries.entries.items[1]);
    try std.testing.expectEqualStrings("", entries.entries.items[2]);
    try std.testing.expectEqualStrings("/bin", entries.entries.items[3]);
    try std.testing.expectEqualStrings("", entries.entries.items[4]);
}

test "command entry helpers filter prefixes and strip windows executable suffixes" {
    try std.testing.expectEqualStrings("trace", commandNameFromEntry("perf-trace", "perf-").?);
    try std.testing.expectEqualStrings("report", commandNameFromEntry("perf-report.exe", "perf-").?);
    try std.testing.expectEqual(@as(?[]const u8, null), commandNameFromEntry("trace", "perf-"));
    try std.testing.expectEqual(@as(?[]const u8, null), commandNameFromEntry("perf-.exe", "perf-"));
    try std.testing.expect(hasExtension("perf-report.exe", ".exe"));
    try std.testing.expect(!hasExtension("perf-report", ".exe"));
}

test "addExecutableEntry models load_command_list filtering without directory I/O" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();

    try std.testing.expect(try addExecutableEntry(&cmds, "perf-report", "perf-", true));
    try std.testing.expect(try addExecutableEntry(&cmds, "perf-stat.exe", "perf-", true));
    try std.testing.expect(!(try addExecutableEntry(&cmds, "README.txt", "perf-", true)));
    try std.testing.expect(!(try addExecutableEntry(&cmds, "perf-script", "perf-", false)));

    cmds.sort();

    try std.testing.expectEqual(@as(usize, 2), cmds.count());
    try std.testing.expectEqualStrings("report", cmds.names.items[0].name);
    try std.testing.expectEqualStrings("stat", cmds.names.items[1].name);
}

test "loadCommandListsFromSource keeps exec-path priority and filters duplicates across PATH" {
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
        .{ .name = "README.md", .is_executable = true },
        .{ .name = "perf-stat", .is_executable = true },
    };
    const other_entries = [_]DirectoryEntry{
        .{ .name = "perf-report.exe", .is_executable = true },
        .{ .name = "perf-trace", .is_executable = true },
        .{ .name = "perf-diff", .is_executable = false },
        .{ .name = "trace", .is_executable = true },
        .{ .name = "perf-trace", .is_executable = true },
    };

    var source = FixtureSource{
        .dirs = &.{
            .{ .path = "/opt/perf/bin", .entries = &exec_entries },
            .{ .path = "/usr/bin", .entries = &other_entries },
        },
    };

    var main_cmds = CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    var other_cmds = CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    try loadCommandListsFromSource(
        null,
        "/opt/perf/bin",
        &.{ "/opt/perf/bin", "/usr/bin" },
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

test "loadCommandListsFromEnvPath preserves raw PATH splitting and exec-path filtering" {
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
    };
    const other_entries = [_]DirectoryEntry{
        .{ .name = "perf-trace", .is_executable = true },
        .{ .name = "perf-trace", .is_executable = true },
    };

    var source = FixtureSource{
        .dirs = &.{
            .{ .path = "", .entries = &.{} },
            .{ .path = "/opt/perf/bin", .entries = &exec_entries },
            .{ .path = "/usr/bin", .entries = &other_entries },
        },
    };

    var main_cmds = CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    var other_cmds = CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    try loadCommandListsFromEnvPath(
        std.testing.allocator,
        null,
        "/opt/perf/bin",
        ":/opt/perf/bin:/usr/bin:",
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

test "parseDimension accepts atoi-style prefixes and rejects invalid values" {
    try std.testing.expectEqual(@as(usize, 40), parseDimension("40"));
    try std.testing.expectEqual(@as(usize, 40), parseDimension(" \t+40lines"));
    try std.testing.expectEqual(@as(usize, 120), parseDimension("120 columns"));
    try std.testing.expectEqual(@as(usize, 0), parseDimension(""));
    try std.testing.expectEqual(@as(usize, 0), parseDimension("abc"));
    try std.testing.expectEqual(@as(usize, 0), parseDimension("-40"));
    try std.testing.expectEqual(@as(usize, 0), parseDimension("+"));
    try std.testing.expectEqual(@as(usize, 0), parseDimension("999999999999999999999999999999"));
}

test "resolveTerminalDimensions prefers explicit environment dimensions before fallback defaults" {
    const from_env = resolveTerminalDimensions("  +40lines", "120 columns", .{
        .rows = 30,
        .cols = 90,
    });
    try std.testing.expectEqual(@as(usize, 40), from_env.rows);
    try std.testing.expectEqual(@as(usize, 120), from_env.cols);

    const from_fallback = resolveTerminalDimensions("40", null, .{
        .rows = 33,
        .cols = 99,
    });
    try std.testing.expectEqual(@as(usize, 33), from_fallback.rows);
    try std.testing.expectEqual(@as(usize, 99), from_fallback.cols);

    const invalid_env = resolveTerminalDimensions("abc", "70", null);
    try std.testing.expectEqual(@as(usize, 25), invalid_env.rows);
    try std.testing.expectEqual(@as(usize, 80), invalid_env.cols);
}

test "pretty-print layout follows the same column math as help.c" {
    const layout = planPrettyPrint(5, 7, 33);
    try std.testing.expectEqual(@as(usize, 4), layout.cols);
    try std.testing.expectEqual(@as(usize, 2), layout.rows);
    try std.testing.expectEqual(@as(usize, 8), layout.spacing);

    const empty = planPrettyPrint(0, 5, 20);
    try std.testing.expectEqual(@as(usize, 1), empty.cols);
    try std.testing.expectEqual(@as(usize, 0), empty.rows);
    try std.testing.expectEqual(@as(usize, 6), empty.spacing);

    const env_layout = planPrettyPrintForTerminal(6, 7, "41", "33", .{
        .rows = 25,
        .cols = 80,
    });
    try std.testing.expectEqual(@as(usize, 4), env_layout.cols);
    try std.testing.expectEqual(@as(usize, 2), env_layout.rows);
    try std.testing.expectEqual(@as(usize, 8), env_layout.spacing);
}

test "writePrettyPrintWithLayout keeps sparse rows and the last printed column single-spaced" {
    var cmds = CmdNames.init(std.testing.allocator);
    defer cmds.deinit();
    try cmds.addCmdName("alpha", 5);
    try cmds.addCmdName("beta", 4);
    try cmds.addCmdName("gamma", 5);
    try cmds.addCmdName("delta", 5);
    try cmds.addCmdName("omega", 5);
    cmds.sort();

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try writePrettyPrintWithLayout(&rendered.writer, cmds, .{
        .cols = 3,
        .rows = 2,
        .spacing = 7,
    });

    try std.testing.expectEqualStrings(
        "  alpha  delta  omega\n" ++
            "  beta   gamma\n",
        rendered.writer.buffered(),
    );
}

test "writeCommandSectionsForTerminal renders main and PATH sections with shared longest-name padding" {
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
            "  stat     top\n" ++
            "\n" ++
            "tools available from elsewhere on your $PATH\n" ++
            "--------------------------------------------\n" ++
            "  annotate\n" ++
            "\n",
        rendered.writer.buffered(),
    );
}

test "writeCommandSectionsForTerminal skips the main section when it is empty" {
    var main_cmds = CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();

    var other_cmds = CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.addCmdName("trace", 5);
    other_cmds.sort();

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try writeCommandSectionsForTerminal(
        &rendered.writer,
        "tools",
        "",
        main_cmds,
        other_cmds,
        "25",
        "20",
        null,
    );

    try std.testing.expectEqualStrings(
        "tools available from elsewhere on your $PATH\n" ++
            "--------------------------------------------\n" ++
            "  trace\n" ++
            "\n",
        rendered.writer.buffered(),
    );
}
