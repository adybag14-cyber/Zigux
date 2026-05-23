const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay keeps single version side effect in rendered request plan" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "--reference",
        "foo.symref",
        "leftover.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 1), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try std.testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try std.testing.expectEqualStrings("--version", request.rendered_args[0]);
                try std.testing.expectEqualStrings("--reference", request.rendered_args[1]);
                try std.testing.expectEqualStrings("foo.symref", request.rendered_args[2]);
                try std.testing.expectEqualStrings("leftover.c", request.rendered_args[3]);

                var output: std.Io.Writer.Allocating = .init(std.testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try std.testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"--reference\",\"foo.symref\",\"leftover.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"foo.symref\"],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay keeps abbreviated version side effect in rendered request plan" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "-d",
        "rightover.h",
        "-T",
        "types.symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 1), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try std.testing.expectEqual(@as(usize, 5), request.rendered_args.len);
                try std.testing.expectEqualStrings("--ver", request.rendered_args[0]);
                try std.testing.expectEqualStrings("-d", request.rendered_args[1]);
                try std.testing.expectEqualStrings("-T", request.rendered_args[2]);
                try std.testing.expectEqualStrings("types.symtypes", request.rendered_args[3]);
                try std.testing.expectEqualStrings("rightover.h", request.rendered_args[4]);

                var output: std.Io.Writer.Allocating = .init(std.testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try std.testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--ver\",\"-d\",\"-T\",\"types.symtypes\",\"rightover.h\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":\"types.symtypes\"}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
