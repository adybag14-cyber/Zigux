const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "genksyms wrapper escapes rendered argv after version side effects" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "--reference",
        "ref\"quote.sym",
        "--dump-types=types\\tab\tout.symtypes",
        "left\nunit.c",
        "-d",
        "right\rtail.h",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("ref\"quote.sym", request.reference_files[0]);
    try testing.expectEqualStrings("types\\tab\tout.symtypes", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
    try testing.expectEqualStrings("--version", request.rendered_args[0]);
    try testing.expectEqualStrings("--reference", request.rendered_args[1]);
    try testing.expectEqualStrings("ref\"quote.sym", request.rendered_args[2]);
    try testing.expectEqualStrings("--dump-types=types\\tab\tout.symtypes", request.rendered_args[3]);
    try testing.expectEqualStrings("-d", request.rendered_args[4]);
    try testing.expectEqualStrings("left\nunit.c", request.rendered_args[5]);
    try testing.expectEqualStrings("right\rtail.h", request.rendered_args[6]);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    const written = output.written();

    try expectContains(written, "ref\\\"quote.sym");
    try expectContains(written, "types\\\\tab\\tout.symtypes");
    try expectContains(written, "left\\nunit.c");
    try expectContains(written, "right\\rtail.h");
    try testing.expectEqual(@as(usize, 1), std.mem.count(u8, written, "\n"));
    try testing.expect(std.mem.indexOfScalar(u8, written[0 .. written.len - 1], '\r') == null);
    try testing.expect(std.mem.indexOfScalar(u8, written, '\t') == null);
}

test "genksyms wrapper escapes option metadata arrays after abbreviated version" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--reference=first\\path.sym",
        "--reference",
        "second\npath.sym",
        "--dump-types",
        "types\"final.symtypes",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena_state.allocator(), &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("first\\path.sym", request.reference_files[0]);
    try testing.expectEqualStrings("second\npath.sym", request.reference_files[1]);
    try testing.expectEqualStrings("types\"final.symtypes", request.dump_types_file.?);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    const written = output.written();

    try expectContains(written, "first\\\\path.sym");
    try expectContains(written, "second\\npath.sym");
    try expectContains(written, "types\\\"final.symtypes");
    try testing.expectEqual(@as(usize, 1), std.mem.count(u8, written, "\n"));
}
