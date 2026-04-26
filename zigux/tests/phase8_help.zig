const std = @import("std");
const help = @import("help");

test "phase 8 help module imports cleanly" {
    _ = help;
}

test "phase 8 help starter slice covers command-list ownership, filtering, exclusion, and layout planning" {
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
    try std.testing.expectEqualStrings("record", help.commandNameFromEntry("perf-record.exe", "perf-").?);

    const layout = help.planPrettyPrint(7, 8, 41);
    try std.testing.expectEqual(@as(usize, 4), layout.cols);
    try std.testing.expectEqual(@as(usize, 2), layout.rows);
    try std.testing.expectEqual(@as(usize, 9), layout.spacing);

    const narrow_layout = help.planPrettyPrint(3, 8, 9);
    try std.testing.expectEqual(@as(usize, 1), narrow_layout.cols);
    try std.testing.expectEqual(@as(usize, 3), narrow_layout.rows);
    try std.testing.expectEqual(@as(usize, 9), narrow_layout.spacing);

    const empty_layout = help.planPrettyPrint(0, 8, 41);
    try std.testing.expectEqual(@as(usize, 1), empty_layout.cols);
    try std.testing.expectEqual(@as(usize, 0), empty_layout.rows);
    try std.testing.expectEqual(@as(usize, 9), empty_layout.spacing);
}

test "phase 8 help command-source layer models load_command_list without directory I/O" {
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
}
