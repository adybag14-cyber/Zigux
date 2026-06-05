const std = @import("std");
const gen = @import("genksyms_crc.zig");

const WriteKind = enum {
    write_all,
    print,
    write_byte,
};

const FailingWriter = struct {
    fail_kind: WriteKind,
    remaining_successes: usize,

    fn shouldFail(self: *FailingWriter, kind: WriteKind) bool {
        if (kind != self.fail_kind) return false;
        if (self.remaining_successes == 0) return true;
        self.remaining_successes -= 1;
        return false;
    }

    pub fn writeAll(self: *FailingWriter, bytes: []const u8) !void {
        _ = bytes;
        if (self.shouldFail(.write_all)) return error.InjectedWriterFailure;
    }

    pub fn print(self: *FailingWriter, comptime fmt: []const u8, args: anytype) !void {
        _ = fmt;
        _ = args;
        if (self.shouldFail(.print)) return error.InjectedWriterFailure;
    }

    pub fn writeByte(self: *FailingWriter, byte: u8) !void {
        _ = byte;
        if (self.shouldFail(.write_byte)) return error.InjectedWriterFailure;
    }
};

test "runGenksymsCrc propagates writer errors from each output path" {
    var header_failure = FailingWriter{
        .fail_kind = .write_all,
        .remaining_successes = 0,
    };
    try std.testing.expectError(
        error.InjectedWriterFailure,
        gen.runGenksymsCrc("int\n", &header_failure),
    );

    var crc_print_failure = FailingWriter{
        .fail_kind = .print,
        .remaining_successes = 0,
    };
    try std.testing.expectError(
        error.InjectedWriterFailure,
        gen.runGenksymsCrc("int\n", &crc_print_failure),
    );

    var byte_failure = FailingWriter{
        .fail_kind = .write_byte,
        .remaining_successes = 3,
    };
    try std.testing.expectError(
        error.InjectedWriterFailure,
        gen.runGenksymsCrc("int\nstruct device\n", &byte_failure),
    );
}
