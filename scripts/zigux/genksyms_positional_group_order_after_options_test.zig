const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(allocator: std.mem.Allocator, args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "positional groups keep raw argv while rendered options stay normalized" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.c",
        "--debug",
        "-r",
        "ref1.symref",
        "middle.c",
        "--dump-types=types1.symtypes",
        "-V",
        "second.c",
        "-T",
        "types2.symtypes",
        "--warnings",
        "third.c",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("ref1.symref", request.reference_files[0]);
    try testing.expectEqualStrings("types2.symtypes", request.dump_types_file.?);

    const expected_rendered = [_][]const u8{
        "--debug",
        "-r",
        "ref1.symref",
        "--dump-types=types1.symtypes",
        "-V",
        "-T",
        "types2.symtypes",
        "--warnings",
        "first.c",
        "middle.c",
        "second.c",
        "third.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--debug\",\"-r\",\"ref1.symref\",\"--dump-types=types1.symtypes\",\"-V\",\"-T\",\"types2.symtypes\",\"--warnings\",\"first.c\",\"middle.c\",\"second.c\",\"third.c\"],\"options\":{\"debug_level\":1,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"ref1.symref\"],\"dump_types_file\":\"types2.symtypes\"}}\n",
        output.written(),
    );
}
