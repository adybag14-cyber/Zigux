const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "required values needing JSON escapes stay data after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input\none.c",
        "--reference=ref\"quoted\\slash.sym",
        "--dump-types",
        "types\tfile.symtypes",
        "tail\rc",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("ref\"quoted\\slash.sym", request.reference_files[0]);
                try testing.expectEqualStrings("types\tfile.symtypes", request.dump_types_file.?);

                const expected_rendered = [_][]const u8{
                    "--reference=ref\"quoted\\slash.sym",
                    "--dump-types",
                    "types\tfile.symtypes",
                    "input\none.c",
                    "tail\rc",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    }
}

test "bridge JSON escapes required values and delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input\none.c",
        "--reference=ref\"quoted\\slash.sym",
        "--dump-types",
        "types\tfile.symtypes",
        "tail\rc",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    const written = output.written();
    try testing.expect(std.mem.indexOf(u8, written, "input\\none.c") != null);
    try testing.expect(std.mem.indexOf(u8, written, "ref\\\"quoted\\\\slash.sym") != null);
    try testing.expect(std.mem.indexOf(u8, written, "types\\tfile.symtypes") != null);
    try testing.expect(std.mem.indexOf(u8, written, "tail\\rc") != null);

    try testing.expect(std.mem.indexOfScalar(u8, written[0 .. written.len - 1], '\n') == null);
    try testing.expect(std.mem.indexOfScalar(u8, written, '\r') == null);
    try testing.expect(std.mem.indexOfScalar(u8, written, '\t') == null);
}
