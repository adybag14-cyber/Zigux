const std = @import("std");
const fixdep = @import("fixdep.zig");

const DeferredOutputFailureWriter = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,
    flushed: bool = false,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(self: *@This()) !void {
        self.flushed = true;
        return error.NoSpaceLeft;
    }
};

test "runFixdep preserves widened multi-target output before stdout-full flush failure" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample2.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const shared_hash_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared\\#config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(shared_hash_dep_path);

    const shared_hash_visible_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared#config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(shared_hash_visible_path);

    const second_config_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample2-config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(second_config_path);

    const shared_object_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample2.so",
        .{base_path},
    );
    defer std.testing.allocator.free(shared_object_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_multi_target.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -Iinclude -DZIGUX_MULTI -c {s} -o module/sample2_stdout_full.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2.c",
        .data = "#define CONFIG_ZIGUX_MULTI 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "shared#config.h",
        .data = "#define CONFIG_ZIGUX_HASH 1\n" ++
            "#define CONFIG_ZIGUX_SHARED_MODULE 1\n" ++
            "#define CONFIG_ZIGUX_HASH 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2-config.h",
        .data = "#define CONFIG_ZIGUX_SECOND 1\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "module/sample2_stdout_full.o module/sample2_stdout_full.second.o: {s} \\\n" ++
            " {s} \\\n" ++
            " {s} \\\n" ++
            " {s} \\\n" ++
            " include/generated/autoconf.h \\\n" ++
            " {s} \\\n" ++
            " {s} \\\n" ++
            " include/generated/autoconf.h \\\n" ++
            " {s}\n",
        .{
            source_path,
            shared_hash_dep_path,
            second_config_path,
            shared_object_path,
            shared_hash_dep_path,
            shared_object_path,
            second_config_path,
        },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_multi_target.d",
        .data = depfile_text,
    });

    var stdout = try DeferredOutputFailureWriter.init(std.testing.allocator);
    defer stdout.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &stdout,
        depfile_path,
        "module/sample2_stdout_full.o",
        cmdline,
    );

    try std.testing.expectError(error.NoSpaceLeft, stdout.flush());
    try std.testing.expect(stdout.flushed);

    const expected_stdout = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_module/sample2_stdout_full.o := {s}\n\n" ++
            "source_module/sample2_stdout_full.o := {s}\n\n" ++
            "deps_module/sample2_stdout_full.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_MULTI) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_HASH) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SHARED) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_SECOND) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "module/sample2_stdout_full.o: $(deps_module/sample2_stdout_full.o)\n\n" ++
            "$(deps_module/sample2_stdout_full.o):\n",
        .{
            cmdline,
            source_path,
            shared_hash_visible_path,
            second_config_path,
            shared_object_path,
        },
    );
    defer std.testing.allocator.free(expected_stdout);

    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
}
