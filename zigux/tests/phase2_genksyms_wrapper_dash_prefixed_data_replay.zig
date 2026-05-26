const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay keeps dash-prefixed short option arguments as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-r",
        "-d",
        "-T",
        "--symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-d", request.reference_files[0]);
    try testing.expectEqualStrings("--symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var rendered: std.Io.Writer.Allocating = .init(testing.allocator);
    defer rendered.deinit();
    try genksyms.renderGenksymsBridge(&rendered.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-r\",\"-d\",\"-T\",\"--symtypes\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"-d\"],\"dump_types_file\":\"--symtypes\"}}\n",
        rendered.written(),
    );
}

test "phase2 genksyms wrapper replay keeps dash-prefixed long option arguments as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "--debug",
        "--dump-types",
        "--types",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--debug", request.reference_files[0]);
    try testing.expectEqualStrings("--types", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var rendered: std.Io.Writer.Allocating = .init(testing.allocator);
    defer rendered.deinit();
    try genksyms.renderGenksymsBridge(&rendered.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"--debug\",\"--dump-types\",\"--types\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--debug\"],\"dump_types_file\":\"--types\"}}\n",
        rendered.written(),
    );
}
