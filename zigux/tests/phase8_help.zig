const std = @import("std");
const help = @import("help");

test "phase 8 help module imports cleanly" {
    _ = help;
}

test "phase 8 help starter slice covers command-list ownership, sorting, exclusion, and layout planning" {
    var main_cmds = help.CmdNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.addCmdName("trace", 5);
    try main_cmds.addCmdName("record", 6);
    try main_cmds.addCmdName("trace", 5);
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

    const layout = help.planPrettyPrint(7, 8, 41);
    try std.testing.expectEqual(@as(usize, 4), layout.cols);
    try std.testing.expectEqual(@as(usize, 2), layout.rows);
    try std.testing.expectEqual(@as(usize, 9), layout.spacing);
}
