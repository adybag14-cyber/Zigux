const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "genksyms terminator keeps required-looking long options after delayed positionals as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "prelude.c",
        "--debug",
        "middle.h",
        "--",
        "--reference",
        "after.symref",
        "--dump-types",
        "after.symtypes",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqual(@as(usize, 8), request.rendered_args.len);
    try testing.expectEqualStrings("--debug", request.rendered_args[0]);
    try testing.expectEqualStrings("prelude.c", request.rendered_args[1]);
    try testing.expectEqualStrings("middle.h", request.rendered_args[2]);
    try testing.expectEqualStrings("--", request.rendered_args[3]);
    try testing.expectEqualStrings("--reference", request.rendered_args[4]);
    try testing.expectEqualStrings("after.symref", request.rendered_args[5]);
    try testing.expectEqualStrings("--dump-types", request.rendered_args[6]);
    try testing.expectEqualStrings("after.symtypes", request.rendered_args[7]);
}

test "genksyms terminator keeps required-looking short tails after parsed required options as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "before.symref",
        "input.c",
        "-Tbefore.symtypes",
        "--",
        "-rpost.symref",
        "-Tpost.symtypes",
        "--reference=tail.symref",
        "--dump-types=tail.symtypes",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("before.symref", request.reference_files[0]);
    try testing.expectEqualStrings("before.symtypes", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 9), request.rendered_args.len);
    try testing.expectEqualStrings("--reference", request.rendered_args[0]);
    try testing.expectEqualStrings("before.symref", request.rendered_args[1]);
    try testing.expectEqualStrings("-Tbefore.symtypes", request.rendered_args[2]);
    try testing.expectEqualStrings("input.c", request.rendered_args[3]);
    try testing.expectEqualStrings("--", request.rendered_args[4]);
    try testing.expectEqualStrings("-rpost.symref", request.rendered_args[5]);
    try testing.expectEqualStrings("-Tpost.symtypes", request.rendered_args[6]);
    try testing.expectEqualStrings("--reference=tail.symref", request.rendered_args[7]);
    try testing.expectEqualStrings("--dump-types=tail.symtypes", request.rendered_args[8]);
}

test "genksyms bridge renders terminator tail without promoting post-terminator required options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-Vd",
        "left.c",
        "--",
        "--reference",
        "after.symref",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-Vd\",\"left.c\",\"--\",\"--reference\",\"after.symref\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
