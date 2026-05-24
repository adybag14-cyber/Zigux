const std = @import("std");
const help = @import("help");

test "phase 8 help module imports cleanly" {
    _ = help;
}

test "phase 8 help command packet keeps the current stable-output helper surface explicit" {
    try std.testing.expectEqualStrings(
        "annotate",
        help.trimCommandPrefix("perf-annotate", help.default_command_prefix).?,
    );
    try std.testing.expectEqualStrings(
        "script",
        help.trimCommandPrefix("perf-script.exe", help.default_command_prefix).?,
    );
    try std.testing.expectEqual(@as(?[]const u8, null), help.trimCommandPrefix("trace2html", help.default_command_prefix));

    var main_cmds = help.CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("report");
    try main_cmds.add("annotate");
    try main_cmds.add("report");
    try main_cmds.add("bench");
    main_cmds.sort();
    main_cmds.uniqSorted();

    try std.testing.expectEqual(@as(usize, 3), main_cmds.count());
    try std.testing.expect(main_cmds.contains("annotate"));
    try std.testing.expect(main_cmds.contains("bench"));
    try std.testing.expect(main_cmds.contains("report"));
    try std.testing.expectEqual(@as(usize, 8), main_cmds.longest());

    var other_cmds = help.CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.add("bench");
    try other_cmds.add("report");
    try other_cmds.add("script");
    other_cmds.sort();
    other_cmds.excludeSorted(&main_cmds);

    try std.testing.expectEqual(@as(usize, 1), other_cmds.count());
    try std.testing.expect(other_cmds.contains("script"));

    const layout = help.computePrettyLayout(5, 8, 32);
    try std.testing.expectEqual(@as(usize, 3), layout.cols);
    try std.testing.expectEqual(@as(usize, 2), layout.rows);
    try std.testing.expectEqual(@as(usize, 9), layout.space);
}

test "phase 8 help rendering keeps the row-major pretty layout and section headings stable" {
    var cmds = help.CommandNames.init(std.testing.allocator);
    defer cmds.deinit();
    for (&[_][]const u8{ "annotate", "bench", "buildid-cache", "diff", "evlist" }) |name| {
        try cmds.add(name);
    }

    const rendered = try help.renderPrettyStringList(std.testing.allocator, &cmds, 32);
    defer std.testing.allocator.free(rendered);
    try std.testing.expectEqualStrings(
        " annotate      diff\n" ++
            " bench         evlist\n" ++
            " buildid-cache\n",
        rendered,
    );

    var main_cmds = help.CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("annotate");
    try main_cmds.add("bench");

    var other_cmds = help.CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.add("report");

    const sections = try help.renderCommandSections(
        std.testing.allocator,
        "subcommands",
        "/usr/libexec/perf-core",
        &main_cmds,
        &other_cmds,
        80,
    );
    defer std.testing.allocator.free(sections);

    try std.testing.expectEqualStrings(
        "available subcommands in '/usr/libexec/perf-core'\n" ++
            "-------------------------------------------------\n" ++
            " annotate bench\n" ++
            "\n" ++
            "subcommands available from elsewhere on your $PATH\n" ++
            "--------------------------------------------------\n" ++
            " report\n" ++
            "\n",
        sections,
    );
}
