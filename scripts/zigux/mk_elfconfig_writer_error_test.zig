const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const InjectedError = error{InjectedWrite};

const FailingWriter = struct {
    calls: usize = 0,
    last_write: []const u8 = "",

    pub fn writeAll(self: *@This(), bytes: []const u8) InjectedError!void {
        self.calls += 1;
        self.last_write = bytes;
        return error.InjectedWrite;
    }
};

const RecordingWriter = struct {
    calls: usize = 0,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{ .bytes = try std.ArrayList(u8).initCapacity(allocator, 32) };
    }

    fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
        self.bytes.deinit(allocator);
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        self.calls += 1;
        try self.bytes.appendSlice(std.testing.allocator, bytes);
    }
};

test "renderOutcome propagates stdout write failures for ELF success defines" {
    const cases = [_]struct {
        outcome: mk_elfconfig.Outcome,
        expected_write: []const u8,
    }{
        .{ .outcome = .elf32, .expected_write = "#define KERNEL_ELFCLASS ELFCLASS32\n" },
        .{ .outcome = .elf64, .expected_write = "#define KERNEL_ELFCLASS ELFCLASS64\n" },
    };

    for (cases) |case| {
        var stdout = FailingWriter{};
        var stderr = try RecordingWriter.init(std.testing.allocator);
        defer stderr.deinit(std.testing.allocator);

        try std.testing.expectError(
            error.InjectedWrite,
            mk_elfconfig.renderOutcome(&stdout, &stderr, case.outcome),
        );
        try std.testing.expectEqual(@as(usize, 1), stdout.calls);
        try std.testing.expectEqualStrings(case.expected_write, stdout.last_write);
        try std.testing.expectEqual(@as(usize, 0), stderr.calls);
        try std.testing.expectEqualStrings("", stderr.bytes.items);
    }
}

test "renderOutcome propagates stderr write failures for diagnostic outcomes" {
    const cases = [_]struct {
        outcome: mk_elfconfig.Outcome,
        expected_write: []const u8,
    }{
        .{ .outcome = .truncated, .expected_write = "Error: input truncated\n" },
        .{ .outcome = .not_elf, .expected_write = "Error: not ELF\n" },
    };

    for (cases) |case| {
        var stdout = try RecordingWriter.init(std.testing.allocator);
        defer stdout.deinit(std.testing.allocator);
        var stderr = FailingWriter{};

        try std.testing.expectError(
            error.InjectedWrite,
            mk_elfconfig.renderOutcome(&stdout, &stderr, case.outcome),
        );
        try std.testing.expectEqual(@as(usize, 0), stdout.calls);
        try std.testing.expectEqualStrings("", stdout.bytes.items);
        try std.testing.expectEqual(@as(usize, 1), stderr.calls);
        try std.testing.expectEqualStrings(case.expected_write, stderr.last_write);
    }
}

test "invalid class remains silent even when both writers would fail" {
    var stdout = FailingWriter{};
    var stderr = FailingWriter{};

    const exit_code = try mk_elfconfig.renderOutcome(&stdout, &stderr, .invalid_class);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 0), stdout.calls);
    try std.testing.expectEqual(@as(usize, 0), stderr.calls);
}
