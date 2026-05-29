const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const WriteError = error{InjectedWriteFailure};

const elf32_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_header = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const truncated_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0 };
const not_elf_header = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class_header = [_]u8{ 0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

const FailingWriter = struct {
    calls: usize = 0,
    bytes_seen: usize = 0,

    pub fn writeAll(self: *@This(), bytes: []const u8) WriteError!void {
        self.calls += 1;
        self.bytes_seen += bytes.len;
        return WriteError.InjectedWriteFailure;
    }
};

const CountingWriter = struct {
    calls: usize = 0,
    bytes_seen: usize = 0,

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        self.calls += 1;
        self.bytes_seen += bytes.len;
    }
};

test "renderOutcome propagates stdout writer failures before returning success" {
    const success_cases = [_]mk_elfconfig.Outcome{ .elf32, .elf64 };

    for (success_cases) |outcome| {
        var stdout = FailingWriter{};
        var stderr = CountingWriter{};

        try std.testing.expectError(
            WriteError.InjectedWriteFailure,
            mk_elfconfig.renderOutcome(&stdout, &stderr, outcome),
        );
        try std.testing.expectEqual(@as(usize, 1), stdout.calls);
        try std.testing.expect(stdout.bytes_seen > 0);
        try std.testing.expectEqual(@as(usize, 0), stderr.calls);
        try std.testing.expectEqual(@as(usize, 0), stderr.bytes_seen);
    }
}

test "renderOutcome propagates stderr writer failures before returning failure" {
    const diagnostic_cases = [_]mk_elfconfig.Outcome{ .truncated, .not_elf };

    for (diagnostic_cases) |outcome| {
        var stdout = CountingWriter{};
        var stderr = FailingWriter{};

        try std.testing.expectError(
            WriteError.InjectedWriteFailure,
            mk_elfconfig.renderOutcome(&stdout, &stderr, outcome),
        );
        try std.testing.expectEqual(@as(usize, 0), stdout.calls);
        try std.testing.expectEqual(@as(usize, 0), stdout.bytes_seen);
        try std.testing.expectEqual(@as(usize, 1), stderr.calls);
        try std.testing.expect(stderr.bytes_seen > 0);
    }
}

test "invalid class returns failure without touching either writer" {
    var stdout = FailingWriter{};
    var stderr = FailingWriter{};

    const exit_code = try mk_elfconfig.renderOutcome(&stdout, &stderr, .invalid_class);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 0), stdout.calls);
    try std.testing.expectEqual(@as(usize, 0), stderr.calls);
    try std.testing.expectEqual(@as(usize, 0), stdout.bytes_seen);
    try std.testing.expectEqual(@as(usize, 0), stderr.bytes_seen);
}

test "runMkElfconfig propagates stdout writer failures after classifying successes" {
    const success_headers = [_][]const u8{ &elf32_header, &elf64_header };

    for (success_headers) |header| {
        var stdout = FailingWriter{};
        var stderr = CountingWriter{};

        try std.testing.expectError(
            WriteError.InjectedWriteFailure,
            mk_elfconfig.runMkElfconfig(header, &stdout, &stderr),
        );
        try std.testing.expectEqual(@as(usize, 1), stdout.calls);
        try std.testing.expect(stdout.bytes_seen > 0);
        try std.testing.expectEqual(@as(usize, 0), stderr.calls);
        try std.testing.expectEqual(@as(usize, 0), stderr.bytes_seen);
    }
}

test "runMkElfconfig propagates stderr writer failures after classifying diagnostics" {
    const diagnostic_headers = [_][]const u8{ &truncated_header, &not_elf_header };

    for (diagnostic_headers) |header| {
        var stdout = CountingWriter{};
        var stderr = FailingWriter{};

        try std.testing.expectError(
            WriteError.InjectedWriteFailure,
            mk_elfconfig.runMkElfconfig(header, &stdout, &stderr),
        );
        try std.testing.expectEqual(@as(usize, 0), stdout.calls);
        try std.testing.expectEqual(@as(usize, 0), stdout.bytes_seen);
        try std.testing.expectEqual(@as(usize, 1), stderr.calls);
        try std.testing.expect(stderr.bytes_seen > 0);
    }
}

test "runMkElfconfig invalid class does not touch fallible writers" {
    var stdout = FailingWriter{};
    var stderr = FailingWriter{};

    const exit_code = try mk_elfconfig.runMkElfconfig(&invalid_class_header, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqual(@as(usize, 0), stdout.calls);
    try std.testing.expectEqual(@as(usize, 0), stderr.calls);
    try std.testing.expectEqual(@as(usize, 0), stdout.bytes_seen);
    try std.testing.expectEqual(@as(usize, 0), stderr.bytes_seen);
}
