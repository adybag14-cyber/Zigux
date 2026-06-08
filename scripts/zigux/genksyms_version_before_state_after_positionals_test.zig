const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "version flags before positional input remain request side effects before long state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "--version",
        "alpha.c",
        "--debug",
        "--warnings",
        "--quiet",
        "--dump",
        "--preserve",
        "--reference",
        "ref.symversions",
        "--dump-types=types.sym",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("ref.symversions", request.reference_files[0]);
                try testing.expectEqualStrings("types.sym", request.dump_types_file.?);

                const expected_rendered = [_][]const u8{
                    "-V",
                    "--version",
                    "--debug",
                    "--warnings",
                    "--quiet",
                    "--dump",
                    "--preserve",
                    "--reference",
                    "ref.symversions",
                    "--dump-types=types.sym",
                    "alpha.c",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "version before long state renders bridge JSON after delayed positional input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "alpha.c",
        "--debug",
        "--reference=ref.symversions",
        "--dump-types",
        "types.sym",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"--debug\",\"--reference=ref.symversions\",\"--dump-types\",\"types.sym\",\"alpha.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"ref.symversions\"],\"dump_types_file\":\"types.sym\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "version before long state preserves side effects on later invalid long failure" {
    const args = [_][]const u8{
        "-V",
        "--ver",
        "alpha.c",
        "--debug",
        "--bad-option=value",
    };

    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 2), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("--bad-option=value", option),
                else => return error.ExpectedInvalidLongOption,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}
