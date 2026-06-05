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
        .failure => error.ExpectedRequestCommand,
    };
}

fn expectBridge(request: genksyms.Request, expected: []const u8) !void {
    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(expected, output.written());
}

test "positional request input preserves repeated later reference ordering" {
    const args = [_][]const u8{
        "input.c",
        "--reference",
        "first.symref",
        "-rsecond.symref",
        "--reference=third.symref",
        "--dump-types",
        "types.symtypes",
    };
    const expected_rendered = [_][]const u8{
        "--reference",
        "first.symref",
        "-rsecond.symref",
        "--reference=third.symref",
        "--dump-types",
        "types.symtypes",
        "input.c",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expectEqual(@as(usize, 3), request.reference_files.len);
    try testing.expectEqualStrings("first.symref", request.reference_files[0]);
    try testing.expectEqualStrings("second.symref", request.reference_files[1]);
    try testing.expectEqualStrings("third.symref", request.reference_files[2]);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);

    try expectBridge(
        request,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"first.symref\",\"-rsecond.symref\",\"--reference=third.symref\",\"--dump-types\",\"types.symtypes\",\"input.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"first.symref\",\"second.symref\",\"third.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
    );
}

test "lone dash request input lets later dump types override earlier values" {
    const args = [_][]const u8{
        "-",
        "--dump-types=early.types",
        "-T",
        "middle.types",
        "-Tlate.types",
        "--reference",
        "after.symref",
    };
    const expected_rendered = [_][]const u8{
        "--dump-types=early.types",
        "-T",
        "middle.types",
        "-Tlate.types",
        "--reference",
        "after.symref",
        "-",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("after.symref", request.reference_files[0]);
    try testing.expectEqualStrings("late.types", request.dump_types_file.?);

    try expectBridge(
        request,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--dump-types=early.types\",\"-T\",\"middle.types\",\"-Tlate.types\",\"--reference\",\"after.symref\",\"-\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"after.symref\"],\"dump_types_file\":\"late.types\"}}\n",
    );
}

test "required option values after request input can look like repeated options" {
    const args = [_][]const u8{
        "seed.sym",
        "--reference",
        "-rnot-an-option.symref",
        "--dump-types",
        "-Tnot-an-option.types",
        "--reference",
        "--dump-types",
    };
    const expected_rendered = [_][]const u8{
        "--reference",
        "-rnot-an-option.symref",
        "--dump-types",
        "-Tnot-an-option.types",
        "--reference",
        "--dump-types",
        "seed.sym",
    };

    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqualSlices([]const u8, &args, request.raw_args);
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
    try testing.expectEqual(@as(usize, 2), request.reference_files.len);
    try testing.expectEqualStrings("-rnot-an-option.symref", request.reference_files[0]);
    try testing.expectEqualStrings("--dump-types", request.reference_files[1]);
    try testing.expectEqualStrings("-Tnot-an-option.types", request.dump_types_file.?);

    try expectBridge(
        request,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"-rnot-an-option.symref\",\"--dump-types\",\"-Tnot-an-option.types\",\"--reference\",\"--dump-types\",\"seed.sym\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"-rnot-an-option.symref\",\"--dump-types\"],\"dump_types_file\":\"-Tnot-an-option.types\"}}\n",
    );
}
