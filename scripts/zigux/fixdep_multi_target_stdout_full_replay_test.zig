const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(self: *@This()) !void {
        _ = self;
        return error.OutputWrite;
    }
};

test "fixdep multi-target stdout-full replay keeps the bounded flush-stage packet intact" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    const depfile = "zigux/tests/fixtures/fixdep/sample_multi_target.d";
    const target = "module/sample2_stdout_full.o";
    const cmdline =
        "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2_stdout_full.o";

    try fixdep.runFixdep(std.testing.allocator, io_instance.io(), &capture, depfile, target, cmdline);

    try std.testing.expectError(error.OutputWrite, capture.flush());

    try std.testing.expectEqualStrings(
        "savedcmd_module/sample2_stdout_full.o := clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2_stdout_full.o\n\n" ++
            "source_module/sample2_stdout_full.o := zigux/tests/fixtures/fixdep/sample2.c\n\n" ++
            "deps_module/sample2_stdout_full.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_MULTI) \\\n" ++
            "  zigux/tests/fixtures/fixdep/shared#config.h \\\n" ++
            "    $(wildcard include/config/ZIGUX_HASH) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SHARED) \\\n" ++
            "  zigux/tests/fixtures/fixdep/sample2-config.h \\\n" ++
            "    $(wildcard include/config/ZIGUX_SECOND) \\\n" ++
            "  zigux/tests/fixtures/fixdep/sample2.so \\\n\n" ++
            "module/sample2_stdout_full.o: $(deps_module/sample2_stdout_full.o)\n\n" ++
            "$(deps_module/sample2_stdout_full.o):\n",
        capture.list.items,
    );

    const expected_stderr = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt",
        std.testing.allocator,
        .limited(1024),
    );
    defer std.testing.allocator.free(expected_stderr);

    try std.testing.expectEqualStrings(
        "fixdep: not all data was written to the output\n",
        expected_stderr,
    );
}
