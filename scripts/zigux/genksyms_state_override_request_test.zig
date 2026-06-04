const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "genksyms request state keeps version side effects through option overrides" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "input-before.c",
        "-wdqD",
        "--dump-types",
        "types.symtypes",
        "--reference=ref.symref",
        "--ver",
        "--quiet",
        "--preserve",
        "input-after.c",
    };
    const expected_rendered = [_][]const u8{
        "--version",
        "-wdqD",
        "--dump-types",
        "types.symtypes",
        "--reference=ref.symref",
        "--ver",
        "--quiet",
        "--preserve",
        "input-before.c",
        "input-after.c",
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
                try testing.expectEqualStrings("ref.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();
                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"-wdqD\",\"--dump-types\",\"types.symtypes\",\"--reference=ref.symref\",\"--ver\",\"--quiet\",\"--preserve\",\"input-before.c\",\"input-after.c\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[\"ref.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms request state preserves explicit terminator tails after overrides" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-VV",
        "-wqwdD",
        "-Ttypes.symtypes",
        "-r",
        "ref.symref",
        "--",
        "--quiet",
        "tail.c",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(request.warnings);
                try testing.expect(request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("ref.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();
                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VV\",\"-wqwdD\",\"-Ttypes.symtypes\",\"-r\",\"ref.symref\",\"--\",\"--quiet\",\"tail.c\"],\"options\":{\"debug_level\":1,\"warnings\":true,\"dump_defs\":true,\"preserve\":false,\"reference_files\":[\"ref.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
