const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "abbreviated inline required long values stay request data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ref=alpha.symref",
        "--dump-t=types.symtypes",
        "--deb",
        "source.c",
        "--war",
        "--qui",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("alpha.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &.{
                    "--ver",
                    "--ref=alpha.symref",
                    "--dump-t=types.symtypes",
                    "--deb",
                    "--war",
                    "--qui",
                    "source.c",
                }, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "abbreviated inline required values render through bridge json" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ref=beta.symref",
        "--dump-t=types.out",
        "--",
        "--ref=tail.symref",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    try testing.expect(std.mem.indexOf(u8, output.written(), "\"argv\":[\"scripts/genksyms/genksyms\",\"--ref=beta.symref\",\"--dump-t=types.out\",\"--\",\"--ref=tail.symref\"]") != null);
    try testing.expect(std.mem.indexOf(u8, output.written(), "\"reference_files\":[\"beta.symref\"]") != null);
    try testing.expect(std.mem.indexOf(u8, output.written(), "\"dump_types_file\":\"types.out\"") != null);
}
