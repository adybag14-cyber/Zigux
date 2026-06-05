const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "dump and preserve long flags remain request state after positional input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "symbols.i",
        "--dump",
        "--preserve",
        "--reference",
        "base.symref",
        "--dump-types",
        "types.symtypes",
    };
    const request = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (request) {
        .command => |command| switch (command) {
            .request => |parsed| {
                try testing.expect(parsed.dump_defs);
                try testing.expect(parsed.preserve);
                try testing.expect(!parsed.warnings);
                try testing.expectEqual(@as(usize, 0), parsed.debug_level);
                try testing.expectEqual(@as(usize, 1), parsed.reference_files.len);
                try testing.expectEqualStrings("base.symref", parsed.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", parsed.dump_types_file.?);

                const expected_rendered = [_][]const u8{
                    "--dump",
                    "--preserve",
                    "--reference",
                    "base.symref",
                    "--dump-types",
                    "types.symtypes",
                    "symbols.i",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, parsed.rendered_args);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();
                try genksyms.renderGenksymsBridge(&output.writer, parsed);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--dump\",\"--preserve\",\"--reference\",\"base.symref\",\"--dump-types\",\"types.symtypes\",\"symbols.i\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[\"base.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "clustered dump preserve flags remain request state after lone dash input" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-",
        "-Dp",
        "--warnings",
        "--quiet",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);

                const expected_rendered = [_][]const u8{
                    "-Dp",
                    "--warnings",
                    "--quiet",
                    "-",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "required option data that looks like dump stays data before later preserve" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-r",
        "--dump",
        "payload.i",
        "--preserve",
        "--dump",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("--dump", request.reference_files[0]);

                const expected_rendered = [_][]const u8{
                    "-r",
                    "--dump",
                    "--preserve",
                    "--dump",
                    "payload.i",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
