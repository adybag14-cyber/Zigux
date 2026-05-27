const std = @import("std");

pub const default_command_prefix = "perf-";
pub const default_terminal_columns: usize = 80;

pub const CommandRecord = struct {
    name: []u8,
    len: usize,

    pub fn deinit(self: *CommandRecord, allocator: std.mem.Allocator) void {
        allocator.free(self.name);
        self.* = undefined;
    }
};

pub const CommandNames = struct {
    allocator: std.mem.Allocator,
    names: std.ArrayList(CommandRecord),

    pub fn init(allocator: std.mem.Allocator) CommandNames {
        return .{
            .allocator = allocator,
            .names = std.ArrayList(CommandRecord).empty,
        };
    }

    pub fn deinit(self: *CommandNames) void {
        for (self.names.items) |*entry| {
            entry.deinit(self.allocator);
        }
        self.names.deinit(self.allocator);
        self.* = undefined;
    }

    pub fn count(self: *const CommandNames) usize {
        return self.names.items.len;
    }

    pub fn add(self: *CommandNames, name: []const u8) !void {
        const owned = try self.allocator.dupe(u8, name);
        errdefer self.allocator.free(owned);

        try self.names.append(self.allocator, .{
            .name = owned,
            .len = owned.len,
        });
    }

    pub fn sort(self: *CommandNames) void {
        var i: usize = 1;
        while (i < self.names.items.len) : (i += 1) {
            var j = i;
            while (j > 0 and lessThan(self.names.items[j], self.names.items[j - 1])) : (j -= 1) {
                std.mem.swap(CommandRecord, &self.names.items[j], &self.names.items[j - 1]);
            }
        }
    }

    pub fn uniqSorted(self: *CommandNames) void {
        if (self.names.items.len == 0) {
            return;
        }

        var write_index: usize = 1;
        var read_index: usize = 1;
        while (read_index < self.names.items.len) : (read_index += 1) {
            const current = self.names.items[read_index];
            const previous = self.names.items[write_index - 1];
            if (std.mem.eql(u8, current.name, previous.name)) {
                self.names.items[read_index].deinit(self.allocator);
                continue;
            }

            if (write_index != read_index) {
                self.names.items[write_index] = self.names.items[read_index];
            }
            write_index += 1;
        }

        self.names.items.len = write_index;
    }

    pub fn excludeSorted(self: *CommandNames, excludes: *const CommandNames) void {
        if (self.names.items.len == 0 or excludes.names.items.len == 0) {
            return;
        }

        var read_index: usize = 0;
        var write_index: usize = 0;
        var exclude_index: usize = 0;

        while (read_index < self.names.items.len and exclude_index < excludes.names.items.len) {
            const current_name = self.names.items[read_index].name;
            const exclude_name = excludes.names.items[exclude_index].name;
            switch (std.mem.order(u8, current_name, exclude_name)) {
                .lt => {
                    if (write_index != read_index) {
                        self.names.items[write_index] = self.names.items[read_index];
                    }
                    read_index += 1;
                    write_index += 1;
                },
                .eq => {
                    self.names.items[read_index].deinit(self.allocator);
                    read_index += 1;
                    exclude_index += 1;
                },
                .gt => {
                    exclude_index += 1;
                },
            }
        }

        while (read_index < self.names.items.len) : (read_index += 1) {
            if (write_index != read_index) {
                self.names.items[write_index] = self.names.items[read_index];
            }
            write_index += 1;
        }

        self.names.items.len = write_index;
    }

    pub fn longest(self: *const CommandNames) usize {
        var longest_name: usize = 0;
        for (self.names.items) |entry| {
            longest_name = @max(longest_name, entry.len);
        }
        return longest_name;
    }

    pub fn contains(self: *const CommandNames, needle: []const u8) bool {
        for (self.names.items) |entry| {
            if (std.mem.eql(u8, entry.name, needle)) {
                return true;
            }
        }
        return false;
    }

    fn lessThan(left: CommandRecord, right: CommandRecord) bool {
        return std.mem.order(u8, left.name, right.name) == .lt;
    }
};

pub const PrettyLayout = struct {
    cols: usize,
    rows: usize,
    space: usize,
};

pub const SearchPathEntryDisposition = enum {
    scan,
    skip_exec_path,
    skip_empty,
};

pub const SearchPathEntry = struct {
    path: []u8,
    disposition: SearchPathEntryDisposition,

    pub fn deinit(self: *SearchPathEntry, allocator: std.mem.Allocator) void {
        allocator.free(self.path);
        self.* = undefined;
    }
};

pub fn hasExtension(filename: []const u8, ext: []const u8) bool {
    return filename.len > ext.len and std.mem.eql(u8, filename[filename.len - ext.len ..], ext);
}

pub fn trimCommandPrefix(entry_name: []const u8, prefix: []const u8) ?[]const u8 {
    if (!std.mem.startsWith(u8, entry_name, prefix)) {
        return null;
    }

    var trimmed = entry_name[prefix.len..];
    if (std.mem.endsWith(u8, trimmed, ".exe")) {
        trimmed = trimmed[0 .. trimmed.len - 4];
    }
    if (trimmed.len == 0) {
        return null;
    }

    return trimmed;
}

pub fn buildOtherCommandSearchPlan(
    allocator: std.mem.Allocator,
    env_path: ?[]const u8,
    exec_path: ?[]const u8,
) ![]SearchPathEntry {
    const path_value = env_path orelse return allocator.alloc(SearchPathEntry, 0);

    var entries = std.ArrayList(SearchPathEntry).empty;
    errdefer {
        for (entries.items) |*entry| {
            entry.deinit(allocator);
        }
        entries.deinit(allocator);
    }

    var iter = std.mem.splitScalar(u8, path_value, ':');
    while (iter.next()) |entry| {
        const owned_path = try allocator.dupe(u8, entry);
        errdefer allocator.free(owned_path);

        const disposition: SearchPathEntryDisposition = if (entry.len == 0)
            .skip_empty
        else if (exec_path != null and std.mem.eql(u8, entry, exec_path.?))
            .skip_exec_path
        else
            .scan;

        try entries.append(allocator, .{
            .path = owned_path,
            .disposition = disposition,
        });
    }

    return entries.toOwnedSlice(allocator);
}

pub fn freeOtherCommandSearchPlan(
    allocator: std.mem.Allocator,
    entries: []SearchPathEntry,
) void {
    for (entries) |*entry| {
        entry.deinit(allocator);
    }
    allocator.free(entries);
}

pub fn countScannableSearchPathEntries(entries: []const SearchPathEntry) usize {
    var count: usize = 0;
    for (entries) |entry| {
        if (entry.disposition == .scan) {
            count += 1;
        }
    }
    return count;
}

pub fn computePrettyLayout(command_count: usize, longest: usize, terminal_columns: usize) PrettyLayout {
    const safe_columns = if (terminal_columns == 0) default_terminal_columns else terminal_columns;
    const max_cols = safe_columns -| 1;
    const space = longest + 1;

    var cols: usize = 1;
    if (space != 0 and space < max_cols) {
        cols = max_cols / space;
        if (cols == 0) {
            cols = 1;
        }
    }

    const rows = if (command_count == 0) 0 else std.math.divCeil(usize, command_count, cols) catch 0;
    return .{
        .cols = cols,
        .rows = rows,
        .space = space,
    };
}

fn renderPrettyStringListWithLongest(
    allocator: std.mem.Allocator,
    cmds: *const CommandNames,
    longest: usize,
    terminal_columns: usize,
) ![]u8 {
    const layout = computePrettyLayout(cmds.count(), longest, terminal_columns);

    var output = std.ArrayList(u8).empty;
    errdefer output.deinit(allocator);

    var row: usize = 0;
    while (row < layout.rows) : (row += 1) {
        try output.append(allocator, ' ');

        var col: usize = 0;
        while (col < layout.cols) : (col += 1) {
            const index = col * layout.rows + row;
            if (index >= cmds.count()) {
                break;
            }

            const entry = cmds.names.items[index];
            const width = if (col == layout.cols - 1 or index + layout.rows >= cmds.count()) 1 else layout.space;
            try output.appendSlice(allocator, entry.name);
            if (width > entry.len) {
                try output.appendNTimes(allocator, ' ', width - entry.len);
            }
        }

        try output.append(allocator, '\n');
    }

    return output.toOwnedSlice(allocator);
}

pub fn renderPrettyStringList(
    allocator: std.mem.Allocator,
    cmds: *const CommandNames,
    terminal_columns: usize,
) ![]u8 {
    return renderPrettyStringListWithLongest(allocator, cmds, cmds.longest(), terminal_columns);
}

pub fn renderCommandSections(
    allocator: std.mem.Allocator,
    title: []const u8,
    exec_path: ?[]const u8,
    main_cmds: *const CommandNames,
    other_cmds: *const CommandNames,
    terminal_columns: usize,
) ![]u8 {
    var output = std.ArrayList(u8).empty;
    errdefer output.deinit(allocator);

    const longest = @max(main_cmds.longest(), other_cmds.longest());

    if (main_cmds.count() != 0) {
        const main_header = if (exec_path) |main_exec_path|
            if (main_exec_path.len != 0)
                try std.fmt.allocPrint(
                    allocator,
                    "available {s} in '{s}'\n",
                    .{ title, main_exec_path },
                )
            else
                try std.fmt.allocPrint(allocator, "available {s}\n", .{title})
        else
            try std.fmt.allocPrint(allocator, "available {s}\n", .{title});
        defer allocator.free(main_header);
        try output.appendSlice(allocator, main_header);
        try output.appendNTimes(allocator, '-', main_header.len - 1);
        try output.append(allocator, '\n');

        const rendered = try renderPrettyStringListWithLongest(allocator, main_cmds, longest, terminal_columns);
        defer allocator.free(rendered);
        try output.appendSlice(allocator, rendered);
        try output.append(allocator, '\n');
    }

    if (other_cmds.count() != 0) {
        const other_header = try std.fmt.allocPrint(
            allocator,
            "{s} available from elsewhere on your $PATH\n",
            .{title},
        );
        defer allocator.free(other_header);
        try output.appendSlice(allocator, other_header);
        try output.appendNTimes(allocator, '-', 39 + title.len);
        try output.append(allocator, '\n');

        const rendered = try renderPrettyStringListWithLongest(allocator, other_cmds, longest, terminal_columns);
        defer allocator.free(rendered);
        try output.appendSlice(allocator, rendered);
        try output.append(allocator, '\n');
    }

    return output.toOwnedSlice(allocator);
}

test "computePrettyLayout falls back to the default width and one-column floor" {
    const fallback = computePrettyLayout(5, "buildid-cache".len, 0);
    try std.testing.expectEqual(@as(usize, 5), fallback.cols);
    try std.testing.expectEqual(@as(usize, 1), fallback.rows);
    try std.testing.expectEqual(@as(usize, 14), fallback.space);

    const narrow = computePrettyLayout(3, "buildid-cache".len, 4);
    try std.testing.expectEqual(@as(usize, 1), narrow.cols);
    try std.testing.expectEqual(@as(usize, 3), narrow.rows);
    try std.testing.expectEqual(@as(usize, 14), narrow.space);
}

test "trimCommandPrefix strips the prefix, optional exe suffix, and rejects empty command names" {
    try std.testing.expectEqualStrings("annotate", trimCommandPrefix("perf-annotate", default_command_prefix).?);
    try std.testing.expectEqualStrings("script", trimCommandPrefix("perf-script.exe", default_command_prefix).?);
    try std.testing.expectEqual(@as(?[]const u8, null), trimCommandPrefix("perf-", default_command_prefix));
    try std.testing.expectEqual(@as(?[]const u8, null), trimCommandPrefix("perf-.exe", default_command_prefix));
    try std.testing.expectEqual(@as(?[]const u8, null), trimCommandPrefix("trace2html", default_command_prefix));
}

test "buildOtherCommandSearchPlan keeps PATH ordering while marking empty and exec-path entries" {
    const plan = try buildOtherCommandSearchPlan(
        std.testing.allocator,
        ":/usr/libexec/perf-core:/bin::/usr/bin:",
        "/usr/libexec/perf-core",
    );
    defer freeOtherCommandSearchPlan(std.testing.allocator, plan);

    try std.testing.expectEqual(@as(usize, 6), plan.len);
    try std.testing.expectEqualStrings("", plan[0].path);
    try std.testing.expectEqual(SearchPathEntryDisposition.skip_empty, plan[0].disposition);
    try std.testing.expectEqualStrings("/usr/libexec/perf-core", plan[1].path);
    try std.testing.expectEqual(SearchPathEntryDisposition.skip_exec_path, plan[1].disposition);
    try std.testing.expectEqualStrings("/bin", plan[2].path);
    try std.testing.expectEqual(SearchPathEntryDisposition.scan, plan[2].disposition);
    try std.testing.expectEqualStrings("", plan[3].path);
    try std.testing.expectEqual(SearchPathEntryDisposition.skip_empty, plan[3].disposition);
    try std.testing.expectEqualStrings("/usr/bin", plan[4].path);
    try std.testing.expectEqual(SearchPathEntryDisposition.scan, plan[4].disposition);
    try std.testing.expectEqualStrings("", plan[5].path);
    try std.testing.expectEqual(SearchPathEntryDisposition.skip_empty, plan[5].disposition);
    try std.testing.expectEqual(@as(usize, 2), countScannableSearchPathEntries(plan));
}

test "buildOtherCommandSearchPlan preserves duplicate and relative scan targets when they are not the exec path" {
    const plan = try buildOtherCommandSearchPlan(
        std.testing.allocator,
        "tools/bin:/usr/bin:tools/bin",
        "/usr/libexec/perf-core",
    );
    defer freeOtherCommandSearchPlan(std.testing.allocator, plan);

    try std.testing.expectEqual(@as(usize, 3), plan.len);
    for (plan) |entry| {
        try std.testing.expectEqual(SearchPathEntryDisposition.scan, entry.disposition);
    }
    try std.testing.expectEqualStrings("tools/bin", plan[0].path);
    try std.testing.expectEqualStrings("/usr/bin", plan[1].path);
    try std.testing.expectEqualStrings("tools/bin", plan[2].path);
    try std.testing.expectEqual(@as(usize, 3), countScannableSearchPathEntries(plan));
}

test "buildOtherCommandSearchPlan returns an empty plan when PATH is unavailable" {
    const plan = try buildOtherCommandSearchPlan(std.testing.allocator, null, "/usr/libexec/perf-core");
    defer freeOtherCommandSearchPlan(std.testing.allocator, plan);

    try std.testing.expectEqual(@as(usize, 0), plan.len);
    try std.testing.expectEqual(@as(usize, 0), countScannableSearchPathEntries(plan));
}

test "CommandNames sort and uniq keep the stable command set" {
    var cmds = CommandNames.init(std.testing.allocator);
    defer cmds.deinit();

    try cmds.add("report");
    try cmds.add("annotate");
    try cmds.add("report");
    try cmds.add("bench");

    cmds.sort();
    cmds.uniqSorted();

    try std.testing.expectEqual(@as(usize, 3), cmds.count());
    try std.testing.expectEqualStrings("annotate", cmds.names.items[0].name);
    try std.testing.expectEqualStrings("bench", cmds.names.items[1].name);
    try std.testing.expectEqualStrings("report", cmds.names.items[2].name);
}

test "excludeSorted removes commands already present in the primary list" {
    var main_cmds = CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("annotate");
    try main_cmds.add("report");
    main_cmds.sort();

    var other_cmds = CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.add("bench");
    try other_cmds.add("report");
    try other_cmds.add("script");
    other_cmds.sort();

    other_cmds.excludeSorted(&main_cmds);

    try std.testing.expectEqual(@as(usize, 2), other_cmds.count());
    try std.testing.expectEqualStrings("bench", other_cmds.names.items[0].name);
    try std.testing.expectEqualStrings("script", other_cmds.names.items[1].name);
}

test "renderPrettyStringList keeps the same row-major pretty layout as help.c" {
    var cmds = CommandNames.init(std.testing.allocator);
    defer cmds.deinit();

    for (&[_][]const u8{ "annotate", "bench", "buildid-cache", "diff", "evlist" }) |name| {
        try cmds.add(name);
    }

    const rendered = try renderPrettyStringList(std.testing.allocator, &cmds, 32);
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        " annotate      diff\n" ++
            " bench         evlist\n" ++
            " buildid-cache\n",
        rendered,
    );
}

test "renderPrettyStringList returns an empty packet for no commands" {
    var cmds = CommandNames.init(std.testing.allocator);
    defer cmds.deinit();

    const rendered = try renderPrettyStringList(std.testing.allocator, &cmds, 80);
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings("", rendered);
}

test "renderCommandSections keeps stable headers for main and fallback command groups" {
    var main_cmds = CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("annotate");
    try main_cmds.add("bench");

    var other_cmds = CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.add("report");

    const rendered = try renderCommandSections(
        std.testing.allocator,
        "subcommands",
        "/usr/libexec/perf-core",
        &main_cmds,
        &other_cmds,
        80,
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "available subcommands in '/usr/libexec/perf-core'\n" ++
            "-------------------------------------------------\n" ++
            " annotate bench\n" ++
            "\n" ++
            "subcommands available from elsewhere on your $PATH\n" ++
            "--------------------------------------------------\n" ++
            " report\n" ++
            "\n",
        rendered,
    );
}

test "renderCommandSections shares longest width across main and fallback groups" {
    var main_cmds = CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("annotate");
    try main_cmds.add("bench");
    try main_cmds.add("diff");

    var other_cmds = CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.add("buildid-cache");

    const rendered = try renderCommandSections(
        std.testing.allocator,
        "subcommands",
        "/usr/libexec/perf-core",
        &main_cmds,
        &other_cmds,
        20,
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "available subcommands in '/usr/libexec/perf-core'\n" ++
            "-------------------------------------------------\n" ++
            " annotate\n" ++
            " bench\n" ++
            " diff\n" ++
            "\n" ++
            "subcommands available from elsewhere on your $PATH\n" ++
            "--------------------------------------------------\n" ++
            " buildid-cache\n" ++
            "\n",
        rendered,
    );
}

test "renderCommandSections emits the fallback-only packet without a blank main header" {
    var main_cmds = CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();

    var other_cmds = CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.add("report");
    try other_cmds.add("script");

    const rendered = try renderCommandSections(
        std.testing.allocator,
        "subcommands",
        "/usr/libexec/perf-core",
        &main_cmds,
        &other_cmds,
        80,
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "subcommands available from elsewhere on your $PATH\n" ++
            "--------------------------------------------------\n" ++
            " report script\n" ++
            "\n",
        rendered,
    );
}

test "renderCommandSections omits an empty quoted exec path when none is available" {
    var main_cmds = CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("annotate");

    var other_cmds = CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    const rendered = try renderCommandSections(
        std.testing.allocator,
        "subcommands",
        null,
        &main_cmds,
        &other_cmds,
        80,
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "available subcommands\n" ++
            "---------------------\n" ++
            " annotate\n" ++
            "\n",
        rendered,
    );
}

test "renderCommandSections treats an empty exec path like a missing one" {
    var main_cmds = CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("annotate");

    var other_cmds = CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    const rendered = try renderCommandSections(
        std.testing.allocator,
        "subcommands",
        "",
        &main_cmds,
        &other_cmds,
        80,
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "available subcommands\n" ++
            "---------------------\n" ++
            " annotate\n" ++
            "\n",
        rendered,
    );
}

test "renderCommandSections keeps an empty exec path unquoted while sharing longest width with fallback commands" {
    var main_cmds = CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("annotate");
    try main_cmds.add("bench");

    var other_cmds = CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.add("buildid-cache");

    const rendered = try renderCommandSections(
        std.testing.allocator,
        "subcommands",
        "",
        &main_cmds,
        &other_cmds,
        20,
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "available subcommands\n" ++
            "---------------------\n" ++
            " annotate\n" ++
            " bench\n" ++
            "\n" ++
            "subcommands available from elsewhere on your $PATH\n" ++
            "--------------------------------------------------\n" ++
            " buildid-cache\n" ++
            "\n",
        rendered,
    );
}

test "renderCommandSections returns an empty packet when both command groups are empty" {
    var main_cmds = CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();

    var other_cmds = CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    const rendered = try renderCommandSections(
        std.testing.allocator,
        "subcommands",
        null,
        &main_cmds,
        &other_cmds,
        80,
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings("", rendered);
}

test "renderPrettyStringList falls back to the default width when terminal columns are unavailable" {
    var cmds = CommandNames.init(std.testing.allocator);
    defer cmds.deinit();
    try cmds.add("annotate");
    try cmds.add("bench");

    const rendered = try renderPrettyStringList(std.testing.allocator, &cmds, 0);
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        " annotate bench\n",
        rendered,
    );
}
