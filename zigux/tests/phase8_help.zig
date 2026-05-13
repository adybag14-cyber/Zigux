const std = @import("std");
const help = @import("help");
const phase8_help_options = @import("phase8_help_options");
const phase8_help_slice = phase8_help_options.phase8_help_slice;

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

test "phase 8 help module imports cleanly" {
    _ = help;
}

test "phase 8 help slice note keeps helper-first output-stable tooling posture and non-goals explicit" {
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "serious repo-hosted tooling"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "tools/lib/subcmd/*.zig"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "output-stable tooling behavior"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "output-stable pretty-print emission"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "full `cmd_help()`-adjacent CLI surface"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "direct directory walking, environment inspection, terminal probing, or a full `cmd_help()`-adjacent CLI surface"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "`opendir()` or `readdir()` parity for command discovery"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "direct `ioctl()`-backed terminal probing"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "direct environment reads or a full `cmd_help()`-adjacent CLI surface"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "make -C zigux phase8-help-test"));
}

test "phase 8 help slice covers command-list ownership, filtering, exclusion, terminal sizing, and layout planning" {
    var main_cmds = help.CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();

    try std.testing.expect(try help.addExecutableEntry(&main_cmds, "perf-trace", "perf-", true));
    try std.testing.expect(try help.addExecutableEntry(&main_cmds, "perf-record.exe", "perf-", true));
    try std.testing.expect(!(try help.addExecutableEntry(&main_cmds, "README.md", "perf-", true)));
    try std.testing.expect(try help.addExecutableEntry(&main_cmds, "perf-.exe", "perf-", true));
    try std.testing.expect(try help.addExecutableEntry(&main_cmds, "perf-trace", "perf-", true));

    main_cmds.sort();
    main_cmds.uniq();

    var excludes = help.CmdNames.init(std.testing.allocator);
    defer excludes.deinit();

    try excludes.addCmdName("record", 6);
    excludes.sort();
    main_cmds.excludeCmds(excludes);

    try std.testing.expectEqual(@as(usize, 2), main_cmds.count());
    try std.testing.expect(main_cmds.isInCmdList(""));
    try std.testing.expect(main_cmds.isInCmdList("trace"));
    try std.testing.expectEqual(@as(usize, 5), main_cmds.longestNameLen());
    try std.testing.expectEqualStrings("", help.commandNameFromEntry("perf-.exe", "perf-").?);
    try std.testing.expectEqualStrings("record", help.commandNameFromEntry("perf-record.exe", "perf-").?);

    const layout = help.planPrettyPrint(7, 8, 41);
    try std.testing.expectEqual(@as(usize, 4), layout.cols);
    try std.testing.expectEqual(@as(usize, 2), layout.rows);
    try std.testing.expectEqual(@as(usize, 9), layout.spacing);

    const narrow_layout = help.planPrettyPrint(3, 8, 9);
    try std.testing.expectEqual(@as(usize, 1), narrow_layout.cols);
    try std.testing.expectEqual(@as(usize, 3), narrow_layout.rows);
    try std.testing.expectEqual(@as(usize, 9), narrow_layout.spacing);

    const edge_layout = help.planPrettyPrint(4, 8, 18);
    try std.testing.expectEqual(@as(usize, 1), edge_layout.cols);
    try std.testing.expectEqual(@as(usize, 4), edge_layout.rows);
    try std.testing.expectEqual(@as(usize, 9), edge_layout.spacing);

    const terminal = help.resolveTerminalDimensions("31", "37", .{
        .rows = 20,
        .cols = 60,
    });
    try std.testing.expectEqual(@as(usize, 31), terminal.rows);
    try std.testing.expectEqual(@as(usize, 37), terminal.cols);

    const fallback_terminal = help.resolveTerminalDimensions("31", null, .{
        .rows = 20,
        .cols = 60,
    });
    try std.testing.expectEqual(@as(usize, 20), fallback_terminal.rows);
    try std.testing.expectEqual(@as(usize, 60), fallback_terminal.cols);

    const default_terminal = help.resolveTerminalDimensions(null, null, null);
    try std.testing.expectEqual(@as(usize, 25), default_terminal.rows);
    try std.testing.expectEqual(@as(usize, 80), default_terminal.cols);

    const env_layout = help.planPrettyPrintForTerminal(7, 8, "31", "37", .{
        .rows = 24,
        .cols = 80,
    });
    try std.testing.expectEqual(@as(usize, 4), env_layout.cols);
    try std.testing.expectEqual(@as(usize, 2), env_layout.rows);
    try std.testing.expectEqual(@as(usize, 9), env_layout.spacing);

    const empty_layout = help.planPrettyPrint(0, 8, 41);
    try std.testing.expectEqual(@as(usize, 4), empty_layout.cols);
    try std.testing.expectEqual(@as(usize, 0), empty_layout.rows);
    try std.testing.expectEqual(@as(usize, 9), empty_layout.spacing);
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

    const prefixed_terminal = help.resolveTerminalDimensions(" +31rows", "+37cols", .{
        .rows = 20,
        .cols = 60,
    });
    try std.testing.expectEqual(@as(usize, 31), prefixed_terminal.rows);
    try std.testing.expectEqual(@as(usize, 37), prefixed_terminal.cols);
}

test "phase 8 help raw PATH splitting keeps empty segments and exec-path exclusion aligned with help.c" {
    var split_entries = try help.splitPathEntries(std.testing.allocator, ":/opt/perf/bin::/usr/bin:");
    defer split_entries.deinit();

    try std.testing.expectEqual(@as(usize, 5), split_entries.count());
    try std.testing.expectEqualStrings("", split_entries.entries.items[0]);
    try std.testing.expectEqualStrings("/opt/perf/bin", split_entries.entries.items[1]);
    try std.testing.expectEqualStrings("", split_entries.entries.items[2]);
    try std.testing.expectEqualStrings("/usr/bin", split_entries.entries.items[3]);
    try std.testing.expectEqualStrings("", split_entries.entries.items[4]);

    const exec_entries = [_]help.DirectoryEntry{
        .{ .name = "perf-stat", .is_executable = true },
        .{ .name = "perf-report.exe", .is_executable = true },
    };
    const other_entries = [_]help.DirectoryEntry{
        .{ .name = "perf-trace", .is_executable = true },
        .{ .name = "perf-report.exe", .is_executable = true },
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
        null,
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
}

test "phase 8 help empty PATH fallback keeps section suppression and output stable" {
    const path_entries = [_]help.DirectoryEntry{
        .{ .name = "perf-report.exe", .is_executable = true },
        .{ .name = "perf-stat", .is_executable = true },
        .{ .name = "README.md", .is_executable = true },
        .{ .name = "perf-stat", .is_executable = true },
    };

    var source = FixtureSource{
        .dirs = &.{
            .{ .path = "", .entries = &path_entries },
        },
    };

    var main_cmds = help.CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    var other_cmds = help.CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    try help.loadCommandListsFromEnvPath(
        std.testing.allocator,
        null,
        null,
        "",
        &main_cmds,
        &other_cmds,
        &source,
        FixtureSource.populate,
    );

    try std.testing.expectEqual(@as(usize, 0), main_cmds.count());
    try std.testing.expectEqual(@as(usize, 2), other_cmds.count());
    try std.testing.expectEqualStrings("report", other_cmds.names.items[0].name);
    try std.testing.expectEqualStrings("stat", other_cmds.names.items[1].name);

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try help.writeCommandSectionsForTerminal(
        &rendered.writer,
        "perf",
        "/ignored",
        main_cmds,
        other_cmds,
        null,
        "24",
        null,
    );

    const other_rule = [_]u8{'-'} ** 43;
    const expected = std.fmt.comptimePrint(
        "perf available from elsewhere on your $PATH
{s}
" ++
            " report stat
" ++
            "
",
        .{other_rule[0..]},
    );

    try std.testing.expectEqualStrings(expected, rendered.writer.buffered());
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
        " annotate report
" ++
            " bench    stat
" ++
            " diff
",
        rendered.writer.buffered(),
    );
}

test "phase 8 help section rendering keeps the stable main and PATH headings reviewable" {
    var main_cmds = help.CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.addCmdName("stat", 4);
    try main_cmds.addCmdName("top", 3);
    main_cmds.sort();

    var other_cmds = help.CmdNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.addCmdName("annotate", 8);
    other_cmds.sort();

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try help.writeCommandSectionsForTerminal(
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
        "available tools in '/opt/perf/bin'
" ++
            "----------------------------------
" ++
            " stat top
" ++
            "
" ++
            "tools available from elsewhere on your $PATH
" ++
            "--------------------------------------------
" ++
            " annotate
" ++
            "
",
        rendered.writer.buffered());
}
