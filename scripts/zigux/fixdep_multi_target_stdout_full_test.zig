const std = @import("std");
const fixdep = @import("fixdep.zig");

const FailingCapture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,
    fail_after: usize,

    fn init(allocator: std.mem.Allocator, fail_after: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, fail_after + 64),
            .allocator = allocator,
            .fail_after = fail_after,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) error{OutputWrite}!void {
        const rendered = std.fmt.allocPrint(self.allocator, fmt, args) catch return error.OutputWrite;
        defer self.allocator.free(rendered);

        const remaining = self.fail_after -| self.list.items.len;
        const writable = @min(remaining, rendered.len);
        self.list.appendSlice(self.allocator, rendered[0..writable]) catch return error.OutputWrite;
        if (writable != rendered.len) {
            return error.OutputWrite;
        }
    }

    pub fn flush(_: *@This()) !void {}
};

test "runFixdep keeps the multi-target prelude before output write failures" {
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

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_multi_target.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const hash_depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared\\#config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(hash_depfile_path);

    const hash_visible_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/shared#config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(hash_visible_path);

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

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2.c",
        .data = "int zigux_fixdep_sample2(void) { return 0; }\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "shared#config.h",
        .data = "#define CONFIG_ZIGUX_HASH 1\n#define CONFIG_ZIGUX_SHARED_MODULE 1\n#define CONFIG_ZIGUX_HASH 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2-config.h",
        .data = "#define CONFIG_ZIGUX_SECOND 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample2.so",
        .data = "placeholder shared-object fixture for fixdep multi-target coverage\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "module/sample2_stdout_full.o: {s} {s} {s} {s}\n",
        .{ source_path, second_config_path, hash_depfile_path, shared_object_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_multi_target.d",
        .data = depfile_text,
    });

    const cmdline = "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2_stdout_full.o";
    const expected_prefix = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_module/sample2_stdout_full.o := {s}\n\n" ++
            "source_module/sample2_stdout_full.o := {s}\n\n" ++
            "deps_module/sample2_stdout_full.o := \\\n" ++
            "  {s} \\\n",
        .{ cmdline, source_path, second_config_path },
    );
    defer std.testing.allocator.free(expected_prefix);

    var capture = try FailingCapture.init(std.testing.allocator, expected_prefix.len);
    defer capture.deinit();

    try std.testing.expectError(
        error.OutputWrite,
        fixdep.runFixdep(
            std.testing.allocator,
            std.testing.io,
            &capture,
            depfile_path,
            "module/sample2_stdout_full.o",
            cmdline,
        ),
    );
    try std.testing.expectEqualStrings(expected_prefix, capture.list.items);
}
