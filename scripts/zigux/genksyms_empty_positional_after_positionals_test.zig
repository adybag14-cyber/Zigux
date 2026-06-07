const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "empty positional suppresses pure version promotion after delayed input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "",
        "-V",
        "--ver",
        "-VV",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 4), request.version_count);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try testing.expectEqualStrings("-V", request.rendered_args[0]);
                try testing.expectEqualStrings("--ver", request.rendered_args[1]);
                try testing.expectEqualStrings("-VV", request.rendered_args[2]);
                try testing.expectEqualStrings("", request.rendered_args[3]);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "empty positional participates in normalized bridge argv after required data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "before.c",
        "",
        "--reference",
        "refs.symref",
        "-Ttypes.symtypes",
        "--warnings",
        "after.h",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("refs.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);

                const expected_rendered = [_][]const u8{
                    "--reference",
                    "refs.symref",
                    "-Ttypes.symtypes",
                    "--warnings",
                    "before.c",
                    "",
                    "after.h",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"refs.symref\",\"-Ttypes.symtypes\",\"--warnings\",\"before.c\",\"\",\"after.h\"],\"options\":{\"debug_level\":0,\"warnings\":true,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"refs.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "empty positional keeps version side effect before later failure" {
    const args = [_][]const u8{
        "",
        "--version",
        "--help=extra",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--help", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
