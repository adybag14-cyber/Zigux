const std = @import("std");

const genksyms = @import("genksyms");

fn expectRequest(arena: std.mem.Allocator, args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(arena, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedGenksymsRequest,
        },
        .failure => error.UnexpectedGenksymsFailure,
    };
}

test "version side effects survive while positional args flush after later options" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "first-positional.c",
        "-d",
        "second-positional.h",
        "--reference",
        "foo.symref",
        "-T",
        "types.symtypes",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try std.testing.expectEqual(@as(usize, 1), request.version_count);
    try std.testing.expectEqual(@as(usize, 1), request.debug_level);
    try std.testing.expect(!request.warnings);
    try std.testing.expect(!request.dump_defs);
    try std.testing.expect(!request.preserve);
    try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
    try std.testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);

    const expected_rendered = [_][]const u8{
        "--version",
        "-d",
        "--reference",
        "foo.symref",
        "-T",
        "types.symtypes",
        "first-positional.c",
        "second-positional.h",
    };
    try std.testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "rendered bridge records flushed positional argv after version side effect" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "leftover-input.c",
        "--warnings",
        "-r",
        "bar.symref",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try std.testing.expectEqual(@as(usize, 1), request.version_count);
    try std.testing.expect(request.warnings);
    try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try std.testing.expectEqualStrings("bar.symref", request.reference_files[0]);

    var output: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-V\",\"--warnings\",\"-r\",\"bar.symref\",\"leftover-input.c\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"bar.symref\"],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
