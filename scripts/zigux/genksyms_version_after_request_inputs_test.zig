const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

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

test "version flags after request inputs stay request side effects" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const allocator = arena_state.allocator();

    const args = [_][]const u8{
        "-r",
        "base.symref",
        "-V",
        "--ver",
        "-VV",
        "--dump-types",
        "types.symtypes",
    };
    const request = try expectRequest(allocator, &args);

    try testing.expectEqual(@as(usize, 4), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("base.symref", request.reference_files[0]);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    const render_request = genksyms.Request{
        .raw_args = &args,
        .rendered_args = request.rendered_args,
        .debug_level = request.debug_level,
        .warnings = request.warnings,
        .dump_defs = request.dump_defs,
        .preserve = request.preserve,
        .reference_files = request.reference_files,
        .dump_types_file = request.dump_types_file,
        .version_count = request.version_count,
    };
    try genksyms.renderGenksymsBridge(&output.writer, render_request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-r\",\"base.symref\",\"-V\",\"--ver\",\"-VV\",\"--dump-types\",\"types.symtypes\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"base.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
        output.written(),
    );
}

test "pure versions followed by a positional become rendered request args" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "-VV",
        "leftover.c",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 3), request.version_count);
    try testing.expectEqual(@as(usize, 3), request.rendered_args.len);
    try testing.expectEqualStrings("--version", request.rendered_args[0]);
    try testing.expectEqualStrings("-VV", request.rendered_args[1]);
    try testing.expectEqualStrings("leftover.c", request.rendered_args[2]);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
}
