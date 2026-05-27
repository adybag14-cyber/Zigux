const std = @import("std");
const help = @import("help");
const phase8_help_options = @import("phase8_help_options");

const phase8_help_slice = phase8_help_options.phase8_help_slice;

test "phase 8 help module imports cleanly" {
    _ = help;
}

test "phase 8 help slice keeps helper-first stable-output evidence explicit" {
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "serious repo-hosted tooling"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "tools/lib/subcmd/*.zig"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "output-stable tooling behavior"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "`make -C zigux phase8-help-test`"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "`CommandNames`, `trimCommandPrefix`, `computePrettyLayout`, `renderPrettyStringList`, and `renderCommandSections`"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "exec-cmd command ownership"));
    try std.testing.expect(std.mem.containsAtLeast(u8, phase8_help_slice, 1, "bridge-heavy libbpf work"));
}

test "phase 8 help command-set helpers keep stable filtering and layout planning" {
    var main_cmds = help.CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();

    try main_cmds.add("trace");
    try main_cmds.add("record");
    try main_cmds.add("");
    try main_cmds.add("trace");
    main_cmds.sort();
    main_cmds.uniqSorted();

    var excludes = help.CommandNames.init(std.testing.allocator);
    defer excludes.deinit();
    try excludes.add("record");
    excludes.sort();
    main_cmds.excludeSorted(&excludes);

    try std.testing.expectEqual(@as(usize, 2), main_cmds.count());
    try std.testing.expect(main_cmds.contains(""));
    try std.testing.expect(main_cmds.contains("trace"));
    try std.testing.expectEqual(@as(usize, 5), main_cmds.longest());
    try std.testing.expectEqual(@as(?[]const u8, null), help.trimCommandPrefix("perf-", help.default_command_prefix));
    try std.testing.expectEqual(@as(?[]const u8, null), help.trimCommandPrefix("perf-.exe", help.default_command_prefix));
    try std.testing.expectEqualStrings("record", help.trimCommandPrefix("perf-record.exe", help.default_command_prefix).?);
    try std.testing.expectEqual(@as(?[]const u8, null), help.trimCommandPrefix("trace2html", help.default_command_prefix));

    const layout = help.computePrettyLayout(7, 8, 41);
    try std.testing.expectEqual(@as(usize, 4), layout.cols);
    try std.testing.expectEqual(@as(usize, 2), layout.rows);
    try std.testing.expectEqual(@as(usize, 9), layout.space);

    const narrow_layout = help.computePrettyLayout(3, 8, 9);
    try std.testing.expectEqual(@as(usize, 1), narrow_layout.cols);
    try std.testing.expectEqual(@as(usize, 3), narrow_layout.rows);
    try std.testing.expectEqual(@as(usize, 9), narrow_layout.space);

    const empty_layout = help.computePrettyLayout(0, 8, 41);
    try std.testing.expectEqual(@as(usize, 4), empty_layout.cols);
    try std.testing.expectEqual(@as(usize, 0), empty_layout.rows);
    try std.testing.expectEqual(@as(usize, 9), empty_layout.space);
}

test "phase 8 help pretty printer keeps the current row-major stable output" {
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
}

test "phase 8 help pretty printer falls back to the default width when terminal columns are unavailable" {
    var cmds = help.CommandNames.init(std.testing.allocator);
    defer cmds.deinit();
    try cmds.add("annotate");
    try cmds.add("bench");

    const rendered = try help.renderPrettyStringList(std.testing.allocator, &cmds, 0);
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        " annotate bench\n",
        rendered,
    );
}

test "phase 8 help section rendering keeps stable main and fallback headings" {
    var main_cmds = help.CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("stat");
    try main_cmds.add("top");
    main_cmds.sort();

    var other_cmds = help.CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.add("annotate");
    other_cmds.sort();

    const rendered = try help.renderCommandSections(
        std.testing.allocator,
        "tools",
        "/opt/perf/bin",
        &main_cmds,
        &other_cmds,
        20,
    );
    defer std.testing.allocator.free(rendered);

    try std.testing.expectEqualStrings(
        "available tools in '/opt/perf/bin'\n" ++
            "----------------------------------\n" ++
            " stat     top\n" ++
            "\n" ++
            "tools available from elsewhere on your $PATH\n" ++
            "--------------------------------------------\n" ++
            " annotate\n" ++
            "\n",
        rendered,
    );
}

test "phase 8 help empty exec path keeps the stable heading unquoted" {
    var main_cmds = help.CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();
    try main_cmds.add("annotate");
    main_cmds.sort();

    var other_cmds = help.CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    const rendered = try help.renderCommandSections(
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

test "phase 8 help fallback-only packet suppresses the empty main heading" {
    var main_cmds = help.CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();

    var other_cmds = help.CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();
    try other_cmds.add("report");
    try other_cmds.add("script");
    other_cmds.sort();

    const rendered = try help.renderCommandSections(
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

test "phase 8 help fully empty section rendering stays empty" {
    var main_cmds = help.CommandNames.init(std.testing.allocator);
    defer main_cmds.deinit();

    var other_cmds = help.CommandNames.init(std.testing.allocator);
    defer other_cmds.deinit();

    const rendered = try help.renderCommandSections(
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
