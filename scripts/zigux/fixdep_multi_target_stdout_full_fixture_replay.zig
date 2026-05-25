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
        defer std.testing.allocator.free(rendered);

        const remaining = self.fail_after -| self.list.items.len;
        const writable = @min(remaining, rendered.len);
        self.list.appendSlice(self.allocator, rendered[0..writable]) catch return error.OutputWrite;
        if (writable != rendered.len) {
            return error.OutputWrite;
        }
    }

    pub fn flush(_: *@This()) !void {}
};

test "runFixdep keeps committed multi-target stdout-full fixture prefix before output write failure" {
    const depfile_path = "zigux/tests/fixtures/fixdep/sample_multi_target.d";
    const cmdline =
        "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2_stdout_full.o";

    const expected_prefix =
        "savedcmd_module/sample2_stdout_full.o := " ++ cmdline ++ "\n\n" ++
        "source_module/sample2_stdout_full.o := zigux/tests/fixtures/fixdep/sample2.c\n\n" ++
        "deps_module/sample2_stdout_full.o := \\\n" ++
        "    $(wildcard include/config/ZIGUX_MULTI) \\\n" ++
        "  zigux/tests/fixtures/fixdep/shared#config.h \\\n";

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
