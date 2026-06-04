const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        .failure => error.UnexpectedParseFailure,
    };
}

test "bridge JSON escapes reference files and dump types option values" {
    const args = [_][]const u8{
        "--reference=alpha\nbeta.symref",
        "--reference",
        "quoted\"ref\\tail.symref",
        "--dump-types",
        "types\twith\"quote\\tail.symtypes",
        "--preserve",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("alpha\nbeta.symref", request.reference_files[0]);
    try testing.expectEqualStrings("quoted\"ref\\tail.symref", request.reference_files[1]);
    try testing.expectEqualStrings("types\twith\"quote\\tail.symtypes", request.dump_types_file.?);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference=alpha\\nbeta.symref\",\"--reference\",\"quoted\\\"ref\\\\tail.symref\",\"--dump-types\",\"types\\twith\\\"quote\\\\tail.symtypes\",\"--preserve\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":true,\"reference_files\":[\"alpha\\nbeta.symref\",\"quoted\\\"ref\\\\tail.symref\"],\"dump_types_file\":\"types\\twith\\\"quote\\\\tail.symtypes\"}}\n",
        output.written(),
    );
}

test "bridge JSON escapes attached short option values in the options payload" {
    const args = [_][]const u8{
        "-ralpha\\short\nref.symref",
        "-Ttypes\\short\tout.symtypes",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("alpha\\short\nref.symref", request.reference_files[0]);
    try testing.expectEqualStrings("types\\short\tout.symtypes", request.dump_types_file.?);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expect(std.mem.containsAtLeast(
        u8,
        output.written(),
        1,
        "\"reference_files\":[\"alpha\\\\short\\nref.symref\"]",
    ));
    try testing.expect(std.mem.containsAtLeast(
        u8,
        output.written(),
        1,
        "\"dump_types_file\":\"types\\\\short\\tout.symtypes\"",
    ));
}
