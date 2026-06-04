const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectRendered(args: []const []const u8, expected: []const u8) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(expected, output.written());
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "version side effect keeps escaped long option request JSON stable" {
    const args = [_][]const u8{
        "--version",
        "--debug",
        "--reference",
        "ref\"quote\\slash\nline.symref",
        "--dump-types",
        "types\tout\rfile",
        "pos\"arg\\tail\n",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("ref\"quote\\slash\nline.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types\tout\rfile", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
                try testing.expectEqualStrings("--version", request.rendered_args[0]);
                try testing.expectEqualStrings("pos\"arg\\tail\n", request.rendered_args[6]);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"--debug\",\"--reference\",\"ref\\\"quote\\\\slash\\nline.symref\",\"--dump-types\",\"types\\tout\\rfile\",\"pos\\\"arg\\\\tail\\n\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"ref\\\"quote\\\\slash\\nline.symref\"],\"dump_types_file\":\"types\\tout\\rfile\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "clustered versions keep short option escaped request JSON stable" {
    const args = [_][]const u8{
        "-VVw",
        "-rref\tone",
        "-Ttype\\\"two",
        "tail\rname",
    };

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("ref\tone", request.reference_files[0]);
                try testing.expectEqualStrings("type\\\"two", request.dump_types_file.?);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }

    try expectRendered(
        &args,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VVw\",\"-rref\\tone\",\"-Ttype\\\\\\\"two\",\"tail\\rname\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"ref\\tone\"],\"dump_types_file\":\"type\\\\\\\"two\"}}\n",
    );
}
