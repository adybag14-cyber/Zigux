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
}
