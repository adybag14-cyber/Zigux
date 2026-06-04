const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "genksyms request keeps raw caller order separate from rendered option order" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input_a.c",
        "--debug",
        "input_b.h",
        "-wqD",
        "--reference",
        "base.symref",
        "-T",
        "types.symtypes",
        "input_c.c",
        "--preserve",
    };
    const expected_rendered = [_][]const u8{
        "--debug",
        "-wqD",
        "--reference",
        "base.symref",
        "-T",
        "types.symtypes",
        "--preserve",
        "input_a.c",
        "input_b.h",
        "input_c.c",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("base.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms rendered bridge uses normalized order without mutating raw args" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "line\nunit.c",
        "--reference",
        "ref\"name.sym",
        "tail\tunit.c",
        "--dump-types=types\\name.symtypes",
    };
    const expected_rendered = [_][]const u8{
        "--reference",
        "ref\"name.sym",
        "--dump-types=types\\name.symtypes",
        "line\nunit.c",
        "tail\tunit.c",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("ref\"name.sym", request.reference_files[0]);
                try testing.expectEqualStrings("types\\name.symtypes", request.dump_types_file.?);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"ref\\\"name.sym\",\"--dump-types=types\\\\name.symtypes\",\"line\\nunit.c\",\"tail\\tunit.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"ref\\\"name.sym\"],\"dump_types_file\":\"types\\\\name.symtypes\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
