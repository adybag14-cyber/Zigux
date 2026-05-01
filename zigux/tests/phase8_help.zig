const std = @import("std");
const help = @import("help");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

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

const FixtureDir = struct {
    path: []const u8,
    entries: []const help.DirectoryEntry,
};

const FixtureSource = struct {
    dirs: []const FixtureDir,

    fn populate(self: *@This(), cmds: *help.CmdNames, path: []const u8, prefix: []const u8) !void {
        for (self.dirs) |dir| {
            if (std.mem.eql(u8, dir.path, path)) {
                try help.addExecutableEntries(cmds, dir.entries, prefix);
                return;
            }
        }
    }
};

fn runAddCmdNameWithFailingAllocator(allocator: std.mem.Allocator) !void {
    var cmds = help.CmdNames.init(allocator);
    defer cmds.deinit();

    try cmds.addCmdName("trace", 5);
}

fn runSplitPathEntriesWithFailingAllocator(allocator: std.mem.Allocator, raw_path: []const u8) !void {
    var entries = try help.splitPathEntries(allocator, raw_path);
    defer entries.deinit();
}

test "phase 8 help module imports cleanly" {
    _ = help;
}

test "phase 8 help phase-level coverage stays focused on integrated command-list behavior" {
    var main_cmds = help.CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try std.testing.expect(try help.addExecutableEntry(&main_cmds, "perf-trace", "perf-", true));
    try std.testing.expect(try help.addExecutableEntry(&main_cmds, "perf-record.exe", "perf-", true));
    try std.testing.expect(!(try help.addExecutableEntry(&main_cmds, "README.md", "perf-", true)));
    try std.testing.expect(!(try help.addExecutableEntry(&main_cmds, "perf-.exe", "perf-", true)));
    try std.testing.expect(try help.addExecutableEntry(&main_cmds, "perf-trace", "perf-", true));
    main_cmds.sort();
    main_cmds.uniq();

    var excludes = help.CmdNames.init(std.testing.allocator);
    defer excludes.deinit();
    try excludes.addCmdName("record", 6);
    excludes.sort();

    main_cmds.excludeCmds(excludes);

    try std.testing.expectEqual(@as(usize, 1), main_cmds.count());
    try std.testing.expect(main_cmds.isInCmdList("trace"));
    try std.testing.expectEqual(@as(usize, 5), main_cmds.longestNameLen());
}

test "phase 8 help owned-copy helpers stay leak-free when allocation fails mid-append" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runAddCmdNameWithFailingAllocator,
        .{},
    );
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runSplitPathEntriesWithFailingAllocator,
        .{":/opt/perf/bin::/usr/bin:"},
    );
}

test "phase 8 help command-source and terminal layers stay aligned with the current help.c slice" {
    const exec_entries = [_]help.DirectoryEntry{
        .{ .name = "perf-stat", .is_executable = true },
        .{ .name = "perf-report.exe", .is_executable = true },
        .{ .name = "perf-stat", .is_executable = true },
    };
    const path_entries = [_]help.DirectoryEntry{
        .{ .name = "perf-report.exe", .is_executable = true },
        .{ .name = "perf-trace", .is_executable = true },
        .{ .name = "perf-diff", .is_executable = false },
        .{ .name = "trace", .is_executable = true },
    };

    var source = FixtureSource{
        .dirs = &.{
            .{ .path = "/opt/perf/bin", .entries = &exec_entries },
            .{ .path = "/usr/bin", .entries = &path_entries },
        },
    };

    var main_cmds = help.CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    var other_cmds = help.CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    try help.loadCommandListsFromSource(
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

    const fallback_terminal = help.resolveTerminalDimensions("0", "120", .{
        .rows = 22,
        .cols = 66,
    });
    try std.testing.expectEqual(@as(usize, 22), fallback_terminal.rows);
    try std.testing.expectEqual(@as(usize, 66), fallback_terminal.cols);
}

test "phase 8 help raw PATH splitting keeps empty segments, custom prefixes, and exec-path exclusion aligned with help.c" {
    var split_entries = try help.splitPathEntries(std.testing.allocator, ":/opt/perf/bin::/usr/bin:");
    defer split_entries.deinit();
    try std.testing.expectEqual(@as(usize, 5), split_entries.count());
    try std.testing.expectEqualStrings("", split_entries.entries.items[0]);
    try std.testing.expectEqualStrings("/opt/perf/bin", split_entries.entries.items[1]);
    try std.testing.expectEqualStrings("", split_entries.entries.items[2]);
    try std.testing.expectEqualStrings("/usr/bin", split_entries.entries.items[3]);
    try std.testing.expectEqualStrings("", split_entries.entries.items[4]);

    var empty_path_entries = try help.splitPathEntries(std.testing.allocator, "");
    defer empty_path_entries.deinit();
    try std.testing.expectEqual(@as(usize, 1), empty_path_entries.count());
    try std.testing.expectEqualStrings("", empty_path_entries.entries.items[0]);

    const exec_entries = [_]help.DirectoryEntry{
        .{ .name = "zigux-stat", .is_executable = true },
        .{ .name = "zigux-report.exe", .is_executable = true },
    };
    const other_entries = [_]help.DirectoryEntry{
        .{ .name = "zigux-trace", .is_executable = true },
        .{ .name = "zigux-report.exe", .is_executable = true },
    };

    var source = FixtureSource{
        .dirs = &.{
            .{ .path = "", .entries = &.{} },
            .{ .path = "/opt/perf/bin", .entries = &exec_entries },
            .{ .path = "/usr/bin", .entries = &other_entries },
        },
    };

    var main_cmds = help.CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    var other_cmds = help.CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    try help.loadCommandListsFromEnvPath(
        std.testing.allocator,
        "zigux-",
        "/opt/perf/bin",
        ":/opt/perf/bin::/usr/bin:",
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

    const empty_only_entries = [_]help.DirectoryEntry{
        .{ .name = "zigux-empty", .is_executable = true },
    };

    var empty_only_source = FixtureSource{
        .dirs = &.{
            .{ .path = "", .entries = &empty_only_entries },
            .{ .path = "/opt/perf/bin", .entries = &.{} },
        },
    };

    var empty_main_cmds = help.CmdNames.init(std.testing.allocator);
    defer empty_main_cmds.deinit();
    var empty_other_cmds = help.CmdNames.init(std.testing.allocator);
    defer empty_other_cmds.deinit();

    try help.loadCommandListsFromEnvPath(
        std.testing.allocator,
        "zigux-",
        "/opt/perf/bin",
        "",
        &empty_main_cmds,
        &empty_other_cmds,
        &empty_only_source,
        FixtureSource.populate,
    );

    try std.testing.expectEqual(@as(usize, 0), empty_main_cmds.count());
    try std.testing.expectEqual(@as(usize, 1), empty_other_cmds.count());
    try std.testing.expectEqualStrings("empty", empty_other_cmds.names.items[0].name);
}

test "phase 8 help output emission keeps column-major pretty-printing pure and testable" {
    var cmds = help.CmdNames.init(std.testing.allocator);
    defer cmds.deinit();
    try cmds.addCmdName("annotate", 8);
    try cmds.addCmdName("bench", 5);
    try cmds.addCmdName("diff", 4);
    try cmds.addCmdName("report", 6);
    try cmds.addCmdName("stat", 4);
    cmds.sort();

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try help.writePrettyPrintStringListForTerminal(
        &rendered.writer,
        cmds,
        cmds.longestNameLen(),
        "31",
        "24",
        .{
            .rows = 25,
            .cols = 80,
        },
    );

    try std.testing.expectEqualStrings(
        "  annotate report\n" ++
            "  bench    stat\n" ++
            "  diff\n",
        rendered.writer.buffered(),
    );
}

test "phase 8 help section rendering keeps list_commands formatting pure and shared-width aware" {
    var main_cmds = help.CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.addCmdName("report", 6);
    try main_cmds.addCmdName("stat", 4);
    main_cmds.sort();

    var other_cmds = help.CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.addCmdName("trace", 5);
    other_cmds.sort();

    try std.testing.expectEqual(@as(usize, 6), help.longestNameLenAcrossLists(main_cmds, other_cmds));

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try help.writeCommandSectionsForTerminal(
        &rendered.writer,
        "perf",
        "/x",
        main_cmds,
        other_cmds,
        null,
        "24",
        null,
    );

    const main_rule = [_]u8{'-'} ** 22;
    const other_rule = [_]u8{'-'} ** 43;
    const expected = std.fmt.comptimePrint(
        "available perf in '/x'\n{s}\n" ++
            "  report stat\n" ++
            "\n" ++
            "perf available from elsewhere on your $PATH\n{s}\n" ++
            "  trace\n" ++
            "\n",
        .{ main_rule[0..], other_rule[0..] },
    );

    try std.testing.expectEqualStrings(expected, rendered.writer.buffered());
}

test "phase 8 help section rendering suppresses empty sections without stray headings or blank lines" {
    var main_cmds = help.CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();

    {
        var other_cmds = help.CmdNames.init(std.testing.allocator);
        defer other_cmds.deinit();
        try other_cmds.addCmdName("trace", 5);
        try other_cmds.addCmdName("version", 7);
        other_cmds.sort();

        var rendered_other_only: std.Io.Writer.Allocating = .init(std.testing.allocator);
        defer rendered_other_only.deinit();

        try help.writeCommandSectionsForTerminal(
            &rendered_other_only.writer,
            "perf",
            "/ignored",
            main_cmds,
            other_cmds,
            null,
            "18",
            null,
        );

        const other_rule = [_]u8{'-'} ** 43;
        const expected_other_only = std.fmt.comptimePrint(
            "perf available from elsewhere on your $PATH\n{s}\n" ++
                "  trace   version\n" ++
                "\n",
            .{other_rule[0..]},
        );

        try std.testing.expectEqualStrings(expected_other_only, rendered_other_only.writer.buffered());
    }

    {
        var other_cmds = help.CmdNames.init(std.testing.allocator);
        defer other_cmds.deinit();

        var rendered_empty: std.Io.Writer.Allocating = .init(std.testing.allocator);
        defer rendered_empty.deinit();

        try help.writeCommandSectionsForTerminal(
            &rendered_empty.writer,
            "perf",
            "/ignored",
            main_cmds,
            other_cmds,
            null,
            "18",
            null,
        );

        try std.testing.expectEqualStrings("", rendered_empty.writer.buffered());
    }
}

test "phase 8 help docs keep the parked stable-output boundary explicit" {
    const slice_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-help-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(slice_note);

    try expectContains(slice_note, "PHASE8_STATUS=parked");
    try expectContains(slice_note, "PHASE8_SLICE=help-command-source-and-terminal-starter");
    try expectContains(slice_note, "tools/lib/subcmd/help.zig");
    try expectContains(slice_note, "zigux/tests/phase8_help.zig");
    try expectContains(slice_note, "helper-first expansion rule");
    try expectContains(slice_note, "serious repo-hosted tooling");
    try expectContains(slice_note, "output-stable tooling behavior");
    try expectContains(slice_note, "stable command-list manipulation logic");
    try expectContains(slice_note, "section-level output stays testable");
    try expectContains(slice_note, "list_commands()");
    try expectContains(slice_note, "does not yet claim:");
    try expectContains(slice_note, "cmd_help()");
}

test "phase 8 help review checklist keeps the parked stable-output packet reviewable" {
    const review_checklist = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(review_checklist);

    try expectContains(review_checklist, "parked Phase 8 `help` packet");
    try expectContains(review_checklist, "Documentation/zigux/phase8-help-slice.md");
    try expectContains(review_checklist, "zigux/tests/phase8_help.zig");
    try expectContains(review_checklist, "`load_command_list()`");
    try expectContains(review_checklist, "`pretty_print_string_list()`");
    try expectContains(review_checklist, "`list_commands()`");
    try expectContains(review_checklist, "helper-first, output-stable tooling behavior");
    try expectContains(review_checklist, "`opendir()` or `readdir()` parity");
    try expectContains(review_checklist, "raw `ioctl()` terminal probing");
}

test "phase 8 help evidence still matches the live C helper anchors" {
    const help_c = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/subcmd/help.c",
        16 * 1024,
    );
    defer std.testing.allocator.free(help_c);

    try expectContains(help_c, "void add_cmdname(struct cmdnames *cmds, const char *name, size_t len)");
    try expectContains(help_c, "void uniq(struct cmdnames *cmds)");
    try expectContains(help_c, "void exclude_cmds(struct cmdnames *cmds, struct cmdnames *excludes)");
    try expectContains(help_c, "static void get_term_dimensions(struct winsize *ws)");
    try expectContains(help_c, "static void pretty_print_string_list(struct cmdnames *cmds, int longest)");
    try expectContains(help_c, "void load_command_list(const char *prefix,");
    try expectContains(help_c, "list_commands_in_dir(main_cmds, exec_path, prefix);");
    try expectContains(help_c, "void list_commands(const char *title, struct cmdnames *main_cmds,");
    try expectContains(help_c, "printf(\"available %s in '%s'\\n\", title, exec_path);");
    try expectContains(help_c, "printf(\"%s available from elsewhere on your $PATH\\n\", title);");
}
