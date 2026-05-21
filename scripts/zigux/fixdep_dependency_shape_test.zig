const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer std.testing.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(_: *@This()) !void {}
};

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "runFixdep keeps later concatenated targets after a continued comment line" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_concatenated_source.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_concatenated_dep.h",
        .{base_path},
    );
    defer std.testing.allocator.free(dep_path);

    const temp_source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_concatenated_temp.c",
        .{base_path},
    );
    defer std.testing.allocator.free(temp_source_path);

    const temp_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_concatenated_temp_dep.h",
        .{base_path},
    );
    defer std.testing.allocator.free(temp_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_concatenated.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_concatenated.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_concatenated_source.c",
        .data = "/* CONFIG_ZIGUX_DT_SOURCE */\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_concatenated_dep.h",
        .data = "#define CONFIG_ZIGUX_DT_HEADER 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_concatenated_temp.c",
        .data = "int zigux_fixdep_sample_concatenated_temp(void) { return 0; }\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_concatenated_temp_dep.h",
        .data = "#define CONFIG_ZIGUX_DT_SECONDARY 1\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_concatenated.o: {s} \\\n" ++
            " {s}\n" ++
            "# rustc comment continues \\\n" ++
            "across an intermediate physical line \\\n" ++
            "before the next real target\n" ++
            "sample_concatenated.o: {s} \\\n" ++
            " {s}\n",
        .{ source_path, dep_path, temp_source_path, temp_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_concatenated.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator, 640);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_concatenated.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_concatenated.o := {s}\n\n" ++
            "source_sample_concatenated.o := {s}\n\n" ++
            "deps_sample_concatenated.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_DT_SOURCE) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_DT_HEADER) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_DT_SECONDARY) \\\n" ++
            "\n" ++
            "sample_concatenated.o: $(deps_sample_concatenated.o)\n\n" ++
            "$(deps_sample_concatenated.o):\n",
        .{ cmdline, source_path, dep_path, temp_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}

test "runFixdep preserves dependency continuation chains across physical lines" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_dependency_continuation_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const dep_one_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_dependency_continuation_dep_one.so",
        .{base_path},
    );
    defer std.testing.allocator.free(dep_one_path);

    const dep_two_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_dependency_continuation_dep_two.so",
        .{base_path},
    );
    defer std.testing.allocator.free(dep_two_path);

    const dep_three_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_dependency_continuation_dep_three.so",
        .{base_path},
    );
    defer std.testing.allocator.free(dep_three_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_dependency_continuation.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_dependency_continuation.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_dependency_continuation_source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_dependency_continuation_dep_one.so",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_dependency_continuation_dep_two.so",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_dependency_continuation_dep_three.so",
        .data = "",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_dependency_continuation.o: {s} \\\n" ++
            " {s} \\\n" ++
            " {s} \\\n" ++
            " {s}\n",
        .{ source_path, dep_one_path, dep_two_path, dep_three_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_dependency_continuation.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_dependency_continuation.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_dependency_continuation.o := {s}\n\n" ++
            "source_sample_dependency_continuation.o := {s}\n\n" ++
            "deps_sample_dependency_continuation.o := \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample_dependency_continuation.o: $(deps_sample_dependency_continuation.o)\n\n" ++
            "$(deps_sample_dependency_continuation.o):\n",
        .{ cmdline, source_path, dep_one_path, dep_two_path, dep_three_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}

test "runFixdep keeps later config deps after continued comment blocks" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_comment_chain_source.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const config_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_comment_chain-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(config_dep_path);

    const later_config_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_comment_chain_later-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(later_config_dep_path);

    const later_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_comment_chain_later_dep.so",
        .{base_path},
    );
    defer std.testing.allocator.free(later_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_comment_chain.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_comment_chain.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_comment_chain_source.c",
        .data = "int zigux_fixdep_sample_comment_chain(void) { return 0; }\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_comment_chain-config.h",
        .data = "#define CONFIG_ZIGUX_CHAIN 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_comment_chain_later-config.h",
        .data = "#define CONFIG_ZIGUX_LATER_CHAIN_MODULE 1\n" ++
            "#define CONFIG_ZIGUX_LATER_CHAIN 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_comment_chain_later_dep.so",
        .data = "",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_comment_chain.o: {s} \\\n" ++
            " {s}\n" ++
            "# generated by rustc\\\n" ++
            "still inside the continued comment\\\n" ++
            "before the next real target\n" ++
            "sample_comment_chain.o: ignored_second_source.rmeta {s} {s}\n",
        .{ source_path, config_dep_path, later_config_dep_path, later_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_comment_chain.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_comment_chain.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_comment_chain.o := {s}\n\n" ++
            "source_sample_comment_chain.o := {s}\n\n" ++
            "deps_sample_comment_chain.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_CHAIN) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_LATER_CHAIN) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample_comment_chain.o: $(deps_sample_comment_chain.o)\n\n" ++
            "$(deps_sample_comment_chain.o):\n",
        .{ cmdline, source_path, config_dep_path, later_config_dep_path, later_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}

test "runFixdep ignores bytes after the first embedded NUL in depfiles" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_nul_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const config_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_nul-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(config_dep_path);

    const later_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_nul_later_dep.so",
        .{base_path},
    );
    defer std.testing.allocator.free(later_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_nul.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_nul.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_nul_source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_nul-config.h",
        .data = "#define CONFIG_ZIGUX_NUL_CHAIN 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_nul_later_dep.so",
        .data = "",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_nul.o: {s} {s}\x00sample_nul.o: ignored_second_source.rmeta {s}\n",
        .{ source_path, config_dep_path, later_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_nul.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_nul.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_nul.o := {s}\n\n" ++
            "source_sample_nul.o := {s}\n\n" ++
            "deps_sample_nul.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_NUL_CHAIN) \\\n" ++
            "\n" ++
            "sample_nul.o: $(deps_sample_nul.o)\n\n" ++
            "$(deps_sample_nul.o):\n",
        .{ cmdline, source_path, config_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
