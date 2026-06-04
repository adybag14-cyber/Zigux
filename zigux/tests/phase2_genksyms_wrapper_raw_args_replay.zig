const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

test "raw args preserve caller order while rendered args normalize delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "leftover.c",
        "-d",
        "--reference",
        "base.symref",
        "rightover.h",
        "-Tinline.types",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);

    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("base.symref", request.reference_files[0]);
                try testing.expectEqualStrings("inline.types", request.dump_types_file.?);

                try testing.expectEqualSlices([]const u8, &args, request.raw_args);

                const expected_rendered = [_][]const u8{
                    "--version",
                    "-d",
                    "--reference",
                    "base.symref",
                    "-Tinline.types",
                    "leftover.c",
                    "rightover.h",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequest,
        },
        else => return error.ExpectedRequest,
    }
}

test "raw args preserve explicit terminator position separately from bridge rendering" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VV",
        "delayed.c",
        "--",
        "-d",
        "--reference",
        "tail.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);

    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);

                try testing.expectEqualSlices([]const u8, &args, request.raw_args);

                const expected_rendered = [_][]const u8{
                    "-VV",
                    "delayed.c",
                    "--",
                    "-d",
                    "--reference",
                    "tail.symref",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

                var rendered: std.Io.Writer.Allocating = .init(testing.allocator);
                defer rendered.deinit();
                try genksyms.renderGenksymsBridge(&rendered.writer, request);
                try testing.expect(std.mem.indexOf(
                    u8,
                    rendered.written(),
                    "\"argv\":[\"scripts/genksyms/genksyms\",\"-VV\",\"delayed.c\",\"--\",\"-d\",\"--reference\",\"tail.symref\"]",
                ) != null);
            },
            else => return error.ExpectedRequest,
        },
        else => return error.ExpectedRequest,
    }
}
