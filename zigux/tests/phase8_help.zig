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

test "phase 8 help module imports cleanly" {
    _ = help;
}

test "phase 8 help focused replay keeps integrated command discovery and section rendering aligned with help.c" {
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
            .{ .path = "", .entries = &.{} },
            .{ .path = "/opt/perf/bin", .entries = &exec_entries },
            .{ .path = "/usr/bin", .entries = &path_entries },
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
    const fallback_terminal = help.resolveTerminalDimensions("0", "120", .{
        .rows = 31,
        .cols = 24,
    });
    try std.testing.expectEqual(@as(usize, 31), fallback_terminal.rows);
    try std.testing.expectEqual(@as(usize, 24), fallback_terminal.cols);

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try help.writeCommandSectionsForTerminal(
        &rendered.writer,
        "perf",
        "/opt/perf/bin",
        main_cmds,
        other_cmds,
        "0",
        "120",
        .{
            .rows = 31,
            .cols = 24,
        },
    );

    const main_rule = [_]u8{'-'} ** 33;
    const other_rule = [_]u8{'-'} ** 43;
    const expected = std.fmt.comptimePrint(
        "available perf in '/opt/perf/bin'\n{s}\n" ++
            "  report stat\n" ++
            "\n" ++
            "perf available from elsewhere on your $PATH\n{s}\n" ++
            "  trace\n" ++
            "\n",
        .{ main_rule[0..], other_rule[0..] },
    );

    try std.testing.expectEqualStrings(expected, rendered.writer.buffered());
}

test "phase 8 help focused replay keeps main-only output free of stray PATH headings" {
    const exec_entries = [_]help.DirectoryEntry{
        .{ .name = "perf-report.exe", .is_executable = true },
        .{ .name = "perf-stat", .is_executable = true },
    };

    var source = FixtureSource{
        .dirs = &.{
            .{ .path = "/opt/perf/bin", .entries = &exec_entries },
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
        "/opt/perf/bin:/opt/perf/bin",
        &main_cmds,
        &other_cmds,
        &source,
        FixtureSource.populate,
    );

    try std.testing.expectEqual(@as(usize, 2), main_cmds.count());
    try std.testing.expectEqual(@as(usize, 0), other_cmds.count());

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try help.writeCommandSectionsForTerminal(
        &rendered.writer,
        "perf",
        "/opt/perf/bin",
        main_cmds,
        other_cmds,
        null,
        "120",
        null,
    );

    const main_rule = [_]u8{'-'} ** 33;
    const expected = std.fmt.comptimePrint(
        "available perf in '/opt/perf/bin'\n{s}\n" ++
            "  report stat\n" ++
            "\n",
        .{main_rule[0..]},
    );

    try std.testing.expectEqualStrings(expected, rendered.writer.buffered());
    try std.testing.expect(std.mem.indexOf(u8, rendered.writer.buffered(), "elsewhere on your $PATH") == null);
}

test "phase 8 help focused replay keeps shared column width stable when PATH commands are longer" {
    const exec_entries = [_]help.DirectoryEntry{
        .{ .name = "perf-report.exe", .is_executable = true },
        .{ .name = "perf-stat", .is_executable = true },
    };
    const path_entries = [_]help.DirectoryEntry{
        .{ .name = "perf-annotate", .is_executable = true },
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

    try help.loadCommandListsFromEnvPath(
        std.testing.allocator,
        null,
        "/opt/perf/bin",
        "/opt/perf/bin:/usr/bin",
        &main_cmds,
        &other_cmds,
        &source,
        FixtureSource.populate,
    );

    try std.testing.expectEqual(@as(usize, 2), main_cmds.count());
    try std.testing.expectEqual(@as(usize, 1), other_cmds.count());
    try std.testing.expectEqual(@as(usize, 8), help.longestNameLenAcrossLists(main_cmds, other_cmds));

    var rendered: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer rendered.deinit();

    try help.writeCommandSectionsForTerminal(
        &rendered.writer,
        "perf",
        "/opt/perf/bin",
        main_cmds,
        other_cmds,
        null,
        "120",
        null,
    );

    const main_rule = [_]u8{'-'} ** 33;
    const other_rule = [_]u8{'-'} ** 43;
    const expected = std.fmt.comptimePrint(
        "available perf in '/opt/perf/bin'\n{s}\n" ++
            "  report   stat\n" ++
            "\n" ++
            "perf available from elsewhere on your $PATH\n{s}\n" ++
            "  annotate\n" ++
            "\n",
        .{ main_rule[0..], other_rule[0..] },
    );

    try std.testing.expectEqualStrings(expected, rendered.writer.buffered());
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
    try expectContains(slice_note, "zigux/tests/phase8_help_only_build.zig");
    try expectContains(slice_note, "zigux/tests/phase8_help_kallsyms_only_build.zig");
    try expectContains(slice_note, "stable command-list manipulation logic");
    try expectContains(slice_note, "Pure writer-driven output emission remains in scope here");
    try expectContains(slice_note, "without widening into terminal, environment, or CLI side effects");
    try expectContains(slice_note, "section-level output stays testable");
    try expectContains(slice_note, "list_commands()");
    try expectContains(slice_note, "fully empty `PATH` fallback");
    try expectContains(slice_note, "phase replay stays centered on integrated command discovery and section rendering");
    try expectContains(slice_note, "make -C zigux phase8-help-test");
    try expectContains(slice_note, "does not yet claim:");
    try expectContains(slice_note, "cmd_help()");
    try expectContains(slice_note, "serious repo-hosted tooling");
    try expectContains(slice_note, "`tools/lib/subcmd/*.zig`");
    try expectContains(slice_note, "output-stable tooling behavior");
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
