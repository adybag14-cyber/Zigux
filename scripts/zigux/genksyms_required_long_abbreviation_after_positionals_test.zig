const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "required long abbreviations consume values after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first-pos.c",
        "--ref",
        "one.symref",
        "--dump-ty",
        "one.symtypes",
        "second-pos.c",
        "--refer=two.symref",
        "--dump-types=two.symtypes",
        "--reference",
        "--literal-reference-value",
        "--dump-t",
        "--literal-dump-types-value",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 3), request.reference_files.len);
                try testing.expectEqualStrings("one.symref", request.reference_files[0]);
                try testing.expectEqualStrings("two.symref", request.reference_files[1]);
                try testing.expectEqualStrings("--literal-reference-value", request.reference_files[2]);
                try testing.expectEqualStrings("--literal-dump-types-value", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.version_count);

                const expected_rendered = [_][]const u8{
                    "--ref",
                    "one.symref",
                    "--dump-ty",
                    "one.symtypes",
                    "--refer=two.symref",
                    "--dump-types=two.symtypes",
                    "--reference",
                    "--literal-reference-value",
                    "--dump-t",
                    "--literal-dump-types-value",
                    "first-pos.c",
                    "second-pos.c",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    }
}

test "required long abbreviation bridge renders consumed option-looking values as option data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "--ref",
        "--reference-looking-value",
        "--dump-t",
        "--dump-types-looking-value",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--ref\",\"--reference-looking-value\",\"--dump-t\",\"--dump-types-looking-value\",\"input.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"--reference-looking-value\"],\"dump_types_file\":\"--dump-types-looking-value\"}}\n",
        output.written(),
    );
}
