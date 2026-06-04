const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| return request,
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    }
}

test "version side effects coexist with long warning quiet request state" {
    const args = [_][]const u8{
        "--version",
        "-V",
        "--warnings",
        "--quiet",
        "--dump",
        "--preserve",
        "--reference",
        "foo.symref",
        "--dump-types=types.symtypes",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);
    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "abbreviated version keeps short warning quiet last write state" {
    const args = [_][]const u8{
        "--ver",
        "--warn",
        "--qui",
        "-w",
        "-q",
        "-D",
        "-p",
        "-rfoo.symref",
        "-Ttypes.symtypes",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);
    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expect(!request.warnings);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "version warning quiet state renders through bridge JSON" {
    const args = [_][]const u8{
        "--version",
        "--warnings",
        "-q",
        "-D",
        "-p",
        "-r",
        "foo.symref",
        "-T",
        "types.symtypes",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"--warnings\",\"-q\",\"-D\",\"-p\",\"-r\",\"foo.symref\",\"-T\",\"types.symtypes\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[\"foo.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
        output.written(),
    );
}
